"""Simple in-memory vector database package."""

from .db import DATA_PATH, INDEX_PATH, MODEL_NAME, VectorDB
from .api import create_app

API_KEY_ENV_VAR = "VECTORDB_API_KEY"

__version__ = "0.1.0"

__all__ = [
    "VectorDB",
    "create_app",
    "INDEX_PATH",
    "DATA_PATH",
    "MODEL_NAME",
    "API_KEY_ENV_VAR",
    "__version__",
]
