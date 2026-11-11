# ROOM9 Sovereign Native DuckDB — Linux and Windows x64 (2026-11-11)

These are the two original platform packages for the Sovereign/ROOM9 DuckDB → SQL/JSON → native/ONNX startup path. Complete binary packages are archived on the owner's Google Drive (links below). This branch is the GitHub distribution index and audit record; **the ZIP binaries themselves are stored in Drive, not checked into Git**.

## Linux — executed in Linux sandbox

**[ROOM9_NATIVE_DUCKDB_SQL_STARTUP_VERIFIED.zip — Google Drive](https://drive.google.com/file/d/1ZFB8eVUl2eg4Ahvnki7FjeyEfxBEp1dR/view)**

- SHA-256: `02d209662cf1a91a6460322270a388810cb18924e71c16441af7d7cfc06f1e91`
- Approximately 45 MiB compressed.
- Tested DuckDB 2.0.0 C API with one persistent session.
- Eight Linux shared libraries loaded; five bundled DuckDB extensions loaded.
- Four ONNX model calls executed via native SQL UDFs.
- Seven SQL UDFs registered; six temporary JSON/Parquet views.
- Sample receipts: native dot = `70.0`; JSON dispatch = `{"actor":"sovereign_native_dot4","result":70.0}`.
- **Not** full historical DuckDB/Lance actor initialization: original 507 MB database and Lance/VSS/AI extension still unavailable in this sandbox.

Build/run scripts inside ZIP: `build.sh`, `run.sh`. See packaged `README.md` and `ROOM9_FULL_STARTUP_VERIFICATION.json`.

## Windows x64 — source/build package, not a tested Windows executable

**[ROOM9_WINDOWS_NATIVE_DUCKDB_STARTUP_BUILD_PACKAGE.zip — Google Drive](https://drive.google.com/file/d/1syrVszXkj_ueDimPROr3pCVVxNOnYwtE/view)**

- SHA-256: `6805ee8d17f706c327b4a214916b8b4e3e4914f51c049579c3c0900843963ed0`
- Approximately 12 MiB compressed.
- Includes native Windows `onnxruntime.dll`, `onnxruntime_providers_shared.dll`, `onnxruntime.lib`, ONNX models, JSON/Parquet data, C code, PowerShell startup/build scripts.
- Requires **existing workstation** `duckdb.dll`, MSVC x64 build tools, Sovereign custom Windows DLLs, and original DuckDB lakehouse.
- Scripts: `build_windows.ps1`, `start_windows.ps1`.
- **Not executed/validated on Windows**; do not treat as release-ready Windows binary.

## Notes

- Both packages were placed in the Google Drive root on Nov 11, 2026.
- Do not treat `.so` as Windows DLL, or generic native DLL loading as DuckDB SQL UDF registration.
- Loaded JSON/Parquet metadata and example UDFs do not mean every stored historical actor and dependency was initialized.
- GitHub branch: `room9-dual-os-2026-11-11`; kept separate from `main` to avoid overwriting other Sovereign work.
