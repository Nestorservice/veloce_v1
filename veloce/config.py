import os
from dotenv import load_dotenv

load_dotenv()

_REQUIRED = [
    "GROQ_API_KEY", "GROQ_ENDPOINT", "GROQ_MODEL_NAME",
    "DEEPSEEK_API_KEY", "DEEPSEEK_ENDPOINT", "DEEPSEEK_MODEL_NAME",
    "PHP_SOURCE_PATH", "MIRROR_WORK_PATH",
]


class Config:
    def __init__(self):
        for key in _REQUIRED:
            if not os.getenv(key):
                raise ValueError(f"Variable d'environnement manquante : {key}")

        self.groq_api_key: str = os.environ["GROQ_API_KEY"]
        self.groq_endpoint: str = os.environ["GROQ_ENDPOINT"]
        self.groq_model_name: str = os.environ["GROQ_MODEL_NAME"]
        self.deepseek_api_key: str = os.environ["DEEPSEEK_API_KEY"]
        self.deepseek_endpoint: str = os.environ["DEEPSEEK_ENDPOINT"]
        self.deepseek_model_name: str = os.environ["DEEPSEEK_MODEL_NAME"]
        self.php_source_path: str = os.environ["PHP_SOURCE_PATH"]
        self.mirror_work_path: str = os.environ["MIRROR_WORK_PATH"]
        self.batch_size: int = int(os.getenv("BATCH_SIZE", "15"))
        self.max_retry_compile: int = int(os.getenv("MAX_RETRY_COMPILE", "3"))
        self.sleep_between_files: int = int(os.getenv("SLEEP_BETWEEN_FILES", "10"))
        self.files_before_cleanup: int = int(os.getenv("FILES_BEFORE_CLEANUP", "50"))
        self.cpu_cores_limit: int = int(os.getenv("CPU_CORES_LIMIT", "2"))
