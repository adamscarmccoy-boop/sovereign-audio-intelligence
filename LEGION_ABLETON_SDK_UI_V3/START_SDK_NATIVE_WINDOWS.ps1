# Starts JSON-only backend; no HTML HUD and no modal webview inside Ableton.
[CmdletBinding()]
param([string]$Catalog="$env:LOCALAPPDATA\LEGION_DAW\sovereign_candidates.json")
$ErrorActionPreference='Stop'
$dir=Split-Path -Parent $MyInvocation.MyCommand.Path
$python=Get-Command py -ErrorAction SilentlyContinue
if(-not $python){$python=Get-Command python -ErrorAction SilentlyContinue}
if(-not $python){throw 'Python 3 must be installed on the workstation.'}
Write-Host 'Starting LEGION native SDK companion (JSON only) 127.0.0.1:8096'
& $python.Source "$dir\candidate_service.py" --port 8096 --catalog $Catalog
