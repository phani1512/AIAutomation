/**
 * RecorderPlayer - Replay Functionality
 * Plays back recorded sessions with speed control and breakpoints
 * Version: 1.0
 */

class RecorderPlayer {
    constructor(config = {}) {
        this.currentSession = null;
        this.currentStep = 0;
        this.isPlaying = false;
        this.isPaused = false;
        this.speed = config.speed || 1; // 1 = normal, 0.5 = half speed, 2 = double speed
        this.breakpoints = new Set(config.breakpoints || []);
        this.onStepComplete = config.onStepComplete || null;
        this.onPlayComplete = config.onPlayComplete || null;
        this.onError = config.onError || null;
        this.onBreakpoint = config.onBreakpoint || null;
        this.highlightDuration = 1000; // ms to highlight elements during replay
        this.actionDelay = config.actionDelay || 500; // Base delay between actions
    }

    /**
     * Load a session for playback
     */
    loadSession(session) {
        if (this.isPlaying) {
            throw new Error('Cannot load session while playing');
        }
        
        this.currentSession = session;
        this.currentStep = 0;
        console.log('[RecorderPlayer] Session loaded:', session.name);
        return this;
    }

    /**
     * Start playing the session
     */
    async play() {
        if (!this.currentSession) {
            throw new Error('No session loaded');
        }

        if (this.isPlaying) {
            console.warn('[RecorderPlayer] Already playing');
            return;
        }

        this.isPlaying = true;
        this.isPaused = false;
        console.log('[RecorderPlayer] ▶️ Starting playback...');

        try {
            const actions = this.currentSession.actions;
            
            for (let i = this.currentStep; i < actions.length; i++) {
                if (!this.isPlaying) {
                    console.log('[RecorderPlayer] ⏹️ Playback stopped');
                    break;
                }

                // Wait if paused
                while (this.isPaused && this.isPlaying) {
                    await this.delay(100);
                }

                const action = actions[i];
                this.currentStep = i;

                // Check for breakpoint
                if (this.breakpoints.has(action.step)) {
                    console.log(`[RecorderPlayer] 🔴 Breakpoint at step ${action.step}`);
                    this.pause();
                    if (this.onBreakpoint) {
                        this.onBreakpoint(action);
                    }
                    await this.waitForResume();
                }

                // Execute action
                console.log(`[RecorderPlayer] Executing step ${action.step}: ${action.type}`);
                await this.executeAction(action);

                // Callback after step complete
                if (this.onStepComplete) {
                    this.onStepComplete(action, i + 1, actions.length);
                }

                // Delay before next action (adjusted by speed)
                const delayTime = this.actionDelay / this.speed;
                await this.delay(delayTime);
            }

            // Playback complete
            this.isPlaying = false;
            this.currentStep = 0;
            console.log('[RecorderPlayer] ✅ Playback complete');
            
            if (this.onPlayComplete) {
                this.onPlayComplete(this.currentSession);
            }

        } catch (error) {
            console.error('[RecorderPlayer] ❌ Playback error:', error);
            this.isPlaying = false;
            
            if (this.onError) {
                this.onError(error);
            }
            throw error;
        }
    }

    /**
     * Execute a recorded action
     */
    async executeAction(action) {
        try {
            // Validate action has a type
            if (!action.type || action.type === 'undefined') {
                console.warn('[RecorderPlayer] Skipping action with undefined type:', action);
                return; // Skip undefined actions
            }
            
            const element = await this.findElement(action.element);
            
            if (!element) {
                throw new Error(`Element not found for action: ${action.type}`);
            }

            // Highlight element before action
            this.highlightElement(element, action.type);

            // Execute based on action type
            switch (action.type) {
                case 'click':
                    await this.executeClick(element);
                    break;

                case 'input':
                    await this.executeInput(element, action.value);
                    break;

                case 'select':
                    await this.executeSelect(element, action.value);
                    break;

                case 'navigate':
                    await this.executeNavigate(action.value);
                    break;

                case 'hover':
                    await this.executeHover(element);
                    break;

                case 'scroll':
                    await this.executeScroll(action.value);
                    break;

                case 'verify':
                    await this.executeVerify(element, action.value);
                    break;

                default:
                    console.warn(`[RecorderPlayer] Unknown action type: ${action.type}`);
            }

            await this.delay(100); // Small delay after action

        } catch (error) {
            console.error(`[RecorderPlayer] Error executing action:`, error);
            throw error;
        }
    }

    /**
     * Find element using recorded element info
     */
    async findElement(recordedElement) {
        // Try multiple strategies in order of preference
        const strategies = [
            // 1. Try ID (most reliable)
            () => recordedElement.id ? document.getElementById(recordedElement.id) : null,
            
            // 2. Try data-testid
            () => recordedElement.attributes?.['data-testid'] ? 
                  document.querySelector(`[data-testid="${recordedElement.attributes['data-testid']}"]`) : null,
            
            // 3. Try name
            () => recordedElement.name ? document.querySelector(`[name="${recordedElement.name}"]`) : null,
            
            // 4. Try CSS selector
            () => recordedElement.cssSelector ? document.querySelector(recordedElement.cssSelector) : null,
            
            // 5. Try XPath
            () => recordedElement.xpath ? this.findByXPath(recordedElement.xpath) : null
        ];

        for (const strategy of strategies) {
            try {
                const element = strategy();
                if (element) {
                    return element;
                }
            } catch (e) {
                // Continue to next strategy
            }
        }

        return null;
    }

