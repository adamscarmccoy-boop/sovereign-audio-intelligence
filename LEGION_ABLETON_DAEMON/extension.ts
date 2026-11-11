// Original LEGION code using only publicly expressible API shapes from the local beta typings.
// The Ableton SDK itself is NOT included in this repository.
import { initialize, AudioClip, type ActivationContext, type Handle } from '@ableton-extensions/sdk';

export function activate(activation: ActivationContext) {
  const context = initialize(activation, '1.0.0');
  const commandId = 'legion.audio.inspectClip';
  context.commands.registerCommand(commandId, async (...args: unknown[]) => {
    const handle = args[0] as Handle | undefined;
    if (!handle) return;
    try {
      const clip = context.getObjectFromHandle(handle, AudioClip);
      const path = clip.filePath;
      // Do not silently upload or alter the audio. The filesystem daemon indexes
      // this path independently. This command verifies clip -> filesystem mapping.
      const escaped = path.replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
      const html = `<!doctype html><meta charset="utf-8"><style>body{font:14px sans-serif;padding:18px;background:#141720;color:#eee}code{overflow-wrap:anywhere}</style><h3>LEGION: Ableton audio path</h3><code>${escaped}</code><p>Filesystem daemon discovers this file without modifying Live's .asd analysis data.</p>`;
      await context.ui.showModalDialog(`data:text/html,${encodeURIComponent(html)}`, 540, 210);
    } catch (e) { console.error('LEGION clip inspection failed', e); }
  });
  void context.ui.registerContextMenuAction('AudioClip','LEGION: inspect indexed audio path',commandId);
}
