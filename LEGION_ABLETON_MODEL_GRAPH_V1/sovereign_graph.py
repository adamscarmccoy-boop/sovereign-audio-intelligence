"""LEGION model-graph proof: native DuckDB C API + pydantic-core + bounded Ableton dispatch.
No persistence, no new user tables, no LLM graph exposure. Requires original source inventory.
"""
from __future__ import annotations
import ctypes, json, os, pathlib, re, time
from typing import Literal, Any
from pydantic import BaseModel, ConfigDict, Field, ValidationError, TypeAdapter
from pydantic_core import SchemaValidator, SchemaSerializer, __version__ as CORE_VERSION

ROOT=pathlib.Path(__file__).resolve().parent
INVENTORY=ROOT/'ableton_sdk_api_inventory.json'
LIB_DEFAULT=pathlib.Path('/mnt/data/ROOM9_NATIVE_DUCKDB_SQL_STARTUP/lance_runtime_probe/libduckdb.so')

class StrictModel(BaseModel):
    model_config=ConfigDict(extra='forbid', strict=True)

class SDKCapability(StrictModel):
    source: Literal['host','class','property']
    owner: str = Field(min_length=1, max_length=160)
    method: str = Field(min_length=1, max_length=160)
    sdk_version: Literal['1.0.0']

class ActorEdge(StrictModel):
    task: str = Field(min_length=1)
    method: str = Field(min_length=1)
    object_type: str = Field(min_length=1)
    sdk_member: str = Field(min_length=1)
    runtime: Literal['ableton_sdk']

class Intent(StrictModel):
    task: Literal['insert_audio_arrangement','insert_audio_session','read_audio_path','set_song_tempo']
    object_handle: str = Field(min_length=1,max_length=160)
    file_path: str|None = Field(default=None,max_length=2048)
    start_time: float|None = Field(default=None,ge=0,le=1000000)
    tempo: float|None= Field(default=None,ge=20,le=999)

class ToolCall(StrictModel):
    type: Literal['function'] = 'function'
    name: Literal['trackCreateAudioClip','clipslotCreateAudioClip','audioclipGetFilePath','songSetTempo']
    arguments: dict[str,Any]

class InsertArrangement(StrictModel):
    handle: str = Field(min_length=1,max_length=160)
    filePath: str = Field(min_length=5,max_length=2048)
    startTime: float = Field(ge=0,le=1000000)

class InsertSession(StrictModel):
    handle: str = Field(min_length=1,max_length=160)
    filePath: str = Field(min_length=5,max_length=2048)

class ReadAudioPath(StrictModel):
    handle: str = Field(min_length=1,max_length=160)

class SetTempo(StrictModel):
    handle: str = Field(min_length=1,max_length=160)
    tempo: float = Field(ge=20,le=999)

MODELS={
 'trackCreateAudioClip':InsertArrangement,
 'clipslotCreateAudioClip':InsertSession,
 'audioclipGetFilePath':ReadAudioPath,
 'songSetTempo':SetTempo,
}
CLASS_OPS={
 'trackCreateAudioClip':('AudioTrack','createAudioClip'),
 'clipslotCreateAudioClip':('ClipSlot','createAudioClip'),
 'audioclipGetFilePath':('AudioClip','filePath'),
 'songSetTempo':('Song','tempo'),
}

