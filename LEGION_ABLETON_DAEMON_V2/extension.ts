import { initialize, AudioTrack, AudioClip, ClipSlot, type ActivationContext, type Handle } from '@ableton-extensions/sdk';

// The SDK invokes context menu callbacks with the target object handle.
// The webview returns an explicit JSON placement selection; Live performs the mutation.
const CHOOSER_URL = 'http://localhost:8096/choose';
type Placement = {
  schema: 'legion.audio.placement.v1';
  action: 'create_arrangement_clip' | 'create_session_clip';
  file_path: string;
  start_time_beats?: number;
};
function parsePlacement(raw: string, expected: Placement['action']): Placement {
  const p: unknown = JSON.parse(raw);
  if (!p || typeof p !== 'object') throw new Error('Invalid placement payload');
  const x=p as Record<string,unknown>;
  if(x.schema!=='legion.audio.placement.v1'||x.action!==expected)throw new Error('Unexpected placement contract');
  if(typeof x.file_path!=='string'||! /^[A-Za-z]:\\/.test(x.file_path)||x.file_path.length>2048)throw new Error('Expected absolute Windows audio file');
  if(expected==='create_arrangement_clip'&&
     (typeof x.start_time_beats!=='number'||!Number.isFinite(x.start_time_beats)||x.start_time_beats<0))throw new Error('Invalid beat position');
  return x as Placement;
}
export function activate(activation: ActivationContext) {
  const ctx = initialize(activation,'1.0.0');
  ctx.commands.registerCommand('legion.audio.placeArrangement', async (...args:unknown[])=>{
    const handle=args[0] as Handle|undefined; if(!handle)return;
    try {
      const track=ctx.getObjectFromHandle(handle,AudioTrack);
      const raw=await ctx.ui.showModalDialog(CHOOSER_URL+'?target=arrangement',780,660);
      if(!raw)return;
      const p=parsePlacement(raw,'create_arrangement_clip');
      // SDK guarantee: this operation is an undoable Live mutation.
      await track.createAudioClip({filePath:p.file_path,startTime:p.start_time_beats!});
      console.log('LEGION arrangement clip created',p.file_path);
    }catch(e){console.error('LEGION arrangement placement failed',e)}
  });
  ctx.commands.registerCommand('legion.audio.placeSession',async (...args:unknown[])=>{
    const handle=args[0] as Handle|undefined;if(!handle)return;
    try {
      const slot=ctx.getObjectFromHandle(handle,ClipSlot);
      if(slot.clip){console.error('LEGION will not overwrite an occupied Session slot');return}
      const raw=await ctx.ui.showModalDialog(CHOOSER_URL+'?target=session',780,660);
      if(!raw)return;
      const p=parsePlacement(raw,'create_session_clip');
      await slot.createAudioClip({filePath:p.file_path});
      console.log('LEGION session clip created',p.file_path);
    }catch(e){console.error('LEGION session placement failed',e)}
  });
  ctx.commands.registerCommand('legion.audio.inspectClip',async (...args:unknown[])=>{
    const handle=args[0] as Handle|undefined;if(!handle)return;
    try {const clip=ctx.getObjectFromHandle(handle,AudioClip);console.log('LEGION clip audio path:',clip.filePath)}
    catch(e){console.error('LEGION inspect failed',e)}
  });
  void ctx.ui.registerContextMenuAction('AudioTrack','LEGION: insert Sovereign audio','legion.audio.placeArrangement');
  void ctx.ui.registerContextMenuAction('ClipSlot','LEGION: load Sovereign audio','legion.audio.placeSession');
  void ctx.ui.registerContextMenuAction('AudioClip','LEGION: inspect audio path','legion.audio.inspectClip');
}
