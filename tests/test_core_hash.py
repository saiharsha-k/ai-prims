import math
import tempfile
import os
from pathlib import Path

import pytest

from aiprims.core.hash import (
    generate_id,
    hash_file,
    hash_directory,
    HashError,
    UnsupportedTypeError,
    NonStringKeyError,
    NonFiniteFloatError,
    PathError,
)


# ─── generate_id — Happy Path ─────────────────────────────────────────────────

class TestGenerateIdHappyPath:

    def test_string(self):
        assert generate_id("hello") == generate_id("hello")

    def test_integer(self):
        assert generate_id(42) == generate_id(42)

    def test_float(self):
        assert generate_id(3.14) == generate_id(3.14)

    def test_bool_true(self):
        assert generate_id(True) == generate_id(True)

    def test_bool_false(self):
        assert generate_id(False) == generate_id(False)

    def test_none(self):
        assert generate_id(None) == generate_id(None)

    def test_bytes(self):
        assert generate_id(b"\xff\xfe") == generate_id(b"\xff\xfe")

    def test_empty_string(self):
        assert generate_id("") == generate_id("")

    def test_empty_dict(self):
        assert generate_id({}) == generate_id({})

    def test_empty_list(self):
        assert generate_id([]) == generate_id([])

    def test_empty_set(self):
        assert generate_id(set()) == generate_id(set())

    def test_dict(self):
        assert generate_id({"a": 1, "b": 2}) == generate_id({"a": 1, "b": 2})

    def test_nested_dict(self):
        obj = {"model": "gpt-4", "config": {"temperature": 0.7, "max_tokens": 100}}
        assert generate_id(obj) == generate_id(obj)

    def test_list(self):
        assert generate_id([1, 2, 3]) == generate_id([1, 2, 3])

    def test_tuple_equals_list(self):
        # tuple and list with same values must produce same hash
        assert generate_id((1, 2, 3)) == generate_id([1, 2, 3])

    def test_set_is_order_independent(self):
        # sets are unordered — same elements regardless of insertion order
        assert generate_id({3, 1, 2}) == generate_id({1, 2, 3})

    def test_returns_64_char_hex_string(self):
        result = generate_id({"key": "value"})
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_different_inputs_produce_different_ids(self):
        assert generate_id("hello") != generate_id("world")
        assert generate_id({"a": 1}) != generate_id({"a": 2})
        assert generate_id([1, 2, 3]) != generate_id([1, 2, 4])

    def test_none_vs_empty_list_are_different(self):
        assert generate_id(None) != generate_id([])

    def test_none_vs_empty_dict_are_different(self):
        assert generate_id(None) != generate_id({})

    def test_bool_vs_int_are_different(self):
        # True and 1 are different values — must hash differently
        assert generate_id(True) != generate_id(1)
        assert generate_id(False) != generate_id(0)

    def test_dict_key_order_independent(self):
        # Same keys and values — different insertion order — same hash
        a = {"z": 1, "a": 2, "m": 3}
        b = {"a": 2, "m": 3, "z": 1}
        assert generate_id(a) == generate_id(b)


# ─── generate_id — Failure Cases ─────────────────────────────────────────────

class TestGenerateIdFailures:

    def test_raises_on_nan(self):
        with pytest.raises(NonFiniteFloatError):
            generate_id(float("nan"))

    def test_raises_on_inf(self):
        with pytest.raises(NonFiniteFloatError):
            generate_id(float("inf"))

    def test_raises_on_negative_inf(self):
        with pytest.raises(NonFiniteFloatError):
            generate_id(float("-inf"))

    def test_raises_on_lambda(self):
        with pytest.raises(UnsupportedTypeError):
            generate_id(lambda x: x)

    def test_raises_on_arbitrary_object(self):
        with pytest.raises(UnsupportedTypeError):
            generate_id(object())

    def test_raises_on_non_string_key_int(self):
        with pytest.raises(NonStringKeyError):
            generate_id({1: "value"})

    def test_raises_on_non_string_key_bool(self):
        with pytest.raises(NonStringKeyError):
            generate_id({True: "value"})

    def test_raises_on_non_string_key_tuple(self):
        with pytest.raises(NonStringKeyError):
            generate_id({(1, 2): "value"})

    def test_raises_on_nested_unsupported_type(self):
        with pytest.raises(UnsupportedTypeError):
            generate_id({"config": {"transform": lambda x: x}})

    def test_raises_on_nested_nan(self):
        with pytest.raises(NonFiniteFloatError):
            generate_id({"score": float("nan")})

    def test_error_is_subclass_of_hash_error(self):
        with pytest.raises(HashError):
            generate_id(float("nan"))

    def test_error_message_is_informative(self):
        with pytest.raises(NonStringKeyError) as exc_info:
            generate_id({1: "value"})
        assert "1" in str(exc_info.value)
        assert "string" in str(exc_info.value).lower()