class DuckDBNative:
    def __init__(self,path=None):
        libpath=path or os.environ.get('LEGION_DUCKDB_SO') or str(LIB_DEFAULT)
        self.lib=ctypes.CDLL(libpath)
        self.lib.duckdb_open.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_void_p)];self.lib.duckdb_open.restype=ctypes.c_int
        self.lib.duckdb_connect.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_void_p)];self.lib.duckdb_connect.restype=ctypes.c_int
        self.lib.duckdb_query.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_void_p];self.lib.duckdb_query.restype=ctypes.c_int
        self.lib.duckdb_destroy_result.argtypes=[ctypes.c_void_p];self.lib.duckdb_column_count.argtypes=[ctypes.c_void_p];self.lib.duckdb_column_count.restype=ctypes.c_uint64
        self.lib.duckdb_row_count.argtypes=[ctypes.c_void_p];self.lib.duckdb_row_count.restype=ctypes.c_uint64
        self.lib.duckdb_value_varchar.argtypes=[ctypes.c_void_p,ctypes.c_uint64,ctypes.c_uint64];self.lib.duckdb_value_varchar.restype=ctypes.c_void_p
        self.lib.duckdb_free.argtypes=[ctypes.c_void_p];self.lib.duckdb_result_error.argtypes=[ctypes.c_void_p];self.lib.duckdb_result_error.restype=ctypes.c_char_p
        self.lib.duckdb_disconnect.argtypes=[ctypes.POINTER(ctypes.c_void_p)];self.lib.duckdb_close.argtypes=[ctypes.POINTER(ctypes.c_void_p)]
        self.db=ctypes.c_void_p();self.conn=ctypes.c_void_p()
        if self.lib.duckdb_open(None,ctypes.byref(self.db)):raise RuntimeError('duckdb_open failed')
        if self.lib.duckdb_connect(self.db,ctypes.byref(self.conn)):raise RuntimeError('duckdb_connect failed')
    def query(self,sql):
        result=ctypes.create_string_buffer(16384)
        state=self.lib.duckdb_query(self.conn,sql.encode('utf-8'),ctypes.byref(result))
        if state:
            msg=self.lib.duckdb_result_error(ctypes.byref(result))
            self.lib.duckdb_destroy_result(ctypes.byref(result))
            raise RuntimeError((msg or b'DuckDB failed').decode('utf-8','replace'))
        try:
            nr=self.lib.duckdb_row_count(ctypes.byref(result));nc=self.lib.duckdb_column_count(ctypes.byref(result));out=[]
            for i in range(nr):
                row=[]
                for j in range(nc):
                    ptr=self.lib.duckdb_value_varchar(ctypes.byref(result),j,i)
                    try:row.append(ctypes.string_at(ptr).decode('utf-8','replace') if ptr else None)
                    finally:
                        if ptr:self.lib.duckdb_free(ptr)
                out.append(row)
            return out
        finally:self.lib.duckdb_destroy_result(ctypes.byref(result))
    def close(self):
        if self.conn:self.lib.duckdb_disconnect(ctypes.byref(self.conn))
        if self.db:self.lib.duckdb_close(ctypes.byref(self.db))


def sdk_rows(inventory):
    rows=[]
    for module,methods in inventory['host_modules'].items():
        for method in methods: rows.append({'source':'host','owner':module,'method':method,'sdk_version':'1.0.0'})
    for cls,details in inventory['sdk_classes'].items():
        for method in details.get('methods',[]):rows.append({'source':'class','owner':cls,'method':method,'sdk_version':'1.0.0'})
        for prop in details.get('properties',[]):rows.append({'source':'property','owner':cls,'method':prop,'sdk_version':'1.0.0'})
    return rows

class Graph:
    def __init__(self,libpath=None):
        self.inventory=json.loads(INVENTORY.read_text(encoding='utf-8'))
        self.capability_schema=SchemaValidator(TypeAdapter(list[SDKCapability]).core_schema)
        self.edge_schema=SchemaValidator(TypeAdapter(list[ActorEdge]).core_schema)
        self.capabilities=[x.model_dump() for x in self.capability_schema.validate_python(sdk_rows(self.inventory))]
        self.edges=self.edge_schema.validate_python(json.loads((ROOT/'actor_edges.json').read_text()))
        self.native=DuckDBNative(libpath)
        # Native DuckDB queries the JSON file directly; TEMP VIEW only, no persistence.
        self.flat=ROOT/'sdk_capabilities.json'
        self.flat.write_text(json.dumps(self.capabilities,indent=2),encoding='utf-8')
        loc=str(self.flat).replace("'","''")
        self.native.query("CREATE TEMP VIEW sdk_capabilities AS SELECT * FROM read_json_auto('"+loc+"')")
        edge_path=str(ROOT/'actor_edges.json').replace("'","''")
        self.native.query("CREATE TEMP VIEW actor_edges AS SELECT * FROM read_json_auto('"+edge_path+"')")
        self.validators={k:SchemaValidator(v.__pydantic_core_schema__) for k,v in MODELS.items()}
        self.serializers={k:SchemaSerializer(v.__pydantic_core_schema__) for k,v in MODELS.items()}
    def count(self):return int(self.native.query('SELECT count(*) FROM sdk_capabilities')[0][0])
    def validate_sdk_mapping(self,method):
        if method not in CLASS_OPS:return False
        cls,member=CLASS_OPS[method]
        # Guarantee source SDK class and host method both present; no invented invocation.
        rows=self.native.query("SELECT count(*) FROM sdk_capabilities WHERE source='class' AND owner='"+cls+"' AND method='"+member+"'")
        if int(rows[0][0])==0:return False
        rows=self.native.query("SELECT count(*) FROM sdk_capabilities WHERE source='host' AND owner='DataModelModule_1_0_0' AND method='"+method+"'")
        return int(rows[0][0])>0
    def plan(self,raw):
        intent=Intent.model_validate(raw)
        # Resolve the task -> actor edge -> SDK member IN DuckDB, not in an LLM or Python lookup.
        safe_task=intent.task.replace("'","''")
        rows=self.native.query("SELECT e.method, e.object_type FROM actor_edges e JOIN sdk_capabilities c ON c.owner=e.object_type AND c.method=e.sdk_member AND c.source='class' JOIN sdk_capabilities h ON h.method=e.method AND h.source='host' AND h.owner='DataModelModule_1_0_0' WHERE e.task='"+safe_task+"'")
        if len(rows)!=1:raise ValueError('Missing or ambiguous registered SDK capability edge')
        method,owner=rows[0]
        if not self.validate_sdk_mapping(method):raise ValueError('SDK operation absent from source inventory: '+method)
        args={'handle':intent.object_handle}
        if method in ('trackCreateAudioClip','clipslotCreateAudioClip'):
            if not intent.file_path:raise ValueError('file_path required')
            if not re.match(r'^[A-Za-z]:\\',intent.file_path):raise ValueError('expected Windows absolute path')
            args['filePath']=intent.file_path
            if method=='trackCreateAudioClip':args['startTime']=intent.start_time if intent.start_time is not None else 0.0
        if method=='songSetTempo':
            if intent.tempo is None:raise ValueError('tempo required')
            args['tempo']=intent.tempo
        validated=self.validators[method].validate_python(args)
        tool_schema=MODELS[method].model_json_schema()
        selected_function={'type':'function','name':method,'description':'Validated Ableton SDK '+owner+' operation', 'parameters':tool_schema}
        return {'task':intent.task,'selected_tool_definition':selected_function,'capability':{'sdk_method':method,'sdk_object':owner},
                'tool_call':ToolCall(name=method,arguments=validated.__dict__).model_dump(),
                'core_schema':tool_schema,
                'transition': ['intent_validated','duckdb_capability_resolved','pydantic_core_validated','sdk_dispatch_pending']}
    def close(self):self.native.close()

