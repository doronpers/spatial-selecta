// Configuration
// Determine API URL based on environment
let API_URL;
if (window.location.hostname === 'localhost' && window.location.port === '8080') {
    // Local development with separate backend
    API_URL = 'http://localhost:8000/api';
} else if (window.location.hostname.includes('onrender.com')) {
    // Render deployment - backend and frontend on different subdomains
    // Extract backend service name from frontend name
    // e.g., spatial-selecta-frontend.onrender.com -> spatial-selecta-api.onrender.com
    const hostname = window.location.hostname;
    const backendName = hostname.replace('-frontend', '-api');
    API_URL = `https://${backendName}/api`;
} else {
    // Production - assume API is on same domain or configured via meta tag
    const apiMeta = document.querySelector('meta[name="api-url"]');
    API_URL = apiMeta ? apiMeta.getAttribute('content') : '/api';
}

// State management
let allTracks = [];
let filteredTracks = [];
let allEngineers = [];
let currentFilters = {
    platform: 'all',
    format: 'all'
};

// Cached DOM elements
const domCache = {
    navTabs: null,
    viewSections: null,
    musicGrid: null,
    engineersGrid: null,
    emptyState: null,
    platformFilter: null,
    formatFilter: null,
    refreshButton: null,
    syncButton: null,
    lastUpdated: null,
    trackModal: null,
    modalBody: null,
    modalClose: null
};

// Track modal state to prevent unnecessary re-renders
let currentModalTrackId = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', async () => {
    initializeDOMCache();
    setupNavigation();
    await Promise.all([
        loadMusicData(),
        loadEngineersData()
    ]);
    setupEventListeners();
    setupModalListeners();
    renderTracks();
    renderEngineers();
    updateLastUpdated();
});

// Cache DOM elements for performance
function initializeDOMCache() {
    domCache.navTabs = document.querySelectorAll('.nav-tabs a');
    domCache.viewSections = document.querySelectorAll('.view-section');
    domCache.musicGrid = document.getElementById('musicGrid');
    domCache.engineersGrid = document.getElementById('engineersGrid');
    domCache.emptyState = document.getElementById('emptyState');
    domCache.platformFilter = document.getElementById('platformFilter');
    domCache.formatFilter = document.getElementById('formatFilter');
    domCache.refreshButton = document.getElementById('refreshButton');
    domCache.syncButton = document.getElementById('syncButton');
    domCache.lastUpdated = document.getElementById('lastUpdated');
    domCache.trackModal = document.getElementById('trackModal');
    domCache.modalBody = document.getElementById('modalBody');
    domCache.modalClose = document.querySelector('.modal-close');
}

// Setup navigation tabs
function setupNavigation() {
    domCache.navTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();

            // Update active tab
            domCache.navTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show target view
            const targetId = tab.getAttribute('data-view') + 'View';
            domCache.viewSections.forEach(section => {
                section.style.display = 'none';
                section.classList.remove('active');
            });

            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.style.display = 'block';
                // Small timeout to allow display:block to apply before opacity transition if we added one
                setTimeout(() => targetSection.classList.add('active'), 10);
            }
        });
    });
}

// Load engineer data from API
async function loadEngineersData() {
    try {
        const response = await fetch(`${API_URL}/engineers?limit=50`);
        if (response.ok) {
            allEngineers = await response.json();
            console.log(`Loaded ${allEngineers.length} engineers`);
        }
    } catch (error) {
        console.warn('Failed to load engineers:', error);
        allEngineers = [];
    }
}

// Render engineers grid
function renderEngineers() {
    if (!domCache.engineersGrid) return;

    if (allEngineers.length === 0) {
        domCache.engineersGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No engineers found.</p>';
        return;
    }

    domCache.engineersGrid.innerHTML = allEngineers.map(eng => `
        <div class="engineer-card">
            <div class="engineer-avatar">
                ${eng.profile_image_url ? `<img src="${eng.profile_image_url}" alt="${eng.name}">` : eng.name.charAt(0)}
            </div>
            <div class="engineer-name">${escapeHtml(eng.name)}</div>
            <div class="mix-count">${eng.mix_count} Mixes</div>
        </div>
    `).join('');
}

