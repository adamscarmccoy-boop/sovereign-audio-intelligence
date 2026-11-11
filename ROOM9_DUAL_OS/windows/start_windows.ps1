param(
 [string]$Lakehouse = 'C:\WEB CASE STUDY\web_intel_sonicdb.duckdb'
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not(Test-Path -LiteralPath "$root\room9_windows_startup.exe")) {throw 'EXE not built yet. Run build_windows.ps1 from an x64 Native Tools session.'}
$env:PATH="$root;$root\native;"+$env:PATH
if(Test-Path -LiteralPath $Lakehouse){$env:SOVEREIGN_DUCKDB_PATH=$Lakehouse}else{Remove-Item Env:SOVEREIGN_DUCKDB_PATH -ErrorAction SilentlyContinue}
$env:ROOM9_STDIN_SQL='1'
Set-Location $root
& "$root\room9_windows_startup.exe" $root
