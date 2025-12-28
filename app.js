// app.js

// Configuration
const API_URL = typeof window !== 'undefined' && window.API_URL ? window.API_URL : 'https://api.spatialselects.com';

// Simple DOM cache to avoid repeated lookups
const domCache = {
  engineersGrid: document.getElementById('engineers-grid'),
  tracksGrid: document.getElementById('tracks-grid'),
  errorBanner: document.getElementById('error-banner'),
  loadingSpinner: document.getElementById('loading-spinner'),
  refreshButton: null,
  syncButton: null,
  lastUpdated: null
};

// In-memory state
let allEngineers = Array.isArray(window.initialEngineers) ? window.initialEngineers : [];
let allTracks = Array.isArray(window.initialTracks) ? window.initialTracks : [];

/**
 * Basic HTML escaping to prevent XSS when injecting strings.
 */
function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Date format pattern for YYYY-MM-DD validation
const DATE_FORMAT_REGEX = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Validate that a date string is in YYYY-MM-DD format and represents a valid date.
 * @param {string} dateStr - The date string to validate
 * @returns {boolean} - True if valid or null/undefined, false otherwise
 */
function isValidDateFormat(dateStr) {
  // null/undefined is valid (optional field), but empty string is not
  if (dateStr == null) return true;
  if (dateStr === '') return false;
  
  // Check format: YYYY-MM-DD
  if (!DATE_FORMAT_REGEX.test(dateStr)) return false;
  
  // Parse components and create UTC date for timezone-consistent validation
  const [year, month, day] = dateStr.split('-').map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  
  if (isNaN(date.getTime())) return false;
  
  // Verify the date components match using UTC methods
  // (prevents dates like 2023-02-30 from being auto-adjusted to 2023-03-02)
  return date.getUTCFullYear() === year &&
         date.getUTCMonth() === month - 1 &&
         date.getUTCDate() === day;
}

/**
 * Validate a track object before rendering/using it.
 * Ensures presence of key fields and that optional date fields, when present,
 * are in YYYY-MM-DD format and represent valid dates.
 */
function validateTrack(track) {
  if (!track || typeof track !== 'object') return false;
  if (!track.id) return false;
  if (!track.title || !track.artist) return false;

  // Validate date format and validity
  const releaseOk = isValidDateFormat(track.releaseDate);
  const atmosOk = isValidDateFormat(track.atmosReleaseDate);

  return releaseOk && atmosOk;
}

/**
 * Render engineers grid safely with null guards.
 */
function renderEngineers() {
  if (!domCache.engineersGrid) return;

  if (!Array.isArray(allEngineers) || allEngineers.length === 0) {
    domCache.engineersGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No engineers found.</p>';
    return;
  }

  domCache.engineersGrid.innerHTML = allEngineers.map(eng => {
    const nameSafe = escapeHtml(eng?.name ?? 'Unknown');
    const imgUrl = typeof eng?.profile_image_url === 'string' ? eng.profile_image_url : null;
    const avatarHtml = imgUrl
      ? `<img src="${escapeHtml(imgUrl)}" alt="${nameSafe}" loading="lazy" referrerpolicy="no-referrer">`
      : escapeHtml(nameSafe.charAt(0));

    const mixCount = Number.isFinite(eng?.mix_count) ? eng.mix_count : 0;

    return `
<div class="engineer-card">
  <div class="engineer-avatar">
    ${avatarHtml}
  </div>
  <div class="engineer-name">${nameSafe}</div>
  <div class="mix-count">${mixCount} Mixes</div>
</div>`;
  }).join('');
}

/**
 * Render tracks grid (basic example; adapt to your UI components).
 */
function renderTracks() {
  if (!domCache.tracksGrid) return;

  if (!Array.isArray(allTracks) || allTracks.length === 0) {
    domCache.tracksGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No tracks found.</p>';
    return;
  }

  domCache.tracksGrid.innerHTML = allTracks.map(track => {
    const titleSafe = escapeHtml(track.title);
    const artistSafe = escapeHtml(track.artist);
    const albumSafe = escapeHtml(track.album ?? '');
    const platformSafe = escapeHtml(track.platform ?? '');
    const art = escapeHtml(track.albumArt ?? '🎵');

    const atmosDate = track.atmosReleaseDate ? new Date(track.atmosReleaseDate) : null;
    const releaseDate = track.releaseDate ? new Date(track.releaseDate) : null;

    const atmosDateStr = atmosDate && !isNaN(atmosDate.getTime()) ? atmosDate.toISOString().slice(0, 10) : '—';
    const releaseDateStr = releaseDate && !isNaN(releaseDate.getTime()) ? releaseDate.toISOString().slice(0, 10) : '—';

    const link = track.musicLink ? `<a href="${escapeHtml(track.musicLink)}" target="_blank" rel="noopener noreferrer">Listen</a>` : '';

    const creditsCount = Array.isArray(track.credits) ? track.credits.length : 0;
    const avgImmStr = typeof track.avgImmersiveness === 'number' ? track.avgImmersiveness.toFixed(2) : '—';
    const shameFlag = track.hallOfShame ? '⚠' : '';

    return `
<div class="track-card">
  <div class="album-art">${art}</div>
  <div class="meta">
    <div class="title">${titleSafe}</div>
    <div class="artist">${artistSafe}</div>
    <div class="album">${albumSafe}</div>
    <div class="platform">${platformSafe}</div>
    <div class="dates">
      <span>Atmos: ${atmosDateStr}</span>
      <span>Release: ${releaseDateStr}</span>
    </div>
    <div class="extras">
      <span>Credits: ${creditsCount}</span>
      <span>Immersiveness: ${avgImmStr}</span>
      <span>${shameFlag}</span>
    </div>
    <div class="actions">${link}</div>
  </div>
</div>`;
  }).join('');
}

