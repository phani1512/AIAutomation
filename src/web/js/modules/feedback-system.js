/**
 * Feedback System Module
 * 
 * Collects user feedback on AI suggestions to improve ML model.
 * - Rate suggestions (useful/not relevant)
 * - Report bugs found
 * - Submit new scenarios
 */

class FeedbackManager {
    constructor() {
        this.currentTestId = null;
        this.selectedSuggestions = new Set();
        this.feedbackQueue = [];
    }

    /**
     * Show rating buttons on a suggestion
     */
    renderRatingButtons(suggestionId, scenarioKey, testCaseId) {
        return `
            <div class="feedback-buttons" style="display: flex; gap: 8px; align-items: center;">
                <button 
                    class="feedback-btn feedback-useful"
                    onclick="feedbackManager.rateSuggestion('${testCaseId}', '${scenarioKey}', 'useful', '${suggestionId}')"
                    style="
                        background: none;
                        border: 1px solid #10B981;
                        color: #10B981;
                        padding: 4px 8px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 11px;
                        display: flex;
                        align-items: center;
                        gap: 4px;
                        transition: all 0.2s;
                    "
                    onmouseover="this.style.background='#10B98110'; this.style.transform='scale(1.05)';"
                    onmouseout="this.style.background='none'; this.style.transform='scale(1)';"
                    title="This suggestion is useful"
                >
                    <span style="font-size: 14px;">👍</span>
                    <span>Useful</span>
                </button>
                <button 
                    class="feedback-btn feedback-not-relevant"
                    onclick="feedbackManager.rateSuggestion('${testCaseId}', '${scenarioKey}', 'not_relevant', '${suggestionId}')"
                    style="
                        background: none;
                        border: 1px solid #EF4444;
                        color: #EF4444;
                        padding: 4px 8px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 11px;
                        display: flex;
                        align-items: center;
                        gap: 4px;
                        transition: all 0.2s;
                    "
                    onmouseover="this.style.background='#EF444410'; this.style.transform='scale(1.05)';"
                    onmouseout="this.style.background='none'; this.style.transform='scale(1)';"
                    title="This suggestion is not relevant"
                >
                    <span style="font-size: 14px;">👎</span>
                    <span>Not Relevant</span>
                </button>
            </div>
        `;
    }

