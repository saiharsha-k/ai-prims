# aiprims

**Foundational execution primitives for AI, ML, and data systems.**

aiprims is a lightweight, opinionated Python library that provides low-level primitives
for execution identity, deterministic hashing, run reproducibility, and traceability
across AI and ML systems.

It operates below orchestration tools, experiment trackers, and model frameworks.
It does not replace them. It sits underneath all of them as a correctness foundation.

> Differences between runs should never be mysterious.

---

## Install

```bash
pip install aiprims
```

---

## Modules

| Module | Status | Purpose |
|---|---|---|
| `aiprims.core.hash` | `v0.1.0` | Deterministic content-derived identity for any object, file, or directory |
| `aiprims.core.manifest` | `v0.1.0` | Immutable execution manifest capturing all run inputs |
| `aiprims.core.idempotency` | `v0.1.0` | Idempotency keys for agent tool calls and pipeline steps |
| `aiprims.core.config` | `v0.1.0` | Canonical config normalisation before hashing |
| `aiprims.core.env` | `v0.1.0` | Environment fingerprinting — Python, OS, packages |
| `aiprims.core.seed` | `v0.1.0` | Explicit randomness control and seed isolation |
| `aiprims.nlp` | `planned` | NLP pipeline execution primitives |
| `aiprims.llm` | `planned` | LLM prompt fingerprinting and inference identity |
| `aiprims.rag` | `planned` | Chunk identity and corpus fingerprinting for RAG systems |
| `aiprims.agents` | `planned` | Execution envelopes and tool call wrapping for agentic systems |

---

## Design Invariants

- Randomness is never implicit — all stochastic behavior must be explicitly seeded or flagged
- All inputs influencing execution must be visible — hidden dependencies are treated as failures
- Identity computation is always deterministic — same inputs, same identity, always
- Run identity is derivable locally — zero reliance on external systems
- Failures are explicit — no silent recovery from invalid states

---

## Part of the Garvaman OSS Stack

aiprims is the foundational layer of a composable AI infrastructure stack:
```
orion → application layer
agiorcx → agent coordination layer
ragaxis → RAG pipeline layer
aiprims → execution primitives (this library)
```

---

## License

MIT © 2026 Sai Harsha Kondaveeti