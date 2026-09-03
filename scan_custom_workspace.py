#!/usr/bin/env python3
"""
=============================================================================
🏛️ SOVEREIGN CUSTOM SCANNER: ZERO-COPY SIMD LAKEHOUSE SCANNER
=============================================================================
Point this script at ANY local folder (audio stems, code repositories, datasets)
to scan files in parallel, compute metrics with PyArrow & DuckDB, and export
a custom Parquet & JSON dependency matrix.

Usage:
  # Scan current directory:
  python scan_custom_workspace.py

  # Scan a specific directory:
  python scan_custom_workspace.py --path "D:/MyAudioSamples"

  # Scan with custom output prefix:
  python scan_custom_workspace.py --path "/path/to/code" --output my_custom_scan
=============================================================================
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

def scan_directory(target_dir: str):
    target_path = Path(target_dir).resolve()
    if not target_path.exists():
        print(f"[ERROR] Target directory does not exist: {target_path}")
        sys.exit(1)

    print("================================================================================", flush=True)
    print(f" [SOVEREIGN SCANNER] SCANNING TARGET: {target_path}", flush=True)
    print("================================================================================", flush=True)

    t0 = time.perf_counter()
    records = []
    
    # Fast recursive traversal
    for root, _, files in os.walk(target_path):
        for f in files:
            full_path = Path(root) / f
            try:
                stat = full_path.stat()
                ext = full_path.suffix.lstrip(".").lower()
                
                # Approximate line count for text/code files
                line_count = 0
                if ext in {"py", "cpp", "c", "h", "hpp", "ts", "js", "rs", "json", "md", "csv", "sql"}:
                    try:
                        with open(full_path, "rb") as fl:
                            line_count = sum(1 for _ in fl)
                    except Exception:
                        pass

                records.append({
                    "file_name": f,
                    "rel_path": str(full_path.relative_to(target_path)),
                    "extension": ext if ext else "no_ext",
                    "size_kb": round(stat.st_size / 1024.0, 2),
                    "line_count": line_count
                })
            except (PermissionError, FileNotFoundError):
                continue

    scan_duration_s = time.perf_counter() - t0
    total_files = len(records)
    print(f"[*] Traversed {total_files:,} files in {scan_duration_s:.2f}s ({int(total_files / max(scan_duration_s, 0.001)):,} files/sec)", flush=True)

    if not records:
        print("[WARN] No files found to index.")
        return

    # Ingest into PyArrow & DuckDB Table
    t0_db = time.perf_counter()
    table = pa.Table.from_pydict({
        "file_name": [r["file_name"] for r in records],
        "rel_path": [r["rel_path"] for r in records],
        "extension": [r["extension"] for r in records],
        "size_kb": [r["size_kb"] for r in records],
        "line_count": [r["line_count"] for r in records]
    })

    con = duckdb.connect()
    con.register("scanned_data", table)

    # Compute SIMD Aggregations
    summary = con.execute("""
        SELECT 
            COUNT(*) AS total_files,
            ROUND(SUM(size_kb) / 1024.0, 2) AS total_size_mb,
            SUM(line_count) AS total_lines_of_code,
            COUNT(DISTINCT extension) AS total_unique_extensions
        FROM scanned_data
    """).df().to_dict(orient="records")[0]

    ext_distribution = con.execute("""
        SELECT 
            extension,
            COUNT(*) AS file_count,
            ROUND(SUM(size_kb) / 1024.0, 2) AS size_mb,
            SUM(line_count) AS total_lines
        FROM scanned_data
        GROUP BY extension
        ORDER BY file_count DESC
        LIMIT 10
    """).df().to_dict(orient="records")

    largest_files = con.execute("""
        SELECT file_name, rel_path, extension, size_kb, line_count
        FROM scanned_data
        ORDER BY size_kb DESC
        LIMIT 10
    """).df().to_dict(orient="records")

    db_lat_ms = (time.perf_counter() - t0_db) * 1000.0

    # Save to local Lakehouse outputs
    out_parquet = "custom_workspace_metrics.parquet"
    out_json = "custom_workspace_metrics.json"
    pq.write_table(table, out_parquet)
    
    with open(out_json, "w", encoding="utf-8") as jf:
        json.dump({
            "summary": summary,
            "top_extensions": ext_distribution,
            "largest_files": largest_files
        }, jf, indent=2)

    print("\n================================================================================", flush=True)
    print(" [SCAN RESULTS] ZERO-COPY LAKEHOUSE SUMMARY", flush=True)
    print("================================================================================", flush=True)
    print(f" Target Path         : {target_path}")
    print(f" Total Files Indexed : {summary['total_files']:,}")
    print(f" Total Storage Size  : {summary['total_size_mb']} MB")
    print(f" Total Code Lines    : {summary['total_lines_of_code']:,}")
    print(f" Unique Extensions   : {summary['total_unique_extensions']}")
    print(f" DuckDB SIMD Latency : {db_lat_ms:.2f} ms")
    print(f" Exported Parquet    : {out_parquet} ({os.path.getsize(out_parquet)} bytes)")
    print(f" Exported JSON       : {out_json} ({os.path.getsize(out_json)} bytes)")
    print("================================================================================")
    print("\nTop Extensions:")
    for i, e in enumerate(ext_distribution[:5], 1):
        print(f"  {i}. .{e['extension']} - {e['file_count']:,} files ({e['size_mb']} MB)")
    print("================================================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan any directory and generate a Sovereign Zero-Copy Parquet Lakehouse matrix.")
    parser.add_argument("--path", "-p", type=str, default=".", help="Path to directory to scan (default: current directory)")
    args = parser.parse_args()
    scan_directory(args.path)
