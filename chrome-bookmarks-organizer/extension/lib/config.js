// Settings shared by the background worker and the options page.

export const HOST_NAME = 'com.bertrandvidal.chrome_bookmarks_organizer';

// Folder names are all configurable on the options page. Matching ignores case,
// spaces and punctuation, so "Worthy Reads" finds "worthy-reads".
export const DEFAULTS = {
  rootFolderName: 'worthy-reads', // your existing top folder; everything is filed inside it
  inboxName: '_inbox',            // created inside the root; drop new links here from any device
  reviewName: '_review',          // created inside the root; links Claude isn't sure about wait here
  sweepMinutes: 15,          // periodic safety-net sweep; new bookmarks also trigger a sweep within ~30s
  minConfidence: 'medium',   // 'high' or 'medium'; anything below goes to _review
  maxPerSweep: 10,
  samplesPerFolder: 6,       // existing titles shown to Claude per folder, for consistency
  model: 'sonnet',           // Claude Code model alias: sonnet, haiku, opus
  useTabFallback: true,      // open the page in a minimized window when a plain fetch is blocked or thin
  cleanTitles: false,        // replace "Title | by X | Medium" with the clean title when filing
  maxAttempts: 3,
};

export const CONFIDENCE_RANK = { low: 0, medium: 1, high: 2 };

export async function getSettings() {
  const { settings } = await chrome.storage.local.get('settings');
  return { ...DEFAULTS, ...(settings || {}) };
}