/**
 * Load music data from API or fallback to JSON file.
 * Merges both branches: keeps Atmos-aware fields/sorting and metadata (credits, avgImmersiveness, hallOfShame).
 */
async function loadMusicData() {
  try {
    // Optional: show loading indicator
    if (domCache.loadingSpinner) domCache.loadingSpinner.style.display = 'block';

    // Try to load from backend API first
    const response = await fetch(`${API_URL}/tracks?limit=100`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'omit'
    });

    if (response.ok) {
      const apiTracks = await response.json();

      // Validate and sanitize data shape
      if (!Array.isArray(apiTracks)) {
        throw new Error('Invalid data format: expected array');
      }

      // Transform API response to match frontend format and validate
      allTracks = apiTracks.map(track => ({
        id: track.id,
        title: track.title,
        artist: track.artist,
        album: track.album,
        format: track.format,
        platform: track.platform,
        // Canonical release date from API
        releaseDate: track.release_date,
        // Prefer explicit atmos_release_date, fall back to general release_date
        atmosReleaseDate: track.atmos_release_date || track.release_date,
        // Frontend extras from both branches
        albumArt: track.album_art || '🎵',
        musicLink: track.music_link || null,
        credits: Array.isArray(track.credits) ? track.credits : [],
        avgImmersiveness: track.avg_immersiveness,
        hallOfShame: track.hall_of_shame
      })).filter(track => validateTrack(track));

      if (allTracks.length === 0) {
        throw new Error('No valid tracks found in API response');
      }

      // Sort by Atmos release date (newest first), fallback to releaseDate
      allTracks.sort((a, b) => {
        const dateA = new Date(a.atmosReleaseDate || a.releaseDate);
        const dateB = new Date(b.atmosReleaseDate || b.releaseDate);

        // Handle unparsable dates by pushing them to the end
        const timeA = isNaN(dateA.getTime()) ? -Infinity : dateA.getTime();
        const timeB = isNaN(dateB.getTime()) ? -Infinity : dateB.getTime();

        return timeB - timeA; // newest first
      });
    } else {
      // Fallback to local JSON (if bundled). Adjust path as needed.
      const fallbackResp = await fetch('/data/tracks.json', {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      if (!fallbackResp.ok) throw new Error('Failed to load fallback tracks.json');
      const jsonTracks = await fallbackResp.json();
      if (!Array.isArray(jsonTracks)) throw new Error('Invalid fallback format: expected array');

      allTracks = jsonTracks
        .map(track => ({
          id: track.id,
          title: track.title,
          artist: track.artist,
          album: track.album,
          format: track.format,
          platform: track.platform,
          releaseDate: track.releaseDate || track.release_date,
          atmosReleaseDate: track.atmosReleaseDate || track.atmos_release_date || track.releaseDate || track.release_date,
          albumArt: track.albumArt || track.album_art || '🎵',
          musicLink: track.musicLink || track.music_link || null,
          credits: Array.isArray(track.credits) ? track.credits : [],
          avgImmersiveness: track.avgImmersiveness ?? track.avg_immersiveness,
          hallOfShame: track.hallOfShame ?? track.hall_of_shame
        }))
        .filter(track => validateTrack(track))
        .sort((a, b) => {
          const dateA = new Date(a.atmosReleaseDate || a.releaseDate);
          const dateB = new Date(b.atmosReleaseDate || b.releaseDate);
          const timeA = isNaN(dateA.getTime()) ? -Infinity : dateA.getTime();
          const timeB = isNaN(dateB.getTime()) ? -Infinity : dateB.getTime();
          return timeB - timeA;
        });
    }
  } catch (err) {
    console.error('loadMusicData error:', err);
    if (domCache.errorBanner) {
      domCache.errorBanner.textContent = 'Failed to load tracks. Please try again later.';
      domCache.errorBanner.style.display = 'block';
    }
  } finally {
    if (domCache.loadingSpinner) domCache.loadingSpinner.style.display = 'none';
    // Re-render UI
    renderTracks();
  }
}

/**
 * Setup refresh button functionality
 */
function setupRefreshButton() {
  if (!domCache.refreshButton) return;

  let refreshInProgress = false;

  domCache.refreshButton.addEventListener('click', async () => {
    if (refreshInProgress) return;

    refreshInProgress = true;
    domCache.refreshButton.textContent = 'Refreshing...';
    domCache.refreshButton.disabled = true;

    try {
      await loadMusicData();
      updateLastUpdated();
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setTimeout(() => {
        domCache.refreshButton.textContent = 'Refresh';
        domCache.refreshButton.disabled = false;
        refreshInProgress = false;
      }, 500);
    }
  });
}

/**
 * Setup sync button functionality - triggers backend to fetch new tracks
 */
function setupSyncButton() {
  if (!domCache.syncButton) return;

  let syncInProgress = false;

  // Check sync availability on load
  checkSyncStatus();

  domCache.syncButton.addEventListener('click', async () => {
    if (syncInProgress || domCache.syncButton.disabled) return;

    syncInProgress = true;
    const originalText = domCache.syncButton.textContent;
    domCache.syncButton.textContent = 'Syncing...';
    domCache.syncButton.disabled = true;
    domCache.syncButton.classList.add('syncing');
    domCache.syncButton.classList.remove('success', 'error');

    try {
      const response = await fetch(`${API_URL}/refresh/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const result = await response.json();
        const added = result.tracks_added || 0;

        domCache.syncButton.textContent = `+${added} new`;
        domCache.syncButton.classList.remove('syncing');
        domCache.syncButton.classList.add('success');

        // Reload the track list to show new data
        await loadMusicData();
        updateLastUpdated();

        // Reset button after delay
        setTimeout(() => {
          domCache.syncButton.textContent = originalText;
          domCache.syncButton.classList.remove('success');
          checkSyncStatus();
        }, 3000);
      } else if (response.status === 429) {
        domCache.syncButton.textContent = 'Try later';
        domCache.syncButton.classList.remove('syncing');
        domCache.syncButton.classList.add('error');

        setTimeout(() => {
          domCache.syncButton.textContent = originalText;
          domCache.syncButton.classList.remove('error');
          checkSyncStatus();
        }, 3000);
      } else {
        throw new Error('Sync failed');
      }
    } catch (error) {
      console.error('Sync failed:', error);
      domCache.syncButton.textContent = 'Error';
      domCache.syncButton.classList.remove('syncing');
      domCache.syncButton.classList.add('error');

      setTimeout(() => {
        domCache.syncButton.textContent = originalText;
        domCache.syncButton.classList.remove('error');
        domCache.syncButton.disabled = false;
        syncInProgress = false;
      }, 3000);
      return;
    }

    syncInProgress = false;
  });
}

/**
 * Check if sync is available (rate limit status)
 */
async function checkSyncStatus() {
  if (!domCache.syncButton) return;

  try {
    const response = await fetch(`${API_URL}/refresh/status`);
    if (response.ok) {
      const status = await response.json();
      if (!status.can_refresh) {
        const minutes = Math.ceil(status.seconds_until_available / 60);
        domCache.syncButton.disabled = true;
        domCache.syncButton.title = `Sync available in ${minutes} minutes`;
      } else {
        domCache.syncButton.disabled = false;
        domCache.syncButton.title = 'Fetch latest tracks from Apple Music (rate limited to once per hour)';
      }
    }
  } catch (error) {
    console.warn('Could not check sync status:', error);
  }
}

/**
 * Update last updated timestamp
 */
function updateLastUpdated() {
  if (!domCache.lastUpdated) return;

  const now = new Date();
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  };
  domCache.lastUpdated.textContent = now.toLocaleString('en-US', options);
}

/**
 * Initialize DOM cache elements that need to be queried after DOM is ready
 */
function initializeDOMCache() {
  domCache.refreshButton = document.getElementById('refreshButton');
  domCache.syncButton = document.getElementById('syncButton');
  domCache.lastUpdated = document.getElementById('lastUpdated');
}

/**
 * Example bootstrapping: load data on DOMContentLoaded.
 */
document.addEventListener('DOMContentLoaded', () => {
  initializeDOMCache();
  renderEngineers();
  renderTracks();
  loadMusicData();
  setupRefreshButton();
  setupSyncButton();
  updateLastUpdated();
});

/**
 * Security considerations:
 * - Do not hardcode secrets/API keys client-side.
 * - Ensure API_URL serves only public-safe data.
 * - Always escape user-supplied strings before injecting into HTML.
 *
 * Edge cases handled:
 * - Missing or invalid dates sort to the end.
 * - credits is normalized to an array.
 * - albumArt uses a safe fallback.
 * - musicLink guards against null to avoid broken anchors.
 */
