from pathlib import Path

_EXCLUDED_DIR_NAMES = {"vendor", "node_modules", ".git", "public"}
_EXCLUDED_PARTIAL = {"cache", "logs", "compiled", "framework"}


class PHPScanner:
    def __init__(self, source_path: str):
        self._root = Path(source_path)

    def scan(self) -> list[Path]:
        return sorted(
            p for p in self._root.rglob("*")
            if p.is_file()
            and not self._is_excluded(p)
            and (p.suffix == ".php" or p.name.endswith(".blade.php"))
        )

    def _is_excluded(self, path: Path) -> bool:
        parts = path.relative_to(self._root).parts
        for part in parts[:-1]:
            if part in _EXCLUDED_DIR_NAMES:
                return True
            if any(excl in part for excl in _EXCLUDED_PARTIAL):
                return True
        return False
