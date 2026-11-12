# Sovereign Music Engine — architecture and execution evidence

**Checkpoint:** 2026-11-12  
**Project:** Sovereign Legion / Kimi Music / Sonic DNA  
**Scope:** Full music intelligence pipeline; **Ableton Live is an integration**, not the entire engine.  
**Status:** Recovery and validation checkpoint, **not** a claim of fully autonomous mastering.

## Executive decision

Keep **generation**, **stem separation**, **acoustic measurement**, **model inference/judging**, **mathematical execution**, and **DAW control** as different functional lanes. Bind them through the **already existing DuckDB, LanceDB and Parquet/JSON model/function registries**. Don't invent new runtime actors, tables or synthetic embeddings to paper over missing contracts. Put the original `sovereign_big_brain_exhaustive.onnx` in ONNX Runtime as a *pre/post evaluation component*, and only give it approval authority once its native 64-D input semantics and 12-D acceptance policy have been confirmed from stored contracts.

## Top-level data and control flow

```text
INPUTS: WAV / tracks / clips / Ableton .als / sample libraries
      |
      +--> GENERATION: kick-to-bass model + sample selection/arrangement
      |      output: composed or arranged audio
      |
      +--> SEPARATION: htdemucs.onnx -> drums / bass / vocals / other
      |
      v
TIME-INDEXED ACOUSTIC MEASUREMENT (PCM -> DSP vectors; preserve frames/timestamps)
      |
      v
EXISTING REGISTRY RESOLUTION
  DuckDB catalog + Lance vector tables + Parquet/JSON manifests
  model_registry / model_tensor_introspection /
  desktop_model_weights_registry / vector_highways_registry /
  execution_routes / capability_nodes and edges
      |
      v
EXACT TRAINED 64-D DNA CONTRACT [unresolved; do not substitute a 64-D vector]
      |
      v
ONNX Runtime: sovereign_big_brain_exhaustive.onnx (BEFORE)
  input: dna_vector float32 [N,64]
  output: dsp_state float32 [N,12]
      |
      v
NATIVE OPERATION: DuckDB SQL / Arrow C buffers / Lance / Rust ABI / C++ / ONNX DSP
      |
      v
MEASURE/ENCODE RESULT IN THE **SAME** FEATURE SPACE
      |
      v
ONNX Runtime: same Big Brain (AFTER)
      |
      v
EXISTING QUALITY CONTRACT (not yet identified) -> accept/reject/retry
      |
      v
Audio + time-indexed feature trajectory + structured execution receipt
```

**Control-plane boundary:** HTTP or LangGraph can orchestrate the outer workflow. Ray can bind/distribute a validated task and its Arrow data, with Pydantic v2 contracts inside the Ray execution context when used. A non-Ray native DuckDB/Arrow execution lane is also possible. Neither Ray nor Python is itself the mastering mathematics. Arrow-compatible memory interfaces reduce conversion; zero-copy must be demonstrated at each individual boundary.

## Proven components vs gaps

| Component | Evidence | Status / caveat |
|---|---|---|
| Sovereign Big Brain | Original `.onnx` plus `.onnx.data` uploaded; native ORT 1.31.0 executed | **Verified model load/inference**, synthetic and audio-derived tests performed; audio-derived vector space compatibility **not** verified |
| Big Brain contract | `dna_vector [N,64]` -> `dsp_state [N,12]` | Verified ONNX IO dimensions; output is not inherently an approval flag |
| Registry model identity | Saved `sovereign_dependency_graph.html` links `sovereign_big_brain_exhaustive.onnx` to `desktop_model_weights_registry` | Registry evidence: path `C:\WEB CASE STUDY\sovereign_big_brain_exhaustive.onnx`, ONNX, registered DirectML/AOT C-ABI, `aot_linked: true`. **Live C-ABI invocation not proved** |
| Registry graph | 4,256 nodes / 6,134 edges / 0 unresolved graph endpoints | Export inspected; no direct stored edge from Big Brain to the correct 64-D encoder or judge threshold |
| `model_config_json_registry.lance` | Drive folder, Lance fragment `1110010001110110111111101521594678858709669d9a2b84.lance`, ~2.98 MB | Persisted Lance dataset located; **rows not decoded** in sandbox |
| Model registry and highways | `model_registry`, `model_tensor_introspection`, `vector_highways_registry`, `execution_routes` | Historically populated; direct live SQL request via FACTORY **timed out** |
| Demucs separation | Original `htdemucs.onnx.bin` and earlier four-stem execution receipt | Four stems demonstrated on a **7.8-second `ONNX_SOV_scars here.wav` excerpt**, not on `SOV_Dumb Dumb Dun` |
| Generation | `audio_llm_v1.pt` training / agent source and generated WAVs | Kick-to-bass DSP mapping plus sample arrangement is **not** the Big Brain judge |
| V3 mastering | `sonic_dna_master_v3.pt`, `sonic_dna_master_v3_train.py` | Separate trained mastering model predicting gain/ratio/threshold; **not** authorized as Big Brain's 64-D encoder merely because both expose 64 dimensions |
| V5 processing | `sonic_dna_batch_master_v5_neural.py` + raw 7.5-second WAV | A distinct mastering run was made, applying Pedalboard; **not evidence of Big Brain acceptance** |
| Historical 147.2s trajectory | User-provided `SOV_Dumb Dumb Dun (1).wav` JSON receipt: 291 inferences, 12-feature gold baseline, trajectory mean/min/max, first five raw vectors | Time-varying metrics demonstrated. Exact frame timestamps, 291-frame sequence, model input encoding, and inference schedule not established |

