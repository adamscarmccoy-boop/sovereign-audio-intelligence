# LEGION DAW â Windows audio discovery daemon (original code, no proprietary SDK dependencies)
# Watches configured folders and emits idempotent JSON events. Does not edit .asd/audio files,
# install a database, or assume an unverified Sovereign actor endpoint exists.
[CmdletBinding()]
param(
  [string[]]$Roots = @('E:\OLD ABLETON','E:\music'),
  [string]$Spool = "$env:LOCALAPPDATA\LEGION_DAW\audio_events.jsonl",
  [string]$StateFile = "$env:LOCALAPPDATA\LEGION_DAW\audio_seen.json",
  [string]$ActorEndpoint = '',
  [string]$AuthToken = $env:LEGION_AUDIO_ACTOR_TOKEN,
  [switch]$SkipInitialScan,
  [int]$StabilitySeconds = 3,
  [int]$RescanMinutes = 60
)
$ErrorActionPreference='Stop'
$extensions = @('.wav','.aif','.aiff','.flac','.mp3','.ogg','.m4a','.w64','.caf')
$script:watchers = [System.Collections.Generic.List[System.IO.FileSystemWatcher]]::new()
$script:subscriptions = [System.Collections.Generic.List[string]]::new()
$script:pending = [System.Collections.Generic.Dictionary[string,datetime]]::new([System.StringComparer]::OrdinalIgnoreCase)
$script:seen = [System.Collections.Generic.Dictionary[string,string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$script:roots = @($Roots | Where-Object {Test-Path -LiteralPath $_ -PathType Container} | ForEach-Object {(Resolve-Path -LiteralPath $_).Path} | Select-Object -Unique)
$spoolDir = Split-Path -Parent $Spool; if ($spoolDir) { [System.IO.Directory]::CreateDirectory($spoolDir) | Out-Null }
$stateDir = Split-Path -Parent $StateFile; if ($stateDir) {[System.IO.Directory]::CreateDirectory($stateDir) | Out-Null}
if (Test-Path -LiteralPath $StateFile) {
 try {
   $loaded = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
   foreach($item in $loaded.PSObject.Properties) {$script:seen[$item.Name]=[string]$item.Value}
 } catch { Write-Warning "State read failed; continuing with empty state: $_" }
}
function Queue-Audio([string]$path) {
 if ([string]::IsNullOrWhiteSpace($path)) {return}
 if ($extensions -notcontains [System.IO.Path]::GetExtension($path).ToLowerInvariant()) {return}
 $script:pending[$path]=[datetime]::UtcNow
}
function Emit-Record([System.IO.FileInfo]$file) {
 $p = $file.FullName
 $fingerprint = "{0}:{1}" -f $file.Length,$file.LastWriteTimeUtc.Ticks
 if ($script:seen.ContainsKey($p) -and $script:seen[$p] -eq $fingerprint) {return}
 $item = [ordered]@{
   event='audio_file_discovered'; schema='legion.audio.file.v1';
   path=$p; bytes=[int64]$file.Length; extension=$file.Extension.ToLowerInvariant();
   last_modified_utc=$file.LastWriteTimeUtc.ToString('o');
   fingerprint=$fingerprint; detected_utc=[datetime]::UtcNow.ToString('o');
   source='legion_windows_fs_watcher'; action='match_existing_registry_then_dispatch'
 }
 $json = ConvertTo-Json -InputObject $item -Compress -Depth 5
 if ([string]::IsNullOrWhiteSpace($ActorEndpoint)) {
   [System.IO.File]::AppendAllText($Spool,$json+[Environment]::NewLine,[System.Text.Encoding]::UTF8)
 } else {
   $url = [uri]$ActorEndpoint
   if ($url.Host -notin @('127.0.0.1','localhost','::1') -and $url.Scheme -ne 'https') {
      throw 'Non-local actor endpoints must use HTTPS.'
   }
   $headers = @{}; if ($AuthToken) {$headers['Authorization']="Bearer $AuthToken"}
   Invoke-RestMethod -Uri $ActorEndpoint -Method Post -ContentType 'application/json' -Headers $headers -Body $json -TimeoutSec 10 | Out-Null
 }
 $script:seen[$p]=$fingerprint
 Write-Host "Indexed event: $p"
}
function Drain-Queue {
 $now=[datetime]::UtcNow
 foreach($p in @($script:pending.Keys)) {
  if (($now - $script:pending[$p]).TotalSeconds -lt $StabilitySeconds) {continue}
  try {
   $f=Get-Item -LiteralPath $p -ErrorAction Stop
   if(-not ($f -is [System.IO.FileInfo])) { $script:pending.Remove($p)|Out-Null;continue }
   if (($now - $f.LastWriteTimeUtc).TotalSeconds -lt $StabilitySeconds) {continue}
   $stream=[System.IO.File]::Open($p,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::Read)
   try { Emit-Record $f } finally {$stream.Dispose()}
   $script:pending.Remove($p)|Out-Null
  } catch [System.IO.FileNotFoundException] {$script:pending.Remove($p)|Out-Null}
    catch {Write-Warning "Retrying pending file '$p': $_"; $script:pending[$p]=[datetime]::UtcNow}
 }
}
function Save-State {
 $obj=@{};foreach($key in $script:seen.Keys){$obj[$key]=$script:seen[$key]}
 $tmp="$StateFile.tmp"; [System.IO.File]::WriteAllText($tmp,(ConvertTo-Json -InputObject $obj -Depth 3 -Compress),[System.Text.Encoding]::UTF8)
 Move-Item -LiteralPath $tmp -Destination $StateFile -Force
}
function Scan-Folders {
 foreach($root in $script:roots) {
   Get-ChildItem -LiteralPath $root -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $extensions -contains $_.Extension.ToLowerInvariant() } |
    ForEach-Object { Queue-Audio $_.FullName }
 }
}
if ($script:roots.Count -eq 0) {throw "No configured folder exists. Roots: $($Roots -join ', ')"}
try {
 foreach($root in $script:roots) {
   $w=[System.IO.FileSystemWatcher]::new($root)
   $w.IncludeSubdirectories=$true; $w.Filter='*'; $w.NotifyFilter=[System.IO.NotifyFilters]'FileName, LastWrite, Size, CreationTime'
   foreach($eventName in @('Created','Changed','Renamed')) {
     $source="legion.$($script:watchers.Count).$eventName"
     Register-ObjectEvent -InputObject $w -EventName $eventName -SourceIdentifier $source | Out-Null
     $script:subscriptions.Add($source)
   }
   $w.EnableRaisingEvents=$true; $script:watchers.Add($w)
   Write-Host "Watching $root"
 }
 if(-not $SkipInitialScan) {Write-Host 'Scanning existing files...';Scan-Folders}
 $lastSave=[datetime]::UtcNow; $lastScan=[datetime]::UtcNow
 while($true) {
   foreach($ev in @(Get-Event | Where-Object { $_.SourceIdentifier -like 'legion.*' })) {
      if($ev.SourceEventArgs.FullPath){ Queue-Audio $ev.SourceEventArgs.FullPath }
      Remove-Event -EventIdentifier $ev.EventIdentifier -ErrorAction SilentlyContinue
   }
   Drain-Queue
   if(([datetime]::UtcNow-$lastSave).TotalSeconds -ge 30){Save-State;$lastSave=[datetime]::UtcNow}
   if($RescanMinutes -gt 0 -and ([datetime]::UtcNow-$lastScan).TotalMinutes -ge $RescanMinutes){Scan-Folders;$lastScan=[datetime]::UtcNow}
   Start-Sleep -Milliseconds 700
 }
} finally {
 Save-State
 foreach($id in $script:subscriptions){Unregister-Event -SourceIdentifier $id -ErrorAction SilentlyContinue}
 foreach($w in $script:watchers){$w.Dispose()}
}
