/**
 * Self-Healing UI Components
 * Handles visual feedback and approval workflow for advanced self-healing (v2)
 */

// API_URL is already declared globally in index-new.html

/**
 * Show healing notification when an element is healed
 * @param {Object} healingData - Healing event data with confidence score
 */
function showHealingNotification(healingData) {
    const {
        healed,
        confidence,
        original_locator,
        working_locator,
        requires_approval,
        healing_event
    } = healingData;
    
    if (!healed) return;
    
    const confidencePct = Math.round(confidence * 100);
    const confidenceLevel = getConfidenceLevel(confidence);
    
    // Get or create notification container
    let container = document.getElementById('healingNotifications');
    if (!container) {
        container = document.createElement('div');
        container.id = 'healingNotifications';
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `healing-notification ${confidenceLevel}`;
    notification.style.cssText = `
        background: white;
        border-left: 4px solid ${getConfidenceColor(confidence)};
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: start; gap: 12px;">
            <div style="font-size: 24px;">🔧</div>
            <div style="flex: 1;">
                <div style="font-weight: bold; margin-bottom: 4px; color: #1f2937;">
                    Element Healed
                </div>
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 12px;">
                    <div><strong>Strategy:</strong> ${healing_event?.strategy || 'Unknown'}</div>
                    <div style="margin-top: 4px;"><strong>Confidence:</strong> 
                        <span style="color: ${getConfidenceColor(confidence)}; font-weight: bold;">
                            ${confidencePct}% (${confidenceLevel})
                        </span>
                    </div>
                </div>
                
                <div style="margin-bottom: 12px;">
                    <details style="cursor: pointer;">
                        <summary style="color: #6b7280; font-size: 12px; user-select: none;">
                            View Details
                        </summary>
                        <div style="margin-top: 8px; padding: 8px; background: #f9fafb; border-radius: 4px; font-size: 11px; font-family: monospace;">
                            <div style="margin-bottom: 4px;"><strong>Original:</strong></div>
                            <div style="color: #ef4444; margin-bottom: 8px; word-break: break-all;">
                                ${escapeHtml(original_locator || 'N/A')}
                            </div>
                            <div style="margin-bottom: 4px;"><strong>New:</strong></div>
                            <div style="color: #10b981; word-break: break-all;">
                                ${escapeHtml(working_locator || 'N/A')}
                            </div>
                        </div>
                    </details>
                </div>
                
                ${requires_approval ? `
                    <div style="padding: 12px; background: #fef3c7; border-radius: 6px; margin-bottom: 12px;">
                        <div style="font-size: 13px; color: #92400e; margin-bottom: 8px;">
                            ⚠️ Low confidence - requires your approval
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button onclick="approveHealing('${healing_event?.id || ''}')" 
                                    style="flex: 1; padding: 6px 12px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 500;">
                                ✅ Accept
                            </button>
                            <button onclick="rejectHealing('${healing_event?.id || ''}')" 
                                    style="flex: 1; padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 500;">
                                ❌ Reject
                            </button>
                        </div>
                    </div>
                ` : `
                    <div style="padding: 8px; background: #d1fae5; border-radius: 4px; color: #065f46; font-size: 12px;">
                        ✅ Auto-approved (high confidence)
                    </div>
                `}
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: #9ca3af; cursor: pointer; font-size: 20px; padding: 0; line-height: 1;">
                ×
            </button>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after 30 seconds if no approval needed
    if (!requires_approval) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 30000);
    }
}

/**
 * Approve a healing decision
 * @param {string} approvalId - Approval request ID
 */
async function approveHealing(approvalId) {
    if (!approvalId) {
        console.error('[Healing] No approval ID provided');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/healing/approve/${approvalId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 'current_user',  // TODO: Get from auth system
                update_test_case: true
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('✅ Healing approved! Test case updated.', 'success');
            // Remove the notification
            document.querySelectorAll('.healing-notification').forEach(n => n.remove());
        } else {
            showToast ('❌ Failed to approve: ' + result.error, 'error');
        }
        
    } catch (error) {
        console.error('[Healing] Error approving:', error);
        showToast('❌ Error approving healing', 'error');
    }
}

/**
 * Reject a healing decision
 * @param {string} approvalId - Approval request ID
 */
async function rejectHealing(approvalId) {
    if (!approvalId) {
        console.error('[Healing] No approval ID provided');
        return;
    }
    
    const reason = prompt('Reason for rejection (optional):');
    
    try {
        const response = await fetch(`${API_URL}/healing/reject/${approvalId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 'current_user',  // TODO: Get from auth system
                reason: reason || 'User rejected'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Healing rejected. Original locator kept.', 'info');
            // Remove the notification
            document.querySelectorAll('.healing-notification').forEach(n => n.remove());
        } else {
            showToast('❌ Failed to reject: ' + result.error, 'error');
        }
        
    } catch (error) {
        console.error('[Healing] Error rejecting:', error);
        showToast('❌ Error rejecting healing', 'error');
    }
}

/**
 * Get confidence level label
 * @param {number} confidence - Confidence score (0-1)
 * @returns {string} Confidence level
 */
function getConfidenceLevel(confidence) {
    if (confidence >= 0.9) return 'Very High';
    if (confidence >= 0.7) return 'High';
    if (confidence >= 0.5) return 'Medium';
    return 'Low';
}

/**
 * Get color for confidence level
 * @param {number} confidence - Confidence score (0-1)
 * @returns {string} Color hex code
 */
function getConfidenceColor(confidence) {
    if (confidence >= 0.8) return '#10b981';  // Green
    if (confidence >= 0.6) return '#f59e0b';  // Orange
    return '#ef4444';  // Red
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type (success, error, info)
 */
function showToast(message, type = 'info') {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6'
    };
    
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10001;
        animation: slideInUp 0.3s ease;
        max-width: 300px;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Export functions for use in other scripts
window.showHealingNotification = showHealingNotification;
window.approveHealing = approveHealing;
window.rejectHealing = rejectHealing;

console.log('[Healing UI] Loaded - v2 Advanced Self-Healing UI components ready');