## Timing and DSP: what is known

The historical track duration is **147.2 seconds** and the receipt reports **291 inferences**. A uniform 291-step schedule would correspond to ~0.506 seconds per step, but **the actual hop/window size and timestamps are unknown**. Minimum and maximum energy do not identify which bars contain breakdowns or drops without the ordered trajectory.

The receipt's 12 reported DSP measurements (RMS, crest, four band energies, centroid, bandwidth, rolloff, flatness, contrast, ZCR) are **not** a drop-in `[291,12]` input to Big Brain. Big Brain needs `[N,64]` `dna_vector`; the 12-D quantity is its output. Whether the 12-D measurements came from librosa, C++ DSP, Essentia, NumPy or another chain must be determined from execution provenance, not field names alone.

## Relevant artifacts and historical sources

- Big Brain original Windows path: `C:\WEB CASE STUDY\sovereign_big_brain_exhaustive.onnx`.
- Drive [ONNX model ranking and IO signatures](https://drive.google.com/file/d/1g5MkpkPYacFSAmDT2oR1CD5lvNF847L5fm5NlsI21zw/view).
- Drive [model registry and actor workflow snapshot](https://drive.google.com/file/d/1pVLjAdikjR9mfdE8UTsLZQEQqJQ137uuWr4zDD4DDms/view) — **not a substitute for live rows**.
- Drive [Lance `model_config_json_registry` directory](https://drive.google.com/drive/folders/1DwUZouXPhhFA8tBhIEpc6_nv-upVamU2).
- Drive [Sonic DNA engine original sources and audio](https://drive.google.com/drive/folders/1_8sADpT6Fwvus9pN6FQt7N7hiEFUUBKh).
- Earlier dependency graph artifact: `sovereign_dependency_graph.html` saved in ChatGPT Library.
- Existing evidence JSON: `sovereign_big_brain_registry_evidence.json` saved in ChatGPT Library.
- Kimi notebook: `SOVEREIGN_KIMI3_DUCKDB_PIPELINE.ipynb` saved in ChatGPT Library.
- Historical native Lance inventory: `lance_cores_manifest_db/lance_cores_manifest` (23 records, Windows paths); Rustworkx is a **separate** graph dependency, not Lance's Rust storage engine.
- October 31 Ray registration reports: `master_lakehouse_consolidated` (8,375 x 5, JSON payload column) and `mined_code_legion` (18,806 x 19) successfully registered by `legion_ray_supervisor.py` through PyArrow Parquet reading. Registration does not itself prove function invocation.

## Verified inconsistency: V3 training network

In `sonic_dna_master_v3_train.py`, `MasteringNet.forward` calculates `z = self.sonic_dna(h)` and normalizes `z`, **but returns `self.master_head(h)`**, bypassing `z`. V5 inference likewise returns `master_head(h)`. Hence the `.pt` checkpoint's 64-D `sonic_dna` layer must **not** be assumed to be the Big Brain's intended upstream representation. It is not proven to share a trained coordinate system with the ONNX judge.

## Execution acceptance contract to recover (no invented thresholds)

For each operation, the persisted task record must identify: (1) exact audio/source time range; (2) feature extractor and **trained 64-D schema**; (3) registered native executor and parameter types; (4) Big Brain pre-state/output; (5) operation receipt and output audio/data; (6) post-state/output using identical extractor and normalization; (7) the **stored** evaluation/threshold/routing contract, not an arbitrary 0.75 or 0.65 from a different vision model. **On missing contract or failed inference, fail closed**: no claimed approval or automatic mastering change.

### One bounded proof to run next

1. Read the **existing** `model_tensor_introspection`, `model_registry`, `desktop_model_weights_registry`, `vector_highways_registry`, `execution_routes`, and decoded `model_config_json_registry.lance` rows for Big Brain; retain row IDs and join evidence.
2. Find the exact registered 64-D encoder, feature labels and normalization. Validate the ONNX `dna_vector` dimensions *and semantics* against that record.
3. Select one short music segment with a known operation and track timecode; evaluate Big Brain before, execute the native operation, re-encode, evaluate after.
4. Load the *real* acceptance policy; produce a typed receipt with inputs, output tensors, delta, gate result and model/binary hashes. If the gate policy is absent, report `JUDGE_OUTPUT_ONLY`, not PASS.
5. Only then extend to complete track-level temporal trajectory and Ableton Live automation.

## Repository / scope decision

**Primary project:** `sovereign-audio-intelligence` (this artifact).  
**Ableton:** optional adapter package handling `.als`, device control, clips, automation and export.  
**Do not** relocate the entire native inference/registry subsystem into the Ableton repository.  
**Do not** publish private model weights, audio stems, credentials, personal workstation manifests, or massive dataset snapshots in a public GitHub repository as part of this architecture document.

---
**Integrity statement:** This is an evidence-oriented architecture checkpoint. Where source documents make stronger claims than live execution verifies, those claims are explicitly labeled historical or unverified.
