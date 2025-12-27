// Configuration
const API_URL = (() => {
    const hostname = window.location.hostname;
    const isDevelopment = hostname === 'localhost' && window.location.port === '8080';
    
    if (isDevelopment) {
        return 'http://localhost:8000/api';  // Local development
    }
    
    // Production: API is proxied through the same domain
    // Frontend on spatialselects.com proxies /api/* to backend
    return '/api';
})();

// State management
let allTracks = [];
let filteredTracks = [];
let currentFilters = {
    platform: 'all',
    format: 'all'
};

// Cached DOM elements
const domCache = {
    musicGrid: null,
    emptyState: null,
    platformFilter: null,
    formatFilter: null,
    refreshButton: null,
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
    await loadMusicData();
    setupEventListeners();
    setupModalListeners();
    renderTracks();
    updateLastUpdated();
});

// Cache DOM elements for performance
function initializeDOMCache() {
    domCache.musicGrid = document.getElementById('musicGrid');
    domCache.emptyState = document.getElementById('emptyState');
    domCache.platformFilter = document.getElementById('platformFilter');
    domCache.formatFilter = document.getElementById('formatFilter');
    domCache.refreshButton = document.getElementById('refreshButton');
    domCache.lastUpdated = document.getElementById('lastUpdated');
    domCache.trackModal = document.getElementById('trackModal');
    domCache.modalBody = document.getElementById('modalBody');
    domCache.modalClose = document.querySelector('.modal-close');
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
                atmosReleaseDate: track.atmos_release_date || track.release_date,
                albumArt: track.album_art || '🎵',
                musicLink: track.music_link || null
            })).filter(track => validateTrack(track));
            
            if (allTracks.length === 0) {
                throw new Error('No valid tracks found in API response');
            }
            
            // Sort by Atmos release date (newest first) - fallback to releaseDate if not available
            sortTracksByAtmosDate(allTracks);
            
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
            
            // Sort by Atmos release date (newest first) - fallback to releaseDate if not available
            sortTracksByAtmosDate(allTracks);
            
            filteredTracks = [...allTracks];
            console.log(`Loaded ${allTracks.length} tracks from data.json (fallback)`);
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
    
    // Required fields (atmosReleaseDate is recommended for new tracks but optional for backwards compatibility)
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
    
    // Validate releaseDate is valid
    const date = new Date(track.releaseDate);
    if (isNaN(date.getTime())) {
        return false;
    }
    
    // Validate atmosReleaseDate if present
    if (track.atmosReleaseDate) {
        if (!dateRegex.test(track.atmosReleaseDate)) {
            return false;
        }
        const atmosDate = new Date(track.atmosReleaseDate);
        if (isNaN(atmosDate.getTime())) {
            return false;
        }
        // Atmos release date should not be before original release date - reject if invalid
        if (atmosDate < date) {
            console.error(`Track ${track.id}: atmosReleaseDate (${track.atmosReleaseDate}) is before releaseDate (${track.releaseDate})`);
            return false;
        }
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
        // Only allow HTTPS for Apple Music links (Apple Music doesn't use HTTP)
        return urlObj.protocol === 'https:';
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

// Sort tracks by Atmos release date (newest first), fallback to releaseDate
function sortTracksByAtmosDate(tracks) {
    return tracks.sort((a, b) => {
        const dateA = new Date(a.atmosReleaseDate || a.releaseDate);
        const dateB = new Date(b.atmosReleaseDate || b.releaseDate);
        return dateB - dateA;
    });
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
    const atmosDate = track.atmosReleaseDate || track.releaseDate;
    const isNew = isNewRelease(atmosDate);
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
                    <span class="release-date">${formatDate(atmosDate)}</span>
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
    
    // Build modal content safely with ARIA attributes
    const trackTitle = escapeHtml(track.title);
    const trackArtist = escapeHtml(track.artist);
    
    // Format dates - show both original and Atmos release dates if different
    const originalDate = formatDate(track.releaseDate);
    const atmosDate = track.atmosReleaseDate ? formatDate(track.atmosReleaseDate) : null;
    const dateDisplay = atmosDate && atmosDate !== originalDate
        ? `<span class="modal-date">Original: ${originalDate} | Atmos: ${atmosDate}</span>`
        : `<span class="modal-date">Released: ${originalDate}</span>`;
    
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
                    ${dateDisplay}
                </div>
            </div>
        </div>
        <div id="modalDescription" class="modal-content-body">
            ${musicLinkHtml}
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
    
    // Focus management for accessibility
    const firstFocusable = domCache.modalBody.querySelector('a, button');
    if (firstFocusable) {
        firstFocusable.focus();
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
