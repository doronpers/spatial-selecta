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

// Load music data from JSON file
async function loadMusicData() {
    try {
        const response = await fetch('data.json');
        allTracks = await response.json();
        
        // Sort by release date (newest first)
        allTracks.sort((a, b) => new Date(b.releaseDate) - new Date(a.releaseDate));
        
        filteredTracks = [...allTracks];
    } catch (error) {
        console.error('Error loading music data:', error);
        allTracks = [];
        filteredTracks = [];
    }
}

// Setup event listeners
function setupEventListeners() {
    const platformFilter = document.getElementById('platformFilter');
    const formatFilter = document.getElementById('formatFilter');
    const refreshButton = document.getElementById('refreshButton');

    platformFilter.addEventListener('change', (e) => {
        currentFilters.platform = e.target.value;
        applyFilters();
    });

    formatFilter.addEventListener('change', (e) => {
        currentFilters.format = e.target.value;
        applyFilters();
    });

    refreshButton.addEventListener('click', async () => {
        refreshButton.textContent = 'Refreshing...';
        refreshButton.disabled = true;
        
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
        const platformMatch = currentFilters.platform === 'all' || track.platform === currentFilters.platform;
        const formatMatch = currentFilters.format === 'all' || track.format === currentFilters.format;
        return platformMatch && formatMatch;
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

// Check if release is within the last 7 days
function isNewRelease(dateString) {
    const releaseDate = new Date(dateString);
    const today = new Date();
    const diffTime = today - releaseDate;
    const diffDays = diffTime / (1000 * 60 * 60 * 24);
    return diffDays <= 7 && diffDays >= 0;
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

// Auto-refresh data every 5 minutes (300000 ms)
setInterval(async () => {
    await loadMusicData();
    applyFilters();
    updateLastUpdated();
}, 300000);
