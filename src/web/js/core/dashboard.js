// Dashboard Statistics and UI

const stats = {
    totalRequests: 0,
    totalTime: 0,
    totalTokens: 0,
    testResults: []
};

function updateDashboardStats() {
    document.getElementById('dashboardTotalRequests').textContent = stats.totalRequests;
    document.getElementById('dashboardAvgTime').textContent = stats.totalTime > 0 ? 
        Math.round(stats.totalTime / stats.totalRequests) + 'ms' : '0ms';
    
    const passed = stats.testResults.filter(r => r.status === 'passed').length;
    const failed = stats.testResults.filter(r => r.status === 'failed').length;
    
    document.getElementById('testsPassedCount').textContent = passed;
    document.getElementById('testsFailedCount').textContent = failed;
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
    
    const passed = stats.testResults.filter(r => r.status === 'passed').length;
    const failed = stats.testResults.filter(r => r.status === 'failed').length;
    
    document.getElementById('testsPassedCount').textContent = passed;
    document.getElementById('testsFailedCount').textContent = failed;
    
    updateRecentTestResults();
    updateActivityTimeline();
}

function updateRecentTestResults() {
    const container = document.getElementById('recentTestResults');
    
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
