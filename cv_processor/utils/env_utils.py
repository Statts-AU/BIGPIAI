# cv_processor/utils/env_utils.py
"""
Environment and configuration utilities.
"""
import os
from pathlib import Path


def load_env_from_file(env_file: str = ".env") -> None:
    """Load environment variables from a .env file."""
    env_path = Path(env_file)
    if not env_path.exists():
        return

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")


def get_env_var(key: str, default: str = None) -> str:
    """Get environment variable with optional default."""
    return os.getenv(key, default)


def ensure_env_var(key: str, default: str = None) -> str:
    """Ensure an environment variable exists, setting default if missing."""
    if key not in os.environ and default is not None:
        os.environ[key] = default
    return os.getenv(key)
