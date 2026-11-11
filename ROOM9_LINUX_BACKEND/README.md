# ROOM9 — Native DuckDB SQL/JSON sovereign bootstrap

**Executed in Linux sandbox** on the actual bundled libraries, ONNX binaries, Parquet sources and two downloaded Drive JSON maps. Native Sovereign functions are registered on the **same DuckDB connection** as the source views and remain callable until the process exits. No registry tables are fabricated.

## Run

```bash
./run.sh
# or for a live SQL session:
ROOM9_STDIN_SQL=1 ./run.sh
# with original lakehouse available locally:
SOVEREIGN_DUCKDB_PATH=/absolute/path/to/web_intel_sonicdb.duckdb ROOM9_STDIN_SQL=1 ./run.sh
```

The supplied Linux executable is built for Linux x86_64. `./build.sh` recompiles it against the included DuckDB and ONNX C headers and shared libraries. It uses no network/CDN and requires a compatible glibc system.

The startup loads every available `sovereign_inspection/sovereign_master_distribution/binaries/*.so`, tries every named DuckDB extension, initializes the four Sovereign ONNX models and publishes these **real SQL UDFs**:

- `sovereign_native_dot4(8 FLOAT arguments)` — calls native SIMD `sovereign_dot_product_f32`.
- `sovereign_native_models()` / `sovereign_native_lanes()` — call the native omni actor exports.
- `sovereign_onnx_projection_first()` / `sovereign_onnx_steerer_first()` / `sovereign_onnx_decoder_first()` / `sovereign_onnx_rotator_first()` — execute actual ONNX Runtime models using deterministic sample tensor inputs, return the first output float.

The ONNX UDFs demonstrate the actual runtime binding; they **do not** constitute an application-specific inference feed from the stored audio records. The two-model steerer→decoder tensor handoff was separately demonstrated in a preceding proof and is not implemented in this SQL bootstrap.

Six `CREATE TEMP VIEW` operations map the existing local Parquet and JSON files without copying/replacing existing tables:
`audio_manifest`, `metadata_vectors`, `audio_vibe`, `core_memory`, `onnx_actor_map`, `onnx_brain_integration`.

Try this after startup in interactive mode:

```sql
SELECT json_object('actor', 'sovereign_onnx_projection_first', 'result', sovereign_onnx_projection_first())::VARCHAR;
SELECT item.model_name, item.old_langgraph_node
FROM onnx_actor_map, UNNEST(mappings) AS t(item) LIMIT 10;
SELECT sovereign_native_dot4(1::FLOAT,2::FLOAT,3::FLOAT,4::FLOAT,5::FLOAT,6::FLOAT,7::FLOAT,8::FLOAT);
```

## Precise limitations

1. This package does **not** contain your 507MB `web_intel_sonicdb.duckdb`: Drive rejected its transfer over 256MB. Point `SOVEREIGN_DUCKDB_PATH` at the real file to connect to that database. It will then additionally read existing persistent catalogs, but this bootstrap does not yet discover and invoke all the unknown custom registry boot routines from the original DB.
2. Eight native ELF libraries loaded, but several do not expose DuckDB's standard extension ABI; hence SQL registrations here use documented DuckDB C API callbacks, not blind `LOAD foo.so`.
3. `LOAD lance`, `LOAD vss`, `LOAD ai` still fail in this sandbox: compatible DuckDB `.duckdb_extension` binaries were not provided. No genuine Lance ANN search has been run.
4. The available Drive JSON maps contain historical model/actor wiring metadata but are not a complete runtime registry snapshot. Likewise six data views are not all your Drive/Windows data.
5. Not a production authorization/sandbox: the interactive SQL mode is for trusted local queries only.

Check **ROOM9_FULL_STARTUP_VERIFICATION.json** and **ROOM9_SQL_NATIVE_BOOT_RECEIPT.jsonl** for actual execution results.
