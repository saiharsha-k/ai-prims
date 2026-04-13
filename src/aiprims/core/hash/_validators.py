import math
from pathlib import Path
from typing import Any

from aiprims.core.hash._errors import (
    NonFiniteFloatError,
    NonStringKeyError,
    PathError,
    UnsupportedTypeError,
)

SUPPORTED_SCALAR_TYPES = (str, int, float, bool, bytes, type(None))
SUPPORTED_COLLECTION_TYPES = (dict, list, tuple, set)
SUPPORTED_TYPES = SUPPORTED_SCALAR_TYPES + SUPPORTED_COLLECTION_TYPES


def validate_object(obj: Any, path: str = "root") -> None:
    """
    Recursively validates that obj contains only supported types.
    Raises explicitly on first violation encountered — never silently coerces.
    """
    if isinstance(obj, bool):
        # bool must be checked before int — bool is a subclass of int in Python
        return

    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise NonFiniteFloatError(obj, path)
        return

    if isinstance(obj, SUPPORTED_SCALAR_TYPES):
        return

    if isinstance(obj, dict):
        for key, value in obj.items():
            if not isinstance(key, str):
                raise NonStringKeyError(key, path)
            validate_object(value, path=f"{path}.{key}")
        return

    if isinstance(obj, (list, tuple)):
        for index, item in enumerate(obj):
            validate_object(item, path=f"{path}[{index}]")
        return

    if isinstance(obj, set):
        for item in obj:
            validate_object(item, path=f"{path}[set item]")
        return

    raise UnsupportedTypeError(type(obj), path)


def validate_file_path(path: str | Path) -> Path:
    """
    Validates that path exists and is a file.
    Returns a resolved Path object.
    Raises PathError explicitly on any violation.
    """
    resolved = Path(path).resolve()

    if not resolved.exists():
        raise PathError(path, "path does not exist")

    if not resolved.is_file():
        raise PathError(path, "path is not a file — use hash_directory() for directories")

    return resolved


def validate_directory_path(path: str | Path) -> Path:
    """
    Validates that path exists and is a directory.
    Returns a resolved Path object.
    Raises PathError explicitly on any violation.
    """
    resolved = Path(path).resolve()

    if not resolved.exists():
        raise PathError(path, "path does not exist")

    if not resolved.is_dir():
        raise PathError(path, "path is not a directory — use hash_file() for files")

    return resolved