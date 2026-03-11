// Application Initialization - Main Entry Point
// This file loads all modular JavaScript files and initializes the application

// Initialize on page load
window.addEventListener('load', async function() {
    await checkAuthentication();
    if (typeof window.checkConnection === 'function') {
        window.checkConnection();
    }
    window.pageFullyLoaded = true;
    
    // Add delay before enabling login to prevent browser auto-submit
    setTimeout(() => {
        window.loginFormReady = true;
        console.log('[APP] Login form ready for user interaction');
    }, 500);
});

window.addEventListener('DOMContentLoaded', () => {
    loadDarkModePreference();
    loadSnippets();
    updateUserInterface();
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Alt+S to stop recording
        if (e.ctrlKey && e.altKey && e.key === 's') {
            e.preventDefault();
            // Check if stopRecording function exists and call it
            if (typeof window.stopRecording === 'function') {
                window.stopRecording();
            }
        }
    });
    
    // Show dashboard by default or load from URL hash
    const hash = window.location.hash.substring(1);
    if (hash) {
        navigateTo(hash);
    }
    // Note: Dashboard will be loaded automatically after login via showMainApp()
    
    // Load test cases to populate dashboard
    loadTestCases();
});

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.remove();
    }
});

// Handle window resize for mobile sidebar
window.addEventListener('resize', function() {
    if (window.innerWidth > 1024) {
        document.querySelector('.sidebar')?.classList.remove('mobile-open');
    }
});

console.log('[APP] Smart Test Generator initialized - Modular architecture loaded');