# ─── hash_file — Happy Path ───────────────────────────────────────────────────

class TestHashFileHappyPath:

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"hello world")
        f2.write_bytes(b"hello world")
        assert hash_file(f1) == hash_file(f2)

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"hello")
        f2.write_bytes(b"world")
        assert hash_file(f1) != hash_file(f2)

    def test_accepts_string_path(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_bytes(b"content")
        result = hash_file(str(f))
        assert isinstance(result, str)
        assert len(result) == 64

    def test_accepts_pathlib_path(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_bytes(b"content")
        result = hash_file(f)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_empty_file_hashes_cleanly(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        result = hash_file(f)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_metadata_ignored(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"same content")
        f2.write_bytes(b"same content")
        # modify timestamp of f2
        os.utime(f2, (0, 0))
        assert hash_file(f1) == hash_file(f2)


# ─── hash_file — Failure Cases ───────────────────────────────────────────────

class TestHashFileFailures:

    def test_raises_on_nonexistent_path(self, tmp_path):
        with pytest.raises(PathError):
            hash_file(tmp_path / "nonexistent.txt")

    def test_raises_when_path_is_directory(self, tmp_path):
        with pytest.raises(PathError):
            hash_file(tmp_path)

    def test_error_is_subclass_of_hash_error(self, tmp_path):
        with pytest.raises(HashError):
            hash_file(tmp_path / "nonexistent.txt")


# ─── hash_directory — Happy Path ─────────────────────────────────────────────

class TestHashDirectoryHappyPath:

    def test_same_structure_same_hash(self, tmp_path):
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()
        (d1 / "a.txt").write_bytes(b"hello")
        (d1 / "b.txt").write_bytes(b"world")
        (d2 / "a.txt").write_bytes(b"hello")
        (d2 / "b.txt").write_bytes(b"world")
        assert hash_directory(d1) == hash_directory(d2)

    def test_different_content_different_hash(self, tmp_path):
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()
        (d1 / "a.txt").write_bytes(b"hello")
        (d2 / "a.txt").write_bytes(b"changed")
        assert hash_directory(d1) != hash_directory(d2)

    def test_different_structure_different_hash(self, tmp_path):
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()
        (d1 / "a.txt").write_bytes(b"hello")
        (d2 / "b.txt").write_bytes(b"hello")
        assert hash_directory(d1) != hash_directory(d2)

    def test_empty_directory_hashes_cleanly(self, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()
        result = hash_directory(d)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_exclude_files(self, tmp_path):
        d = tmp_path / "dir"
        d.mkdir()
        (d / "a.txt").write_bytes(b"hello")
        (d / "b.txt").write_bytes(b"world")
        hash_with_b = hash_directory(d)
        hash_without_b = hash_directory(d, exclude=["b.txt"])
        assert hash_with_b != hash_without_b

    def test_returns_64_char_hex_string(self, tmp_path):
        d = tmp_path / "dir"
        d.mkdir()
        (d / "file.txt").write_bytes(b"content")
        result = hash_directory(d)
        assert isinstance(result, str)
        assert len(result) == 64


# ─── hash_directory — Failure Cases ──────────────────────────────────────────

class TestHashDirectoryFailures:

    def test_raises_on_nonexistent_path(self, tmp_path):
        with pytest.raises(PathError):
            hash_directory(tmp_path / "nonexistent")

    def test_raises_when_path_is_file(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_bytes(b"content")
        with pytest.raises(PathError):
            hash_directory(f)

    def test_error_is_subclass_of_hash_error(self, tmp_path):
        with pytest.raises(HashError):
            hash_directory(tmp_path / "nonexistent")