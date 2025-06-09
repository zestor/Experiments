"""Simple in-memory vector database package.

The module exports constants for the environment variables recognised by the
command line interface:

``HOST_ENV_VAR`` and ``PORT_ENV_VAR`` specify where the REST API binds when
running ``vectordb serve``. ``API_KEY_ENV_VAR`` defines the variable used to
configure an optional API key. ``INDEX_PATH_ENV_VAR`` and ``DATA_PATH_ENV_VAR``
can override the default locations of the index and stored texts. ``MODEL_NAME_ENV_VAR``
allows overriding the default embedding model used by :class:`VectorDB` and the
command line interface.
"""

from .db import DATA_PATH, INDEX_PATH, MODEL_NAME, VectorDB
from .api import create_app

API_KEY_ENV_VAR = "VECTORDB_API_KEY"
HOST_ENV_VAR = "VECTORDB_HOST"
PORT_ENV_VAR = "VECTORDB_PORT"
INDEX_PATH_ENV_VAR = "VECTORDB_INDEX_PATH"
DATA_PATH_ENV_VAR = "VECTORDB_DATA_PATH"
MODEL_NAME_ENV_VAR = "VECTORDB_MODEL_NAME"

__version__ = "0.1.0"

__all__ = [
    "VectorDB",
    "create_app",
    "INDEX_PATH",
    "DATA_PATH",
    "MODEL_NAME",
    "API_KEY_ENV_VAR",
    "HOST_ENV_VAR",
    "PORT_ENV_VAR",
    "INDEX_PATH_ENV_VAR",
    "DATA_PATH_ENV_VAR",
    "MODEL_NAME_ENV_VAR",
    "__version__",
]
