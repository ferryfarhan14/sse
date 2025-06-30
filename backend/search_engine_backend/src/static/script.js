// API Configuration
const API_BASE_URL = '/api';

// DOM Elements
const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const resultsList = document.getElementById('resultsList');
const resultsTitle = document.getElementById('resultsTitle');
const resultsCount = document.getElementById('resultsCount');
const loadingIndicator = document.getElementById('loadingIndicator');
const noResults = document.getElementById('noResults');

// Admin Modal Elements
const adminBtn = document.getElementById('adminBtn');
const adminModal = document.getElementById('adminModal');
const closeModal = document.getElementById('closeModal');
const addDomainForm = document.getElementById('addDomainForm');
const domainInput = document.getElementById('domainInput');
const domainsList = document.getElementById('domainsList');
const crawlForm = document.getElementById('crawlForm');
const urlsInput = document.getElementById('urlsInput');
const totalPages = document.getElementById('totalPages');
const totalDomains = document.getElementById('totalDomains');

// Toast Element
const toast = document.getElementById('toast');

// State
let currentQuery = '';

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadDomains();
    loadStats();
});

// Event Listeners
function initializeEventListeners() {
    // Search Form
    searchForm.addEventListener('submit', handleSearch);
    
    // Admin Modal
    adminBtn.addEventListener('click', openAdminModal);
    closeModal.addEventListener('click', closeAdminModal);
    adminModal.addEventListener('click', function(e) {
        if (e.target === adminModal) {
            closeAdminModal();
        }
    });
    
    // Admin Forms
    addDomainForm.addEventListener('submit', handleAddDomain);
    crawlForm.addEventListener('submit', handleCrawlUrls);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAdminModal();
        }
        if (e.key === '/' && !isInputFocused()) {
            e.preventDefault();
            searchInput.focus();
        }
    });
}

// Search Functions
async function handleSearch(e) {
    e.preventDefault();
    
    const query = searchInput.value.trim();
    if (!query) return;
    
    currentQuery = query;
    showLoading();
    hideResults();
    hideNoResults();
    
    try {
        const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}&limit=20`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Search failed');
        }
        
        hideLoading();
        
        if (data.results && data.results.length > 0) {
            displayResults(data.results, query);
        } else {
            showNoResults();
        }
        
    } catch (error) {
        hideLoading();
        showToast('Error: ' + error.message, 'error');
        console.error('Search error:', error);
    }
}

function displayResults(results, query) {
    resultsTitle.textContent = `Hasil Pencarian untuk "${query}"`;
    resultsCount.textContent = `${results.length} hasil ditemukan`;
    
    resultsList.innerHTML = '';
    
    results.forEach(result => {
        const resultElement = createResultElement(result);
        resultsList.appendChild(resultElement);
    });
    
    showResults();
}

function createResultElement(result) {
    const div = document.createElement('div');
    div.className = 'result-item';
    
    const title = result.title || 'Untitled';
    const url = result.url || '#';
    const description = result.description || result.content || 'No description available';
    const domain = result.domain || '';
    const lastUpdated = result.last_updated ? new Date(result.last_updated).toLocaleDateString('id-ID') : '';
    
    div.innerHTML = `
        <a href="${url}" target="_blank" class="result-title">${escapeHtml(title)}</a>
        <div class="result-url">${escapeHtml(url)}</div>
        <div class="result-description">${escapeHtml(description)}</div>
        <div class="result-meta">
            <span><i class="fas fa-globe"></i> ${escapeHtml(domain)}</span>
            ${lastUpdated ? `<span><i class="fas fa-clock"></i> ${lastUpdated}</span>` : ''}
        </div>
    `;
    
    div.addEventListener('click', function(e) {
        if (e.target.tagName !== 'A') {
            window.open(url, '_blank');
        }
    });
    
    return div;
}

// Admin Functions
function openAdminModal() {
    adminModal.classList.remove('hidden');
    loadDomains();
    loadStats();
}

function closeAdminModal() {
    adminModal.classList.add('hidden');
}

async function handleAddDomain(e) {
    e.preventDefault();
    
    const domain = domainInput.value.trim();
    if (!domain) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/domains`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to add domain');
        }
        
        showToast(data.message, 'success');
        domainInput.value = '';
        loadDomains();
        loadStats();
        
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
        console.error('Add domain error:', error);
    }
}

async function handleCrawlUrls(e) {
    e.preventDefault();
    
    const urlsText = urlsInput.value.trim();
    if (!urlsText) return;
    
    const urls = urlsText.split('\n')
        .map(url => url.trim())
        .filter(url => url.length > 0);
    
    if (urls.length === 0) {
        showToast('Please enter at least one URL', 'error');
        return;
    }
    
    try {
        showToast('Starting crawl process...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/crawl`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ urls })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Crawl failed');
        }
        
        showToast(data.message, 'success');
        urlsInput.value = '';
        loadStats();
        
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
        console.error('Crawl error:', error);
    }
}

async function loadDomains() {
    try {
        const response = await fetch(`${API_BASE_URL}/domains`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load domains');
        }
        
        displayDomains(data.domains || []);
        
    } catch (error) {
        console.error('Load domains error:', error);
        domainsList.innerHTML = '<p class="error">Failed to load domains</p>';
    }
}

function displayDomains(domains) {
    if (domains.length === 0) {
        domainsList.innerHTML = '<p class="text-muted">No domains added yet</p>';
        return;
    }
    
    domainsList.innerHTML = '';
    domains.forEach(domain => {
        const span = document.createElement('span');
        span.className = 'domain-tag';
        span.textContent = domain;
        domainsList.appendChild(span);
    });
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load stats');
        }
        
        totalPages.textContent = data.total_pages || 0;
        totalDomains.textContent = data.total_domains || 0;
        
    } catch (error) {
        console.error('Load stats error:', error);
        totalPages.textContent = 'Error';
        totalDomains.textContent = 'Error';
    }
}

// UI Helper Functions
function showLoading() {
    loadingIndicator.classList.remove('hidden');
}

function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

function showResults() {
    searchResults.classList.remove('hidden');
}

function hideResults() {
    searchResults.classList.add('hidden');
}

function showNoResults() {
    noResults.classList.remove('hidden');
}

function hideNoResults() {
    noResults.classList.add('hidden');
}

function showToast(message, type = 'info') {
    const toastIcon = toast.querySelector('.toast-icon');
    const toastMessage = toast.querySelector('.toast-message');
    
    // Set icon based on type
    let iconClass = 'fas fa-info-circle';
    if (type === 'success') iconClass = 'fas fa-check-circle';
    else if (type === 'error') iconClass = 'fas fa-exclamation-circle';
    else if (type === 'info') iconClass = 'fas fa-info-circle';
    
    toastIcon.className = `toast-icon ${iconClass}`;
    toastMessage.textContent = message;
    
    // Remove existing type classes and add new one
    toast.className = `toast ${type}`;
    
    // Show toast
    toast.classList.add('show');
    
    // Hide after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement && (
        activeElement.tagName === 'INPUT' || 
        activeElement.tagName === 'TEXTAREA' || 
        activeElement.contentEditable === 'true'
    );
}

// Keyboard shortcuts info
console.log('Keyboard shortcuts:');
console.log('- Press "/" to focus search input');
console.log('- Press "Escape" to close modal');

