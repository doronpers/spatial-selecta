// app.js

// Configuration
const determineApiUrl = () => {
  // Allow explicit override via window.API_URL (highest priority)
  if (typeof window !== 'undefined' && window.API_URL) {
    return window.API_URL;
  }
  
  // Check if running locally
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname || '';
    
    const isFileProtocol = protocol === 'file:';
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '';
    const isNotHttps = protocol !== 'https:';
    const isNotProductionDomain = !hostname.includes('spatialselects.com') && 
                                  !hostname.includes('onrender.com');
    
    // Use localhost API if: file://, localhost, empty hostname (file://), or not HTTPS and not production domain
    if (isFileProtocol || isLocalhost || (isNotHttps && isNotProductionDomain)) {
      return 'http://localhost:8000';
    }
  }
  
  // Default to production API
  return 'https://api.spatialselects.com';
};
const API_URL = determineApiUrl();
console.log('API_URL determined:', API_URL, 'Protocol:', typeof window !== 'undefined' ? window.location.protocol : 'N/A', 'Hostname:', typeof window !== 'undefined' ? window.location.hostname : 'N/A');

// Simple DOM cache to avoid repeated lookups
const domCache = {
  engineersSection: null, // Will be initialized after DOM ready
  releasesSection: null, // Will be initialized after DOM ready
  errorBanner: null, // Will be initialized after DOM ready
  loadingSpinner: null, // Will be initialized after DOM ready
  refreshButton: null,
  syncButton: null,
  lastUpdated: null,
  platformFilter: null,
  formatFilter: null
};

// In-memory state
let allEngineers = Array.isArray(window.initialEngineers) ? window.initialEngineers : [];
let allTracks = Array.isArray(window.initialTracks) ? window.initialTracks : [];
let filteredTracks = [];
let currentFilters = {
  platform: 'all',
  format: 'all'
};

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
 * Validate URL is HTTPS to prevent XSS
 */
