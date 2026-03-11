// Navigation Functions

// Page loader cache
const pageCache = {};

async function loadPage(pageName) {
    // Check cache first
    if (pageCache[pageName]) {
        console.log(`[PAGE LOADER] Loading ${pageName} from cache`);
        return pageCache[pageName];
    }
    
    try {
        console.log(`[PAGE LOADER] Fetching ${pageName} from server`);
        const response = await fetch(`/web/pages/${pageName}.html`);
        if (!response.ok) {
            throw new Error(`Failed to load page: ${response.status}`);
        }
        const html = await response.text();
        pageCache[pageName] = html;
        return html;
    } catch (error) {
        console.error(`[PAGE LOADER] Error loading ${pageName}:`, error);
        return `<div style="padding: 40px; text-align: center; color: var(--error);">
            <h3>⚠️ Failed to load page</h3>
            <p>Could not load ${pageName}. Please check your connection and try again.</p>
        </div>`;
    }
}

async function navigateTo(page) {
    // Page name mapping
    const pageFileMap = {
        'dashboard': 'dashboard',
        'generate': 'generate-code',
        'locator': 'locator-suggestions',
        'action': 'action-suggestions',
        'recorder': 'test-recorder',
        'browser': 'browser-control',
        'semantic': 'semantic-analysis',
        'testcases': 'test-suite',
        'snippets': 'code-snippets',
        'screenshot': 'screenshot-ai',
        'testrunner': 'test-runner'
    };
    
    const pageFileName = pageFileMap[page];
    if (!pageFileName) {
        console.error(`[NAVIGATION] Unknown page: ${page}`);
        return;
    }
    
    // Load page content
    const pageContent = await loadPage(pageFileName);
    
    // Get or create page container
    const pageContainerId = 'pageContentContainer';
    let container = document.getElementById(pageContainerId);
    if (!container) {
        // Create container if it doesn't exist
        const mainContent = document.querySelector('.main-content');
        container = document.createElement('div');
        container.id = pageContainerId;
        mainContent.appendChild(container);
    }
    
    // Insert page content
    container.innerHTML = pageContent;
    
    // Hide all pages (legacy cleanup)
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
    });
    
    // Show the newly loaded page
    const loadedPage = container.querySelector('.page-section');
    if (loadedPage) {
        loadedPage.classList.add('active');
        loadedPage.style.display = 'block';
    }
    
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
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
        'snippets': 'Code Snippets',
        'screenshot': 'Screenshot AI',
        'testrunner': 'Test Runner'
    };
    const titleElement = document.getElementById('currentPageTitle');
    if (titleElement && pageTitles[page]) {
        titleElement.textContent = pageTitles[page];
    }
    
    // Update URL hash
    window.location.hash = page;
    
    // Load data for specific pages
    if (page === 'dashboard') {
        // Initialize dashboard stats when navigating to dashboard
        setTimeout(() => {
            if (typeof window.updateDashboardStats === 'function') {
                window.updateDashboardStats();
            }
            if (typeof window.updateRecentTestResults === 'function') {
                window.updateRecentTestResults();
            }
            if (typeof window.updateActivityTimeline === 'function') {
                window.updateActivityTimeline();
            }
        }, 100);
    } else if (page === 'semantic') {
        setTimeout(() => refreshSemanticSessions(), 100);
    } else if (page === 'testcases') {
        setTimeout(() => loadTestCases(), 100);
    }
    
    // Re-apply syntax highlighting if Prism is available
    if (window.Prism) {
        Prism.highlightAll();
    }
    
    // Close sidebar on mobile
    if (window.innerWidth <= 1024) {
        document.querySelector('.sidebar').classList.remove('mobile-open');
    }
    
    console.log(`[NAVIGATION] Navigated to ${page} (${pageFileName})`);
}

function toggleSidebar() {
    console.log('[NAVIGATION] toggleSidebar called');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    const toggleIcon = document.getElementById('toggleIcon');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
    
    // Change arrow direction
    if (sidebar.classList.contains('collapsed')) {
        toggleIcon.textContent = '▶'; // Right arrow when collapsed
    } else {
        toggleIcon.textContent = '◀'; // Left arrow when expanded
    }
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
window.loadDarkModePreference = loadDarkModePreference;
