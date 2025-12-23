// Configuration
const API_URL = window.location.hostname === 'localhost' && window.location.port === '8080'
    ? 'http://localhost:8000/api'  // Local development with separate backend
    : '/api';  // Production - assume API is on same domain

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
                albumArt: track.album_art || '🎵'
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
    const validPlatforms = ['Apple Music', 'Amazon Music'];
    const validFormats = ['Dolby Atmos', '360 Reality Audio'];
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
            if (value === 'all' || value === 'Apple Music' || value === 'Amazon Music') {
                currentFilters.platform = value;
                debouncedApplyFilters();
            }
        });
    }

    domCache.formatFilter.addEventListener('change', (e) => {
        const value = e.target.value;
        // Validate filter value
        if (value === 'all' || value === 'Dolby Atmos' || value === '360 Reality Audio') {
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
        const formatMatch = currentFilters.format === 'all' || track.format === currentFilters.format;
        return formatMatch;
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
function scheduleWeeklyRefresh() {
    let refreshInterval = null;
    let lastRefreshMinute = -1;
    
    const checkAndRefresh = async () => {
        // Use Page Visibility API to pause when tab is hidden
        if (document.hidden) {
            return;
        }
        
        const now = new Date();
        
        // Convert to ET (UTC-5 or UTC-4 during DST)
        const etOffset = -5 * 60; // Standard time offset in minutes
        const localOffset = now.getTimezoneOffset();
        const etTime = new Date(now.getTime() + (localOffset + etOffset) * 60000);
        
        // Check if it's Friday (5) and 3 PM (15:00)
        const isFriday = etTime.getDay() === 5;
        const hour = etTime.getHours();
        const minute = etTime.getMinutes();
        
        // Refresh if it's Friday between 3:00 PM and 3:01 PM ET (only once per minute)
        if (isFriday && hour === 15 && minute === 0 && minute !== lastRefreshMinute) {
            lastRefreshMinute = minute;
            await loadMusicData();
            applyFilters();
            updateLastUpdated();
        }
    };
    
    // Check every minute, but pause when tab is hidden
    refreshInterval = setInterval(checkAndRefresh, 60000);
    
    // Pause interval when tab is hidden, resume when visible
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            // Tab is hidden, interval will naturally pause checks
            return;
        } else {
            // Tab is visible, check immediately
            checkAndRefresh();
        }
    });
    
    // Initial check
    checkAndRefresh();
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
