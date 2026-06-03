from unittest.mock import patch, MagicMock
from veloce.compiler import Compiler


def proc(returncode=0, stdout="", stderr=""):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


def test_go_build_success():
    compiler = Compiler(go_path="C:\\fake\\backend", flutter_path="C:\\fake\\frontend", cpu_cores=2)
    with patch("subprocess.run", return_value=proc(0)):
        result = compiler.build_go()
    assert result.success is True
    assert result.errors == ""


def test_go_build_failure_captures_stderr():
    compiler = Compiler(go_path="C:\\fake\\backend", flutter_path="C:\\fake\\frontend", cpu_cores=2)
    with patch("subprocess.run", return_value=proc(1, stderr="./main.go:5: undefined: foo")):
        result = compiler.build_go()
    assert result.success is False
    assert "undefined: foo" in result.errors


def test_flutter_analyze_success():
    compiler = Compiler(go_path="C:\\fake\\backend", flutter_path="C:\\fake\\frontend", cpu_cores=2)
    with patch("subprocess.run", return_value=proc(0, stdout="No issues found!")):
        result = compiler.analyze_flutter()
    assert result.success is True


def test_go_build_sets_gomaxprocs():
    compiler = Compiler(go_path="C:\\fake\\backend", flutter_path="C:\\fake\\frontend", cpu_cores=2)
    with patch("subprocess.run", return_value=proc(0)) as mock_run:
        compiler.build_go()
    env = mock_run.call_args.kwargs.get("env", {})
    assert env.get("GOMAXPROCS") == "2"
