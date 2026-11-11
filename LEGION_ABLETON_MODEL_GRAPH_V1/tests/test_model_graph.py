import sys, pathlib, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from sovereign_graph import Graph, Intent, MockLiveRuntime, run_demo, MODELS
from pydantic_core import ValidationError

class TheoryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.graph=Graph();cls.runtime=MockLiveRuntime()
 @classmethod
 def tearDownClass(cls):cls.graph.close()
 def test_native_duckdb_discover_full_inventory(self):
  self.assertEqual(self.graph.count(),250)
  self.assertEqual(int(self.graph.native.query("select count(*) from sdk_capabilities where source='host'")[0][0]),126)
 def test_select_only_mapped_actors(self):
  for x in MODELS:self.assertTrue(self.graph.validate_sdk_mapping(x))
  self.assertFalse(self.graph.validate_sdk_mapping('unsafeArbitraryMethod'))
 def test_create_arrangement_clip(self):
  plan=self.graph.plan({'task':'insert_audio_arrangement','object_handle':'track-3','file_path':r'E:\music\kick.wav','start_time':8.0})
  self.assertEqual(plan['tool_call']['name'],'trackCreateAudioClip')
  self.assertEqual(plan['tool_call']['arguments']['startTime'],8.0)
  self.assertEqual(self.runtime.execute(plan)['status'],'mock_executed')
  self.assertNotIn('sdk_graph',plan)
 def test_create_session_clip(self):
  p=self.graph.plan({'task':'insert_audio_session','object_handle':'slot-2','file_path':r'E:\music\vocal.wav'})
  self.assertEqual(p['tool_call']['name'],'clipslotCreateAudioClip')
  self.assertEqual(self.runtime.execute(p)['status'],'mock_executed')
  with self.assertRaisesRegex(ValueError,'occupied'):self.runtime.execute(p)
 def test_get_clip_path(self):
  p=self.graph.plan({'task':'read_audio_path','object_handle':'clip-1'})
  self.assertIn('file_path',self.runtime.execute(p))
 def test_song_tempo(self):
  p=self.graph.plan({'task':'set_song_tempo','object_handle':'song-1','tempo':126.5})
  self.assertEqual(self.runtime.execute(p)['tempo'],126.5)
 def test_pydantic_core_strict_rejection(self):
  with self.assertRaises(ValidationError):self.graph.plan({'task':'set_song_tempo','object_handle':'song-1','tempo':'128'})
  with self.assertRaises(ValidationError):self.graph.plan({'task':'set_song_tempo','object_handle':'song-1','tempo':2000.0})
  with self.assertRaises(ValidationError):self.graph.plan({'task':'read_audio_path','object_handle':'clip-1','unexpected':True})
  with self.assertRaises(ValidationError):self.graph.validators['trackCreateAudioClip'].validate_python({'handle':'x','filePath':'y','startTime':0,'extra':True})
 def test_reject_unbound_unsupported_file(self):
  with self.assertRaisesRegex(ValueError,'Windows absolute'):self.graph.plan({'task':'insert_audio_arrangement','object_handle':'track-3','file_path':'../../bad.wav'})
  with self.assertRaisesRegex(ValueError,'required'):self.graph.plan({'task':'insert_audio_arrangement','object_handle':'track-3'})
 def test_no_llm_no_sdk_execution_claim(self):
  receipt=run_demo()
  self.assertEqual(receipt['llm_calls'],0)
  self.assertIn('MOCK ONLY',receipt['execution'])
if __name__=='__main__':unittest.main(verbosity=2)
