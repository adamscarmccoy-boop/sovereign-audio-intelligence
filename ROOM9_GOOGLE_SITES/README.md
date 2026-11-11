# ROOM9 · Sovereign Control Center — Google Sites embed

A responsive, dark-mode website shell for the existing self-hosted ROOM9 DuckDB/LanceDB/ONNX control plane.

**[Download complete Google Sites embed ZIP](https://drive.google.com/file/d/1SxLTY2bm6Df0tNdhQ5v6Avov3dJjkX0D/view)**

**[Get the standalone embed HTML](https://drive.google.com/file/d/1-hlyXlWvsk8oUigxkLjKkBcNNGEXIJng/view)**

The ZIP includes `room9_google_sites_embed.html` (paste the entire contents into **Google Sites → Insert → Embed → Embed code**) and `README.txt`. Google Sites publishing still must be completed in the owner's Google Sites editor; this GitHub commit and Drive upload do **not** publish a Google Site.

### Features

- Responsive DuckDB, LanceDB, runtime health, ONNX and native actor launcher cards.
- Editable/persisted URL for your **actual** ROOM9 backend.
- GET `/health` browser connectivity probe with clear CORS/auth errors.
- Separate navigation to original ROOM9 Lance API path (`/api/room9/lance/tables`) when available.
- Optional iframe view (requires server frame-ancestors policy that permits Google Sites).
- No fake statuses or fabricated calls; the frontend does not implement a backend.
- Original Windows server default: `http://127.0.0.1:8097`. For remote use, a separately authenticated HTTPS route to ROOM9 is necessary. The existing Tailscale `/mcp` path is a different server and should not be substituted.

### Security

Never expose unrestricted SQL/MCP/ONNX actor execution anonymously. A public Google Site is not authentication for the underlying runtime.
