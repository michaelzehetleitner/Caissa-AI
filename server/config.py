import os
from functools import lru_cache
from pathlib import Path

import streamlit as st

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


def _candidate_secret_paths() -> list[Path]:
    base_dir = Path(__file__).resolve().parent
    repo_root = base_dir.parent
    return [
        base_dir / ".streamlit" / "secrets.toml",
        repo_root / ".streamlit" / "secrets.toml",
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
    ]


@lru_cache(maxsize=1)
def _load_local_secrets() -> dict:
    merged: dict = {}
    for path in _candidate_secret_paths():
        if not path.exists():
            continue
        try:
            with path.open("rb") as fh:
                merged.update(tomllib.load(fh))
        except Exception as exc:  # pragma: no cover
            print(f"Warning: unable to parse secrets file {path}: {exc}")
    return merged


def get_secret(key: str, default=None):
    """
    Retrieves a secret by first checking environment variables, then Streamlit’s
    secrets store, and finally local .streamlit/secrets.toml fallbacks.
    """
    env_value = os.getenv(key)
    if env_value:
        return env_value

    try:
        secret_value = st.secrets[key]
        if secret_value:
            return secret_value
    except Exception:
        pass

    local_value = _load_local_secrets().get(key)
    if local_value:
        return local_value

    if default is not None:
        return default

    raise KeyError(
        f"Secret '{key}' not found. Provide it via environment variables or a .streamlit/secrets.toml file."
    )


__all__ = ["get_secret"]
