import hashlib
import os
from pathlib import Path
from typing import Any

from aiprims.core.hash._canonical import canonicalise, normalise
from aiprims.core.hash._validators import (
    validate_directory_path,
    validate_file_path,
    validate_object,
)

CHUNK_SIZE = 65536  # 64KB — safe for large files without memory pressure


def generate_id(obj: Any) -> str:
    """
    Generates a deterministic SHA-256 identity for any supported Python object.

    Identity is derived from the value of the object — not its memory address,
    type name, or Python session state. The same value always produces the
    same identity across machines, OS, and Python versions.

    Args:
        obj: Any supported Python object. Supported types:
             str, int, float (finite), bool, None,
             dict (string keys only), list, tuple, set, bytes.
             Nested combinations of the above are fully supported.

    Returns:
        Lowercase SHA-256 hex string — always 64 characters.

    Raises:
        UnsupportedTypeError: if obj contains an unsupported type.
        NonStringKeyError: if a dict with non-string keys is encountered.
        NonFiniteFloatError: if NaN or Inf float values are encountered.

    Example:
        >>> generate_id({"model": "gpt-4", "temperature": 0.7})
        'a3f9c2d1e8b47f6d...'

        >>> generate_id(["step1", "step2", "step3"])
        'b7e3f1c9d4a2...'
    """
    validate_object(obj)
    normalised = normalise(obj)
    canonical_bytes = canonicalise(normalised)
    return hashlib.sha256(canonical_bytes).hexdigest()


def hash_file(path: str | Path) -> str:
    """
    Generates a deterministic SHA-256 identity for a file.

    Identity is derived from binary content only.
    File metadata — timestamps, permissions, owner — are ignored entirely.
    The same file content on any machine always produces the same identity.

    Uses chunked reading — safe for arbitrarily large files.

    Args:
        path: Path to the file. Accepts str or pathlib.Path.

    Returns:
        Lowercase SHA-256 hex string — always 64 characters.

    Raises:
        PathError: if path does not exist or is not a file.

    Example:
        >>> hash_file("/data/corpus/document.pdf")
        'c9f2e8d1a4b7...'
    """
    resolved = validate_file_path(path)
    hasher = hashlib.sha256()

    with open(resolved, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def hash_directory(
    path: str | Path,
    exclude: list[str] | None = None,
) -> str:
    """
    Generates a deterministic SHA-256 identity for a directory.

    Identity is derived from the content and structure of all files within
    the directory — recursively. Both file content and relative paths are
    included in the identity computation.

    Files are sorted by relative path before hashing — ensuring deterministic
    ordering regardless of filesystem traversal order.

    Args:
        path: Path to the directory. Accepts str or pathlib.Path.
        exclude: Optional list of filenames or relative paths to exclude.
                 Exact filename match only. Default is None — nothing excluded.

    Returns:
        Lowercase SHA-256 hex string — always 64 characters.

    Raises:
        PathError: if path does not exist or is not a directory.

    Example:
        >>> hash_directory("/data/corpus/")
        'd1e2f3a4b5c6...'

        >>> hash_directory("/data/corpus/", exclude=[".git", "__pycache__"])
        'e2f3a4b5c6d7...'
    """
    resolved = validate_directory_path(path)
    exclude_set = set(exclude) if exclude else set()

    file_hashes: list[tuple[str, str]] = []

    for root, dirs, files in os.walk(resolved):
        # Sort dirs in-place — controls os.walk traversal order
        dirs.sort()

        for filename in sorted(files):
            if filename in exclude_set:
                continue

            abs_path = Path(root) / filename
            relative_path = str(abs_path.relative_to(resolved))

            if relative_path in exclude_set:
                continue

            file_hash = hash_file(abs_path)
            file_hashes.append((relative_path, file_hash))

    # Combine relative paths and file hashes into a single canonical structure
    # generate_id on this list gives the directory its stable identity
    return generate_id(file_hashes)