    /**
     * Find element by XPath
     */
    findByXPath(xpath) {
        const result = document.evaluate(
            xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
        );
        return result.singleNodeValue;
    }

    /**
     * Execute click action
     */
    async executeClick(element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await this.delay(200);
        element.click();
    }

    /**
     * Execute input action
     */
    async executeInput(element, value) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await this.delay(200);
        
        // Clear existing value
        element.value = '';
        element.focus();
        
        // Type character by character for realistic replay
        for (const char of value) {
            element.value += char;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            await this.delay(50 / this.speed); // Typing delay
        }
        
        element.dispatchEvent(new Event('change', { bubbles: true }));
        element.blur();
    }

    /**
     * Execute select action
     */
    async executeSelect(element, value) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await this.delay(200);
        
        element.value = value;
        element.dispatchEvent(new Event('change', { bubbles: true }));
    }

    /**
     * Execute navigate action
     */
    async executeNavigate(url) {
        console.log(`[RecorderPlayer] Navigating to: ${url}`);
        window.location.href = url;
        // Wait for page load
        await this.delay(2000 / this.speed);
    }

    /**
     * Execute hover action
     */
    async executeHover(element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await this.delay(200);
        
        const event = new MouseEvent('mouseover', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        element.dispatchEvent(event);
    }

    /**
     * Execute scroll action
     */
    async executeScroll(scrollData) {
        if (typeof scrollData === 'number') {
            window.scrollTo({ top: scrollData, behavior: 'smooth' });
        } else if (scrollData?.x !== undefined && scrollData?.y !== undefined) {
            window.scrollTo({ top: scrollData.y, left: scrollData.x, behavior: 'smooth' });
        }
        await this.delay(300);
    }

    /**
     * Execute verify action
     */
    async executeVerify(element, expectedValue) {
        const actualValue = element.textContent || element.value;
        if (actualValue !== expectedValue) {
            throw new Error(`Verification failed: expected "${expectedValue}", got "${actualValue}"`);
        }
        console.log(`[RecorderPlayer] ✓ Verification passed`);
    }

    /**
     * Highlight element during replay
     */
    highlightElement(element, actionType) {
        const colors = {
            click: '#10b981',
            input: '#3b82f6',
            select: '#8b5cf6',
            navigate: '#f59e0b',
            hover: '#14b8a6',
            scroll: '#6366f1',
            verify: '#10b981'
        };

        const color = colors[actionType] || '#10b981';
        
        element.style.outline = `3px solid ${color}`;
        element.style.outlineOffset = '2px';
        element.style.boxShadow = `0 0 15px ${color}`;

        setTimeout(() => {
            element.style.outline = '';
            element.style.outlineOffset = '';
            element.style.boxShadow = '';
        }, this.highlightDuration);
    }

    /**
     * Pause playback
     */
    pause() {
        this.isPaused = true;
        console.log('[RecorderPlayer] ⏸️ Paused');
    }

    /**
     * Resume playback
     */
    resume() {
        this.isPaused = false;
        console.log('[RecorderPlayer] ▶️ Resumed');
    }

    /**
     * Stop playback
     */
    stop() {
        this.isPlaying = false;
        this.isPaused = false;
        this.currentStep = 0;
        console.log('[RecorderPlayer] ⏹️ Stopped');
    }

    /**
     * Set playback speed
     */
    setSpeed(speed) {
        if (speed <= 0) {
            throw new Error('Speed must be positive');
        }
        this.speed = speed;
        console.log(`[RecorderPlayer] Speed set to ${speed}x`);
    }

    /**
     * Add breakpoint at step
     */
    addBreakpoint(step) {
        this.breakpoints.add(step);
        console.log(`[RecorderPlayer] Breakpoint added at step ${step}`);
    }

    /**
     * Remove breakpoint
     */
    removeBreakpoint(step) {
        this.breakpoints.delete(step);
        console.log(`[RecorderPlayer] Breakpoint removed from step ${step}`);
    }

    /**
     * Clear all breakpoints
     */
    clearBreakpoints() {
        this.breakpoints.clear();
        console.log('[RecorderPlayer] All breakpoints cleared');
    }

    /**
     * Jump to specific step
     */
    jumpToStep(step) {
        if (step < 0 || step >= this.currentSession.actions.length) {
            throw new Error('Invalid step number');
        }
        this.currentStep = step;
        console.log(`[RecorderPlayer] Jumped to step ${step}`);
    }

    /**
     * Wait for resume (when paused)
     */
    async waitForResume() {
        while (this.isPaused && this.isPlaying) {
            await this.delay(100);
        }
    }

    /**
     * Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get current playback state
     */
    getState() {
        return {
            isPlaying: this.isPlaying,
            isPaused: this.isPaused,
            currentStep: this.currentStep,
            totalSteps: this.currentSession?.actions.length || 0,
            speed: this.speed,
            breakpoints: Array.from(this.breakpoints),
            sessionName: this.currentSession?.name
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RecorderPlayer;
}

// Create global instance
if (typeof window !== 'undefined') {
    window.RecorderPlayer = RecorderPlayer;
}
