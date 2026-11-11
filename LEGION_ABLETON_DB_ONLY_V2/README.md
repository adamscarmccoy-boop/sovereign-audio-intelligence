# LEGION Ableton — independent DuckDB/SDK model layer V2

**No existing Sovereign actors or LangGraph instance required.** The native DuckDB C API reads the SDK inventory as a SQL TEMP VIEW. An independent `sdk_routes` JSON relation maps the four verified actions to SDK methods. SQL joins resolve the operation, and six pydantic-core Rust validators check inputs and registry records. The actual Ableton execution is an SDK adapter separate from the database.

The SDK inventory, four explicit routes, and strict argument validators ship with the adapter. **There is no `actor_edges.json`, existing actor registry, MCP gateway, JSON catalog export, or new persistent table.** You can optionally attach your existing DuckDB in READ_ONLY mode by setting `LEGION_DATABASE_PATH`. The SDK capability resolver does not depend on tables in that attached database. LanceDB is not required for the four SDK commands and is not claimed to be connected. The demo runtime is a mock, not running Ableton.

Run `python sovereign_graph.py`, or `python -m unittest discover -s tests -v`. On Windows, configure `LEGION_DUCKDB_SO` to point to a genuine Windows DuckDB DLL with C API exports, and use `LEGION_DATABASE_PATH` only if desired. The provided Linux test uses the local native `.so` for tests.

Next production boundary: SDK runtime JSON transport and direct optional DuckDB/LanceDB reads with no actor dependency. The full SDK graph is not sent to an LLM.
