"""
aiprims.core.hash
-----------------
Deterministic, value-based identity primitives for Python objects, files,
and directories.

Core principle: the same input always produces the same identity — across
machines, OS versions, and Python versions. Identity is derived from value,
never from memory address, type name, or session state.

Serialisation standard: RFC 8785 JSON Canonicalization Scheme (JCS)
Hashing algorithm:      SHA-256 (via Python stdlib hashlib)
Return type:            Lowercase hex string — always 64 characters

Public API:
    generate_id(obj)                   → str
    hash_file(path)                    → str
    hash_directory(path, exclude=None) → str

Errors:
    HashError            — base error for all core.hash failures
    UnsupportedTypeError — unsupported type passed to generate_id
    NonStringKeyError    — non-string dict key passed to generate_id
    NonFiniteFloatError  — NaN or Inf float passed to generate_id
    PathError            — invalid path passed to hash_file or hash_directory

Supported types for generate_id:
    str, int, float (finite only), bool, None,
    dict (string keys only), list, tuple, set, bytes
    Nested combinations of the above are fully supported.

Non-goals:
    - Does not store or cache hashes
    - Does not compare hashes (use == on return values)
    - Does not hash tensors or arbitrary class instances
    - Does not handle async I/O
    - Does not guarantee bit-level output stability across major versions

Example:
    >>> from aiprims.core.hash import generate_id, hash_file, hash_directory
    >>> generate_id({"model": "gpt-4", "temperature": 0.7})
    'a3f9c2d1...'
    >>> hash_file("/data/document.pdf")
    'b7e3f1c9...'
    >>> hash_directory("/data/corpus/", exclude=[".git"])
    'c9f2e8d1...'
"""

from aiprims.core.hash._errors import (
    HashError,
    NonFiniteFloatError,
    NonStringKeyError,
    PathError,
    UnsupportedTypeError,
)
from aiprims.core.hash._hasher import (
    generate_id,
    hash_directory,
    hash_file,
)

__all__ = [
    "generate_id",
    "hash_file",
    "hash_directory",
    "HashError",
    "UnsupportedTypeError",
    "NonStringKeyError",
    "NonFiniteFloatError",
    "PathError",
]