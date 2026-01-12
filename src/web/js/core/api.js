// API Configuration and Helper Functions
const API_URL = 'http://localhost:5002';

// Helper function for authenticated API calls
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('session_token');
    
    if (!token) {
        showLoginModal();
        throw new Error('Authentication required');
    }
    
    options.headers = options.headers || {};
    options.headers['Authorization'] = token;
    options.credentials = 'include';
    
    try {
        const response = await fetch(url, options);
        
        if (response.status === 401) {
            // Session expired
            localStorage.removeItem('session_token');
            localStorage.removeItem('username');
            localStorage.removeItem('email');
            showLoginModal();
            throw new Error('Session expired. Please login again.');
        }
        
        return response;
    } catch (error) {
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to server. Please check if the server is running.');
        }
        throw error;
    }
}

// Check API connection
async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            const statusElement = document.getElementById('apiStatus');
            const dotElement = document.querySelector('.status-dot');
            if (statusElement) {
                statusElement.textContent = 'Connected';
            }
            if (dotElement) {
                dotElement.classList.add('connected');
            }
        } else {
            showConnectionError();
        }
    } catch (error) {
        showConnectionError();
    }
}

function showConnectionError() {
    const statusElement = document.getElementById('apiStatus');
    const dotElement = document.querySelector('.status-dot');
    if (statusElement) {
        statusElement.textContent = 'Disconnected';
    }
    if (dotElement) {
        dotElement.classList.add('error');
        dotElement.classList.remove('connected');
    }
}

// Alias for backward compatibility
const checkHealth = checkConnection;
