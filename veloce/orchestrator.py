import subprocess
from pathlib import Path

from veloce.config import Config
from veloce.ai_client import AIClient
from veloce.php_scanner import PHPScanner
from veloce.batch_processor import BatchProcessor
from veloce.code_generator import CodeGenerator
from veloce.compiler import Compiler
from veloce.sast import SASTScanner
from veloce.git_automator import GitAutomator
from veloce.machine_guard import MachineGuard


class Orchestrator:
    def __init__(self, config: Config):
        cfg = config
        work = cfg.mirror_work_path
        self._ai = AIClient(cfg)
        self._scanner = PHPScanner(work)
        self._batcher = BatchProcessor(cfg.batch_size)
        self._generator = CodeGenerator(
            self._ai,
            go_output=f"{work}\\target\\backend",
            flutter_output=f"{work}\\target\\frontend",
            sleep_seconds=cfg.sleep_between_files,
        )
        self._compiler = Compiler(
            go_path=f"{work}\\target\\backend",
            flutter_path=f"{work}\\target\\frontend",
            cpu_cores=cfg.cpu_cores_limit,
        )
        self._sast = SASTScanner(go_path=f"{work}\\target\\backend")
        self._git = GitAutomator(repo_path=work)
        self._guard = MachineGuard(
            cleanup_every=cfg.files_before_cleanup,
            go_path=f"{work}\\target\\backend",
            flutter_path=f"{work}\\target\\frontend",
        )
        self._cfg = cfg

    def _setup_targets(self) -> None:
        """Cree les repertoires cibles et initialise le module Go si absent."""
        work = self._cfg.mirror_work_path
        go_path = Path(f"{work}\\target\\backend")
        flutter_path = Path(f"{work}\\target\\frontend")
        go_path.mkdir(parents=True, exist_ok=True)
        flutter_path.mkdir(parents=True, exist_ok=True)
        if not (go_path / "go.mod").exists():
            subprocess.run(
                ["go", "mod", "init", "veloce/backend"],
                cwd=go_path,
                capture_output=True,
            )
            print("[Veloce] go.mod initialise dans target/backend")

    async def run(self) -> None:
        self._setup_targets()
        print("[Veloce] Scan PHP en cours...")
        files = self._scanner.scan()
        print(f"[Veloce] {len(files)} fichiers detectes.")

        batches = self._batcher.make_batches(files)
        print(f"[Veloce] {len(batches)} batches de {self._cfg.batch_size} fichiers max.\n")

        total_files = 0
        for idx, batch in enumerate(batches, 1):
            print(f"--- Batch {idx}/{len(batches)} ({len(batch)} fichiers) ---")

            gen = await self._generator.translate_batch(batch, idx)
            total_files += len(batch)

            # Compilation Go avec retry
            go_ok = True
            for attempt in range(1, self._cfg.max_retry_compile + 1):
                go_result = self._compiler.build_go()
                if go_result.success:
                    break
                print(f"  [Go compile] Tentative {attempt} echouee : {go_result.errors[:150]}")
                if attempt == self._cfg.max_retry_compile:
                    print(f"  [ALERTE] Go compile echec definitif — batch {idx} skippe.")
                    go_ok = False

            if not go_ok:
                continue

            # Analyse Flutter avec retry
            for attempt in range(1, self._cfg.max_retry_compile + 1):
                flutter_result = self._compiler.analyze_flutter()
                if flutter_result.success:
                    break
                if attempt == self._cfg.max_retry_compile:
                    print(f"  [ALERTE] Flutter analyze echec definitif — batch {idx}.")

            # SAST
            sast = self._sast.scan()
            if sast.blocks_push:
                print(f"  [SAST BLOQUE] Vulnerabilites HIGH sur batch {idx} — push annule.")
                for issue in sast.issues:
                    print(f"    {issue.get('rule_id')} : {issue.get('details')}")
                continue

            # Git push
            all_files = gen.go_files + gen.dart_files
            if all_files:
                try:
                    self._git.commit_and_push(all_files, module_name="migration", batch_index=idx)
                    print(f"  [Git] Batch {idx} pousse.")
                except RuntimeError as e:
                    print(f"  [Git ERREUR] {e}")

            # Nettoyage disque
            self._guard.tick(total_files)

        await self._ai.close()
        print("\n[Veloce] Pipeline termine.")