function isValidHttpsUrl(url) {
  if (!url || typeof url !== 'string') return false;
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

/**
 * Render engineers grid safely with null guards.
 */
function renderEngineers() {
  if (!domCache.engineersSection) return;

  if (!Array.isArray(allEngineers) || allEngineers.length === 0) {
    domCache.engineersSection.innerHTML = '<div class="engineers-grid"><p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No engineers found.</p></div>';
    return;
  }

  const engineersHtml = allEngineers.map(eng => {
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

  domCache.engineersSection.innerHTML = `<div class="engineers-grid">${engineersHtml}</div>`;
}

/**
 * Apply filters to tracks based on current filter state
 */
function applyFilters() {
  filteredTracks = allTracks.filter(track => {
    const platformMatch = currentFilters.platform === 'all' || track.platform === currentFilters.platform;
    const formatMatch = currentFilters.format === 'all' || track.format === currentFilters.format;
    return platformMatch && formatMatch;
  });
  renderTracks();
}

/**
 * Render tracks grid with filtering support
 */
function renderTracks() {
  if (!domCache.releasesSection) return;

  const tracksToRender = filteredTracks.length > 0 ? filteredTracks : allTracks;

  if (!Array.isArray(tracksToRender) || tracksToRender.length === 0) {
    domCache.releasesSection.innerHTML = '<div class="empty-state"><p>No tracks found.</p></div>';
    return;
  }

  const tracksHtml = tracksToRender.map(track => {
    const titleSafe = escapeHtml(track.title);
    const artistSafe = escapeHtml(track.artist);
    const albumSafe = escapeHtml(track.album ?? '');
    const platformSafe = escapeHtml(track.platform ?? '');
    const formatSafe = escapeHtml(track.format ?? '');
    const art = escapeHtml(track.albumArt ?? '🎵');

    const atmosDate = track.atmosReleaseDate ? new Date(track.atmosReleaseDate) : null;
    const releaseDate = track.releaseDate ? new Date(track.releaseDate) : null;

    const atmosDateStr = atmosDate && !isNaN(atmosDate.getTime()) ? atmosDate.toISOString().slice(0, 10) : '—';
    const releaseDateStr = releaseDate && !isNaN(releaseDate.getTime()) ? releaseDate.toISOString().slice(0, 10) : '—';

    // Validate musicLink is HTTPS before rendering
    const link = track.musicLink && isValidHttpsUrl(track.musicLink)
      ? `<a href="${escapeHtml(track.musicLink)}" target="_blank" rel="noopener noreferrer" class="music-link-btn">Listen on ${platformSafe}</a>`
      : '';

    const creditsCount = Array.isArray(track.credits) ? track.credits.length : 0;
    const avgImmStr = typeof track.avgImmersiveness === 'number' ? track.avgImmersiveness.toFixed(2) : '—';
    const shameFlag = track.hallOfShame ? '<span class="hall-of-shame-badge">⚠ Fake Atmos</span>' : '';

    // Check if new release (within last 30 days)
    const isNew = atmosDate && !isNaN(atmosDate.getTime()) && 
      (Date.now() - atmosDate.getTime()) < (30 * 24 * 60 * 60 * 1000);
    const newBadge = isNew ? '<span class="new-badge">New</span>' : '';

    return `
<div class="music-card">
  <div class="album-art-display">${art}</div>
  <div class="format-badge">${formatSafe}</div>
  <div class="card-content">
    <div class="track-title">${titleSafe}${newBadge}</div>
    <div class="track-artist">${artistSafe}</div>
    <div class="track-album">${albumSafe}</div>
    <div class="card-footer">
      <span class="platform-badge">${platformSafe}</span>
      <span class="release-date">${atmosDateStr}</span>
    </div>
    ${link ? `<div style="margin-top: 1rem;">${link}</div>` : ''}
    ${shameFlag ? `<div style="margin-top: 0.5rem;">${shameFlag}</div>` : ''}
  </div>
</div>`;
  }).join('');

  domCache.releasesSection.innerHTML = `<div class="music-grid">${tracksHtml}</div>`;
}

/**
 * Load music data from API or fallback to JSON file.
 * Merges both branches: keeps Atmos-aware fields/sorting and metadata (credits, avgImmersiveness, hallOfShame).
 */
async function loadMusicData() {
  try {
    // Optional: show loading indicator
    if (domCache.loadingSpinner) domCache.loadingSpinner.style.display = 'block';

    // Build API URL with filter parameters
    const params = new URLSearchParams();
    params.append('limit', '100');
    if (currentFilters.platform !== 'all') {
      params.append('platform', currentFilters.platform);
    }
    if (currentFilters.format !== 'all') {
      params.append('format', currentFilters.format);
    }

    const apiEndpoint = `${API_URL}/api/tracks?${params.toString()}`;

    // Try to load from backend API first
    let response;
    try {
      response = await fetch(apiEndpoint, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        credentials: 'omit'
      });
    } catch (fetchError) {
      // Network error - try fallback to data.json
      throw new Error('API_FETCH_FAILED');
    }

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
      // Fallback to local JSON file
      const fallbackResp = await fetch('/data.json', {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      if (!fallbackResp.ok) throw new Error('Failed to load fallback data.json');
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
    // If API fetch failed, try fallback to data.json
    if (err.message === 'API_FETCH_FAILED') {
      try {
        const fallbackResp = await fetch('/data.json', {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        });
        if (fallbackResp.ok) {
          const jsonTracks = await fallbackResp.json();
          if (Array.isArray(jsonTracks)) {
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
            return; // Success - exit early
          }
        }
      } catch (fallbackErr) {
        // If using file:// protocol, show helpful message
        if (typeof window !== 'undefined' && window.location.protocol === 'file:') {
          if (domCache.errorBanner) {
            domCache.errorBanner.innerHTML = '⚠️ Using file:// protocol. Please use a local HTTP server:<br>Run: <code>python -m http.server 8080</code> or <code>npx http-server</code><br>Then open: <code>http://localhost:8080</code>';
            domCache.errorBanner.style.display = 'block';
          }
          return; // Exit early to avoid showing generic error
        }
      }
    }
    
    console.error('loadMusicData error:', err);
    if (domCache.errorBanner) {
      const isFileProtocol = typeof window !== 'undefined' && window.location.protocol === 'file:';
      if (isFileProtocol) {
        domCache.errorBanner.innerHTML = '⚠️ Using file:// protocol. Please use a local HTTP server:<br>Run: <code>python -m http.server 8080</code> or <code>npx http-server</code><br>Then open: <code>http://localhost:8080</code>';
      } else {
        domCache.errorBanner.textContent = 'Failed to load tracks. Please try again later.';
      }
      domCache.errorBanner.style.display = 'block';
    }
  } finally {
    if (domCache.loadingSpinner) domCache.loadingSpinner.style.display = 'none';
    // Apply filters and re-render UI
    applyFilters();
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
      const response = await fetch(`${API_URL}/api/refresh/sync`, {
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
    const response = await fetch(`${API_URL}/api/refresh/status`);
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
 * Setup filter event listeners
 */
function setupFilters() {
  if (domCache.platformFilter) {
    domCache.platformFilter.addEventListener('change', (e) => {
      currentFilters.platform = e.target.value;
      loadMusicData();
    });
  }

  if (domCache.formatFilter) {
    domCache.formatFilter.addEventListener('change', (e) => {
      currentFilters.format = e.target.value;
      loadMusicData();
    });
  }
}

/**
 * Setup view switching for navigation tabs
 */
function setupViewSwitching() {
  const navLinks = document.querySelectorAll('.nav-tabs a[data-view]');
  const viewSections = document.querySelectorAll('.view-section');

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const viewName = link.getAttribute('data-view');

      // Update active nav link
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');

      // Update active view section
      viewSections.forEach(section => section.classList.remove('active'));
      const targetSection = document.getElementById(`${viewName}View`);
      if (targetSection) {
        targetSection.classList.add('active');
      }

      // Load data for specific views if needed
      if (viewName === 'engineers') {
        loadEngineers();
      }
    });
  });
}

/**
 * Load engineers data from API
 */
async function loadEngineers() {
  try {
    const response = await fetch(`${API_URL}/api/engineers?limit=50`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'omit'
    });

    if (response.ok) {
      allEngineers = await response.json();
      renderEngineers();
    }
  } catch (err) {
    console.error('loadEngineers error:', err);
  }
}

/**
 * Initialize DOM cache elements that need to be queried after DOM is ready
 */
function initializeDOMCache() {
  domCache.refreshButton = document.getElementById('refreshButton');
  domCache.syncButton = document.getElementById('syncButton');
  domCache.lastUpdated = document.getElementById('lastUpdated');
  domCache.platformFilter = document.getElementById('platformFilter');
  domCache.formatFilter = document.getElementById('formatFilter');
  domCache.releasesSection = document.getElementById('releases');
  domCache.engineersSection = document.getElementById('engineers');
  domCache.errorBanner = document.getElementById('error-banner');
  domCache.loadingSpinner = document.getElementById('loading-spinner');
}

/**
 * Example bootstrapping: load data on DOMContentLoaded.
 */
document.addEventListener('DOMContentLoaded', () => {
  initializeDOMCache();
  setupViewSwitching();
  setupFilters();
  setupRefreshButton();
  setupSyncButton();
  loadMusicData();
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
