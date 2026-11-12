# Sovereign Music Engine
**Architecture & verification checkpoint — November 12, 2026**

Sovereign Music Engine is an evolving local-first music intelligence platform for generation, stem separation, acoustic analysis, neural inference, DSP processing, and DAW integration. **Ableton Live is an integration surface, not the entire engine.**

> **Status:** Components have been demonstrated individually. Fully autonomous, closed-loop mastering has **not** been verified.

## System boundaries

```text
Audio / samples / sessions
    ├── Generation and arrangement
    ├── Stem separation (Demucs ONNX)
    └── Time-indexed acoustic feature analysis
              │
              ▼
   Existing model and execution registries
   (DuckDB · Lance · Parquet/JSON)
              │
              ▼
   Exact model input contract — to verify
              │
              ▼
   Big Brain ONNX BEFORE operation
       [N,64] -> [N,12]
              │
              ▼
   Registered DSP / C++ / Rust / ONNX operation
              │
              ▼
   Re-measure and encode in the SAME feature space
              │
              ▼
   Big Brain ONNX AFTER operation
              │
              ▼
   Existing acceptance policy — to verify
              │
              ▼
   Audio + timeline + typed execution receipt
```

HTTP/LangGraph may coordinate outer workflows; Ray may bind/distribute validated tasks; DuckDB, Lance, Arrow-compatible interfaces, and native runtimes handle the relevant data and computation paths. A native path is a design target unless the specific boundary is demonstrated. Arrow compatibility does not alone prove zero-copy.

## Distinct capabilities

| Lane | Responsibility |
|---|---|
| Generation | Model-guided sample selection and arrangement |
| Separation | Demucs-based stems: drums, bass, vocals, other |
| Acoustic analysis | Preserve measurements *over time*, not only whole-track averages |
| Registry resolution | Reuse existing model metadata, native functions, and route bindings |
| Evaluation | Invoke the intended Big Brain ONNX before and after a registered operation |
| DSP execution | Explicitly selected operations via existing native or audio-processing tools |
| DAW integration | Ableton Live sessions, clips, devices, automation, and export |

## Big Brain: confirmed contract and limits

The original `sovereign_big_brain_exhaustive.onnx` was loaded and executed in ONNX Runtime. It takes **`dna_vector` float32 `[N,64]`** and returns **`dsp_state` float32 `[N,12]`**. The output is **not automatically a pass/fail verdict**.

A saved registry/dependency-graph export identifies the model and records a native execution surface. That historical registration does **not** prove successful live native dispatcher invocation or reveal the exact trained 64-D input encoding.

The original model was tested before and after a mathematical change, and audio-derived inference was also attempted. **No validated music-quality approval** can be claimed until the upstream representation and acceptance criteria are matched to the model's training contract.

## Verified evidence and unresolved connections

| Evidence | Current conclusion |
|---|---|
| Big Brain model and external weights | Loaded; native ORT inference succeeded |
| ONNX tensor signatures | 64-D input / 12-D output verified |
| Stored dependency graph | 4,256 nodes, 6,134 edges; Big Brain model identity matched |
| Persisted Lance model-config registry | Located; its raw rows not yet decoded in this environment |
| Demucs | Four-stem output demonstrated on a short excerpt (not the 147.2 s reference track) |
| Music generation | Separate model and generated audio assets recovered |
| V5-style mastering | Separate DSP processing run; **not proof of Big Brain judge approval** |
| Historical song trajectory | 147.2 s and 291 reported inferences; exact frame timestamps and actual model input path unverified |
| Live DuckDB route joins | Could not be completed because the connected service timed out |
| Automatic before/after judge with stored gate rules | **Not yet demonstrated** |

### Important distinctions

- The 12-feature historical acoustic summary is **not** itself a valid `[N,64]` Big Brain input.
- Two tensors both having 64 dimensions **does not** establish a shared training space.
- Minimum/maximum spectral or bass energy cannot locate drops or breakdowns without timestamps.
- The original V3 training source calculates a 64-D `sonic_dna` representation but feeds the mastering head from another intermediate tensor; **do not silently substitute that representation** as the Big Brain input.
- A failed model call or missing policy must yield an **unverified/no-decision state**, not an automatic approval.

## Next reproducible proof

1. Read the **existing** model, tensor-introspection, native execution, and vector-highway registry records; retain the exact row identifiers and relationships.
2. Identify and validate the trained **64-D input schema**, feature labels, normalization, and source model.
3. Pick a short timestamped audio segment and a registered operation.
4. Execute **Big Brain → operation → same-feature-space Big Brain**, collecting tensor values, model hashes, audio deltas, and native executor receipts.
5. Apply only an **existing verified acceptance policy**. Otherwise report `JUDGE_OUTPUT_ONLY`.
6. After one valid loop, extend the temporal analysis across a whole arrangement and expose it through Ableton integration.

## Publication and scope

This repository documents the *engine*. Ableton-specific adapters belong in an Ableton-facing integration package. The architecture report intentionally omits machine-local paths, private registry contents, audio assets, and model weights. Do not interpret historical benchmarks or registry declarations as new performance measurements.

**Evidence policy:** verified execution, historical documentation, hypotheses, and remaining blockers are distinguished explicitly.
