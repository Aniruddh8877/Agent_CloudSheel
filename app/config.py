import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment
load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    def __init__(self):
        self.api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
        self.model: str = os.getenv("DEFAULT_MODEL", "gemini-3.8-flash").strip()
        self.host: str = os.getenv("HOST", "127.0.0.1")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.notes_dir: Path = BASE_DIR / "user_data" / "notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def get_api_key(self) -> str:
        return self.api_key

    def set_api_key(self, key: str, save_to_env: bool = True):
        self.api_key = key.strip()
        os.environ["GEMINI_API_KEY"] = self.api_key
        if save_to_env:
            self._update_env_file("GEMINI_API_KEY", self.api_key)

    def set_model(self, model: str, save_to_env: bool = True):
        self.model = model.strip()
        os.environ["DEFAULT_MODEL"] = self.model
        if save_to_env:
            self._update_env_file("DEFAULT_MODEL", self.model)

    def _update_env_file(self, key: str, value: str):
        try:
            lines = []
            key_found = False
            if ENV_PATH.exists():
                with open(ENV_PATH, "r", encoding="utf-8") as f:
                    lines = f.readlines()

            new_lines = []
            for line in lines:
                if line.startswith(f"{key}=") or line.startswith(f"#{key}="):
                    new_lines.append(f"{key}={value}\n")
                    key_found = True
                else:
                    new_lines.append(line)

            if not key_found:
                new_lines.append(f"{key}={value}\n")

            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception as e:
            print(f"Warning: Could not save to .env: {e}")

settings = Settings()
