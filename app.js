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

// Initialize the app
document.addEventListener('DOMContentLoaded', async () => {
    await loadMusicData();
    setupEventListeners();
    renderTracks();
    updateLastUpdated();
});

// Load music data from API or fallback to JSON file
async function loadMusicData() {
    try {
        // Try to load from backend API first
        const response = await fetch(`${API_URL}/tracks?limit=100`);
        
        if (response.ok) {
            const apiTracks = await response.json();
            
            // Transform API response to match frontend format
            allTracks = apiTracks.map(track => ({
                id: track.id,
                title: track.title,
                artist: track.artist,
                album: track.album,
                format: track.format,
                platform: track.platform,
                releaseDate: track.release_date,
                albumArt: track.album_art || '🎵'
            }));
            
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
            const response = await fetch('data.json');
            allTracks = await response.json();
            
            // Sort by release date (newest first)
            allTracks.sort((a, b) => new Date(b.releaseDate) - new Date(a.releaseDate));
            
            filteredTracks = [...allTracks];
            console.log(`Loaded ${allTracks.length} tracks from data.json`);
        } catch (fallbackError) {
            console.error('Error loading music data:', fallbackError);
            allTracks = [];
            filteredTracks = [];
        }
    }
}

// Setup event listeners
function setupEventListeners() {
    const formatFilter = document.getElementById('formatFilter');
    const refreshButton = document.getElementById('refreshButton');

    formatFilter.addEventListener('change', (e) => {
        currentFilters.format = e.target.value;
        applyFilters();
    });

    refreshButton.addEventListener('click', async () => {
        refreshButton.textContent = 'Refreshing...';
        refreshButton.disabled = true;
        
        // Try to trigger backend refresh if API is available
        try {
            const refreshResponse = await fetch(`${API_URL}/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (refreshResponse.ok) {
                const result = await refreshResponse.json();
                console.log('Backend refresh completed:', result);
            }
        } catch (error) {
            console.log('Backend API not available for refresh:', error.message);
        }
        
        // Always reload data from current source
        await loadMusicData();
        applyFilters();
        updateLastUpdated();
        
        setTimeout(() => {
            refreshButton.textContent = 'Refresh';
            refreshButton.disabled = false;
        }, 500);
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
    const musicGrid = document.getElementById('musicGrid');
    const emptyState = document.getElementById('emptyState');
    
    if (filteredTracks.length === 0) {
        musicGrid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    musicGrid.style.display = 'grid';
    emptyState.style.display = 'none';
    
    musicGrid.innerHTML = filteredTracks.map(track => createTrackCard(track)).join('');
}

// Create a track card HTML
function createTrackCard(track) {
    const isNew = isNewRelease(track.releaseDate);
    const newBadge = isNew ? '<span class="new-badge">New</span>' : '';
    
    return `
        <div class="music-card" data-track-id="${track.id}">
            <div class="card-content">
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
    const lastUpdatedElement = document.getElementById('lastUpdated');
    const now = new Date();
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true
    };
    lastUpdatedElement.textContent = now.toLocaleString('en-US', options);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Schedule auto-refresh for Fridays at 3 PM ET
function scheduleWeeklyRefresh() {
    const checkAndRefresh = async () => {
        const now = new Date();
        
        // Convert to ET (UTC-5 or UTC-4 during DST)
        const etOffset = -5 * 60; // Standard time offset in minutes
        const localOffset = now.getTimezoneOffset();
        const etTime = new Date(now.getTime() + (localOffset + etOffset) * 60000);
        
        // Check if it's Friday (5) and 3 PM (15:00)
        const isFriday = etTime.getDay() === 5;
        const hour = etTime.getHours();
        const minute = etTime.getMinutes();
        
        // Refresh if it's Friday between 3:00 PM and 3:01 PM ET
        if (isFriday && hour === 15 && minute === 0) {
            await loadMusicData();
            applyFilters();
            updateLastUpdated();
        }
    };
    
    // Check every minute
    setInterval(checkAndRefresh, 60000);
}

scheduleWeeklyRefresh();
