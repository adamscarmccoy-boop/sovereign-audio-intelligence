# ROOM9 Linux backend — original executed package

## Full Linux backend archive (46,857,800 bytes)
**[Download complete verified Linux backend ZIP from Google Drive](https://drive.google.com/file/d/1jU5SLiGURWlDupyoS21a6ISNyoz44C5o/view)**

The original native archive contains the Linux DuckDB shared C library, compiled Sovereign ELF kernels, ONNX runtime, four ONNX models, Parquet/JSON data and the executable C startup. This repository includes **the original source, scripts, README and verification JSON** in this directory.

- Source: [room9_full_startup.c](./room9_full_startup.c)
- Build: [build.sh](./build.sh)
- Run: [run.sh](./run.sh)
- Execution receipt: [ROOM9_FULL_STARTUP_VERIFICATION.json](./ROOM9_FULL_STARTUP_VERIFICATION.json)
- Frontend site: [ROOM9_WEBSITE/index.html](../ROOM9_WEBSITE/index.html)

**Important:** GitHub stores source and receipts; the 46.9MB compiled ZIP is hosted on Drive. A direct GitHub API blob upload of the ZIP failed due to connector transport limits, so the ZIP is not yet a tracked GitHub file. Linux native execution was verified in the sandbox; full original historical DuckDB and Lance ANN integration was not.

The older separated distribution was deleted at the user's direction, and this newly uploaded copy of the full Linux runtime is the canonical archive on Drive.
