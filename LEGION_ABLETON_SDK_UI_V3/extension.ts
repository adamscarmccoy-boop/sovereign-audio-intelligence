import { initialize, AudioTrack, AudioClip, ClipSlot, type ActivationContext, type Handle } from '@ableton-extensions/sdk';

/**
 * LEGION v0.3.0: SDK-native UI ONLY. No showModalDialog(), no HTML HUD,
 * no WebView, no DOM, no IFrame. Only Ableton context-menu actions.
 *
 * A local JSON service supplies already-indexed/available audio candidate paths.
 * Live mutates its own set via official createAudioClip() APIs.
 */
const API = 'http://127.0.0.1:8096/api/legion/audio/candidates';
const REQUEST_TIMEOUT_MS = 2000;
const MAX_RESULTS = 1000;
const MAX_FILE_PATH = 2048;
interface Candidate { file_path: string; label?: string; score: number | null; available: boolean; }
interface Catalog { schema: 'legion.audio.catalog.v1'; candidates: Candidate[]; }
let offset = 0;
let pending = false;

function validCandidate(value: unknown): value is Candidate {
  if (!value || typeof value !== 'object') return false;
  const v = value as Record<string, unknown>;
  return typeof v.file_path === 'string' && v.file_path.length <= MAX_FILE_PATH &&
    /^[A-Za-z]:\\/.test(v.file_path) && v.available === true &&
    (v.score === null || (typeof v.score === 'number' && Number.isFinite(v.score)));
}

async function readCandidates(): Promise<Candidate[]> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    // Fetch and JSON parsing are asynchronous. The Live UI never waits on an HTML modal.
    const response = await fetch(API, { method: 'GET', signal: controller.signal, cache: 'no-store' });
    if (!response.ok) throw new Error('LEGION bridge HTTP ' + response.status);
    const data: unknown = await response.json();
    if (!data || typeof data !== 'object') throw new Error('Invalid candidate catalog');
    const catalog = data as Partial<Catalog>;
    if (catalog.schema !== 'legion.audio.catalog.v1' || !Array.isArray(catalog.candidates)) {
      throw new Error('Unexpected candidate JSON schema');
    }
    return catalog.candidates.slice(0, MAX_RESULTS).filter(validCandidate);
  } finally {
    clearTimeout(timeout);
  }
}

function report(error: unknown, action: string): void {
  console.error('LEGION ' + action + ':', error instanceof Error ? error.message : String(error));
}

export function activate(activation: ActivationContext): void {
  const ctx = initialize(activation, '1.0.0');

  async function insert(handle: Handle | undefined, destination: 'arrangement' | 'session', advance: boolean): Promise<void> {
    if (!handle || pending) return;
    pending = true;
    try {
      // Resolve target immediately; only known SDK handles are accepted.
      const target = destination === 'arrangement'
        ? ctx.getObjectFromHandle(handle, AudioTrack)
        : ctx.getObjectFromHandle(handle, ClipSlot);
      if (destination === 'session' && (target as ClipSlot<'1.0.0'>).clip !== null) {
        console.warn('LEGION: session slot occupied; nothing changed.');
        return;
      }
      const candidates = await readCandidates();
      if (!candidates.length) {
        console.warn('LEGION: no available candidate files. Check the local 8096 service.');
        return;
      }
      if (advance) offset = (offset + 1) % candidates.length;
      const candidate = candidates[offset % candidates.length];
      // Recheck the slot after awaiting network I/O.
      if (destination === 'session') {
        const slot = target as ClipSlot<'1.0.0'>;
        if (slot.clip !== null) return;
        await slot.createAudioClip({ filePath: candidate.file_path });
      } else {
        // Explicit placement at beat zero: the SDK does not promise a selection time
        // for an AudioTrack context action. Do not guess playhead position.
        await (target as AudioTrack<'1.0.0'>).createAudioClip({ filePath: candidate.file_path, startTime: 0 });
      }
      console.info('LEGION: placed', candidate.file_path, 'rank', offset + 1, 'of', candidates.length);
    } catch (error) {
      report(error, 'insert failed');
    } finally {
      pending = false;
    }
  }

  ctx.commands.registerCommand('legion.audio.insertBestArrangement', (...args: unknown[]) => {
    void insert(args[0] as Handle | undefined, 'arrangement', false);
  });
  ctx.commands.registerCommand('legion.audio.insertNextArrangement', (...args: unknown[]) => {
    void insert(args[0] as Handle | undefined, 'arrangement', true);
  });
  ctx.commands.registerCommand('legion.audio.insertBestSession', (...args: unknown[]) => {
    void insert(args[0] as Handle | undefined, 'session', false);
  });
  ctx.commands.registerCommand('legion.audio.insertNextSession', (...args: unknown[]) => {
    void insert(args[0] as Handle | undefined, 'session', true);
  });
  ctx.commands.registerCommand('legion.audio.inspectClip', (...args: unknown[]) => {
    try {
      const handle = args[0] as Handle | undefined;
      if (handle) console.info('LEGION clip:', ctx.getObjectFromHandle(handle, AudioClip).filePath);
    } catch (error) { report(error, 'inspect failed'); }
  });
  ctx.commands.registerCommand('legion.audio.resetRank', () => {
    offset = 0;
    console.info('LEGION: candidate rank reset to #1');
  });

  // Exactly the SDK's supported UI: context menus, not persistent sidebars.
  void ctx.ui.registerContextMenuAction('AudioTrack', 'LEGION: Insert top sample at beat 0', 'legion.audio.insertBestArrangement');
  void ctx.ui.registerContextMenuAction('AudioTrack', 'LEGION: Insert next ranked sample at beat 0', 'legion.audio.insertNextArrangement');
  void ctx.ui.registerContextMenuAction('ClipSlot', 'LEGION: Load top sample (empty slot)', 'legion.audio.insertBestSession');
  void ctx.ui.registerContextMenuAction('ClipSlot', 'LEGION: Load next ranked sample (empty slot)', 'legion.audio.insertNextSession');
  void ctx.ui.registerContextMenuAction('AudioClip', 'LEGION: Log audio path', 'legion.audio.inspectClip');
}
