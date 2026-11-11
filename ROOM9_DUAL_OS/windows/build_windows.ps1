param(
 [string]$DuckDbDll = 'C:\WEB CASE STUDY\src\target\release\duckdb.dll',
 [string]$NativeDllFolder = 'C:\WEB CASE STUDY\src\target\release',
 [string]$Lakehouse = 'C:\WEB CASE STUDY\web_intel_sonicdb.duckdb'
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
if (-not (Test-Path -LiteralPath $DuckDbDll)) { throw "DuckDB Windows DLL missing: $DuckDbDll" }
# Require Visual Studio 2022/2026 x64 C/C++ build tools; run from x64 Native Tools PowerShell.
foreach($cmd in @('cl.exe','lib.exe','dumpbin.exe')) { if(-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "Missing $cmd. Launch x64 Native Tools Command Prompt/PowerShell and rerun this script." } }
$symbols=[regex]::Matches((Get-Content "$root\room9_windows_startup.c" -Raw),'\bduckdb_[a-zA-Z_0-9]+\s*\(') | ForEach-Object { $_.Value -replace '\s*\($','' } | Sort-Object -Unique
$exports=(& dumpbin.exe /EXPORTS $DuckDbDll) -join "`n"
$missing=@($symbols | Where-Object { $exports -notmatch "(?m)\b$([regex]::Escape($_))\s*$" })
if($missing.Count){throw "duckdb.dll lacks required exports: $($missing -join ', '). Use an ABI-compatible Windows DuckDB DLL."}
$defs=@('LIBRARY duckdb.dll','EXPORTS') + @($symbols)
[IO.File]::WriteAllLines("$root\duckdb_windows.def",$defs)
& lib.exe '/nologo' '/machine:x64' '/def:duckdb_windows.def' '/out:duckdb_windows_import.lib'
if($LASTEXITCODE){throw 'DuckDB import library generation failed'}
Copy-Item -LiteralPath $DuckDbDll -Destination "$root\duckdb.dll" -Force
$NativeFiles=Get-ChildItem -LiteralPath $NativeDllFolder -Filter '*.dll' -File -ErrorAction Stop | Where-Object { $_.Name -match '(?i)sovereign|lance|onnx' }
foreach($f in $NativeFiles){Copy-Item -LiteralPath $f.FullName -Destination "$root\native\$($f.Name)" -Force}
& cl.exe '/nologo' '/O2' '/W3' '/TC' '/I.' 'room9_windows_startup.c' '/link' '/OUT:room9_windows_startup.exe' 'duckdb_windows_import.lib' 'onnxruntime.lib'
if($LASTEXITCODE){throw "Compilation failed ($LASTEXITCODE)"}
Write-Host "Built: $root\room9_windows_startup.exe" -ForegroundColor Green
Write-Host "DLL copies: $($NativeFiles.Count)" -ForegroundColor Cyan
if(Test-Path -LiteralPath $Lakehouse){Write-Host 'Original lakehouse detected; start.ps1 will use read-only connection.'}
else{Write-Warning 'Original lakehouse not found at specified path; fallback uses in-memory DuckDB.'}
