import time
from dataclasses import dataclass, field
from pathlib import Path
from veloce.prompts import GO_PROMPT, DART_PROMPT
from veloce.ai_client import AIClient


@dataclass
class GenerationResult:
    go_files: list[str] = field(default_factory=list)
    dart_files: list[str] = field(default_factory=list)
    batch_index: int = 0


class CodeGenerator:
    def __init__(self, ai_client: AIClient, go_output: str, flutter_output: str, sleep_seconds: int = 10):
        self._ai = ai_client
        self._go_out = Path(go_output)
        self._dart_out = Path(flutter_output)
        self._sleep = sleep_seconds

    async def translate_batch(self, files: list[Path], batch_index: int) -> GenerationResult:
        result = GenerationResult(batch_index=batch_index)
        if not files:
            return result

        php_files = [f for f in files if f.suffix == ".php" and ".blade." not in f.name]
        blade_files = [f for f in files if ".blade.php" in f.name]

        if php_files:
            content = self._read_files(php_files)
            code = await self._ai.complete(GO_PROMPT.format(php_content=content))
            out = self._go_out / f"batch_{batch_index:03d}" / "generated.go"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(code, encoding="utf-8")
            result.go_files.append(str(out))
            if self._sleep:
                time.sleep(self._sleep)

        if blade_files:
            content = self._read_files(blade_files)
            code = await self._ai.complete(DART_PROMPT.format(blade_content=content))
            out = self._dart_out / f"batch_{batch_index:03d}" / "generated.dart"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(code, encoding="utf-8")
            result.dart_files.append(str(out))

        return result

    def _read_files(self, files: list[Path]) -> str:
        parts = []
        for f in files:
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                parts.append(f"### {f.name} ###\n{text}\n")
            except OSError:
                pass
        return "\n".join(parts)
