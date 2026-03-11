// UI Helper Functions

function showLoading(show) {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.classList.toggle('active', show);
    }
    
    document.querySelectorAll('.btn').forEach(btn => {
        btn.disabled = show;
    });
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--primary);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setPrompt(text) {
    const promptInput = document.getElementById('promptInput');
    if (promptInput) {
        promptInput.value = text;
    }
}

// Safely set element style (handles null elements from dynamic page loading)
function safeSetStyle(elementId, property, value) {
    const element = document.getElementById(elementId);
    if (element && element.style) {
        element.style[property] = value;
    }
}

// Safely set element display style
function safeSetDisplay(elementId, displayValue) {
    safeSetStyle(elementId, 'display', displayValue);
}

// Expose functions to window object
window.showLoading = showLoading;
window.showNotification = showNotification;
window.escapeHtml = escapeHtml;
window.setPrompt = setPrompt;
window.safeSetStyle = safeSetStyle;
window.safeSetDisplay = safeSetDisplay;
