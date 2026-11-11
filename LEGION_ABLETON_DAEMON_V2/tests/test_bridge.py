import unittest,sys,tempfile,pathlib,json,threading,urllib.request
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import bridge
class BridgeTests(unittest.TestCase):
 def test_roots(self):
  self.assertTrue(bridge.allow_root(r'E:\music\a.wav',[r'E:\music']))
  self.assertFalse(bridge.allow_root(r'E:\music2\a.wav',[r'E:\music']))
 def test_manifest_and_dedupe(self):
  item={'type':'audio_asset','metadata':json.dumps({'Filename':'kick.wav','Full_Path':r'E:\music\kick.wav'})}
  x=bridge.normalize_catalog([item,item],[r'E:\music'],exists=lambda p:True)
  self.assertEqual(len(x),1);self.assertIsNone(x[0]['score']);self.assertTrue(x[0]['available'])
 def test_hidden_and_unavailable(self):
  items=[{'file_path':r'E:\music\._junk.wav'},{'file_path':r'E:\music\kick.wav'},{'file_path':r'C:\Windows\bad.wav'}]
  self.assertEqual(bridge.normalize_catalog(items,[r'E:\music'],exists=lambda p:False),[])
 def test_spool(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d,'events.jsonl')
   p.write_text('not-json\n'+json.dumps({'schema':'legion.audio.file.v1','event':'audio_file_discovered','path':r'E:\music\new.wav'})+'\n')
   events=bridge.read_spool(str(p));self.assertEqual(len(events),1);self.assertEqual(events[0]['source'],'legion_windows_fs_watcher')
 def test_http_catalog(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d,'catalog.json');path.write_text(json.dumps({'candidates':[{'file_path':r'E:\music\kick.wav','score':0.8}]}))
   original_exists=bridge.is_present;bridge.is_present=lambda _:True
   oldfile=bridge.Handler.catalog_file;oldroots=bridge.Handler.roots
   bridge.Handler.catalog_file=str(path);bridge.Handler.roots=[r'E:\music']
   server=bridge.ThreadingHTTPServer(('127.0.0.1',0),bridge.Handler)
   t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
   try:
    base='http://127.0.0.1:'+str(server.server_port)
    with urllib.request.urlopen(base+'/api/legion/audio/candidates') as response:
     got=json.load(response);self.assertEqual(got['total_available'],1);self.assertEqual(got['candidates'][0]['score'],0.8)
    with urllib.request.urlopen(base+'/health') as response:self.assertEqual(json.load(response)['status'],'online')
    with urllib.request.urlopen(base+'/choose') as response:self.assertIn('LEGION',response.read().decode())
   finally:
    server.shutdown();server.server_close();t.join(timeout=3)
    bridge.is_present=original_exists;bridge.Handler.catalog_file=oldfile;bridge.Handler.roots=oldroots
if __name__=='__main__':unittest.main()
