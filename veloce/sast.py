import json
import subprocess
from dataclasses import dataclass, field

_BLOCKING_SEVERITIES = {"HIGH", "CRITICAL"}


@dataclass
class SASTResult:
    safe: bool
    issues: list[dict] = field(default_factory=list)
    blocks_push: bool = False


class SASTScanner:
    def __init__(self, go_path: str):
        self._go_path = go_path

    def scan(self) -> SASTResult:
        result = subprocess.run(
            ["gosec", "-fmt=json", "./..."],
            cwd=self._go_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return SASTResult(safe=True)

        issues = self._parse_issues(result.stdout)
        blocks = any(i.get("severity", "").upper() in _BLOCKING_SEVERITIES for i in issues)
        return SASTResult(safe=False, issues=issues, blocks_push=blocks)

    def _parse_issues(self, output: str) -> list[dict]:
        try:
            parsed = json.loads(output)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return parsed.get("Issues", [])
        except (json.JSONDecodeError, AttributeError):
            pass
        return []