// Load music data from API or fallback to JSON file
async function loadMusicData() {
    try {
        // Try to load from backend API first
        const response = await fetch(`${API_URL}/tracks?limit=100`);

        if (response.ok) {
            const apiTracks = await response.json();

            // Validate and sanitize data
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
                releaseDate: track.release_date,
                albumArt: track.album_art || '🎵',
                credits: track.credits || [],
                avgImmersiveness: track.avg_immersiveness,
                hallOfShame: track.hall_of_shame
            })).filter(track => validateTrack(track));

            if (allTracks.length === 0) {
                throw new Error('No valid tracks found in API response');
            }

            // Sort by release date (newest first)
            allTracks.sort((a, b) => new Date(b.releaseDate) - new Date(a.releaseDate));

            filteredTracks = [...allTracks];
            console.log(`Loaded ${allTracks.length} tracks from API`);
        } else {
            throw new Error('API not available, falling back to data.json');
        }
    } catch (error) {
        console.warn('Backend API not available, loading from data.json:', error.message);

        // Fallback to loading from static JSON file
        try {
            const response = await fetch('data.json', {
                cache: 'default',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Validate and sanitize data
            if (!Array.isArray(data)) {
                throw new Error('Invalid data format: expected array');
            }

            // Validate and sanitize each track
            allTracks = data.filter(track => validateTrack(track));

            if (allTracks.length === 0) {
                throw new Error('No valid tracks found in data');
            }

            // Sort by release date (newest first)
            allTracks.sort((a, b) => new Date(b.releaseDate) - new Date(a.releaseDate));

            filteredTracks = [...allTracks];
            console.log(`Loaded ${allTracks.length} tracks from data.json`);
        } catch (fallbackError) {
            console.error('Error loading music data:', fallbackError);
            // Show user-friendly error message
            if (domCache.emptyState) {
                domCache.emptyState.innerHTML = '<p>Unable to load music data. Please try refreshing the page.</p>';
                domCache.emptyState.style.display = 'block';
            }
            allTracks = [];
            filteredTracks = [];
        }
    }
}

// Validate track data structure and values
function validateTrack(track) {
    if (!track || typeof track !== 'object') {
        return false;
    }

    // Required fields
    const requiredFields = ['id', 'title', 'artist', 'album', 'format', 'platform', 'releaseDate'];
    for (const field of requiredFields) {
        if (!(field in track) || track[field] === null || track[field] === undefined) {
            return false;
        }
    }

    // Validate ID is a number
    if (typeof track.id !== 'number' || track.id <= 0 || !Number.isInteger(track.id)) {
        return false;
    }

    // Validate string fields
    const stringFields = ['title', 'artist', 'album', 'format', 'platform'];
    for (const field of stringFields) {
        if (typeof track[field] !== 'string' || track[field].trim().length === 0) {
            return false;
        }
    }

    // Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(track.releaseDate)) {
        return false;
    }

    // Validate date is valid
    const date = new Date(track.releaseDate);
    if (isNaN(date.getTime())) {
        return false;
    }

    // Validate platform and format values
    const validPlatforms = ['Apple Music'];
    const validFormats = ['Dolby Atmos'];
    if (!validPlatforms.includes(track.platform) || !validFormats.includes(track.format)) {
        return false;
    }

    // Validate musicLink if present (must be valid HTTP/HTTPS URL)
    if (track.musicLink && !isValidUrl(track.musicLink)) {
        return false;
    }

    return true;
}

