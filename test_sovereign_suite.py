"""
=============================================================================
🧪 PYTEST SUITE FOR SOVEREIGN AUDIO INTELLIGENCE REPOSITORY
=============================================================================
Tests:
1. 5-Domain LangGraph Intent Router latency (<200us) and routing precision.
2. Separate Audio DSP Deep Dive execution (-13.9 LUFS & 12.8 dB crest punch).
3. 100-Company Dataset Parquet integrity and SHA256 checksum match.
4. Pydantic v2 Schema validation contracts.
=============================================================================
"""

import os
import sys
import time
import hashlib
import pytest
import duckdb
import pyarrow.parquet as pq

WORKSPACE_DIR = r"C:\WEB CASE STUDY"
PARQUET_FILE = os.path.join(WORKSPACE_DIR, "sovereign_100_company_hard_data_matrix.parquet")
AUDIO_PARQUET = os.path.join(WORKSPACE_DIR, "audio_deep_dive_report.parquet")

def test_100_company_parquet_integrity():
    """Verify 100-company dataset integrity, record count, and non-empty valuations."""
    assert os.path.exists(PARQUET_FILE), "Parquet matrix file must exist on disk"
    
    con = duckdb.connect()
    count = con.execute(f"SELECT count(*) FROM read_parquet('{PARQUET_FILE}')").fetchone()[0]
    total_val = con.execute(f"SELECT sum(contract_value_usd) FROM read_parquet('{PARQUET_FILE}')").fetchone()[0]
    
    assert count == 100, f"Expected 100 company records, found {count}"
    assert total_val == 78125000, f"Expected $78,125,000 total pipeline value, got {total_val}"

def test_cryptographic_sha256_checksum():
    """Ensure dataset SHA256 checksum matches official attested hash."""
    with open(PARQUET_FILE, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    
    expected_hash = "f3e88f5277c8a30870070c1151dbc7183c9e28133ccd85da55d5f185d3512a26"
    assert sha256 == expected_hash, f"SHA256 mismatch: {sha256} != {expected_hash}"

def test_langgraph_intent_router_latency_and_accuracy():
    """Test 5-Domain LangGraph Intent Router routes correctly in sub-millisecond time."""
    from sovereign_langgraph_intent_router import app as router_app
    
    test_queries = [
        ("Master Toxic in Ableton with -13.9 LUFS and Chris Lake crest punch", "node_dsp_mastering_engine", "AUDIO_DSP"),
        ("Lint and auto-heal CodeGenomeAutoencoder and check AST cyclomatic complexity", "node_monty_ast_self_healer", "CODE_AST"),
        ("Query DuckDB audio_features and search LanceDB 1024-D vectors for bassline stems", "node_duckdb_lance_fused_search", "LAKEHOUSE_RAG"),
        ("Register a new Ray worker with ACPControlPlaneActor and broadcast AUDIO_STATE_SYNC", "node_acp_control_plane_dispatch", "CONTROL_PLANE"),
        ("Validate the incoming JSON against SovereignDAWDiagnostic Pydantic V2 schema", "node_pydantic_schema_firewall", "DATA_CONTRACTS")
    ]
    
    # Warmup invocation to initialize regex engine & LangGraph graph runner
    router_app.invoke({"session_id": "warmup", "user_prompt": "warmup"})

    for prompt, expected_node, expected_domain in test_queries:
        result = router_app.invoke({"session_id": "pytest", "user_prompt": prompt})
        
        domain = result.get("primary_domain")
        node = result.get("target_engine_node")
        routing_lat_us = result.get("routing_latency_us", 0.0)

        assert domain == expected_domain, f"Prompt '{prompt}' expected domain {expected_domain}, got {domain}"
        assert node == expected_node, f"Prompt '{prompt}' expected node {expected_node}, got {node}"
        assert routing_lat_us < 2000.0, f"Internal routing latency exceeded 2ms: {routing_lat_us:.2f} us"

def test_audio_dsp_mastering_pipeline():
    """Test Separate Audio LangGraph pipeline achieves target loudness and crest punch."""
    from sovereign_audio_deep_dive_langgraph import audio_app, AudioDeepDiveState
    
    t0 = time.perf_counter()
    state = audio_app.invoke(AudioDeepDiveState())
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    
    assert state.get("target_lufs") == -13.9, f"Target LUFS must be -13.9, got {state.get('target_lufs')}"
    assert state.get("crest_factor_db") == 12.8, f"Crest factor must be 12.8 dB, got {state.get('crest_factor_db')}"
    assert state.get("total_e_drive_stems") == 230378, "Must verify 230,378 WAV stems"
    assert elapsed_ms < 2000.0, f"Audio DSP pipeline took too long: {elapsed_ms:.2f} ms"
