import subprocess


class MachineGuard:
    def __init__(self, cleanup_every: int, go_path: str, flutter_path: str):
        self._every = cleanup_every
        self._go_path = go_path
        self._flutter_path = flutter_path

    def tick(self, file_count: int) -> None:
        if file_count % self._every == 0:
            self._run_cleanup()

    def _run_cleanup(self) -> None:
        subprocess.run(["go", "clean", "-cache"], cwd=self._go_path, capture_output=True)
        subprocess.run(["flutter", "clean"], cwd=self._flutter_path, capture_output=True)