// Validate URL to prevent XSS via javascript: or data: URLs
function isValidUrl(url) {
    if (typeof url !== 'string' || url.trim().length === 0) {
        return false;
    }

    try {
        const urlObj = new URL(url);
        // Only allow http and https protocols
        return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch (e) {
        return false;
    }
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Setup event listeners
function setupEventListeners() {
    if (!domCache.platformFilter || !domCache.formatFilter || !domCache.refreshButton) {
        console.error('Required DOM elements not found');
        return;
    }

    // Debounced filter application for better performance
    const debouncedApplyFilters = debounce(applyFilters, 150);

    if (domCache.platformFilter) {
        domCache.platformFilter.addEventListener('change', (e) => {
            const value = e.target.value;
            // Validate filter value
            if (value === 'all' || value === 'Apple Music') {
                currentFilters.platform = value;
                debouncedApplyFilters();
            }
        });
    }

    domCache.formatFilter.addEventListener('change', (e) => {
        const value = e.target.value;
        // Validate filter value
        if (value === 'all' || value === 'Dolby Atmos') {
            currentFilters.format = value;
            debouncedApplyFilters();
        }
    });

    // Rate limiting for refresh button
    let refreshInProgress = false;
    domCache.refreshButton.addEventListener('click', async () => {
        if (refreshInProgress) {
            return;
        }

        refreshInProgress = true;
        domCache.refreshButton.textContent = 'Refreshing...';
        domCache.refreshButton.disabled = true;

        // Note: Backend refresh endpoint requires authentication
        // Frontend refresh button only reloads data, not triggering backend scan
        // To trigger backend refresh, use the API directly with authentication token

        // Reload data from current source
        try {
            await loadMusicData();
            applyFilters();
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

    // Sync button - triggers backend to fetch new tracks from Apple Music
    if (domCache.syncButton) {
        setupSyncButton();
    }
}

// Setup sync button functionality
function setupSyncButton() {
    let syncInProgress = false;

    // Check sync availability on load
    checkSyncStatus();

    domCache.syncButton.addEventListener('click', async () => {
        if (syncInProgress || domCache.syncButton.disabled) {
            return;
        }

        syncInProgress = true;
        const originalText = domCache.syncButton.textContent;
        domCache.syncButton.textContent = 'Syncing...';
        domCache.syncButton.disabled = true;
        domCache.syncButton.classList.add('syncing');
        domCache.syncButton.classList.remove('success', 'error');

        try {
            const response = await fetch(`${API_URL}/refresh/sync`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                const added = result.tracks_added || 0;
                const updated = result.tracks_updated || 0;

                domCache.syncButton.textContent = `+${added} new`;
                domCache.syncButton.classList.remove('syncing');
                domCache.syncButton.classList.add('success');

                // Reload the track list to show new data
                await loadMusicData();
                applyFilters();
                updateLastUpdated();

                // Reset button after delay
                setTimeout(() => {
                    domCache.syncButton.textContent = originalText;
                    domCache.syncButton.classList.remove('success');
                    checkSyncStatus();
                }, 3000);
            } else if (response.status === 429) {
                // Rate limited
                const data = await response.json();
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

// Check if sync is available (rate limit status)
async function checkSyncStatus() {
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
        // If status check fails, leave button enabled
        console.warn('Could not check sync status:', error);
    }
}

// Apply filters to tracks
function applyFilters() {
    filteredTracks = allTracks.filter(track => {
        const platformMatch = currentFilters.platform === 'all' || track.platform === currentFilters.platform;
        const formatMatch = currentFilters.format === 'all' || track.format === currentFilters.format;
        return platformMatch && formatMatch;
    });

    renderTracks();
}

// Render tracks to the grid
function renderTracks() {
    if (!domCache.musicGrid || !domCache.emptyState) {
        return;
    }

    if (filteredTracks.length === 0) {
        domCache.musicGrid.style.display = 'none';
        domCache.emptyState.style.display = 'block';
        return;
    }

    domCache.musicGrid.style.display = 'grid';
    domCache.emptyState.style.display = 'none';

    // Use DocumentFragment for better performance
    const fragment = document.createDocumentFragment();
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = filteredTracks.map(track => createTrackCard(track)).join('');

    while (tempDiv.firstChild) {
        fragment.appendChild(tempDiv.firstChild);
    }

    domCache.musicGrid.innerHTML = '';
    domCache.musicGrid.appendChild(fragment);

    // Re-setup event delegation after render
    setupCardClickDelegation();
}

// Create a track card HTML
function createTrackCard(track) {
    const isNew = isNewRelease(track.releaseDate);
    const newBadge = isNew ? '<span class="new-badge">New</span>' : '';
    const albumArtDisplay = track.albumArt ? `<div class="album-art-display">${track.albumArt}</div>` : '';

    return `
        <div class="music-card" data-track-id="${track.id}">
            <div class="card-content">
                ${albumArtDisplay}
                <span class="format-badge">${escapeHtml(track.format)}</span>
                <h3 class="track-title">${escapeHtml(track.title)}${newBadge}</h3>
                <p class="track-artist">${escapeHtml(track.artist)}</p>
                <p class="track-album">${escapeHtml(track.album)}</p>
                <div class="card-footer">
                    <span class="platform-badge">${escapeHtml(track.platform)}</span>
                    <span class="release-date">${formatDate(track.releaseDate)}</span>
                </div>
            </div>
        </div>
    `;
}

// Check if release is within the last 30 days
function isNewRelease(dateString) {
    const releaseDate = new Date(dateString);
    const today = new Date();
    const diffTime = today - releaseDate;
    const diffDays = diffTime / (1000 * 60 * 60 * 24);
    return diffDays <= 30 && diffDays >= 0;
}

// Format date to readable string
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Update last updated timestamp
function updateLastUpdated() {
    if (!domCache.lastUpdated) {
        return;
    }

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

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Schedule auto-refresh for Fridays at 3 PM ET
// Note: This is a client-side implementation that only works when the page is open.
// For production, use server-side cron jobs or scheduled tasks.
function scheduleWeeklyRefresh() {
    // Calculate milliseconds until next Friday 3 PM ET
    const getNextRefreshTime = () => {
        const now = new Date();
        const etNow = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));
        const etNowTime = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));

        // Get current ET day and time
        const currentDay = etNowTime.getDay(); // 0 = Sunday, 5 = Friday
        const currentHour = etNowTime.getHours();
        const currentMinute = etNowTime.getMinutes();

        // Calculate days until next Friday
        let daysUntilFriday = (5 - currentDay + 7) % 7;
        if (daysUntilFriday === 0 && (currentHour < 15 || (currentHour === 15 && currentMinute === 0))) {
            // It's Friday and before 3 PM, refresh today
            daysUntilFriday = 0;
        } else if (daysUntilFriday === 0) {
            // It's Friday but after 3 PM, refresh next Friday
            daysUntilFriday = 7;
        }

        // Calculate target time: next Friday at 3:00 PM ET
        const targetET = new Date(etNowTime);
        targetET.setDate(targetET.getDate() + daysUntilFriday);
        targetET.setHours(15, 0, 0, 0);

        // Convert ET time back to local time for setTimeout
        const etOffset = etNowTime.getTime() - now.getTime();
        const targetLocal = new Date(targetET.getTime() - etOffset);

        const msUntilRefresh = targetLocal.getTime() - now.getTime();
        return Math.max(msUntilRefresh, 60000); // Minimum 1 minute
    };

    const scheduleNextRefresh = () => {
        const msUntilRefresh = getNextRefreshTime();

        setTimeout(async () => {
            // Only refresh if page is visible
            if (!document.hidden) {
                console.log('Auto-refreshing data (scheduled weekly refresh)');
                await loadMusicData();
                applyFilters();
                updateLastUpdated();
            }

            // Schedule next refresh (weekly)
            scheduleNextRefresh();
        }, msUntilRefresh);
    };

    // Start scheduling
    scheduleNextRefresh();

    // Also check when page becomes visible (in case we missed the scheduled time)
    document.addEventListener('visibilitychange', async () => {
        if (!document.hidden) {
            const etNow = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/New_York' }));
            const isFriday = etNow.getDay() === 5;
            const is3PM = etNow.getHours() === 15 && etNow.getMinutes() < 5; // 5 minute window

            if (isFriday && is3PM) {
                // Check if we should refresh (avoid multiple refreshes)
                const lastRefresh = localStorage.getItem('lastAutoRefresh');
                const now = Date.now();
                if (!lastRefresh || now - parseInt(lastRefresh) > 300000) { // 5 minutes
                    localStorage.setItem('lastAutoRefresh', now.toString());
                    await loadMusicData();
                    applyFilters();
                    updateLastUpdated();
                }
            }
        }
    });
}

scheduleWeeklyRefresh();

// Use event delegation for better performance (no memory leaks)
// Attach single listener to music grid instead of individual cards
function setupCardClickDelegation() {
    if (!domCache.musicGrid) {
        return;
    }

    // Remove existing listener if any (idempotent)
    domCache.musicGrid.removeEventListener('click', handleCardClick);

    // Add single delegated listener
    domCache.musicGrid.addEventListener('click', handleCardClick);
}

function handleCardClick(e) {
    // Find the closest music-card element
    const card = e.target.closest('.music-card');
    if (!card) {
        return;
    }

    const trackIdAttr = card.getAttribute('data-track-id');
    if (!trackIdAttr) {
        return;
    }

    const trackId = parseInt(trackIdAttr, 10);
    if (isNaN(trackId) || trackId <= 0) {
        return;
    }

    const track = allTracks.find(t => t.id === trackId);
    if (track) {
        openTrackModal(track);
    }
}

function openTrackModal(track) {
    if (!domCache.trackModal || !domCache.modalBody || !track) {
        return;
    }

    // Prevent unnecessary re-render if same track is already open
    if (currentModalTrackId === track.id && domCache.trackModal.style.display === 'block') {
        return;
    }

    currentModalTrackId = track.id;

    // Validate and sanitize musicLink URL
    let musicLinkHtml = '';
    if (track.musicLink && isValidUrl(track.musicLink)) {
        const safeUrl = escapeHtml(track.musicLink);
        const platformText = escapeHtml(track.platform);
        musicLinkHtml = `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer" class="music-link-btn">Listen on ${platformText}</a>`;
    }

    const albumArtDisplay = track.albumArt ? `<div class="modal-album-art">${escapeHtml(track.albumArt)}</div>` : '';

    // Credits Section
    let creditsHtml = '';
    if (track.credits && track.credits.length > 0) {
        creditsHtml = `
            <div class="modal-section">
                <h3 class="modal-section-title">Credits</h3>
                <div class="credits-list">
                    ${track.credits.map(credit => `
                        <div class="credit-item">
                            <span class="credit-role">${escapeHtml(credit.role)}:</span>
                            <span class="credit-name">${escapeHtml(credit.engineer_name)}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Community Rating Section
    let ratingHtml = `
        <div class="modal-section">
            <h3 class="modal-section-title">Community Quality</h3>
            <div class="rating-display">
                <div class="immersiveness-score">
                    <span class="score-label">Immersiveness:</span>
                    <span class="score-value">${track.avgImmersiveness ? track.avgImmersiveness.toFixed(1) : 'N/A'}/10</span>
                </div>
                ${track.hallOfShame ? '<div class="hall-of-shame-badge">⚠️ Hall of Shame (Fake Atmos Reported)</div>' : ''}
            </div>
            <div class="rating-controls">
                <p>Rate this mix:</p>
                <div class="star-rating" data-track-id="${track.id}">
                    ${[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(n => `<button class="star-btn" data-rating="${n}" title="${n}/10">★</button>`).join('')}
                </div>
                <label class="fake-atmos-check">
                    <input type="checkbox" id="fakeAtmosCheck"> Report as Fake Atmos
                </label>
                <button id="submitRatingBtn" class="submit-rating-btn" data-track-id="${track.id}">Submit Rating</button>
            </div>
        </div>
    `;

    // Build modal content
    const trackTitle = escapeHtml(track.title);
    const trackArtist = escapeHtml(track.artist);
    domCache.modalBody.innerHTML = `
        <div class="modal-header">
            ${albumArtDisplay}
            <div class="modal-title-section">
                <span class="modal-format-badge">${escapeHtml(track.format)}</span>
                <h2 id="modalTitle" class="modal-track-title">${trackTitle}</h2>
                <p class="modal-artist">${trackArtist}</p>
                <p class="modal-album">${escapeHtml(track.album)}</p>
                <div class="modal-meta">
                    <span class="modal-platform">${escapeHtml(track.platform)}</span>
                    <span class="modal-date">Released ${formatDate(track.releaseDate)}</span>
                </div>
            </div>
        </div>
        <div id="modalDescription" class="modal-content-body">
            ${musicLinkHtml}
            ${creditsHtml}
            ${ratingHtml}
            ${track.review ? `<div class="modal-section">
                <h3 class="modal-section-title">Review</h3>
                <p class="modal-text">${escapeHtml(track.review)}</p>
            </div>` : ''}
            ${track.technicalDetails ? `<div class="modal-section">
                <h3 class="modal-section-title">Technical Details</h3>
                <p class="modal-text">${escapeHtml(track.technicalDetails)}</p>
            </div>` : ''}
            ${track.comparisonNotes ? `<div class="modal-section">
                <h3 class="modal-section-title">Platform Notes</h3>
                <p class="modal-text">${escapeHtml(track.comparisonNotes)}</p>
            </div>` : ''}
        </div>
    `;

    domCache.trackModal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    // Add event listeners for rating
    const starBtns = domCache.modalBody.querySelectorAll('.star-btn');
    starBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const rating = parseInt(e.target.dataset.rating);
            starBtns.forEach(b => {
                b.classList.toggle('active', parseInt(b.dataset.rating) <= rating);
            });
            domCache.modalBody.setAttribute('data-selected-rating', rating);
        });
    });

    // Submit rating handler
    const submitBtn = domCache.modalBody.querySelector('#submitRatingBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', () => submitRating(track.id));
    }

    // Focus management for accessibility
    const firstFocusable = domCache.modalBody.querySelector('a, button');
    if (firstFocusable) {
        firstFocusable.focus();
    }
}

// Submit rating
async function submitRating(trackId) {
    const rating = domCache.modalBody.getAttribute('data-selected-rating');
    const isFake = document.getElementById('fakeAtmosCheck')?.checked;

    if (!rating && !isFake) {
        alert('Please select a rating score or report as fake.');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/tracks/${trackId}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                score: rating ? parseInt(rating) : 0,
                is_fake: !!isFake
            })
        });

        if (response.ok) {
            alert('Rating submitted! Thank you.');
            // Update UI to reflect success (disable buttons, etc)
            const submitBtn = document.getElementById('submitRatingBtn');
            if (submitBtn) {
                submitBtn.textContent = 'Submitted';
                submitBtn.disabled = true;
            }
        } else {
            alert('Failed to submit rating. You may have been rate limited.');
        }
    } catch (e) {
        console.error('Error submitting rating:', e);
        alert('Error submitting rating.');
    }
}

function closeTrackModal() {
    if (!domCache.trackModal) {
        return;
    }

    domCache.trackModal.style.display = 'none';
    document.body.style.overflow = '';
    currentModalTrackId = null;
}

// Setup modal event listeners
function setupModalListeners() {
    if (!domCache.modalClose || !domCache.trackModal) {
        return;
    }

    // Close button click handler and keyboard support
    domCache.modalClose.addEventListener('click', closeTrackModal);
    domCache.modalClose.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            closeTrackModal();
        }
    });

    // Close modal when clicking outside of it
    domCache.trackModal.addEventListener('click', (e) => {
        if (e.target === domCache.trackModal) {
            closeTrackModal();
        }
    });

    // Close modal with Escape key (single listener on document)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && domCache.trackModal && domCache.trackModal.style.display === 'block') {
            closeTrackModal();
        }
    });
}

// Initialize card click delegation after DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Setup event delegation for card clicks
    setupCardClickDelegation();
});
