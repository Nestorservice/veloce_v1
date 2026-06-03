import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from veloce.compiler import Compiler


def proc(returncode=0, stdout="", stderr=""):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


@pytest.fixture
def go_dir(tmp_path):
    """Repertoire Go avec go.mod present (requis pour build_go)."""
    (tmp_path / "go.mod").write_text("module veloce/backend\n\ngo 1.21\n")
    return str(tmp_path)


def test_go_build_success(go_dir):
    compiler = Compiler(go_path=go_dir, flutter_path="C:\\fake\\frontend", cpu_cores=2)
    with patch("subprocess.run", return_value=proc(0)):
        result = compiler.build_go()
    assert result.success is True
    assert result.errors == ""


def test_go_build_failure_captures_stderr(go_dir):
    compiler = Compiler(go_path=go_dir, flutter_path="C:\\fake\\frontend", cpu_cores=2)
    with patch("subprocess.run", return_value=proc(1, stderr="./main.go:5: undefined: foo")):
        result = compiler.build_go()
    assert result.success is False
    assert "undefined: foo" in result.errors


def test_go_build_skips_when_no_gomod():
    """Sans go.mod, build_go retourne succes (rien a compiler encore)."""
    compiler = Compiler(go_path="C:\\fake\\no-module", flutter_path="C:\\fake\\frontend", cpu_cores=2)
    result = compiler.build_go()
    assert result.success is True


def test_flutter_analyze_skips_when_no_pubspec():
    """Sans pubspec.yaml, analyze_flutter retourne succes (projet pas encore cree)."""
    compiler = Compiler(go_path="C:\\fake\\backend", flutter_path="C:\\fake\\no-flutter", cpu_cores=2)
    result = compiler.analyze_flutter()
    assert result.success is True


def test_flutter_analyze_success(tmp_path):
    (tmp_path / "pubspec.yaml").write_text("name: test\n")
    compiler = Compiler(go_path="C:\\fake\\backend", flutter_path=str(tmp_path), cpu_cores=2)
    with patch("shutil.which", return_value="flutter"), \
         patch("subprocess.run", return_value=proc(0, stdout="No issues found!")):
        result = compiler.analyze_flutter()
    assert result.success is True


def test_go_build_sets_gomaxprocs(go_dir):
    compiler = Compiler(go_path=go_dir, flutter_path="C:\\fake\\frontend", cpu_cores=2)
    with patch("subprocess.run", return_value=proc(0)) as mock_run:
        compiler.build_go()
    env = mock_run.call_args.kwargs.get("env", {})
    assert env.get("GOMAXPROCS") == "2"
