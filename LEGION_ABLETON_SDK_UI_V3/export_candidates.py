#!/usr/bin/env python3
"""Create JSON snapshot for the read-only local chooser from an EXISTING Sovereign output.
Input: actor result JSON/list OR read-only SELECT against original DuckDB (optional duckdb Python driver).
Never creates/mutates any DB tables. Output is a JSON cache file, not an authority source.
"""
import argparse,json,pathlib,sys
from bridge_catalog import normalize_catalog,DEFAULT_ROOTS

def main():
 p=argparse.ArgumentParser()
 source=p.add_mutually_exclusive_group(required=True)
 source.add_argument('--input-json',type=pathlib.Path)
 source.add_argument('--db',type=pathlib.Path)
 p.add_argument('--query-file',type=pathlib.Path,help='Required with --db; a single SELECT query mapping path/label/score columns')
 p.add_argument('--out',type=pathlib.Path,required=True)
 p.add_argument('--root',action='append',default=[])
 a=p.parse_args()
 if a.db:
  if not a.query_file:p.error('--query-file is required with --db')
  sql=a.query_file.read_text(encoding='utf-8').strip()
  if not sql.lower().startswith(('select ','with ')) or sql.count(';')>1 or (';' in sql.rstrip(';')):
   p.error('Query must be a single SELECT / WITH statement')
  try:import duckdb
  except ImportError:p.error('To use --db, install DuckDB in this process or use --input-json from your existing ROOM9 actor')
  con=duckdb.connect(database=str(a.db),read_only=True)
  try:
   result=con.execute(sql)
   col=[d[0] for d in result.description]
   raw=[dict(zip(col,r)) for r in result.fetchall()]
  finally:con.close()
 else:
  raw=json.loads(a.input_json.read_text(encoding='utf-8-sig'))
 candidates=normalize_catalog(raw,a.root or DEFAULT_ROOTS)
 envelope={'schema':'legion.audio.catalog.v1','candidates':candidates,'source':'existing_sovereign_export','count':len(candidates)}
 a.out.parent.mkdir(parents=True,exist_ok=True)
 temp=a.out.with_name(a.out.name+'.tmp')
 temp.write_text(json.dumps(envelope,indent=2,ensure_ascii=False),encoding='utf-8')
 temp.replace(a.out)
 print(json.dumps({'output':str(a.out),'available':len(candidates),'input':'duckdb_read_only' if a.db else 'actor_json'}))
if __name__=='__main__':main()
