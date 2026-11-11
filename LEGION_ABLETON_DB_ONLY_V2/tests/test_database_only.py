import unittest,sys,pathlib,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from sovereign_graph import Graph,MockLiveRuntime,run_demo
from pydantic_core import ValidationError
class StandaloneTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.g=Graph()
 @classmethod
 def tearDownClass(cls):cls.g.close()
 def test_sdk_inventory(self):self.assertEqual(self.g.count(),250)
 def test_database_routes(self):self.assertEqual(int(self.g.native.query('SELECT count(*) FROM sdk_routes')[0][0]),4)
 def test_no_actor_registry(self):
  names={r[0] for r in self.g.native.query('SHOW ALL TABLES')}
  self.assertNotIn('actor_edges',names)
 def test_no_preexisting_actor_dependency(self):self.assertTrue(self.g.validate_sdk_mapping('trackCreateAudioClip'))
 def test_sdk_insert(self):
  p=self.g.plan({'task':'insert_audio_arrangement','object_handle':'track-3','file_path':r'E:\music\kick.wav','start_time':8.0})
  self.assertEqual(MockLiveRuntime().execute(p)['status'],'mock_executed')
 def test_strict_validation(self):
  with self.assertRaises(ValidationError):self.g.plan({'task':'set_song_tempo','object_handle':'song-1','tempo':'128'})
 def test_simulation_report(self):self.assertFalse(run_demo()['legacy_actor_registry_used'])
if __name__=='__main__':unittest.main()
