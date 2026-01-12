// Navigation Functions

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
    
    // Update page title in header
    const pageTitles = {
        'dashboard': 'Dashboard',
        'generate': 'Generate Code',
        'locator': 'Locator Suggestions',
        'action': 'Action Suggestions',
        'recorder': 'Test Recorder',
        'browser': 'Browser Control',
        'semantic': 'Semantic Analysis',
        'testcases': 'Test Suite',
        'snippets': 'Code Snippets'
    };
    const titleElement = document.getElementById('currentPageTitle');
    if (titleElement && pageTitles[page]) {
        titleElement.textContent = pageTitles[page];
    }
    
    // Update URL hash
    window.location.hash = page;
    
    // Load data for specific pages
    if (page === 'semantic') {
        refreshSemanticSessions();
    } else if (page === 'testcases') {
        loadTestCases();
    }
    
    // Close sidebar on mobile
    if (window.innerWidth <= 1024) {
        document.querySelector('.sidebar').classList.remove('mobile-open');
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('mobile-open');
}

// Dark mode toggle
function toggleDarkMode() {
    const body = document.body;
    const slider = document.getElementById('darkModeSlider');
    
    body.classList.toggle('dark-mode');
    
    if (body.classList.contains('dark-mode')) {
        slider.textContent = '☀️';
        localStorage.setItem('darkMode', 'enabled');
    } else {
        slider.textContent = '🌙';
        localStorage.setItem('darkMode', 'disabled');
    }
}

function loadDarkModePreference() {
    const darkMode = localStorage.getItem('darkMode');
    const slider = document.getElementById('darkModeSlider');
    
    if (darkMode === 'enabled') {
        document.body.classList.add('dark-mode');
        if (slider) slider.textContent = '☀️';
    } else {
        if (slider) slider.textContent = '🌙';
    }
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.classList.add('active');
    
    // Reload snippets when switching to snippets tab
    if (tabName === 'snippets' && typeof loadSnippets === 'function') {
        loadSnippets();
    }
}

// Expose functions to global window object for inline onclick handlers
window.navigateTo = navigateTo;
window.toggleSidebar = toggleSidebar;
window.toggleDarkMode = toggleDarkMode;
window.switchTab = switchTab;
