from pathlib import Path
from veloce.batch_processor import BatchProcessor


def paths(names):
    return [Path(f"app/{n}") for n in names]


def test_splits_into_correct_max_size():
    files = paths([f"file{i}.php" for i in range(50)])
    batches = BatchProcessor(batch_size=15).make_batches(files)
    assert all(len(b) <= 15 for b in batches)
    assert sum(len(b) for b in batches) == 50


def test_groups_same_directory_together():
    files = [
        Path("app/Models/User.php"),
        Path("app/Models/Post.php"),
        Path("app/Http/Controllers/UserController.php"),
        Path("resources/views/home.blade.php"),
    ]
    batches = BatchProcessor(batch_size=15).make_batches(files)
    all_files = [f for b in batches for f in b]
    assert set(all_files) == set(files)


def test_empty_input_returns_empty():
    assert BatchProcessor(batch_size=15).make_batches([]) == []


def test_single_batch_for_few_files():
    batches = BatchProcessor(batch_size=15).make_batches(paths(["a.php", "b.php"]))
    assert len(batches) == 1