class MockLiveRuntime:
    """Strict stand-in for Live SDK. Does NOT open Ableton or claim successful production execution."""
    def __init__(self):self.state={'tracks':{'track-3':[]},'slots':{'slot-2':None},'clips':{'clip-1':r'E:\\music\\bass_ref.wav'},'song':{'song-1':128.0}}
    def execute(self,plan):
        call=ToolCall.model_validate(plan['tool_call']);method=call.name
        args=MODELS[method].model_validate(call.arguments)
        if method=='trackCreateAudioClip':
            if args.handle not in self.state['tracks']:raise ValueError('unknown track handle')
            clip={'file_path':args.filePath,'start_time':args.startTime};self.state['tracks'][args.handle].append(clip);return {'status':'mock_executed','created_clip':clip}
        if method=='clipslotCreateAudioClip':
            if args.handle not in self.state['slots']:raise ValueError('unknown slot')
            if self.state['slots'][args.handle] is not None:raise ValueError('slot occupied')
            clip={'file_path':args.filePath};self.state['slots'][args.handle]=clip;return {'status':'mock_executed','created_clip':clip}
        if method=='audioclipGetFilePath':
            return {'status':'mock_executed','file_path':self.state['clips'][args.handle]}
        if method=='songSetTempo':
            if args.handle not in self.state['song']:raise ValueError('unknown song')
            self.state['song'][args.handle]=args.tempo;return {'status':'mock_executed','tempo':args.tempo}
        raise ValueError('disallowed method')

def run_demo():
    t0=time.perf_counter();g=Graph();live=MockLiveRuntime()
    inputs=[
      {'task':'insert_audio_arrangement','object_handle':'track-3','file_path':r'E:\music\bass_loop_128.wav','start_time':16.0},
      {'task':'insert_audio_session','object_handle':'slot-2','file_path':r'E:\music\kick_128.wav'},
      {'task':'read_audio_path','object_handle':'clip-1'},
      {'task':'set_song_tempo','object_handle':'song-1','tempo':128.0},
    ]
    executions=[]
    for raw in inputs:
        p=g.plan(raw);result=live.execute(p)
        executions.append({'task':raw['task'],'selected_tool':p['tool_call']['name'],'transition':p['transition']+['mock_runtime_executed'], 'result':result,
                           'llm_tools_sent':0})
    receipt={'theory':'full_sdk_graph_in_DuckDB -> bounded capability -> pydantic_core_Rust -> SDK-runtime',
      'sdk_source':g.inventory['source'],'duckdb':'native C API via libduckdb.so; in-memory TEMP VIEW only',
      'sdk_capability_rows':g.count(),'sdk_host_methods':sum(len(v) for v in g.inventory['host_modules'].values()),
      'pydantic_core_version':CORE_VERSION,'pydantic_core_schema_validators':len(g.validators)+2,
      'full_capability_registry_validated_in_rust':len(g.capabilities),'actor_edges_validated_in_rust':len(g.edges),
      'llm_entire_graph_exposed':False,'llm_calls':0,'execution':'MOCK ONLY; no Live Beta or original Windows DuckDB',
      'latency_ms':round((time.perf_counter()-t0)*1000,2),'executions':executions}
    g.close();(ROOT/'test_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    return receipt
if __name__=='__main__':print(json.dumps(run_demo(),indent=2))
