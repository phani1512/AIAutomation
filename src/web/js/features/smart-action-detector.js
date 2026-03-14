/**
 * Smart Action Detector
 * Intelligently detects, debounces, and groups user actions to avoid duplicate recording
 */

class SmartActionDetector {
    constructor() {
        this.pendingActions = new Map();
        this.lastActions = new Map();
        this.actionGroups = [];
        this.config = {
            inputDebounceDelay: 500,      // Wait 500ms after last keystroke
            clickDebounceDelay: 300,       // Prevent double-click duplicates
            scrollDebounceDelay: 300,      // Debounce scroll events
            groupingWindow: 2000           // Group related actions within 2s
        };
        this.framework = 'vanilla';
    }

    /**
     * Handle input events with smart debouncing
     */
    handleInput(element, value, callback) {
        const key = this.getElementKey(element);
        
        // Clear existing timeout
        if (this.pendingActions.has(key)) {
            clearTimeout(this.pendingActions.get(key));
        }
        
        // Set new timeout
        const timeoutId = setTimeout(() => {
            // Check if value actually changed
            const lastValue = this.lastActions.get(key);
            if (lastValue !== value) {
                callback(element, value);
                this.lastActions.set(key, value);
            }
            this.pendingActions.delete(key);
        }, this.config.inputDebounceDelay);
        
        this.pendingActions.set(key, timeoutId);
    }

    /**
     * Handle click events with duplicate prevention
     */
    handleClick(element, callback) {
        const key = this.getElementKey(element);
        const now = Date.now();
        const lastClick = this.lastActions.get(`${key}_click`);
        
        // Prevent rapid duplicate clicks (double-click protection)
        if (lastClick && (now - lastClick) < this.config.clickDebounceDelay) {
            console.log('[SmartDetector] Ignoring duplicate click');
            return false;
        }
        
        // Check if this is a file input trigger button
        if (this.isFileInputTrigger(element)) {
            console.log('[SmartDetector] File input trigger detected - skipping click');
            return false;
        }
        
        // Check if this is a framework-specific element that shouldn't be recorded
        if (this.shouldSkipFrameworkElement(element)) {
            console.log('[SmartDetector] Framework element skipped');
            return false;
        }
        
        this.lastActions.set(`${key}_click`, now);
        callback(element);
        return true;
    }

    /**
     * Handle select events
     */
    handleSelect(element, value, callback) {
        const key = this.getElementKey(element);
        const lastValue = this.lastActions.get(key);
        
        // Only record if value changed
        if (lastValue !== value) {
            callback(element, value);
            this.lastActions.set(key, value);
            return true;
        }
        
        return false;
    }

    /**
     * Handle scroll events with debouncing
     */
    handleScroll(element, callback) {
        const key = `scroll_${this.getElementKey(element)}`;
        
        if (this.pendingActions.has(key)) {
            clearTimeout(this.pendingActions.get(key));
        }
        
        const timeoutId = setTimeout(() => {
            callback(element);
            this.pendingActions.delete(key);
        }, this.config.scrollDebounceDelay);
        
        this.pendingActions.set(key, timeoutId);
    }

    /**
     * Detect action patterns and group related actions
     */
    detectActionPattern(actions) {
        if (actions.length < 2) return null;
        
        // Pattern: Form fill (multiple inputs + submit)
        const formPattern = this.detectFormFillPattern(actions);
        if (formPattern) return formPattern;
        
        // Pattern: Navigation sequence
        const navPattern = this.detectNavigationPattern(actions);
        if (navPattern) return navPattern;
        
        // Pattern: Search flow
        const searchPattern = this.detectSearchPattern(actions);
        if (searchPattern) return searchPattern;
        
        return null;
    }

    /**
     * Detect form fill pattern
     */
    detectFormFillPattern(actions) {
        const recentActions = actions.slice(-5); // Look at last 5 actions
        const inputActions = recentActions.filter(a => 
            a.type === 'input' || a.type === 'click_and_input' || a.type === 'select'
        );
        const submitAction = recentActions.find(a => 
            a.type === 'click' && 
            (a.element.attributes.type === 'submit' || 
             a.element.text?.toLowerCase().includes('submit') ||
             a.element.text?.toLowerCase().includes('login'))
        );
        
        if (inputActions.length >= 2 && submitAction) {
            return {
                pattern: 'form_fill',
                name: 'Form Fill Pattern',
                actions: [...inputActions, submitAction],
                confidence: 0.9
            };
        }
        
        return null;
    }

    /**
     * Detect navigation pattern
     */
    detectNavigationPattern(actions) {
        const recentActions = actions.slice(-3);
        const hasHover = recentActions.some(a => a.type === 'hover');
        const hasClicks = recentActions.filter(a => a.type === 'click').length >= 2;
        
        if (hasHover && hasClicks) {
            return {
                pattern: 'navigation',
                name: 'Navigation Sequence',
                actions: recentActions,
                confidence: 0.8
            };
        }
        
        return null;
    }

