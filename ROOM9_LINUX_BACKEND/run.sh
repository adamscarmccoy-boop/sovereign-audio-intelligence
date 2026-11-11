#!/bin/sh
set -eu
cd "$(dirname "$0")"
ROOT="$(pwd)"
ln -sf libonnxruntime.so.1.31.0 "$ROOT/ort_drive_run/lib/libonnxruntime.so"
ln -sf libonnxruntime.so.1.31.0 "$ROOT/ort_drive_run/lib/libonnxruntime.so.1"
export LD_LIBRARY_PATH="$ROOT/lance_runtime_probe:$ROOT/ort_drive_run/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
chmod +x "$ROOT/room9_full_startup"
exec "$ROOT/room9_full_startup" "$ROOT"
