import json
from unittest.mock import patch, MagicMock
from veloce.sast import SASTScanner


def proc(returncode, stdout="", stderr=""):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


def test_clean_code_passes():
    scanner = SASTScanner(go_path="C:\\fake\\backend")
    with patch("subprocess.run", return_value=proc(0, stdout='{"Issues":[]}')):
        result = scanner.scan()
    assert result.safe is True
    assert result.blocks_push is False


def test_detects_high_severity_vulnerability():
    issue = [{"severity": "HIGH", "rule_id": "G401", "details": "Weak crypto", "file": "main.go", "line": "10"}]
    scanner = SASTScanner(go_path="C:\\fake\\backend")
    with patch("subprocess.run", return_value=proc(1, stdout=json.dumps(issue))):
        result = scanner.scan()
    assert result.safe is False
    assert result.blocks_push is True
    assert result.issues[0]["rule_id"] == "G401"


def test_low_severity_does_not_block_push():
    issue = [{"severity": "LOW", "rule_id": "G104", "details": "Errors unhandled", "file": "main.go", "line": "5"}]
    scanner = SASTScanner(go_path="C:\\fake\\backend")
    with patch("subprocess.run", return_value=proc(1, stdout=json.dumps(issue))):
        result = scanner.scan()
    assert result.safe is False
    assert result.blocks_push is False
