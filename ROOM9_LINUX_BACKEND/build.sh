#!/bin/sh
set -eu
cd "$(dirname "$0")"
ln -sf libonnxruntime.so.1.31.0 ort_drive_run/lib/libonnxruntime.so
ln -sf libonnxruntime.so.1.31.0 ort_drive_run/lib/libonnxruntime.so.1
cc -O2 room9_full_startup.c -L lance_runtime_probe -lduckdb -L ort_drive_run/lib -lonnxruntime -Wl,-rpath,'$ORIGIN/lance_runtime_probe' -Wl,-rpath,'$ORIGIN/ort_drive_run/lib' -ldl -lm -o room9_full_startup
printf 'Compiled room9_full_startup\n'
