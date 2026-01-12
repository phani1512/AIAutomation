// Dashboard Functions

let stats = {
    testsRun: 0,
    testsPassed: 0,
    testsFailed: 0,
    testResults: []
};

// AI Model metrics
let aiMetrics = {
    totalRequests: 0,
    totalTokens: 0,
    totalResponseTime: 0,
    avgResponseTime: 0
};

function updateAIMetrics(tokens, responseTimeMs) {
    aiMetrics.totalRequests++;
    aiMetrics.totalTokens += tokens;
    aiMetrics.totalResponseTime += responseTimeMs;
    aiMetrics.avgResponseTime = Math.round(aiMetrics.totalResponseTime / aiMetrics.totalRequests);
    
    // Update UI
    const totalRequestsEl = document.getElementById('totalRequests');
    const tokensGeneratedEl = document.getElementById('tokensGenerated');
    const avgTimeEl = document.getElementById('avgTime');
    
    if (totalRequestsEl) totalRequestsEl.textContent = aiMetrics.totalRequests;
    if (tokensGeneratedEl) tokensGeneratedEl.textContent = aiMetrics.totalTokens;
    if (avgTimeEl) avgTimeEl.textContent = aiMetrics.avgResponseTime + 'ms';
    
    console.log('[METRICS] Updated:', aiMetrics);
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
                        <strong style="color: var(--text-primary);">${result.name}</strong>
                        <span class="badge ${result.status === 'passed' ? 'success' : result.status === 'failed' ? 'error' : 'warning'}">
                            ${result.status.toUpperCase()}
                        </span>
                    </div>
                    <div style="font-size: 0.85em; color: var(--text-secondary);">
                        ${result.timestamp} • ${result.duration}
                    </div>
                    ${result.details ? `<div style="margin-top: 5px; font-size: 0.85em; color: var(--text-tertiary);">${result.details}</div>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function updateActivityTimeline() {
    const container = document.getElementById('activityTimeline');
    
    if (stats.testResults.length === 0) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">No recent activity</div>';
        return;
    }
    
    container.innerHTML = stats.testResults.slice(0, 5).map(result => `
        <div style="padding: 12px; border-left: 3px solid ${result.status === 'passed' ? 'var(--success)' : 'var(--error)'}; margin-bottom: 10px; background: var(--bg-secondary); border-radius: 4px;">
            <div style="font-weight: 500; color: var(--text-primary);">${result.name}</div>
            <div style="font-size: 0.85em; color: var(--text-secondary); margin-top: 4px;">${result.timestamp}</div>
        </div>
    `).join('');
}

function updateDashboardStats() {
    const testsRunCount = document.getElementById('testsRunCount');
    const testsPassedCount = document.getElementById('testsPassedCount');
    const testsFailedCount = document.getElementById('testsFailedCount');
    
    if (testsRunCount) testsRunCount.textContent = stats.testsRun;
    if (testsPassedCount) testsPassedCount.textContent = stats.testsPassed;
    if (testsFailedCount) testsFailedCount.textContent = stats.testsFailed;
}

function updateDashboardFromTestSuite(sessions) {
    if (!sessions || sessions.length === 0) return;
    
    stats.testsRun = sessions.length;
    updateDashboardStats();
}

function updateDashboardWithExecutionResults(suiteData) {
    if (!suiteData || !suiteData.results) return;
    
    suiteData.results.forEach(result => {
        addTestResult(
            result.test_name,
            result.status,
            `${result.duration}s`,
            result.error || ''
        );
    });
    
    stats.testsRun = suiteData.total_tests;
    stats.testsPassed = suiteData.passed;
    stats.testsFailed = suiteData.failed;
    
    updateDashboardStats();
}

async function checkConnection() {
    try {
        console.log('[CONNECTION] Checking API server at:', window.API_URL);
        const response = await fetch(`${window.API_URL}/health`);
        const data = await response.json();
        
        console.log('[CONNECTION] Health check response:', data);
        
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const modelInfo = document.getElementById('modelInfo');
        
        if (statusDot) statusDot.className = 'status-dot connected';
        if (statusText) statusText.textContent = 'Connected to SLM';
        if (modelInfo) modelInfo.textContent = `Model: ${data.version || data.model_version || 'v3.0'}`;
        
        console.log('[CONNECTION] Successfully connected');
    } catch (error) {
        console.error('[CONNECTION] Failed:', error);
        showError();
    }
}

function showError() {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (statusDot) statusDot.className = 'status-dot error';
    if (statusText) statusText.textContent = 'SLM Server Offline';
}

// Expose functions to global scope for HTML onclick handlers
window.stats = stats;
window.aiMetrics = aiMetrics;
window.updateAIMetrics = updateAIMetrics;
window.addTestResult = addTestResult;
window.updateRecentTestResults = updateRecentTestResults;
window.updateActivityTimeline = updateActivityTimeline;
window.updateDashboardStats = updateDashboardStats;
window.updateDashboardFromTestSuite = updateDashboardFromTestSuite;
window.updateDashboardWithExecutionResults = updateDashboardWithExecutionResults;
window.checkConnection = checkConnection;
window.showError = showError;

