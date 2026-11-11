#!/usr/bin/env python3
"""Loopback-only, read-only Sovereign sample chooser for the Ableton beta SDK.

No custom DB, no filesystem copies, no unknown SQL execution, no cloud upload.
Reads an existing actor's JSON catalog/export (LEGION_AUDIO_CANDIDATES).
"""
from __future__ import annotations
import json
import os
import re
import argparse
import html
import pathlib
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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

HTML='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LEGION · Select audio</title><style>body{font:14px system-ui;background:#111827;color:#f9fafb;margin:0;padding:20px}h1{margin:0 0 6px;font-size:24px}p{color:#b7c3d6}label{display:block;margin:14px 0 6px}input{font:inherit;border:1px solid #536477;border-radius:6px;padding:10px;background:#1b2838;color:#fff;width:95%}button{cursor:pointer;font:inherit;color:white;background:#315c93;border:0;border-radius:7px;padding:10px}button:disabled{opacity:.5;cursor:not-allowed}.row{border:1px solid #405069;padding:10px;margin:8px 0;border-radius:8px;display:flex;justify-content:space-between;gap:14px;align-items:center}.row small{color:#bacadd;overflow-wrap:anywhere;display:block}.row strong{display:block}.row button{flex-shrink:0}.msg{padding:12px;color:#ffdc9a}</style>
<h1>LEGION / Sovereign audio</h1><p>Choose a file already indexed by the existing Sovereign actor. No audio is uploaded or copied.</p>
<label for="q">Filter audio</label><input id="q" placeholder="Kick, 128, bass, vocal…" autocomplete="off">
<section id="results" aria-live="polite">Loading local catalog…</section>
<script>
const params=new URLSearchParams(location.search);const target=params.get('target')==='session'?'session':'arrangement';
let data=[];const results=document.getElementById('results'),filter=document.getElementById('q');
function closeWith(payload){let json=JSON.stringify(payload);if(window.chrome?.webview?.postMessage){window.chrome.webview.postMessage({method:'close_and_send',params:[json]})}else if(window.webkit?.messageHandlers?.live){window.webkit.messageHandlers.live.postMessage({method:'close_and_send',params:[json]})}else{results.textContent='Requires Ableton Live Extensions dialog host';}}
function render(){const q=filter.value.trim().toLowerCase();results.replaceChildren();const matches=data.filter(r=>(r.label+' '+r.file_path).toLowerCase().includes(q)).slice(0,60);if(!matches.length){const p=document.createElement('p');p.className='msg';p.textContent='No available indexed files match. Export candidates from the existing Sovereign actor first.';results.append(p);return}for(const r of matches){const row=document.createElement('div');row.className='row';const info=document.createElement('div');const strong=document.createElement('strong');strong.textContent=r.label;const small=document.createElement('small');small.textContent=(r.score===null?'Not yet ranked · ':('Score '+r.score+' · '))+r.file_path;info.append(strong,small);const btn=document.createElement('button');btn.textContent=target==='session'?'Load in slot':'Insert clip';btn.addEventListener('click',()=>{const beat=document.getElementById('beat');const startTime=target==='session'?undefined:Number(beat.value);if(target==='arrangement'&&(!Number.isFinite(startTime)||startTime<0)){alert('Start beat must be >= 0');return}closeWith({schema:'legion.audio.placement.v1',action:target==='session'?'create_session_clip':'create_arrangement_clip',file_path:r.file_path,...(target==='arrangement'?{start_time_beats:startTime}:{})});});row.append(info,btn);results.append(row);}}
const beatLabel=document.createElement('label');beatLabel.textContent='Arrangement start (beats)';beatLabel.htmlFor='beat';const beat=document.createElement('input');beat.id='beat';beat.type='number';beat.min='0';beat.step='0.25';beat.value='0';if(target==='arrangement'){filter.before(beatLabel);filter.before(beat)}
filter.addEventListener('input',render);
fetch('/api/legion/audio/candidates',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(x=>{data=x.candidates;render()}).catch(e=>{results.textContent='Local bridge unavailable: '+e.message});
</script></html>'''

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

class Handler(BaseHTTPRequestHandler):
    catalog_file:str=''
    roots:list[str]=[]
    spool_file:str=''
    def send_json(self, payload, code=200):
        b=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode()
        self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        path=urllib.parse.urlsplit(self.path).path
        if path=='/health':return self.send_json({'schema':'legion.audio.health.v1','service':'legion_audio_bridge','status':'online','catalog_path':self.catalog_file,'binding':'127.0.0.1','database_mutations':False})
        if path=='/choose':
            data=HTML.encode('utf-8');self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'");self.send_header('X-Frame-Options','DENY');self.send_header('Content-Length',str(len(data)));self.end_headers();return self.wfile.write(data)
        if path=='/api/legion/audio/candidates':
            try:
                payload=[]
                if self.catalog_file and os.path.isfile(self.catalog_file):
                    with open(self.catalog_file,encoding='utf-8-sig') as f:payload=json.load(f)
                recs=payload.get('candidates',[]) if isinstance(payload,dict) else payload
                candidates=normalize_catalog([*recs,*read_spool(self.spool_file)],self.roots)
                return self.send_json({'schema':'legion.audio.catalog.v1','candidates':candidates,'source':'existing_sovereign_actor_export','total_available':len(candidates)})
            except (OSError,ValueError) as exc:return self.send_json({'error':'invalid_catalog','detail':str(exc)[:200]},500)
        self.send_json({'error':'not_found'},404)
    def do_POST(self):return self.send_json({'error':'read_only_bridge'},405)
    def log_message(self,fmt,*args):print('LEGION',fmt%args,flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8096);ap.add_argument('--catalog',default=os.environ.get('LEGION_AUDIO_CANDIDATES',''));ap.add_argument('--root',action='append',default=[]);ap.add_argument('--spool',default=os.path.join(os.environ.get('LOCALAPPDATA',''), 'LEGION_DAW','audio_events.jsonl') if os.environ.get('LOCALAPPDATA') else '');a=ap.parse_args()
    if not 1024<=a.port<=65535:ap.error('port out of range')
    Handler.catalog_file=a.catalog;Handler.roots=a.root or DEFAULT_ROOTS;Handler.spool_file=a.spool
    server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
    print(f'LEGION chooser http://127.0.0.1:{a.port}/choose | source: {a.catalog or "NOT CONFIGURED"}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
