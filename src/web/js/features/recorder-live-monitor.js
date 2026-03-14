/**
 * Recorder Live Monitor - Real-time updates for recording session
 * Enhances UX by showing live status without overloading main file
 */

class RecorderLiveMonitor {
    constructor() {
        this.pollingInterval = null;
        this.timerInterval = null;
        this.sessionStartTime = null;
        this.lastActionCount = 0;
        this.lastUrl = '';
        this.lastTabCount = 0;
        this.isActive = false;
    }

    start(sessionId) {
        if (this.isActive) return;
        
        this.isActive = true;
        this.sessionStartTime = Date.now();
        console.log('[Live Monitor] Started monitoring session:', sessionId);
        
        // Start session timer (updates every second)
        this.timerInterval = setInterval(() => {
            this.updateSessionTimer();
        }, 1000);
        
        // Poll every 2 seconds for updates
        this.pollingInterval = setInterval(() => {
            this.checkBrowserStatus(sessionId);
        }, 2000);
        
        // Initial check
        this.checkBrowserStatus(sessionId);
    }

    async checkBrowserStatus(sessionId) {
        try {
            const response = await fetch(`${API_URL}/recorder/browser-status/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.updateUI(data);
                }
            }
        } catch (error) {
            console.error('[Live Monitor] Error checking status:', error);
        }
    }

    updateUI(data) {
        // Update current URL display
        if (data.current_url && data.current_url !== this.lastUrl) {
            this.lastUrl = data.current_url;
            this.displayCurrentUrl(data.current_url);
        }

        // Update tab count
        if (data.tab_count !== undefined && data.tab_count !== this.lastTabCount) {
            this.lastTabCount = data.tab_count;
            this.displayTabCount(data.tab_count);
        }

        // Update action count
        if (data.action_count !== undefined && data.action_count !== this.lastActionCount) {
            this.lastActionCount = data.action_count;
            this.updateActionCount(data.action_count);
        }

        // Update browser window state
        if (data.browser_visible !== undefined) {
            this.updateBrowserVisibility(data.browser_visible);
        }
    }

    displayCurrentUrl(url) {
        const urlDisplay = document.getElementById('liveRecorderUrl');
        if (urlDisplay) {
            try {
                const urlObj = new URL(url);
                urlDisplay.textContent = `📍 ${urlObj.hostname}${urlObj.pathname}`;
                urlDisplay.title = url;
            } catch (e) {
                urlDisplay.textContent = `📍 ${url.substring(0, 50)}...`;
            }
        }
    }

    displayTabCount(count) {
        const tabDisplay = document.getElementById('liveTabCount');
        if (tabDisplay) {
            tabDisplay.textContent = count === 1 ? '1 tab' : `${count} tabs`;
            
            // Visual indicator if multiple tabs
            if (count > 1) {
                tabDisplay.style.background = 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)';
                tabDisplay.style.animation = 'pulse 2s infinite';
            } else {
                tabDisplay.style.background = 'rgba(255,255,255,0.1)';
                tabDisplay.style.animation = 'none';
            }
        }
    }

    updateActionCount(count) {
        const countDisplay = document.getElementById('liveActionCount');
        if (countDisplay) {
            countDisplay.textContent = count;
            
            // Pulse animation on update
            countDisplay.style.transform = 'scale(1.2)';
            setTimeout(() => {
                countDisplay.style.transform = 'scale(1)';
            }, 200);
        }
    }

    updateBrowserVisibility(isVisible) {
        const visibilityIndicator = document.getElementById('browserVisibilityIndicator');
        if (visibilityIndicator) {
            if (isVisible) {
                visibilityIndicator.textContent = '🟢';
                visibilityIndicator.title = 'Browser is active';
            } else {
                visibilityIndicator.textContent = '🟡';
                visibilityIndicator.title = 'Browser may be minimized';
            }
        }
    }

    stop() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        this.isActive = false;
        this.sessionStartTime = null;
        this.lastActionCount = 0;
        this.lastUrl = '';
        this.lastTabCount = 0;
        
        // Reset UI displays
        const timeDisplay = document.getElementById('liveSessionTime');
        if (timeDisplay) {
            timeDisplay.textContent = '00:00';
        }
        
        console.log('[Live Monitor] Stopped - timer reset to 00:00');
    }

    updateSessionTimer() {
        if (!this.sessionStartTime) return;
        
        const elapsed = Math.floor((Date.now() - this.sessionStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        const timeDisplay = document.getElementById('liveSessionTime');
        if (timeDisplay) {
            timeDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
    }

    // Bring browser window to front
    async bringBrowserToFront() {
        try {
            const response = await fetch(`${API_URL}/recorder/focus-browser`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                console.log('[Live Monitor] Browser focused');
                return true;
            }
        } catch (error) {
            console.error('[Live Monitor] Error focusing browser:', error);
        }
        return false;
    }
}

// Export to window
window.RecorderLiveMonitor = RecorderLiveMonitor;
