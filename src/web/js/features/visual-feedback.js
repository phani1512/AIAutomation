/**
 * Visual Feedback System
 * Provides real-time visual indicators for recorded actions
 */

class RecorderVisualFeedback {
    constructor() {
        this.indicators = [];
        this.config = {
            indicatorDuration: 2000,
            highlightDuration: 1500,
            maxIndicators: 10,
            colors: {
                click: '#10b981',
                input: '#3b82f6',
                select: '#8b5cf6',
                navigate: '#f59e0b',
                hover: '#14b8a6',
                scroll: '#6366f1',
                verify: '#10b981'
            },
            icons: {
                click: '👆',
                input: '⌨️',
                select: '📋',
                navigate: '🌐',
                hover: '👉',
                scroll: '↕️',
                verify: '✓',
                screenshot: '📸'
            }
        };
        this.ensureStylesInjected();
    }

    /**
     * Inject styles for visual feedback
     */
    ensureStylesInjected() {
        if (document.getElementById('recorder-visual-feedback-styles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'recorder-visual-feedback-styles';
        style.textContent = `
            .recorder-indicator {
                position: absolute;
                z-index: 999998;
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.95), rgba(5, 150, 105, 0.95));
                color: white;
                border-radius: 20px;
                padding: 6px 12px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 6px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                animation: recorderFadeIn 0.2s ease-out, recorderFadeOut 0.3s ease-in 1.7s forwards;
                pointer-events: none;
            }

            @keyframes recorderFadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px) scale(0.9);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            @keyframes recorderFadeOut {
                from {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
                to {
                    opacity: 0;
                    transform: translateY(-10px) scale(0.9);
                }
            }

            .indicator-icon {
                font-size: 16px;
                line-height: 1;
            }

            .indicator-step {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: 700;
                min-width: 20px;
                text-align: center;
            }

            .recorder-highlight {
                outline: 3px solid !important;
                outline-offset: 2px !important;
                animation: recorderPulse 1s ease-in-out;
            }

            @keyframes recorderPulse {
                0%, 100% {
                    outline-color: var(--highlight-color);
                    outline-width: 3px;
                }
                50% {
                    outline-color: var(--highlight-color);
                    outline-width: 5px;
                }
            }

            .recorder-ripple {
                position: absolute;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(16, 185, 129, 0.6), transparent);
                transform: scale(0);
                animation: recorderRipple 0.6s ease-out;
                pointer-events: none;
                z-index: 999997;
            }

            @keyframes recorderRipple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Show visual feedback for a recorded action
     */
    showRecordedAction(element, actionType, actionCount, value = null) {
        if (!element || !element.getBoundingClientRect) {
            console.warn('[VisualFeedback] Invalid element provided');
            return;
        }

        // Highlight the element
        this.highlightElement(element, actionType);

        // Show indicator
        this.showIndicator(element, actionType, actionCount, value);

        // Show ripple effect for clicks
        if (actionType === 'click') {
            this.showRipple(element);
        }

        // Cleanup old indicators
        this.cleanupOldIndicators();
    }

    /**
     * Highlight element with colored outline
     */
    highlightElement(element, actionType) {
        const color = this.config.colors[actionType] || this.config.colors.click;
        
        // Apply highlight
        element.classList.add('recorder-highlight');
        element.style.setProperty('--highlight-color', color);

        // Remove highlight after duration
        setTimeout(() => {
            element.classList.remove('recorder-highlight');
        }, this.config.highlightDuration);
    }

    /**
     * Show floating indicator next to element
     */
    showIndicator(element, actionType, actionCount, value) {
        const rect = element.getBoundingClientRect();
        const indicator = document.createElement('div');
        indicator.className = 'recorder-indicator';
        
        const color = this.config.colors[actionType] || this.config.colors.click;
        indicator.style.background = `linear-gradient(135deg, ${color}f0, ${this.darkenColor(color)}f0)`;

        const icon = this.config.icons[actionType] || '✓';
        const label = this.getActionLabel(actionType, value);

        indicator.innerHTML = `
            <span class="indicator-icon">${icon}</span>
            <span>${label}</span>
            <span class="indicator-step">${actionCount}</span>
        `;

        // Position indicator
        const topOffset = rect.top + window.scrollY;
        const leftOffset = rect.right + window.scrollX + 10;

        indicator.style.top = `${topOffset}px`;
        indicator.style.left = `${leftOffset}px`;

        document.body.appendChild(indicator);
        this.indicators.push(indicator);

        // Auto-remove after duration
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.parentNode.removeChild(indicator);
            }
            this.indicators = this.indicators.filter(ind => ind !== indicator);
        }, this.config.indicatorDuration);
    }

    /**
     * Show ripple effect on click
     */
    showRipple(element) {
        const rect = element.getBoundingClientRect();
        const ripple = document.createElement('div');
        ripple.className = 'recorder-ripple';

        const size = Math.max(rect.width, rect.height);
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.top = `${rect.top + window.scrollY + rect.height / 2 - size / 2}px`;
        ripple.style.left = `${rect.left + window.scrollX + rect.width / 2 - size / 2}px`;

        document.body.appendChild(ripple);

        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }

    /**
     * Get action label text
     */
    getActionLabel(actionType, value) {
        const labels = {
            click: 'Click',
            input: 'Type',
            select: 'Select',
            navigate: 'Navigate',
            hover: 'Hover',
            scroll: 'Scroll',
            verify: 'Verify'
        };

        let label = labels[actionType] || actionType;

        if (value && (actionType === 'input' || actionType === 'select')) {
            const displayValue = value.length > 15 ? value.substring(0, 15) + '...' : value;
            label += `: ${displayValue}`;
        }

        return label;
    }

    /**
     * Cleanup old indicators
     */
    cleanupOldIndicators() {
        while (this.indicators.length > this.config.maxIndicators) {
            const oldIndicator = this.indicators.shift();
            if (oldIndicator && oldIndicator.parentNode) {
                oldIndicator.parentNode.removeChild(oldIndicator);
            }
        }
    }

    /**
     * Darken color for gradient
     */
    darkenColor(color) {
        // Simple color darkening
        const hex = color.replace('#', '');
        const r = Math.max(0, parseInt(hex.substr(0, 2), 16) - 30);
        const g = Math.max(0, parseInt(hex.substr(2, 2), 16) - 30);
        const b = Math.max(0, parseInt(hex.substr(4, 2), 16) - 30);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    /**
     * Show action recorded toast
     */
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            padding: 12px 20px;
            border-radius: 10px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            z-index: 999999;
            animation: recorderFadeIn 0.2s ease-out, recorderFadeOut 0.3s ease-in 2.7s forwards;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }

    /**
     * Show recording started overlay
     */
    showRecordingStarted() {
        this.showToast('🎬 Recording started! Perform your actions.', 'success');
    }

    /**
     * Show recording stopped overlay
     */
    showRecordingStopped(actionCount) {
        this.showToast(`⏹️ Recording stopped! ${actionCount} actions captured.`, 'success');
    }

    /**
     * Show recording paused overlay
     */
    showRecordingPaused() {
        this.showToast('⏸️ Recording paused', 'success');
    }

    /**
     * Show recording resumed overlay
     */
    showRecordingResumed() {
        this.showToast('▶️ Recording resumed', 'success');
    }

    /**
     * Clear all indicators
     */
    clearAll() {
        this.indicators.forEach(indicator => {
            if (indicator && indicator.parentNode) {
                indicator.parentNode.removeChild(indicator);
            }
        });
        this.indicators = [];
    }

    /**
     * Show screenshot captured feedback
     */
    showScreenshotCaptured() {
        this.showToast('📸 Screenshot captured!', 'success');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RecorderVisualFeedback;
}

// Create global instance
if (typeof window !== 'undefined') {
    window.RecorderVisualFeedback = RecorderVisualFeedback;
}
