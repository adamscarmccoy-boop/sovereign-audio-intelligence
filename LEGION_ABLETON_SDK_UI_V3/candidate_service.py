#!/usr/bin/env python3
"""Native SDK UI companion: JSON-only loopback service. No HTML, HUD or modal."""
from __future__ import annotations
import argparse, json, os, pathlib, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from bridge_catalog import normalize_catalog, read_spool, DEFAULT_ROOTS

class Handler(BaseHTTPRequestHandler):
    roots = DEFAULT_ROOTS
    catalog_file = ''
    spool_file = ''
    def reply(self, code: int, payload: dict):
        data = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        self.send_response(code)
        for k, v in [('Content-Type','application/json; charset=utf-8'),('Cache-Control','no-store'),
                     ('X-Content-Type-Options','nosniff'),('Content-Length',str(len(data)))]:
            self.send_header(k,v)
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        path=urllib.parse.urlsplit(self.path).path
        if path == '/health':
            return self.reply(200,{'schema':'legion.audio.health.v1','service':'legion_candidate_service',
                                   'status':'online','modal_ui':False,'database_mutations':False})
        if path == '/api/legion/audio/candidates':
            try:
                payload=[]
                if self.catalog_file and os.path.isfile(self.catalog_file):
                    with open(self.catalog_file,encoding='utf-8-sig') as f: payload=json.load(f)
                records = payload.get('candidates',[]) if isinstance(payload,dict) else payload
                candidates = normalize_catalog([*records,*read_spool(self.spool_file)],self.roots)
                return self.reply(200,{'schema':'legion.audio.catalog.v1','candidates':candidates,
                                       'total_available':len(candidates)})
            except (OSError,ValueError,TypeError) as exc:
                return self.reply(500,{'error':'invalid_catalog','detail':str(exc)[:200]})
        return self.reply(404,{'error':'not_found'})
    def do_POST(self): return self.reply(405,{'error':'read_only'})
    def log_message(self,fmt,*args): print('LEGION:',fmt%args,flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8096)
    parser.add_argument('--catalog',default=os.environ.get('LEGION_AUDIO_CANDIDATES',''))
    parser.add_argument('--spool',default=os.path.join(os.environ.get('LOCALAPPDATA',''),'LEGION_DAW','audio_events.jsonl'))
    parser.add_argument('--root',action='append',default=[])
    args=parser.parse_args()
    if not 1024 <= args.port <= 65535: parser.error('port out of range')
    Handler.roots=args.root or DEFAULT_ROOTS
    Handler.catalog_file=args.catalog
    Handler.spool_file=args.spool
    srv=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print('LEGION SDK-native companion:',f'http://127.0.0.1:{args.port}/health',flush=True)
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()
if __name__=='__main__': main()
