import os
import subprocess
from dataclasses import dataclass


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
        result = subprocess.run(
            ["flutter", "analyze"],
            cwd=self._flutter_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return CompileResult(success=True)
        return CompileResult(success=False, errors=result.stdout + result.stderr)
