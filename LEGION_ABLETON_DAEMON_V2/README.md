# LEGION → Ableton Live Beta: reverse-designed from final playback action

**Finished user action:** In Ableton Live, right-click an **AudioTrack → “LEGION: insert Sovereign audio”** or an **empty ClipSlot → “LEGION: load Sovereign audio”**. A local modal displays verified existing-file sample matches, and the selection goes into Ableton as a real AudioClip through the SDK. No synthetic clips, no `.asd` changes, no copying the user's music collection into a new database.

## Working backward: source-of-truth contracts

1. **Live mutation (final)**: exact SDK v1 methods `AudioTrack.createAudioClip({filePath,startTime})` and `ClipSlot.createAudioClip({filePath})`. Must be invoked by user action; empty Session slot only.
2. **Selection JSON** (`contracts/placement.example.json`): `schema`, `action`, `file_path`, optional `start_time_beats`; returned by the local modal using Ableton's documented `close_and_send` bridge.
3. **Candidate JSON** (`contracts/candidates.example.json`): `file_path`, `label`, `score` (nullable), `source`, `available`. Must map to **an existing file** under allowed roots. `score` is supplied by the original Sovereign actor; we do not fabricate it.
4. **Lookup**: `bridge.py` is a loopback-only HTTP chooser on `127.0.0.1:8096`. `GET /choose`, `GET /api/legion/audio/candidates`, `GET /health`. It reads `LEGION_AUDIO_CANDIDATES` (an actor-exported JSON file) and the recent existing watcher JSONL outbox. New unranked files appear with `analysis_status: discovered_unanalyzed`; scored actor outputs take priority. No POST, arbitrary SQL execution, auth-secret storage, or public HTTP service.
5. **Existing DuckDB/Lance**: actor output is authoritative. `export_candidates.py --input-json` converts existing JSON exports (including `audio_manifest_vectors.json`) into the chooser format; or `--db original.duckdb --query-file authorized_select.sql` uses existing DuckDB **read-only**. Nothing automatically guarantees the historical actor pipeline is executing; your real ranker and schema columns must be connected here.
6. **Ingestion**: `watch_audio.ps1` monitors specified Windows directories, waits for stable files, and emits `legion.audio.file.v1` JSON events to an existing Sovereign actor endpoint (when verified) or JSONL spool. It does **not** write directly into unverified historical tables.

### Contract flow

```text
NEW AUDIO → FileSystemWatcher → legion.audio.file.v1 → EXISTING DuckDB/actor
                                                       ↓ (registered DSP/ONNX)
ABLETON AudioClip ← placement JSON ← local chooser ← candidate JSON ← EXISTING Lance ranker
```

### Startup (Windows)

Use your **licensed** Ableton beta extension project; install the `.tgz` SDK and CLI locally (do not publish them). Copy `extension.ts` and `manifest.json` into that project, then build/package with the Ableton CLI. `extension.ts` type-checks against the uploaded SDK 1.0.0-beta.0 using `tsc --noEmit --target ES2022 --module NodeNext --moduleResolution NodeNext --skipLibCheck`.

Start the chooser using the Python on your workstation (no extra Python packages):

```powershell
$env:LEGION_AUDIO_CANDIDATES = "$env:LOCALAPPDATA\LEGION_DAW\sovereign_candidates.json"
py -3 .\bridge.py --port 8096
```

Export a ranked JSON result **from the existing Sovereign actor** to that location. Or consume the user's 500-record original manifest when available:

```powershell
py -3 .\export_candidates.py --input-json .\audio_manifest_vectors.json --out "$env:LOCALAPPDATA\LEGION_DAW\sovereign_candidates.json"
```

Only paths present on the machine and under allowed audio roots appear in Live's chooser. Scores are nullable; manifest entries are metadata-only and not claimed to be ANN results.

Monitor the previously verified roots with the included watcher:

```powershell
powershell -NoProfile -File .\watch_audio.ps1 -Roots 'E:\OLD ABLETON','E:\music'
```

### Verified / not yet verified

**Verified in this sandbox:** the source compiles against the user-supplied beta SDK declarations; JSON contract validation, candidate deduplication, path-root guard and sample-service HTTP endpoints are unit tested on Linux. All three uploaded Ableton beta packages were saved to the user's Google Drive in a prior turn.

**Not verified:** running this extension in your Windows Ableton beta, the original Sovereign actor → JSON export binding, and live Lance ANN results. They require your Windows workstation with Ableton Live beta and original SQL actor registrations. No real clips were changed during sandbox tests.

**Security:** Strict loopback bind, roots checked against filesystem, no general SQL/HTTP command endpoint. Keep beta SDK archives privately; this package contains only our original code and JSON contracts.

### Dataset investigation

The 500 available `audio_manifest_vectors.json` entries are **494 WAV and 6 MP3**, all referencing **C:**, not the E: drive. All 500 `vector` fields are *strings* like `[Vector dimension: 768]`, **not actual embedding arrays**. They can seed exact-path lookup, but not a Lance ANN similarity search. The original E: audio collection and numerical vectors must come from your workstation's existing indexes and registered models. See `ORIGINAL_MANIFEST_AUDIT.json`.

To start watching as well as browsing use `START_BRIDGE_WINDOWS.ps1 -StartWatcher` (if configured roots exist). Watcher-discovered files are immediately selectable but clearly labeled unranked; this is not a substitute for real DSP/ONNX analysis.
