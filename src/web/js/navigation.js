// Navigation and UI Functions

function navigateTo(page) {
    // Hide all pages
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.remove('active');
        section.style.display = '';
    });
    
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected page
    const pageId = page + 'Page';
    const pageElement = document.getElementById(pageId);
    if (pageElement) {
        pageElement.classList.add('active');
    }
    
    // Highlight active nav item
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        const onClick = item.getAttribute('onclick');
        if (onClick && onClick.includes(`'${page}'`)) {
            item.classList.add('active');
        }
    });
    
    // Page-specific initialization
    if (page === 'semantic') {
        refreshSemanticSessions();
    } else if (page === 'testcases') {
        loadTestCases();
    } else if (page === 'dashboard') {
        // Update dashboard stats when navigating to dashboard
        if (typeof window.updateDashboardStats === 'function') {
            window.updateDashboardStats();
        }
        if (typeof window.updateRecentTestResults === 'function') {
            window.updateRecentTestResults();
        }
        if (typeof window.updateActivityTimeline === 'function') {
            window.updateActivityTimeline();
        }
    }
    
    // Update URL hash
    window.location.hash = page;
    
    // Close sidebar on mobile
    if (window.innerWidth <= 1024) {
        document.querySelector('.sidebar').classList.remove('mobile-open');
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('mobile-open');
}

function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle('dark-mode');
    
    const isDark = body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    
    const slider = document.getElementById('darkModeSlider');
    if (slider) {
        slider.textContent = isDark ? '🌙' : '☀️';
    }
}

function loadDarkModePreference() {
    const isDark = localStorage.getItem('darkMode') === 'true';
    if (isDark) {
        document.body.classList.add('dark-mode');
        const slider = document.getElementById('darkModeSlider');
        if (slider) {
            slider.textContent = '🌙';
        }
    }
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        font-weight: 500;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showLoading(show) {
    const loading = document.querySelector('.loading');
    if (loading) {
        loading.classList.toggle('active', show);
    }
}

// Expose functions to global scope for HTML onclick handlers
window.navigateTo = navigateTo;
window.toggleSidebar = toggleSidebar;
window.toggleDarkMode = toggleDarkMode;
window.loadDarkModePreference = loadDarkModePreference;
window.showNotification = showNotification;
window.showLoading = showLoading;
