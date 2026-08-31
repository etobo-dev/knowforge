import os

from dotenv import load_dotenv

load_dotenv()


def get_env(*, key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Environment variable {key} is not set")
    return value


def get_env_or(*, key: str, default: str) -> str:
    value = os.getenv(key)
    return value if value else default
