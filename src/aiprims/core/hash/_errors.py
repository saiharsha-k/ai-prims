class HashError(Exception):
    """Base error for all aiprims.core.hash failures."""
    pass


class UnsupportedTypeError(HashError):
    """
    Raised when generate_id encounters a type that cannot be
    deterministically serialised.

    Supported types: str, int, float (finite), bool, None,
                     dict (string keys only), list, tuple, set, bytes.
    """
    def __init__(self, type_: type, path: str = "root"):
        self.type_ = type_
        self.path = path
        super().__init__(
            f"Unsupported type '{type_.__name__}' encountered at path '{path}'. "
            f"aiprims.core.hash supports: str, int, float (finite), bool, None, "
            f"dict (string keys only), list, tuple, set, bytes. "
            f"Serialise this value to a supported type before calling generate_id()."
        )


class NonStringKeyError(HashError):
    """
    Raised when generate_id encounters a dictionary with non-string keys.
    JSON canonicalisation requires all dictionary keys to be strings.
    """
    def __init__(self, key: object, path: str = "root"):
        self.key = key
        self.path = path
        super().__init__(
            f"Non-string dictionary key '{key}' of type '{type(key).__name__}' "
            f"encountered at path '{path}'. "
            f"All dictionary keys must be strings. "
            f"Convert keys to strings before calling generate_id()."
        )


class NonFiniteFloatError(HashError):
    """
    Raised when generate_id encounters NaN or Inf float values.
    These have no canonical deterministic representation.
    """
    def __init__(self, value: float, path: str = "root"):
        self.value = value
        self.path = path
        super().__init__(
            f"Non-finite float value '{value}' encountered at path '{path}'. "
            f"NaN and Inf have no canonical identity. "
            f"Replace or remove this value before calling generate_id()."
        )


class PathError(HashError):
    """
    Raised when hash_file or hash_directory receives an invalid path.
    """
    def __init__(self, path: object, reason: str):
        self.path = path
        super().__init__(
            f"Invalid path '{path}': {reason}"
        )