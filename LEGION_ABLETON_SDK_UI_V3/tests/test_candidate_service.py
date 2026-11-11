import unittest, threading, json, pathlib, tempfile, urllib.request, urllib.error, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from candidate_service import Handler, ThreadingHTTPServer

class ServiceTests(unittest.TestCase):
    def test_json_only_service(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d,'catalog.json')
            p.write_text(json.dumps({'candidates':[]}),encoding='utf-8')
            old=(Handler.catalog_file, Handler.roots, Handler.spool_file)
            Handler.catalog_file=str(p);Handler.roots=[r'E:\music'];Handler.spool_file=''
            server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                base=f'http://127.0.0.1:{server.server_port}'
                with urllib.request.urlopen(base+'/health') as r:
                    data=json.load(r);self.assertFalse(data['modal_ui'])
                with urllib.request.urlopen(base+'/api/legion/audio/candidates') as r:
                    data=json.load(r);self.assertEqual(data['schema'],'legion.audio.catalog.v1')
                with self.assertRaises(urllib.error.HTTPError) as cm:
                    urllib.request.urlopen(base+'/choose')
                self.assertEqual(cm.exception.code,404)
                with self.assertRaises(urllib.error.HTTPError) as cm:
                    urllib.request.urlopen(urllib.request.Request(base+'/choose',data=b'{}'))
                self.assertEqual(cm.exception.code,405)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=3)
                Handler.catalog_file,Handler.roots,Handler.spool_file=old

if __name__=='__main__': unittest.main()
