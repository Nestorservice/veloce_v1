import subprocess


class GitAutomator:
    def __init__(self, repo_path: str):
        self._repo_path = repo_path

    def commit_and_push(self, files: list[str], module_name: str, batch_index: int) -> None:
        self._run(["git", "add"] + files)
        msg = f"feat(migration): migrate {module_name} batch-{batch_index:03d}"
        self._run(["git", "commit", "-m", msg])
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=self._repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git push a echoue : {result.stderr}")

    def _run(self, cmd: list[str]) -> None:
        result = subprocess.run(cmd, cwd=self._repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Commande '{' '.join(cmd[:2])}' a echoue : {result.stderr}")
