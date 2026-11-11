# ROOM9 Ableton sample chooser: uses existing manifests/actor outputs. No new databases.
[CmdletBinding()]
param(
  [string]$Catalog = "$env:LOCALAPPDATA\LEGION_DAW\sovereign_candidates.json",
  [switch]$StartWatcher
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$python=Get-Command py -ErrorAction SilentlyContinue
if(-not $python){$python=Get-Command python -ErrorAction SilentlyContinue}
if(-not $python){throw 'Python runtime not found (bridge uses only standard library).'}
$manifest=Join-Path $root 'private_data\audio_manifest_vectors.json'
if(-not(Test-Path -LiteralPath $Catalog) -and (Test-Path -LiteralPath $manifest)) {
  & $python.Source "$root\export_candidates.py" --input-json $manifest --out $Catalog
  if($LASTEXITCODE){throw 'Local manifest conversion failed'}
}
$env:LEGION_AUDIO_CANDIDATES=$Catalog
if($StartWatcher){
 $existingRoots = @('E:\OLD ABLETON','E:\music') | Where-Object {Test-Path -LiteralPath $_}
 if($existingRoots.Count){
   $quotedScript='"' + (Join-Path $root 'watch_audio.ps1') + '"'
   $quotedRoots=($existingRoots | ForEach-Object {'"'+$_+'"'}) -join ' ' 
   $argsText="-NoProfile -ExecutionPolicy Bypass -File $quotedScript -Roots $quotedRoots"
   $proc=Start-Process -FilePath powershell.exe -ArgumentList $argsText -PassThru
   Write-Host "Audio discovery daemon started PID $($proc.Id)"
 }else{Write-Warning 'No E:\ audio roots found; watcher was not started'}
}
Write-Host 'LEGION chooser starting on http://127.0.0.1:8096/choose'
& $python.Source "$root\bridge.py" --port 8096 --catalog $Catalog
