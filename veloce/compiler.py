import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompileResult:
    success: bool
    errors: str = ""


class Compiler:
    def __init__(self, go_path: str, flutter_path: str, cpu_cores: int = 2):
        self._go_path = go_path
        self._flutter_path = flutter_path
        self._cpu_cores = cpu_cores

    def build_go(self) -> CompileResult:
        # Si pas de go.mod, rien a compiler encore
        if not (Path(self._go_path) / "go.mod").exists():
            return CompileResult(success=True)
        env = os.environ.copy()
        env["GOMAXPROCS"] = str(self._cpu_cores)
        result = subprocess.run(
            ["go", "build", "./..."],
            cwd=self._go_path,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode == 0:
            return CompileResult(success=True)
        return CompileResult(success=False, errors=result.stderr or result.stdout)

    def analyze_flutter(self) -> CompileResult:
        # Pas de projet Flutter initialise : rien a analyser
        if not (Path(self._flutter_path) / "pubspec.yaml").exists():
            return CompileResult(success=True)
        # Chercher flutter dans le PATH (Windows : flutter ou flutter.bat)
        flutter_bin = shutil.which("flutter") or shutil.which("flutter.bat")
        if not flutter_bin:
            print("  [Info] flutter introuvable dans PATH subprocess — analyse ignoree")
            return CompileResult(success=True)
        result = subprocess.run(
            [flutter_bin, "analyze"],
            cwd=self._flutter_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return CompileResult(success=True)
        return CompileResult(success=False, errors=result.stdout + result.stderr)