    /**
     * Rate a suggestion
     */
    async rateSuggestion(testCaseId, scenarioKey, rating, suggestionId) {
        try {
            console.log('[FEEDBACK] Rating suggestion:', scenarioKey, '=', rating);
            
            const response = await fetch(`${API_URL}/semantic/feedback/rate-scenario`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    test_case_id: testCaseId,
                    scenario_key: scenarioKey,
                    rating: rating,
                    features: {}
                })
            });

            const data = await response.json();
            
            if (data.success) {
                console.log('[FEEDBACK] ✓ Rating recorded');
                
                // Visual feedback
                const suggestionElement = document.getElementById(suggestionId);
                if (suggestionElement) {
                    const color = rating === 'useful' ? '#10B981' : '#EF4444';
                    suggestionElement.style.borderColor = color;
                    suggestionElement.style.background = `${color}10`;
                    
                    // Disable rating buttons
                    const feedbackButtons = suggestionElement.querySelector('.feedback-buttons');
                    if (feedbackButtons) {
                        feedbackButtons.innerHTML = `
                            <span style="font-size: 11px; color: ${color}; font-weight: 500;">
                                ${rating === 'useful' ? '✓ Marked as useful' : '✓ Marked as not relevant'}
                            </span>
                        `;
                    }
                }
                
                this.showToast(rating === 'useful' ? 'Thanks! 👍' : 'Thanks for feedback 👎', 'success');
            } else {
                console.error('[FEEDBACK] Failed:', data.error);
                this.showToast('Failed to save feedback', 'error');
            }
            
        } catch (error) {
            console.error('[FEEDBACK] Error:', error);
            this.showToast('Error saving feedback', 'error');
        }
    }

    /**
     * Show bug report modal after test execution
     */
    showBugReportModal(testCaseId, scenariosUsed) {
        const modal = document.createElement('div');
        modal.id = 'bugReportModal';
        modal.className = 'modal-overlay';
        modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000;';
        
        modal.innerHTML = `
            <div style="
                background: var(--bg-primary, white);
                border-radius: 12px;
                padding: 24px;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            ">
                <h3 style="margin: 0 0 16px 0; color: var(--text-primary); font-size: 20px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 24px;">🐛</span>
                    Test Execution Feedback
                </h3>
                
                <div style="margin-bottom: 20px;">
                    <p style="color: var(--text-secondary); font-size: 14px; margin: 0;">
                        Did this test find any bugs or issues?
                    </p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-secondary); border-radius: 8px; cursor: pointer; margin-bottom: 8px;">
                        <input type="radio" name="found_bugs" value="yes" style="width: 18px; height: 18px;">
                        <div>
                            <div style="font-weight: 600; color: var(--text-primary);">✅ Yes, found bugs</div>
                            <div style="font-size: 12px; color: var(--text-secondary);">This test caught issues that need fixing</div>
                        </div>
                    </label>
                    
                    <label style="display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-secondary); border-radius: 8px; cursor: pointer;">
                        <input type="radio" name="found_bugs" value="no" style="width: 18px; height: 18px;">
                        <div>
                            <div style="font-weight: 600; color: var(--text-primary);">⭕ No bugs found</div>
                            <div style="font-size: 12px; color: var(--text-secondary);">Test passed without issues</div>
                        </div>
                    </label>
                </div>
                
                <div id="bugTypeSection" style="display: none; margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary); font-size: 14px;">
                        What type of bugs? (Select all that apply)
                    </label>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; padding: 8px; cursor: pointer;">
                            <input type="checkbox" value="validation" style="width: 16px; height: 16px;">
                            <span style="font-size: 13px; color: var(--text-primary);">Validation Error</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; padding: 8px; cursor: pointer;">
                            <input type="checkbox" value="security" style="width: 16px; height: 16px;">
                            <span style="font-size: 13px; color: var(--text-primary);">Security Issue</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; padding: 8px; cursor: pointer;">
                            <input type="checkbox" value="ui" style="width: 16px; height: 16px;">
                            <span style="font-size: 13px; color: var(--text-primary);">UI/Display Issue</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; padding: 8px; cursor: pointer;">
                            <input type="checkbox" value="crash" style="width: 16px; height: 16px;">
                            <span style="font-size: 13px; color: var(--text-primary);">Crash/Error</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; padding: 8px; cursor: pointer;">
                            <input type="checkbox" value="performance" style="width: 16px; height: 16px;">
                            <span style="font-size: 13px; color: var(--text-primary);">Performance Issue</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; padding: 8px; cursor: pointer;">
                            <input type="checkbox" value="other" style="width: 16px; height: 16px;">
                            <span style="font-size: 13px; color: var(--text-primary);">Other</span>
                        </label>
                    </div>
                </div>
                
                <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px;">
                    <button 
                        onclick="document.getElementById('bugReportModal').remove();"
                        style="
                            padding: 10px 20px;
                            background: var(--bg-secondary);
                            color: var(--text-primary);
                            border: 1px solid var(--border-color);
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 500;
                        "
                    >
                        Skip
                    </button>
                    <button 
                        onclick="feedbackManager.submitBugReport('${testCaseId}', ${JSON.stringify(scenariosUsed).replace(/"/g, '&quot;')})"
                        style="
                            padding: 10px 20px;
                            background: #7C3AED;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 500;
                        "
                    >
                        Submit Feedback
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show/hide bug type section based on selection
        const bugRadios = modal.querySelectorAll('input[name="found_bugs"]');
        const bugTypeSection = modal.querySelector('#bugTypeSection');
        
        bugRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.value === 'yes') {
                    bugTypeSection.style.display = 'block';
                } else {
                    bugTypeSection.style.display = 'none';
                }
            });
        });
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    /**
     * Submit bug report
     */
    async submitBugReport(testCaseId, scenariosUsed) {
        const modal = document.getElementById('bugReportModal');
        const foundBugs = modal.querySelector('input[name="found_bugs"]:checked');
        
        if (!foundBugs) {
            this.showToast('Please select whether bugs were found', 'warning');
            return;
        }
        
        const foundBugsValue = foundBugs.value === 'yes';
        const bugTypes = [];
        
        if (foundBugsValue) {
            const bugTypeCheckboxes = modal.querySelectorAll('#bugTypeSection input[type="checkbox"]:checked');
            bugTypeCheckboxes.forEach(cb => bugTypes.push(cb.value));
        }
        
        try {
            console.log('[FEEDBACK] Submitting bug report:', { foundBugs: foundBugsValue, bugTypes });
            
            const response = await fetch(`${API_URL}/semantic/feedback/test-result`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    test_case_id: testCaseId,
                    scenarios_used: scenariosUsed,
                    found_bugs: foundBugsValue,
                    bug_types: bugTypes
                })
            });

            const data = await response.json();
            
            if (data.success) {
                console.log('[FEEDBACK] ✓ Bug report submitted');
                this.showToast('Thank you for your feedback! 🙏', 'success');
                modal.remove();
            } else {
                console.error('[FEEDBACK] Failed:', data.error);
                this.showToast('Failed to submit feedback', 'error');
            }
            
        } catch (error) {
            console.error('[FEEDBACK] Error:', error);
            this.showToast('Error submitting feedback', 'error');
        }
    }

    /**
     * Show feedback dashboard
     */
    async showFeedbackDashboard() {
        try {
            console.log('[FEEDBACK] Loading dashboard...');
            
            const response = await fetch(`${API_URL}/semantic/feedback/summary`);
            const data = await response.json();
            
            if (!data.success) {
                this.showToast('Failed to load feedback data', 'error');
                return;
            }
            
            const summary = data.summary;
            
            const modal = document.createElement('div');
            modal.id = 'feedbackDashboard';
            modal.className = 'modal-overlay';
            modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000; overflow-y: auto;';
            
            modal.innerHTML = `
                <div style="
                    background: var(--bg-primary, white);
                    border-radius: 12px;
                    padding: 32px;
                    max-width: 800px;
                    width: 90%;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    margin: 20px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                        <h2 style="margin: 0; color: var(--text-primary); font-size: 24px; display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 32px;">📊</span>
                            Feedback Dashboard
                        </h2>
                        <button 
                            onclick="document.getElementById('feedbackDashboard').remove();"
                            style="
                                background: none;
                                border: none;
                                font-size: 24px;
                                cursor: pointer;
                                color: var(--text-secondary);
                                padding: 4px 8px;
                            "
                        >✕</button>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px;">
                        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 20px; border-radius: 12px; color: white;">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Total Ratings</div>
                            <div style="font-size: 36px; font-weight: 700;">${summary.total_ratings || 0}</div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); padding: 20px; border-radius: 12px; color: white;">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Useful %</div>
                            <div style="font-size: 36px; font-weight: 700;">${Math.round(summary.useful_percentage || 0)}%</div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); padding: 20px; border-radius: 12px; color: white;">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Test Results</div>
                            <div style="font-size: 36px; font-weight: 700;">${summary.total_test_results || 0}</div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); padding: 20px; border-radius: 12px; color: white;">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">User Suggestions</div>
                            <div style="font-size: 36px; font-weight: 700;">${summary.total_user_suggestions || 0}</div>
                        </div>
                    </div>
                    
                    <div style="background: var(--bg-secondary); padding: 20px; border-radius: 12px; margin-bottom: 24px;">
                        <h3 style="margin: 0 0 16px 0; color: var(--text-primary); font-size: 18px;">Rating Distribution</h3>
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            ${this.renderProgressBar('Useful', summary.rating_distribution?.useful || 0, summary.total_ratings || 1, '#10B981')}
                            ${this.renderProgressBar('Not Relevant', summary.rating_distribution?.not_relevant || 0, summary.total_ratings || 1, '#EF4444')}
                            ${this.renderProgressBar('Already Exists', summary.rating_distribution?.already_exists || 0, summary.total_ratings || 1, '#F59E0B')}
                        </div>
                    </div>
                    
                    <div style="font-size: 12px; color: var(--text-secondary); text-align: center;">
                        Last updated: ${summary.last_updated ? new Date(summary.last_updated).toLocaleString() : 'Never'}
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Close on outside click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
            
        } catch (error) {
            console.error('[FEEDBACK] Error loading dashboard:', error);
            this.showToast('Error loading feedback dashboard', 'error');
        }
    }

    /**
     * Render progress bar for dashboard
     */
    renderProgressBar(label, value, total, color) {
        const percentage = total > 0 ? (value / total * 100) : 0;
        return `
            <div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-size: 13px; color: var(--text-primary); font-weight: 500;">${label}</span>
                    <span style="font-size: 13px; color: var(--text-secondary);">${value} (${Math.round(percentage)}%)</span>
                </div>
                <div style="background: rgba(0,0,0,0.1); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: ${color}; height: 100%; width: ${percentage}%; transition: width 0.3s;"></div>
                </div>
            </div>
        `;
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            warning: '#F59E0B',
            info: '#3B82F6'
        };
        
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: ${colors[type]};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10001;
            font-size: 14px;
            font-weight: 500;
            animation: slideIn 0.3s ease-out;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Global instance
window.feedbackManager = new FeedbackManager();

console.log('[FEEDBACK] Feedback system loaded');
