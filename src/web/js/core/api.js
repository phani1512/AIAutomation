// API Configuration and Helper Functions
// API_URL is defined in index-new.html inline script

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
            document.getElementById('statusDot').classList.add('connected');
            document.getElementById('statusText').textContent = 'Connected to SLM API';
            document.getElementById('modelInfo').textContent = `Model: ${data.model}`;
        } else {
            showConnectionError();
        }
    } catch (error) {
        showConnectionError();
    }
}

// Alias for backward compatibility
const checkHealth = checkConnection;

function showConnectionError() {
    document.getElementById('statusDot').classList.add('error');
    document.getElementById('statusText').textContent = 'API Server Not Running';
    document.getElementById('modelInfo').textContent = 'Please start: python src/main/python/api_server_modular.py';
}

// Expose functions and constants to window object
window.API_URL = API_URL;
window.authenticatedFetch = authenticatedFetch;
window.checkConnection = checkConnection;
window.checkHealth = checkHealth;
window.showConnectionError = showConnectionError;
