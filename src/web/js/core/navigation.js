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
        'semantic': 'semantic-analysis',
        'testcases': 'test-suite',
        'snippets': 'code-snippets',
        'screenshot': 'screenshot-ai',
        'testBuilder': 'test-builder'
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
        'semantic': 'Semantic Analysis',
        'testcases': 'Test Suite',
        'snippets': 'Code Snippets',
        'screenshot': 'Screenshot AI',
        'testBuilder': 'Test Builder'
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
        // Wait for DOM elements to be available, with retries
        const initDashboard = (retries = 0) => {
            const testsPassed = document.getElementById('testsPassedCount');
            if (!testsPassed && retries < 10) {
                console.log('[Navigation] Dashboard elements not ready, retrying... (' + retries + ')');
                setTimeout(() => initDashboard(retries + 1), 100);
                return;
            }
            
            console.log('[Navigation] Dashboard elements ready, initializing...');
            
            // Reload stats data from localStorage and update the existing window.stats object
            // DON'T create a new object - update the existing reference
            if (typeof window.loadStats === 'function' && window.stats) {
                const freshData = window.loadStats();
                // Update properties on existing object to maintain reference
                window.stats.totalRequests = freshData.totalRequests;
                window.stats.totalTime = freshData.totalTime;
                window.stats.totalTokens = freshData.totalTokens;
                window.stats.testResults = freshData.testResults;
                console.log('[Navigation] 🔄 Synced window.stats with localStorage:', window.stats);
            }
            
            if (typeof window.updateDashboardStats === 'function') {
                window.updateDashboardStats();
            }
            if (typeof window.updateRecentTestResults === 'function') {
                window.updateRecentTestResults();
            }
            if (typeof window.updateActivityTimeline === 'function') {
                window.updateActivityTimeline();
            }
        };
        setTimeout(initDashboard, 50);
    } else if (page === 'semantic') {
        setTimeout(() => refreshSemanticSessions(), 100);
    } else if (page === 'testcases') {
        setTimeout(() => loadTestCases(), 100);
    } else if (page === 'testBuilder') {
        // Initialize Test Builder when navigating to it
        setTimeout(() => {
            if (typeof window.TestBuilder !== 'undefined' && typeof window.TestBuilder.init === 'function') {
                console.log('[Navigation] Initializing Test Builder');
                window.TestBuilder.init();
            }
        }, 100);
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

// Sidebar toggle - now handled by sidebar-collapse-simple.js
// This function is overridden by the new implementation
function toggleSidebar() {
    console.log('[NAVIGATION] toggleSidebar placeholder - will be overridden');
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
