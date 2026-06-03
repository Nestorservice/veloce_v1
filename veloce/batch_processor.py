from pathlib import Path
from collections import defaultdict


class BatchProcessor:
    def __init__(self, batch_size: int = 15):
        self._batch_size = batch_size

    def make_batches(self, files: list[Path]) -> list[list[Path]]:
        if not files:
            return []

        by_dir: dict[str, list[Path]] = defaultdict(list)
        for f in files:
            by_dir[str(f.parent)].append(f)

        batches, current = [], []
        for dir_files in by_dir.values():
            for f in dir_files:
                current.append(f)
                if len(current) >= self._batch_size:
                    batches.append(current)
                    current = []
        if current:
            batches.append(current)
        return batches
