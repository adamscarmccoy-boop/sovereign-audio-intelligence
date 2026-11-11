# LEGION Ableton Typed Model Graph — executable proof V1

## Hypothesis

**Complete static Ableton SDK capability structure stays in DuckDB. The LLM receives no full graph. Native SQL resolves a bounded actor edge; `pydantic-core` (Rust) validates the SDK capability registry, actor edges and selected arguments. The Ableton SDK runtime executes the final call.**

## Tested execution

We actually executed the following in the Linux sandbox:

- Loaded the **real DuckDB 2.0.0 C ABI (`libduckdb.so`)** by `ctypes`, maintained one native connection, and created two **temporary views** from JSON (`sdk_capabilities` and `actor_edges`). No persistent tables or user's database were modified.
- Parsed the **static beta 1.0.0 SDK inventory extracted from its TypeScript declarations**. This is *not* the JSON output of a running Ableton session. Validated **250 capability records** (126 host-module members and 124 class members/properties) using Pydantic v2 / compiled Rust `pydantic-core` validators.
- Validated **4 actor edges**. DuckDB SQL performs a three-way join between intent edge, SDK class member and SDK host method to authorize a selected capability. Python contains the Pydantic models for four bounded operations, not a prompt full of SDK graph data.
- Validated input and execution arguments using compiled Pydantic-core schema validators. Invalid types, extra fields, out-of-range tempo, unsupported path formats, and occupied session slots are rejected.
- Executed four operations **against a mock Live runtime**: Arrangement audio insertion, Session slot audio insertion, audio path read, and tempo change. No actual Live Set was modified.
- Type-checked the separate **real Ableton SDK execution adapter** in `extension.ts` against the original `@ableton-extensions/sdk@1.0.0-beta.0` declarations with TypeScript strict mode. The adapter uses only documented SDK object-handle methods and property setters and opens no HUD or modal.
- Nine Python unit tests pass, and the route required **zero LLM calls**.

`test_receipt.json` is the exact latest local run. This is a bounded architectural proof, **not** proof that the original ~507 MB DuckDB, real LanceDB, existing Sovereign actor registry, LangGraph runtime or Live beta have been attached. **LangGraph was not installed or executed in this sandbox**; the four-stage deterministic transition is a persisted-JSON graph *representation*, not LangGraph engine runtime execution.

## Reproduction

Keep `ableton_sdk_api_inventory.json` (from your private SDK package), `actor_edges.json`, `sovereign_graph.py` and `tests/` together. On Linux, set `LEGION_DUCKDB_SO` to a native DuckDB C-ABI library (`libduckdb.so`). On Windows use `duckdb.dll` with matching C ABI. This package doesn't distribute that library.

```bash
python -m pip install 'pydantic>=2'  # if not already installed
export LEGION_DUCKDB_SO=/path/to/libduckdb.so
python -m unittest discover -s tests -v
python sovereign_graph.py
```

For the SDK adapter type-check, install Ableton's SDK in your **local licensed extension workspace** (do not publish SDK binaries separately), then:

```bash
tsc --strict --noEmit --target ES2022 --moduleResolution bundler --module ESNext extension.ts
```

`extension.ts` exports `executeApprovedToolCall(ctx, raw)` for a future context-menu/registered-command handler. **It is not yet registered as a runnable Ableton extension**. Integrate it into your existing extension activation/command callbacks, and feed the resulting bounded JSON through your existing authenticated gateway. Do not let a remote client choose arbitrary object methods or pass raw SQL to Live.

## What happens next on Sovereign Windows

1. Point the native DuckDB connector at the **existing** lakehouse and its actor/model/graph registry, rather than the scratch in-memory DuckDB used in this proof. The existing registry and SDK beta inventory must be reconciled without creating duplicate tables.
2. Adapt `actor_edges.json` into the existing registered actor/highway rows, and have `LangGraph` (if the actual runtime is loaded) consume only already resolved edges.
3. Bind the SDK adapter to real Live object handles inside the beta extension process, not the Python mock. Resolve handles via `ctx.getObjectFromHandle()` and enforce active Live Set lifetime rules.
4. Connect real file existence, DuckDB metadata and Lance ANN candidate rankings. No fabricated embeddings, no cache file as source of truth.
5. Exercise one empty Session slot or test project first; confirm a genuine Live response before enabling general write capabilities.

## Design limits

- Pydantic-core Rust *validates and serializes* models; it does not execute DuckDB queries, ONNX, Lance ANN or LangGraph itself.
- The full 250-record inventory exists only as local SQL/JSON and isn't given to an LLM. The selected OpenAI-compatible function definition lives in `selected_tool_definition` for optional later use.
- The actual SDK methods are verified by static TypeScript declarations; no live Ableton deployment is claimed.
- Redistributing Ableton's original SDK packages publicly may violate its license, so this source distribution contains **no Ableton SDK archive**.
