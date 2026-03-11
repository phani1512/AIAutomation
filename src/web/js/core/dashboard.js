// Dashboard Statistics and UI

// Load stats from localStorage or initialize with defaults
function loadStats() {
    const savedStats = localStorage.getItem('dashboardStats');
    if (savedStats) {
        try {
            const parsed = JSON.parse(savedStats);
            return {
                totalRequests: parsed.totalRequests || 0,
                totalTime: parsed.totalTime || 0,
                totalTokens: parsed.totalTokens || 0,
                testResults: parsed.testResults || []
            };
        } catch (e) {
            console.error('[Dashboard] Error loading stats:', e);
            return {
                totalRequests: 0,
                totalTime: 0,
                totalTokens: 0,
                testResults: []
            };
        }
    }
    return {
        totalRequests: 0,
        totalTime: 0,
        totalTokens: 0,
        testResults: []
    };
}

// Save stats to localStorage
function saveStats() {
    try {
        localStorage.setItem('dashboardStats', JSON.stringify(stats));
    } catch (e) {
        console.error('[Dashboard] Error saving stats:', e);
    }
}

const stats = loadStats();

function updateDashboardStats() {
    const totalRequestsEl = document.getElementById('dashboardTotalRequests');
    const avgTimeEl = document.getElementById('dashboardAvgTime');
    const passedEl = document.getElementById('testsPassedCount');
    const failedEl = document.getElementById('testsFailedCount');
    
    if (totalRequestsEl) {
        totalRequestsEl.textContent = stats.totalRequests;
    }
    
    if (avgTimeEl) {
        avgTimeEl.textContent = stats.totalTime > 0 ? 
            Math.round(stats.totalTime / stats.totalRequests) + 'ms' : '0ms';
    }
    
    const passed = stats.testResults.filter(r => r.status === 'passed').length;
    const failed = stats.testResults.filter(r => r.status === 'failed').length;
    
    if (passedEl) {
        passedEl.textContent = passed;
    }
    
    if (failedEl) {
        failedEl.textContent = failed;
    }
}

function addTestResult(name, status, duration, details = '') {
    const result = {
        name: name,
        status: status,
        duration: duration,
        details: details,
        timestamp: new Date().toLocaleString()
    };
    
    stats.testResults.unshift(result);
    if (stats.testResults.length > 10) {
        stats.testResults = stats.testResults.slice(0, 10);
    }
    
    // Save to localStorage
    saveStats();
    
    const passed = stats.testResults.filter(r => r.status === 'passed').length;
    const failed = stats.testResults.filter(r => r.status === 'failed').length;
    
    const passedCountEl = document.getElementById('testsPassedCount');
    const failedCountEl = document.getElementById('testsFailedCount');
    
    if (passedCountEl) passedCountEl.textContent = passed;
    if (failedCountEl) failedCountEl.textContent = failed;
    
    updateRecentTestResults();
    updateActivityTimeline();
}

function updateRecentTestResults() {
    const container = document.getElementById('recentTestResults');
    if (!container) return;
    
    if (stats.testResults.length === 0) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">No test results yet. Start generating and running tests!</div>';
        return;
    }
    
    container.innerHTML = stats.testResults.map(result => `
        <div class="test-result-item ${result.status}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span style="font-size: 1.2em;">${result.status === 'passed' ? '✅' : result.status === 'failed' ? '❌' : '⏸️'}</span>
                        <strong style="color: var(--text-primary);">${result.name}</strong>
                    </div>
                    ${result.details ? `<p style="color: var(--text-secondary); font-size: 0.9em; margin: 0 0 8px 0;">${result.details}</p>` : ''}
                    <div style="display: flex; gap: 15px; font-size: 0.85em; color: var(--text-tertiary);">
                        <span>⏱️ ${result.duration}ms</span>
                        <span>📅 ${result.timestamp}</span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function updateActivityTimeline() {
    const container = document.getElementById('activityTimeline');
    if (!container) return;
    
    if (stats.testResults.length === 0) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Your activity will appear here</div>';
        return;
    }
    
    container.innerHTML = stats.testResults.slice(0, 5).map((result, index) => `
        <div style="display: flex; gap: 15px; margin-bottom: 20px; ${index < stats.testResults.length - 1 ? 'padding-bottom: 20px; border-bottom: 1px solid var(--border-color);' : ''}">
            <div style="font-size: 2em; opacity: 0.5;">${result.status === 'passed' ? '✅' : result.status === 'failed' ? '❌' : '⏸️'}</div>
            <div style="flex: 1;">
                <strong style="color: var(--text-primary);">${result.name}</strong>
                <div style="color: var(--text-secondary); font-size: 0.9em; margin-top: 4px;">${result.timestamp}</div>
            </div>
            <div style="color: var(--text-tertiary); font-size: 0.9em;">${result.duration}ms</div>
        </div>
    `).join('');
}

// Expose functions and stats to window object
window.stats = stats;
window.updateDashboardStats = updateDashboardStats;
window.addTestResult = addTestResult;
window.updateRecentTestResults = updateRecentTestResults;
window.updateActivityTimeline = updateActivityTimeline;
window.saveStats = saveStats;

// Initialize dashboard on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            updateDashboardStats();
            updateRecentTestResults();
            updateActivityTimeline();
        }, 100);
    });
} else {
    // DOM already loaded
    setTimeout(() => {
        updateDashboardStats();
        updateRecentTestResults();
        updateActivityTimeline();
    }, 100);
}
