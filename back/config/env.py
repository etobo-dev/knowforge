import os

from dotenv import load_dotenv

load_dotenv()


def get_env(*, key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Environment variable {key} is not set")
    return value


def get_bool_env(*, key: str) -> bool:
    value = os.getenv(key)
    if value is None or value == "":
        raise ValueError(f"Environment variable {key} is not set")
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError(f"Environment variable {key} must be 'true' or 'false'")