    /**
     * Detect search pattern
     */
    detectSearchPattern(actions) {
        const recentActions = actions.slice(-3);
        const searchInput = recentActions.find(a => 
            (a.type === 'input' || a.type === 'click_and_input') &&
            (a.element.attributes.name?.toLowerCase().includes('search') ||
             a.element.attributes.placeholder?.toLowerCase().includes('search') ||
             a.element.attributes.id?.toLowerCase().includes('search'))
        );
        const searchButton = recentActions.find(a =>
            a.type === 'click' &&
            (a.element.text?.toLowerCase().includes('search') ||
             a.element.attributes.title?.toLowerCase().includes('search'))
        );
        
        if (searchInput && searchButton) {
            return {
                pattern: 'search',
                name: 'Search Flow',
                actions: [searchInput, searchButton],
                confidence: 0.95
            };
        }
        
        return null;
    }

    /**
     * Detect framework-specific elements
     */
    detectFrameworkElements(element) {
        // React detection
        if (this.isReactElement(element)) {
            this.framework = 'react';
            return 'react';
        }
        
        // Vue detection
        if (this.isVueElement(element)) {
            this.framework = 'vue';
            return 'vue';
        }
        
        // Angular detection
        if (this.isAngularElement(element)) {
            this.framework = 'angular';
            return 'angular';
        }
        
        this.framework = 'vanilla';
        return 'vanilla';
    }

    /**
     * Check if element is React component
     */
    isReactElement(element) {
        let current = element;
        while (current) {
            // Check for React fiber
            if (current._reactRootContainer || 
                current._reactInternalInstance ||
                Object.keys(current).some(key => key.startsWith('__react'))) {
                return true;
            }
            
            // Check for React Select specifically
            if (current.id && current.id.includes('react-select')) {
                return true;
            }
            
            if (current.className && typeof current.className === 'string') {
                if (current.className.includes('react-select') || 
                    current.className.includes('__option') ||
                    current.className.includes('__menu')) {
                    return true;
                }
            }
            
            current = current.parentElement;
        }
        return false;
    }

    /**
     * Check if element is Vue component
     */
    isVueElement(element) {
        let current = element;
        while (current) {
            if (current.__vue__ || current.hasAttribute('data-v-')) {
                return true;
            }
            current = current.parentElement;
        }
        return false;
    }

    /**
     * Check if element is Angular component
     */
    isAngularElement(element) {
        let current = element;
        while (current) {
            if (current.hasAttribute('ng-version')) {
                return true;
            }
            const attrs = Array.from(current.attributes || []);
            if (attrs.some(attr => attr.name.startsWith('ng-') || attr.name.startsWith('_ng'))) {
                return true;
            }
            current = current.parentElement;
        }
        return false;
    }

    /**
     * Check if element should be skipped (framework-specific)
     */
    shouldSkipFrameworkElement(element) {
        // Skip React Select option elements
        if (element.id && element.id.includes('react-select') && element.id.includes('-option-')) {
            return true;
        }
        
        // Skip React Select menu elements
        if (element.className && typeof element.className === 'string') {
            const className = element.className;
            if (className.includes('select__option') || 
                className.includes('select__menu') ||
                className.includes('select__menu-list')) {
                return true;
            }
        }
        
        // Skip Vue virtual scroll elements
        if (element.hasAttribute('data-v-virtual-scroller')) {
            return true;
        }
        
        // Skip Angular CDK overlay elements
        if (element.className && typeof element.className === 'string') {
            if (element.className.includes('cdk-overlay') || 
                element.className.includes('mat-option')) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Check if element is a file input trigger
     */
    isFileInputTrigger(element) {
        // Check if clicking this triggers a file input
        const onclick = element.getAttribute('onclick');
        if (onclick && onclick.includes('file') && onclick.includes('click')) {
            return true;
        }
        
        // Check if parent has file input
        const parent = element.parentElement;
        if (parent) {
            const fileInput = parent.querySelector('input[type="file"]');
            if (fileInput) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Get unique key for element
     */
    getElementKey(element) {
        if (element.id) return `id:${element.id}`;
        if (element.name) return `name:${element.name}`;
        
        // Generate key from XPath
        const xpath = this.generateSimpleXPath(element);
        return `xpath:${xpath}`;
    }

    /**
     * Generate simple XPath for element identification
     */
    generateSimpleXPath(element) {
        if (element.id) return `//*[@id="${element.id}"]`;
        
        let path = '';
        let current = element;
        let depth = 0;
        
        while (current && current.nodeType === Node.ELEMENT_NODE && depth < 5) {
            let index = 0;
            let sibling = current.previousSibling;
            
            while (sibling) {
                if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === current.tagName) {
                    index++;
                }
                sibling = sibling.previousSibling;
            }
            
            const tagName = current.tagName.toLowerCase();
            const pathIndex = index > 0 ? `[${index + 1}]` : '';
            path = `/${tagName}${pathIndex}${path}`;
            
            current = current.parentElement;
            depth++;
        }
        
        return path || '/unknown';
    }

    /**
     * Clear all pending actions (useful when stopping recording)
     */
    clearPending() {
        this.pendingActions.forEach(timeoutId => clearTimeout(timeoutId));
        this.pendingActions.clear();
    }

    /**
     * Reset detector state
     */
    reset() {
        this.clearPending();
        this.lastActions.clear();
        this.actionGroups = [];
        this.framework = 'vanilla';
    }

    /**
     * Get statistics about detected actions
     */
    getStats() {
        return {
            pendingActions: this.pendingActions.size,
            lastActions: this.lastActions.size,
            actionGroups: this.actionGroups.length,
            framework: this.framework
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SmartActionDetector;
}

// Create global instance
if (typeof window !== 'undefined') {
    window.SmartActionDetector = SmartActionDetector;
}
