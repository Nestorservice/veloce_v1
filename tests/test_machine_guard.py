from unittest.mock import patch, MagicMock
from veloce.machine_guard import MachineGuard


def test_cleanup_fires_at_correct_intervals():
    guard = MachineGuard(cleanup_every=50, go_path="C:\\fake\\backend", flutter_path="C:\\fake\\frontend")
    with patch.object(guard, "_run_cleanup") as mock_clean:
        for i in range(1, 151):
            guard.tick(i)
    assert mock_clean.call_count == 3  # a 50, 100, 150


def test_cleanup_not_called_before_threshold():
    guard = MachineGuard(cleanup_every=50, go_path="C:\\fake\\backend", flutter_path="C:\\fake\\frontend")
    with patch.object(guard, "_run_cleanup") as mock_clean:
        for i in range(1, 50):
            guard.tick(i)
    mock_clean.assert_not_called()


def test_run_cleanup_calls_go_and_flutter_clean():
    guard = MachineGuard(cleanup_every=50, go_path="C:\\fake\\backend", flutter_path="C:\\fake\\frontend")
    with patch("subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:
        guard._run_cleanup()
    commands = [" ".join(c.args[0]) for c in mock_run.call_args_list]
    assert any("go clean" in c for c in commands)
    assert any("flutter clean" in c for c in commands)
