# LEGION / Ableton Beta — SDK-native UI v0.3.0

**Replaces the blocking HTML HUD and SDK modal dialogs.** No embedded HTML browser, no ROOM9 iframe, no WebView, no `ui.showModalDialog()` and no modal progress dialogs in this path.

## Native Ableton UI

The uploaded `@ableton-extensions/sdk@1.0.0-beta.0` exposes UI APIs for **context menus**, **modal dialogs**, and **progress dialogs**, but no documented persistent side panel. This V3 uses *only* `ui.registerContextMenuAction` as the Live UI surface.

Right-click an audio track: **Insert top sample at beat 0**, **Insert next ranked sample at beat 0**. Right-click an empty Session clip slot: **Load top** or **Load next ranked**. Right-click an Audio Clip: **Log audio path**. The actions use `commands.registerCommand` and the typed `AudioTrack.createAudioClip` / `ClipSlot.createAudioClip` APIs. The placement action is async, with a 2-second timeout for the JSON GET and a pending-operation guard; it never opens a blocking modal window. `next` cycles ranked candidates; it does not claim to be similarity search unless your Sovereign ranker supplies that ordering.

The `candidate_service.py` companion serves **JSON only** (`GET /health` and `GET /api/legion/audio/candidates`) at `127.0.0.1:8096`. `/choose` does not exist; HTTP POST returns 405. `bridge_catalog.py` carries previously verified file-root validation and JSON normalization; the HTML chooser is not used or served. The server never changes a DuckDB table and does not upload audio.

The host still requires an existing valid `LEGION_AUDIO_CANDIDATES` JSON export from your Sovereign actor or an authorized read-only DuckDB SELECT. No fabricated scores: unranked files have score=null. Only actual files under configured allowed roots are returned. If the JSON service isn't running, the extension logs a short error and does not mutate Live. If the destination Session slot is occupied, it does not overwrite it. Arrangement insertion is explicitly at beat **zero** because an AudioTrack context-menu callback does not document a mouse-click timeline beat.

## Install on Windows

1. In your licensed local Ableton extension project, use SDK/CLI beta 1.0.0 locally; don't publish the SDK archives themselves.
2. Replace the old HUD/modal `extension.ts` with this `extension.ts` and keep the `manifest.json` entry `dist/extension.js` as expected by your Ableton extension toolchain.
3. Build/package using your local Ableton Extensions CLI and load it in your Live beta.
4. Set `$env:LEGION_AUDIO_CANDIDATES` to a real actor export or create it using `export_candidates.py`. Launch `START_SDK_NATIVE_WINDOWS.ps1`.
5. Test one empty Session slot first; check Live's extension console and existing sample file availability.

## What is verified

- TypeScript type-check against user-supplied Ableton SDK 1.0.0-beta.0 declarations.
- JSON-only service endpoints, allowed-root filtering, no HUD route, and HTTP 405 POST in sandbox tests.

**Not verified:** Live beta runtime loading, actual insert into a real Live Set, and historical DuckDB/Lance ranker binding. The SDK runtime's availability of global `fetch` must be tested inside Live; if unavailable, this needs an SDK-supported network adapter rather than an undocumented host escape hatch. The filesystem watcher remains separate, so its activity cannot freeze Live's UI thread.
