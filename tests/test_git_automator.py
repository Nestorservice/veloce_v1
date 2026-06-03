import pytest
from unittest.mock import patch, MagicMock
from veloce.git_automator import GitAutomator


def ok():
    m = MagicMock()
    m.returncode = 0
    m.stdout = ""
    m.stderr = ""
    return m


def fail(msg="error"):
    m = MagicMock()
    m.returncode = 1
    m.stdout = ""
    m.stderr = msg
    return m


def test_commit_and_push_calls_add_commit_push():
    automator = GitAutomator(repo_path="C:\\fake\\repo")
    with patch("subprocess.run", return_value=ok()) as mock_run:
        automator.commit_and_push(files=["backend/main.go"], module_name="auth", batch_index=1)
    commands = [c.args[0] for c in mock_run.call_args_list]
    assert any("add" in cmd for cmd in commands)
    assert any("commit" in cmd for cmd in commands)
    assert any("push" in cmd for cmd in commands)


def test_commit_message_contains_module_and_batch():
    automator = GitAutomator(repo_path="C:\\fake\\repo")
    with patch("subprocess.run", return_value=ok()) as mock_run:
        automator.commit_and_push(files=["backend/main.go"], module_name="user-auth", batch_index=5)
    commit_call = next(c for c in mock_run.call_args_list if "commit" in c.args[0])
    msg = " ".join(commit_call.args[0])
    assert "user-auth" in msg
    assert "005" in msg


def test_raises_on_push_failure():
    automator = GitAutomator(repo_path="C:\\fake\\repo")
    with patch("subprocess.run", side_effect=[ok(), ok(), fail("rejected")]):
        with pytest.raises(RuntimeError, match="git push"):
            automator.commit_and_push(files=["backend/main.go"], module_name="auth", batch_index=1)
