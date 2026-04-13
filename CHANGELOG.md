# Changelog

All notable changes to aiprims are documented here.
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-04-13

### Added — `aiprims.core.hash`

First functional module release.

Provides three deterministic identity primitives for Python objects, files,
and directories. Identity is derived from value — not memory address, session
state, or Python version.

**Functions:**
- `generate_id(obj)` — hashes any supported Python object using RFC 8785
  JSON Canonicalization Scheme + SHA-256
- `hash_file(path)` — hashes a file by binary content, ignoring metadata
- `hash_directory(path, exclude=None)` — hashes a directory by content and
  structure recursively

**Errors:**
- `HashError` — base error class
- `UnsupportedTypeError` — unsupported type passed to generate_id
- `NonStringKeyError` — non-string dict key encountered
- `NonFiniteFloatError` — NaN or Inf float encountered
- `PathError` — invalid path passed to hash_file or hash_directory

**Supported types for generate_id:**
str, int, float (finite), bool, None, dict (string keys only),
list, tuple, set, bytes — nested combinations fully supported.

**Serialisation standard:** RFC 8785 (JCS)
**Hashing algorithm:** SHA-256

---

## [0.0.1] — 2026-04-13

### Added
- Initial scaffold release
- Package structure with core, nlp, llm, rag, agents modules
- pyproject.toml, README, LICENSE, GitHub Actions publish workflow