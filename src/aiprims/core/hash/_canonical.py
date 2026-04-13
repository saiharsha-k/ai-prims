from typing import Any

import rfc8785


def normalise(obj: Any) -> Any:
    """
    Recursively normalises supported Python types into
    RFC 8785 compatible structures before canonicalisation.

    Normalisation rules:
    - tuple  → list      (order preserved)
    - set    → sorted list (sorted by string representation for stability)
    - bytes  → hex string
    - All other supported types pass through unchanged.

    Assumes validate_object() has already been called.
    No validation is performed here — normalise is a pure transformation.
    """
    if isinstance(obj, bool):
        # bool before int — bool is subclass of int
        return obj

    if isinstance(obj, (str, int, float, type(None))):
        return obj

    if isinstance(obj, bytes):
        return obj.hex()

    if isinstance(obj, dict):
        return {key: normalise(value) for key, value in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [normalise(item) for item in obj]

    if isinstance(obj, set):
        # Sort by string representation of each normalised element
        # This ensures stable ordering regardless of element types
        normalised_items = [normalise(item) for item in obj]
        return sorted(normalised_items, key=lambda x: str(x))

    # Should never reach here — validate_object catches unsupported types first
    raise TypeError(
        f"Unexpected type '{type(obj).__name__}' reached normalise(). "
        f"Ensure validate_object() is called before normalise()."
    )


def canonicalise(obj: Any) -> bytes:
    """
    Converts a normalised Python object into a canonical UTF-8 byte
    sequence using RFC 8785 JSON Canonicalization Scheme.

    Returns deterministic bytes — same structure always produces
    same bytes across any machine, OS, or Python version.
    """
    return rfc8785.dumps(obj)