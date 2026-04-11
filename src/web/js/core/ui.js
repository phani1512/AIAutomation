// UI Helper Functions

function showLoading(show, message = 'Loading...', showCancelButton = false) {
    const loadingElement = document.getElementById('loading');
    const overlay = document.getElementById('loadingOverlay');
    const messageDiv = document.getElementById('loadingMessage');
    const cancelBtn = document.getElementById('cancelExecutionBtn');
    
    if (show) {
        // Show loading
        if (loadingElement) {
            loadingElement.style.display = 'flex';
            loadingElement.classList.add('active');
        }
        
        // Show overlay
        if (overlay) {
            overlay.style.display = 'block';
        }
        
        // Set custom message
        if (messageDiv) {
            messageDiv.textContent = message;
        }
        
        // Show/hide cancel button
        if (cancelBtn) {
            cancelBtn.style.display = showCancelButton ? 'block' : 'none';
            
            // Setup cancel button event listener
            if (showCancelButton) {
                const newCancelBtn = cancelBtn.cloneNode(true);
                cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
                newCancelBtn.addEventListener('click', () => {
                    console.log('[UI] Cancel button clicked');
                    hideLoading();
                    showNotification('⚠️ Operation cancelled', 'warning');
                });
            }
        }
        
        // Disable buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.disabled = true;
        });
    } else {
        // Hide loading
        hideLoading();
    }
}

function hideLoading() {
    const loadingElement = document.getElementById('loading');
    const overlay = document.getElementById('loadingOverlay');
    const cancelBtn = document.getElementById('cancelExecutionBtn');
    
    if (loadingElement) {
        loadingElement.style.display = 'none';
        loadingElement.classList.remove('active');
    }
    
    if (overlay) {
        overlay.style.display = 'none';
    }
    
    if (cancelBtn) {
        cancelBtn.style.display = 'none';
    }
    
    // Re-enable buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.disabled = false;
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    
    // Color based on type
    let bgColor = 'var(--primary)';
    if (type === 'success') bgColor = '#10b981';
    else if (type === 'error') bgColor = '#ef4444';
    else if (type === 'warning') bgColor = '#f59e0b';
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
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
    }, 3000);
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
window.hideLoading = hideLoading;
window.showNotification = showNotification;
window.escapeHtml = escapeHtml;
window.setPrompt = setPrompt;
window.safeSetStyle = safeSetStyle;
window.safeSetDisplay = safeSetDisplay;
