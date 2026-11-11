/** LEGION V4: SDK execution adapter. Uses actual Ableton 1.0.0 beta SDK object handles.
 * No HTML/modal/HUD. Accepts only an already validated, bounded capability call.
 * Actual transport should be mapped to existing Sovereign gateway actor dispatch.
 */
import { AudioTrack, ClipSlot, AudioClip, Song, type Handle, type ExtensionContext } from '@ableton-extensions/sdk';

export type ToolName = 'trackCreateAudioClip' | 'clipslotCreateAudioClip' | 'audioclipGetFilePath' | 'songSetTempo';
export type BoundedToolCall = { type: 'function'; name: ToolName; arguments: Record<string, unknown> };

function requiredString(value: unknown, key: string): string {
  if (typeof value !== 'string' || !value.length || value.length > 2048) throw Error('Invalid ' + key);
  return value;
}
function requiredNumber(value: unknown, key: string, min: number, max: number): number {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max) throw Error('Invalid ' + key);
  return value;
}
/** Must be invoked within the Ableton extension runtime after Sovereign validated a call.
 * Revalidates untrusted data at the actual SDK boundary; never takes arbitrary method names.
 */
export async function executeApprovedToolCall(ctx: ExtensionContext<'1.0.0'>, raw: unknown): Promise<unknown> {
  if (!raw || typeof raw !== 'object') throw Error('Invalid tool call');
  const call = raw as Record<string, unknown>;
  if (call.type !== 'function' || typeof call.name !== 'string') throw Error('Invalid function envelope');
  if (!call.arguments || typeof call.arguments !== 'object' || Array.isArray(call.arguments)) throw Error('Invalid arguments');
  const args = call.arguments as Record<string, unknown>;
  const handle = requiredString(args.handle, 'handle') as unknown as Handle;
  switch (call.name) {
    case 'trackCreateAudioClip': {
      const track = ctx.getObjectFromHandle(handle, AudioTrack);
      const filePath = requiredString(args.filePath, 'filePath');
      const startTime = requiredNumber(args.startTime, 'startTime', 0, 1e6);
      await track.createAudioClip({ filePath, startTime });
      return { status: 'executed_in_live', action: call.name };
    }
    case 'clipslotCreateAudioClip': {
      const slot = ctx.getObjectFromHandle(handle, ClipSlot);
      if (slot.clip !== null) throw Error('Session slot occupied');
      const filePath = requiredString(args.filePath, 'filePath');
      await slot.createAudioClip({ filePath });
      return { status: 'executed_in_live', action: call.name };
    }
    case 'audioclipGetFilePath': {
      const clip = ctx.getObjectFromHandle(handle, AudioClip);
      return { status: 'executed_in_live', action: call.name, filePath: clip.filePath };
    }
    case 'songSetTempo': {
      const song = ctx.getObjectFromHandle(handle, Song);
      const tempo = requiredNumber(args.tempo, 'tempo', 20, 999);
      song.tempo = tempo;
      return { status: 'executed_in_live', action: call.name, tempo };
    }
    default: throw Error('Unregistered Ableton capability');
  }
}
