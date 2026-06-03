import asyncio
from veloce.config import Config
from veloce.orchestrator import Orchestrator

if __name__ == "__main__":
    config = Config()
    asyncio.run(Orchestrator(config).run())
