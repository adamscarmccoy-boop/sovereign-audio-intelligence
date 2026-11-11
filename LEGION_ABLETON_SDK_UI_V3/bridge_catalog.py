#!/usr/bin/env python3
"""Original catalog normalization and spool reader for SDK-native LEGION UI.

No custom DB, no filesystem copies, no unknown SQL execution, no cloud upload.
Reads an existing actor's JSON catalog/export (LEGION_AUDIO_CANDIDATES).
"""
from __future__ import annotations
import json
import os
import re
import pathlib

SUPPORTED={'.wav','.aif','.aiff','.flac','.mp3','.ogg','.m4a','.w64','.caf'}
DEFAULT_ROOTS=[r'E:\OLD ABLETON',r'E:\music',r'C:\Users\adams\MusicSandbox',r'C:\WEB CASE STUDY']
MAX_CANDIDATES=5000
MAX_SPOOL_BYTES=8*1024*1024


def windows_norm(path:str)->str:
    return path.replace('/','\\').casefold().rstrip('\\')


def allow_root(path:str, roots:list[str])->bool:
    p=windows_norm(path)
    return any(p==windows_norm(r) or p.startswith(windows_norm(r)+'\\') for r in roots)


def is_present(path:str)->bool:
    return os.path.isfile(path)


def normalize_catalog(input_obj,roots:list[str],exists=None):
    if exists is None: exists=is_present
    """Normalize existing actor output OR supplied audio_manifest_vectors records."""
    items=input_obj.get('candidates',[]) if isinstance(input_obj,dict) else input_obj
    if not isinstance(items,list): raise ValueError('expected array or {"candidates": []}')
    out=[];seen=set()
    for rec in items[:MAX_CANDIDATES*3]:
        if not isinstance(rec,dict):continue
        if rec.get('type')=='audio_asset' and isinstance(rec.get('metadata'),str):
            try: meta=json.loads(rec['metadata'])
            except (ValueError,TypeError):continue
            path=meta.get('Full_Path')
            candidate={'file_path':path,'label':meta.get('Filename'),'source':'audio_manifest_vectors.json','score':None}
        else:
            candidate=rec
            path=candidate.get('file_path') or candidate.get('path')
        if not isinstance(path,str) or not path.strip():continue
        p=path.strip()
        if not re.match(r'^[A-Za-z]:\\',p):continue
        if not allow_root(p,roots):continue
        if pathlib.PureWindowsPath(p).suffix.lower() not in SUPPORTED:continue
        if pathlib.PureWindowsPath(p).name.startswith('._'):continue
        key=windows_norm(p)
        if key in seen:continue
        seen.add(key)
        file_exists=bool(exists(p))
        if not file_exists:continue  # never promise a clip Ableton cannot open
        score=candidate.get('score')
        if not isinstance(score,(float,int)) or isinstance(score,bool):score=None
        source=str(candidate.get('source') or 'sovereign_actor_export')[:100]
        out.append({'schema':'legion.audio.candidate.v1','file_path':p,'label':str(candidate.get('label') or pathlib.PureWindowsPath(p).name)[:220],
                    'score':score,'source':source,'analysis_status':'discovered_unanalyzed' if source=='legion_windows_fs_watcher' else 'existing_registry_metadata',
                    'available':True})
        if len(out)>=MAX_CANDIDATES:break
    return sorted(out,key=lambda x:(x['score'] is None,-(x['score'] or 0),x['label'].lower()))

def read_spool(path:str):
    """Read bounded newest JSONL discovery events; never consumes/mutates the outbox."""
    if not path or not os.path.isfile(path):return []
    events=[]
    with open(path,'rb') as stream:
        stream.seek(0,2);size=stream.tell();start=max(0,size-MAX_SPOOL_BYTES)
        stream.seek(start)
        if start:stream.readline()  # discard potentially truncated first record
        for raw in stream:
            try:r=json.loads(raw.decode('utf-8-sig'))
            except (ValueError,UnicodeError):continue
            if isinstance(r,dict) and r.get('schema')=='legion.audio.file.v1' and r.get('event')=='audio_file_discovered':
                events.append({'path':r.get('path'),'source':'legion_windows_fs_watcher','score':None})
    return events[-MAX_CANDIDATES:]

