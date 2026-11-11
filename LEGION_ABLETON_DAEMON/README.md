# LEGION DAW — Ableton beta + filesystem audio event bridge

**Status:** original source, static-checked against user-supplied beta typings; not tested inside Ableton or connected to the user's historical SQL actor dispatch. Does not include or redistribute Ableton's proprietary beta SDK.

## What the provided beta SDK supports (verified from `index.d.mts`)

- `AudioClip.filePath`: identify audio used by a Live clip.
- `AudioTrack.createAudioClip({filePath,startTime,...})`: place a WAV/audio file on an Arrangement track.
- `ClipSlot.createAudioClip({filePath,...})`: put audio into a Session slot.
- `Resources.importIntoProject(filePath)`: copy an external file into the Live project.
- `Resources.renderPreFxAudio(track,startTime,endTime)`: render track audio into a WAV.
- Context menu command registration: `Commands.registerCommand` + `Ui.registerContextMenuAction`.

**Not established:** the SDK itself exposes a general OS file-watcher, the binary `.asd` analysis format, unrestricted arbitrary network I/O, or a built-in API for Sovereign DuckDB/LanceDB. The file-watcher must run externally, and the existing DuckDB actor endpoint needs to be bound by its actual documented contract.

## Windows audio watcher

PowerShell 5+ script `watch_audio.ps1` uses .NET `FileSystemWatcher` for real-time change notifications and periodic reconciliation. It watches all subfolders, ignores `.asd`, waits for files to settle, remembers file length/mtime fingerprints, emits JSONL events, and avoids altering audio files.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\watch_audio.ps1 -Roots 'E:\OLD ABLETON','E:\music'
```

Events default to `%LOCALAPPDATA%\LEGION_DAW\audio_events.jsonl`. The spool is an **outbox** for your existing Sovereign actor; it is **not a new DuckDB database or schema**. Once a real authenticated actor endpoint has been verified, pass `-ActorEndpoint 'http://127.0.0.1:<actual_port>/<actual_route>'` to POST the same records instead of spooling. Never guess a route; don't point directly at unprotected public MCP/SQL services.

Sample event:

```json
{"event":"audio_file_discovered","schema":"legion.audio.file.v1","path":"E:\\music\\loop.wav","bytes":1000000,"extension":".wav","last_modified_utc":"2026-11-11T08:00:00Z","fingerprint":"1000000:638984160000000000","detected_utc":"2026-11-11T08:00:03Z","source":"legion_windows_fs_watcher","action":"match_existing_registry_then_dispatch"}
```

## Ableton extension

`extension.ts` registers an AudioClip context menu command and resolves `AudioClip.filePath` with the supplied beta API. It is a minimal proof of clip-to-file mapping; the external watcher already discovers paths. Build it **inside your licensed local SDK project**, rather than checking SDK code or binaries into GitHub.

## Safety and integration

- User-supplied beta SDK terms restrict standalone SDK redistribution and treat non-public beta material as confidential. Keep the `.tgz` archives in private storage. Our own code is okay to publish; a private GitHub repository is not a blanket license override.
- No modifications to Ableton `.asd` files, project audio, or existing database schema.
- No bulk copying 500GB of audio to cloud; only metadata and existing native actor commands need leave the watcher.
- The watcher detects paths and creates event records; it **does not** claim to execute your historical DSP/ONNX/Lance actors without that original registration layer.
