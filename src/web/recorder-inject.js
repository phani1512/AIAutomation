/**
 * Browser Action Recorder - Injection Script
 * This script captures user interactions on the page
 * Version: 2.3.1 - SCROLL DEBUG + BUG FIX (elementSignature removed, Build: 20260314-1645)
 */

(function() {
    'use strict';
    
    console.log('='.repeat(60));
    console.log('[Recorder Script] ✅ Version 2.3.1 - BUILD 20260314-1645');
    console.log('[Recorder Script] ✅ SCROLL DEBUG LOGGING ACTIVE');
    console.log('[Recorder Script] ✅ elementSignature BUG FIXED');
    console.log('[Recorder Script] Loaded at:', new Date().toISOString());
    console.log('='.repeat(60));
    
    // ============== SMART ACTION DETECTOR CLASS ==============
    class SmartActionDetector {
        constructor() {
            this.pendingActions = new Map();
            this.lastActions = new Map();
            this.actionGroups = [];
            this.recordedActions = [];
            this.config = {
                inputDebounceDelay: 500,
                clickDebounceDelay: 300,
                scrollDebounceDelay: 300,
                groupingWindow: 2000
            };
            this.framework = 'vanilla';
        }

        handleInput(element, value, callback) {
            const key = this.getElementKey(element);
            if (this.pendingActions.has(key)) {
                clearTimeout(this.pendingActions.get(key));
            }
            const timeoutId = setTimeout(() => {
                const lastValue = this.lastActions.get(key);
                if (lastValue !== value) {
                    callback(element, value);
                    this.lastActions.set(key, value);
                }
                this.pendingActions.delete(key);
            }, this.config.inputDebounceDelay);
            this.pendingActions.set(key, timeoutId);
        }

        handleClick(element, callback) {
            const key = this.getElementKey(element);
            const now = Date.now();
            const lastClick = this.lastActions.get(`${key}_click`);
            if (lastClick && (now - lastClick) < this.config.clickDebounceDelay) {
                console.log('[SmartDetector] Ignoring duplicate click');
                return false;
            }
            if (this.isFileInputTrigger(element) || this.shouldSkipFrameworkElement(element)) {
                console.log('[SmartDetector] Skipping framework/file element');
                return false;
            }
            this.lastActions.set(`${key}_click`, now);
            callback(element);
            return true;
        }

        detectFrameworkElements(element) {
            if (this.isReactElement(element)) return 'react';
            if (this.isVueElement(element)) return 'vue';
            if (this.isAngularElement(element)) return 'angular';
            return 'vanilla';
        }

        isReactElement(element) {
            let current = element;
            while (current) {
                if (current._reactRootContainer || current._reactInternalInstance ||
                    Object.keys(current).some(key => key.startsWith('__react'))) return true;
                if (current.id && current.id.includes('react-select')) return true;
                if (current.className && typeof current.className === 'string') {
                    if (current.className.includes('react-select') || 
                        current.className.includes('__option') ||
                        current.className.includes('__menu')) return true;
                }
                current = current.parentElement;
            }
            return false;
        }

        isVueElement(element) {
            let current = element;
            while (current) {
                if (current.__vue__ || current.hasAttribute('data-v-')) return true;
                current = current.parentElement;
            }
            return false;
        }

        isAngularElement(element) {
            let current = element;
            while (current) {
                if (current.hasAttribute('ng-version')) return true;
                const attrs = Array.from(current.attributes || []);
                if (attrs.some(attr => attr.name.startsWith('ng-') || attr.name.startsWith('_ng'))) return true;
                current = current.parentElement;
            }
            return false;
        }

        shouldSkipFrameworkElement(element) {
            if (element.id && element.id.includes('react-select') && element.id.includes('-option-')) return true;
            if (element.className && typeof element.className === 'string') {
                const className = element.className;
                if (className.includes('select__option') || className.includes('select__menu') ||
                    className.includes('select__menu-list')) return true;
                if (className.includes('cdk-overlay') || className.includes('mat-option')) return true;
            }
            if (element.hasAttribute('data-v-virtual-scroller')) return true;
            return false;
        }

        isFileInputTrigger(element) {
            const onclick = element.getAttribute('onclick');
            if (onclick && onclick.includes('file') && onclick.includes('click')) return true;
            const parent = element.parentElement;
            if (parent && parent.querySelector('input[type="file"]')) return true;
            return false;
        }

        detectActionPattern(actions) {
            if (actions.length < 2) return null;
            return this.detectFormFillPattern(actions) || 
                   this.detectSearchPattern(actions) || null;
        }

        detectFormFillPattern(actions) {
            const recentActions = actions.slice(-5);
            const inputActions = recentActions.filter(a => 
                a.type === 'input' || a.type === 'click_and_input' || a.type === 'select'
            );
            const submitAction = recentActions.find(a => 
                a.type === 'click' && (a.element?.type === 'submit' || 
                a.element?.text?.toLowerCase().includes('submit'))
            );
            if (inputActions.length >= 2 && submitAction) {
                return { pattern: 'form_fill', actions: [...inputActions, submitAction], confidence: 0.9 };
            }
            return null;
        }

        detectSearchPattern(actions) {
            const recentActions = actions.slice(-3);
            const searchInput = recentActions.find(a => 
                (a.type === 'input' || a.type === 'click_and_input') &&
                (a.element?.name?.toLowerCase().includes('search') ||
                 a.element?.placeholder?.toLowerCase().includes('search'))
            );
            const searchButton = recentActions.find(a =>
                a.type === 'click' && a.element?.text?.toLowerCase().includes('search')
            );
            if (searchInput && searchButton) {
                return { pattern: 'search', actions: [searchInput, searchButton], confidence: 0.95 };
            }
            return null;
        }

        getElementKey(element) {
            if (element.id) return `id:${element.id}`;
            if (element.name) return `name:${element.name}`;
            return `xpath:${this.generateSimpleXPath(element)}`;
        }

        generateSimpleXPath(element) {
            if (element.id) return `//*[@id="${element.id}"]`;
            let path = '', current = element, depth = 0;
            while (current && current.nodeType === Node.ELEMENT_NODE && depth < 5) {
                let index = 0, sibling = current.previousSibling;
                while (sibling) {
                    if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === current.tagName) index++;
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

        addRecordedAction(action) {
            this.recordedActions.push(action);
            const pattern = this.detectActionPattern(this.recordedActions);
            if (pattern) {
                console.log('[SmartDetector] 🎯 Pattern detected:', pattern.pattern);
                this.actionGroups.push(pattern);
            }
        }

        getStats() {
            return {
                totalActions: this.recordedActions.length,
                patterns: this.actionGroups.length,
                pendingActions: this.pendingActions.size,
                detectedPatterns: this.actionGroups.map(p => p.pattern)
            };
        }

        reset() {
            this.pendingActions.forEach(t => clearTimeout(t));
            this.pendingActions.clear();
            this.lastActions.clear();
            this.actionGroups = [];
            this.recordedActions = [];
        }
    }
    // ============== END SMART ACTION DETECTOR ==============
    
    // ============== VISUAL FEEDBACK SYSTEM ==============
    class RecorderVisualFeedback {
        constructor() {
            this.indicators = [];
            this.config = {
                indicatorDuration: 2000,
                highlightDuration: 1500,
                maxIndicators: 10,
                colors: {
                    click: '#10b981', input: '#3b82f6', select: '#8b5cf6',
                    navigate: '#f59e0b', hover: '#14b8a6', scroll: '#6366f1', verify: '#10b981'
                },
                icons: {
                    click: '👆', input: '⌨️', select: '📋', navigate: '🌐',
                    hover: '👉', scroll: '↕️', verify: '✓', screenshot: '📸'
                }
            };
            this.ensureStylesInjected();
        }

        ensureStylesInjected() {
            if (document.getElementById('recorder-visual-feedback-styles')) return;
            const style = document.createElement('style');
            style.id = 'recorder-visual-feedback-styles';
            style.textContent = `
                .recorder-indicator {
                    position: absolute; z-index: 999998;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.95), rgba(5, 150, 105, 0.95));
                    color: white; border-radius: 20px; padding: 6px 12px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    animation: recorderFadeIn 0.2s ease-out, recorderFadeOut 0.3s ease-in 1.7s forwards;
                    pointer-events: none;
                }
                @keyframes recorderFadeIn {
                    from { opacity: 0; transform: translateY(-10px) scale(0.9); }
                    to { opacity: 1; transform: translateY(0) scale(1); }
                }
                @keyframes recorderFadeOut {
                    from { opacity: 1; transform: translateY(0) scale(1); }
                    to { opacity: 0; transform: translateY(-10px) scale(0.9); }
                }
                .recorder-highlight {
                    outline: 3px solid !important; outline-offset: 2px !important;
                    animation: recorderPulse 1s ease-in-out;
                }
                @keyframes recorderPulse {
                    0%, 100% { outline-color: var(--highlight-color); outline-width: 3px; }
                    50% { outline-color: var(--highlight-color); outline-width: 5px; }
                }
                .recorder-ripple {
                    position: absolute; border-radius: 50%;
                    background: radial-gradient(circle, rgba(16, 185, 129, 0.6), transparent);
                    transform: scale(0); animation: recorderRipple 0.6s ease-out;
                    pointer-events: none; z-index: 999997;
                }
                @keyframes recorderRipple {
                    to { transform: scale(4); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        showRecordedAction(element, actionType, actionCount, value = null) {
            if (!element || !element.getBoundingClientRect) return;
            this.highlightElement(element, actionType);
            this.showIndicator(element, actionType, actionCount, value);
            if (actionType === 'click') this.showRipple(element);
            this.cleanupOldIndicators();
        }

        highlightElement(element, actionType) {
            const color = this.config.colors[actionType] || this.config.colors.click;
            element.classList.add('recorder-highlight');
            element.style.setProperty('--highlight-color', color);
            setTimeout(() => element.classList.remove('recorder-highlight'), this.config.highlightDuration);
        }

        showIndicator(element, actionType, actionCount, value) {
            const rect = element.getBoundingClientRect();
            const indicator = document.createElement('div');
            indicator.className = 'recorder-indicator';
            const color = this.config.colors[actionType] || this.config.colors.click;
            indicator.style.background = `linear-gradient(135deg, ${color}f0, ${color}cc)`;
            const icon = this.config.icons[actionType] || '✓';
            const label = actionType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            indicator.innerHTML = `
                <span class="indicator-icon">${icon}</span>
                <span>${label}</span>
                <span class="indicator-step" style="background: rgba(255,255,255,0.3);border-radius: 10px;padding: 2px 6px;font-size: 11px;">${actionCount}</span>
            `;
            indicator.style.top = `${rect.top + window.scrollY}px`;
            indicator.style.left = `${rect.right + window.scrollX + 10}px`;
            document.body.appendChild(indicator);
            this.indicators.push(indicator);
            setTimeout(() => {
                if (indicator.parentNode) indicator.parentNode.removeChild(indicator);
                this.indicators = this.indicators.filter(ind => ind !== indicator);
            }, this.config.indicatorDuration);
        }

        showRipple(element) {
            const rect = element.getBoundingClientRect();
            const ripple = document.createElement('div');
            ripple.className = 'recorder-ripple';
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.top = `${rect.top + window.scrollY + rect.height / 2 - size / 2}px`;
            ripple.style.left = `${rect.left + window.scrollX + rect.width / 2 - size / 2}px`;
            document.body.appendChild(ripple);
            setTimeout(() => { if (ripple.parentNode) ripple.parentNode.removeChild(ripple); }, 600);
        }

        cleanupOldIndicators() {
            while (this.indicators.length > this.config.maxIndicators) {
                const old = this.indicators.shift();
                if (old.parentNode) old.parentNode.removeChild(old);
            }
        }
    }
    // ============== END VISUAL FEEDBACK SYSTEM ==============
    
    const API_URL = 'http://localhost:5002';
    let isRecording = false;
    let actionCount = 0;
    let messageObserver = null;
    let observedMessages = new Set();
    
    // Initialize Smart Action Detector & Visual Feedback
    const smartDetector = new SmartActionDetector();
    const visualFeedback = new RecorderVisualFeedback();
    console.log('[Recorder] ✅ Smart Action Detector initialized');
    console.log('[Recorder] ✅ Visual Feedback System initialized');
    
    // Expose to window for external checks
    window.isRecording = false;
    window.smartDetector = smartDetector;
    window.visualFeedback = visualFeedback;
    
    // Helper function to show visual feedback
    function showVisualFeedback(element, type = 'click', value = null) {
        visualFeedback.showRecordedAction(element, type, actionCount, value);
    }
    
    // Intercept window.open to record new window/tab navigation
    const originalWindowOpen = window.open;
    window.open = function(...args) {
        const url = args[0];
        const target = args[1] || '_blank';
        
        if (isRecording) {
            console.log(`[Recorder] 🪟 New window/tab opened: ${url}`);
            
            // Record the action using document.body as the element since it's a window-level action
            recordAction('navigate', document.body, `window.open("${url}", "${target}")`);
        }
        
        // Call the original window.open
        return originalWindowOpen.apply(this, args);
    };

    // Helper function to get element info
    function getElementInfo(element) {
        const text = element.textContent?.trim() || null;
        const innerText = element.innerText?.trim() || null;
        
        return {
            tagName: element.tagName.toLowerCase(),
            id: element.id || null,
            name: element.name || null,
            className: element.className || null,
            type: element.type || null,
            text: text ? text.substring(0, 100) : null,
            innerText: innerText ? innerText.substring(0, 100) : null,
            href: element.href || null,
            ariaLabel: element.getAttribute('aria-label') || null,
            title: element.title || null,
            value: element.value || null,
            placeholder: element.placeholder || null,
            xpath: getXPath(element)
        };
    }

    // Get XPath for element
    function getXPath(element) {
        if (element.id !== '') {
            return `//*[@id="${element.id}"]`;
        }
        
        if (element === document.body) {
            return '/html/body';
        }

        let ix = 0;
        const siblings = element.parentNode?.childNodes || [];
        
        for (let i = 0; i < siblings.length; i++) {
            const sibling = siblings[i];
            
            if (sibling === element) {
                return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
            }
            
            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                ix++;
            }
        }
    }

    // Record action to server
    async function recordAction(actionType, element, value = null) {
        if (!isRecording) {
            console.log('[Recorder] ⚠️ Not recording - action ignored:', actionType);
            return;
        }

        const elementInfo = getElementInfo(element);

        console.log(`[Recorder] 📝 Recording ${actionType}:`, elementInfo);
        
        // Track action in Smart Detector for pattern detection
        const actionData = {
            type: actionType,
            element: elementInfo,
            value: value,
            timestamp: Date.now()
        };
        smartDetector.addRecordedAction(actionData);

        try {
            console.log(`[Recorder] 🌐 Sending to ${API_URL}/recorder/record-action`);
            const response = await fetch(`${API_URL}/recorder/record-action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action_type: actionType,
                    element: elementInfo,
                    value: value
                }),
                mode: 'cors'
            });

            console.log(`[Recorder] 📡 Response status: ${response.status} ${response.statusText}`);

            if (!response.ok) {
                console.error(`[Recorder] ❌ Failed to record action: ${response.status} ${response.statusText}`);
                const errorText = await response.text();
                console.error('[Recorder] Error details:', errorText);
                return;
            }

            const data = await response.json();
            console.log('[Recorder] ✅ Server response:', data);
            
            // Update action count from server's actual count
            if (data.total_actions !== undefined) {
                actionCount = data.total_actions;
                // Update the counter display in browser controls
                const counterElement = document.getElementById('actionCounter');
                if (counterElement) {
                    counterElement.textContent = actionCount;
                }
            }
            
            // Only show visual feedback if action was actually recorded (not skipped)
            if (!data.skipped) {
                showVisualFeedback(element, actionType, value);
            }
        } catch (error) {
            console.error('[Recorder] ❌ Error recording action:', error);
            
            // Provide specific error messages
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                console.error('[Recorder] 💥 Network error: Cannot connect to recorder API at', API_URL);
                console.error('[Recorder] ⚠️ Make sure the API server is running on http://localhost:5002');
            } else if (error.message.includes('CORS')) {
                console.error('[Recorder] 🚫 CORS error: The API server needs to allow cross-origin requests');
            } else {
                console.error('[Recorder] Error details:', error.message);
            }
        }
    }

    // Record action with target (for drag-and-drop)
    async function recordActionWithTarget(actionType, sourceElement, targetElement) {
        if (!isRecording) {
            console.log('[Recorder] ⚠️ Not recording - action ignored:', actionType);
            return;
        }

        const elementInfo = getElementInfo(sourceElement);
        const targetInfo = getElementInfo(targetElement);

        console.log(`[Recorder] 📝 Recording ${actionType}:`, elementInfo, '→', targetInfo);

        try {
            // Generate target locator
            let targetLocator = null;
            if (targetInfo.id) {
                targetLocator = `By.id("${targetInfo.id}")`;
            } else if (targetInfo.xpath) {
                targetLocator = `By.xpath("${targetInfo.xpath}")`;
            }

            const response = await fetch(`${API_URL}/recorder/record-action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action_type: actionType,
                    element: elementInfo,
                    target_locator: targetLocator,
                    value: null
                }),
                mode: 'cors'
            });

            if (!response.ok) {
                console.error(`[Recorder] ❌ Failed to record action: ${response.status} ${response.statusText}`);
                const errorText = await response.text();
                console.error('[Recorder] Error details:', errorText);
                return;
            }

            const data = await response.json();
            console.log('[Recorder] ✅ Server response:', data);
            
            // Update action count from server's actual count
            if (data.total_actions !== undefined) {
                actionCount = data.total_actions;
                // Update the counter display in browser controls
                const counterElement = document.getElementById('actionCounter');
                if (counterElement) {
                    counterElement.textContent = actionCount;
                }
            }
            
            // Only show visual feedback if action was actually recorded (not skipped)
            if (!data.skipped) {
                console.log('[Recorder] Action recorded successfully:', data);
                
                // Visual feedback
                element.style.outline = '2px solid #10b981';
                setTimeout(() => {
                    element.style.outline = '';
                }, 500);
            } else {
                console.log('[Recorder] Action skipped (duplicate):', data);
            }

        } catch (error) {
            console.error('[Recorder] Error recording action:', error);
        }
    }

    // Keyboard shortcuts
    let isPaused = false;
    let lastInputValues = new Map(); // Track last recorded values to avoid duplicates
    let activeInputElement = null; // Track currently active input element
    let inputRecordedForElement = new Set(); // Track which elements we've already recorded in this session
    let lastClickedElement = null; // Track last clicked element to avoid duplicates
    let lastClickTime = 0; // Track last click time
    let fileInputTriggered = false; // Track if a file input button was clicked
    let datePickerActiveField = null; // Track the input field associated with an active date picker
    let datePickerPendingValue = null; // Track the pending date value from picker
    let dateInputMonitorInterval = null; // Interval for monitoring date inputs

    // Monitor all date inputs for value changes (backup mechanism for calendar pickers)
    function startDateInputMonitoring() {
        if (dateInputMonitorInterval) return;
        
        dateInputMonitorInterval = setInterval(() => {
            if (!isRecording || isPaused) return;
            
            // Find all date-related input fields
            const dateInputs = document.querySelectorAll(
                'input[type="date"], ' +
                'input[type="datetime-local"], ' +
                'input[type="text"][class*="date"], ' +
                'input[class*="datepicker"], ' +
                'input[data-provide="datepicker"], ' +
                'input[id*="date"], ' +
                'input[name*="date"]'
            );
            
            dateInputs.forEach(input => {
                const currentValue = input.value;
                const lastValue = lastInputValues.get(input) || '';
                
                // Check if value changed and we haven't recorded it yet
                if (currentValue && currentValue !== lastValue) {
                    const elementKey = `${input.id || input.name || input.className}_${currentValue}`;
                    
                    if (!inputRecordedForElement.has(elementKey)) {
                        console.log('[Recorder] 📅 Date input value changed (via monitoring):', currentValue);
                        recordAction('click_and_input', input, currentValue);
                        lastInputValues.set(input, currentValue);
                        inputRecordedForElement.add(elementKey);
                    }
                }
            });
        }, 500); // Check every 500ms
    }

    function stopDateInputMonitoring() {
        if (dateInputMonitorInterval) {
            clearInterval(dateInputMonitorInterval);
            dateInputMonitorInterval = null;
        }
    }

    // Track when user starts typing in an input field
    document.addEventListener('focusin', function(e) {
        if (!isRecording || isPaused) return;
        const target = e.target;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
            console.log('[Recorder] 🎯 Focus entered input:', {
                tag: target.tagName,
                type: target.type,
                id: target.id,
                name: target.name,
                class: target.className,
                value: target.value
            });
            activeInputElement = target;
            // Store the initial value when user enters the field
            if (!lastInputValues.has(target)) {
                lastInputValues.set(target, target.value || '');
            }
        }
    }, true);
    
    // Track typing in input fields using Smart Detector
    document.addEventListener('input', function(e) {
        if (!isRecording || isPaused) return;
        
        const target = e.target;
        
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
            console.log('[Recorder] ⌨️ Input event detected:', {
                tag: target.tagName,
                type: target.type,
                value: target.value
            });
            
            // Use Smart Detector for intelligent debouncing
            smartDetector.handleInput(target, target.value.trim(), (element, value) => {
                if (!isRecording) return;
                
                const lastValue = lastInputValues.get(element) || '';
                const elementKey = `${element.id || element.name || element.className}_${value}`;
                
                if (value && value !== lastValue && !inputRecordedForElement.has(elementKey)) {
                    console.log('[Recorder] 📝 Recording input (via Smart Detector):', value);
                    recordAction('click_and_input', element, value);
                    lastInputValues.set(element, value);
                    inputRecordedForElement.add(elementKey);
                }
            });
        }
    }, true);

    // Track when user leaves an input field - use focusout instead of blur
    document.addEventListener('focusout', function(e) {
        if (!isRecording || isPaused) return;
        
        const target = e.target;
        
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
            console.log('[Recorder] 👋 Focus left input:', {
                tag: target.tagName,
                type: target.type,
                value: target.value
            });
            // Only process if this is the active element
            if (activeInputElement !== target) {
                return;
            }
            
            const currentValue = target.value.trim();
            const lastValue = lastInputValues.get(target) || '';
            
            // Create a unique key for this field and value combination
            const elementKey = `${target.id || target.name || target.className}_${currentValue}`;
            
            // Special handling for date/calendar inputs
            const isDateInput = target.type === 'date' || target.type === 'datetime-local' || 
                               target.type === 'month' || target.type === 'week' || target.type === 'time' ||
                               target.classList.contains('datepicker') || 
                               target.getAttribute('data-provide') === 'datepicker' ||
                               target.hasAttribute('data-date') ||
                               target.closest('.datepicker') !== null;
            
            // For date inputs, always record on focusout if value changed
            // This handles both typing and calendar selection
            if (isDateInput && currentValue && currentValue !== lastValue) {
                recordAction('click_and_input', target, currentValue);
                lastInputValues.set(target, currentValue);
                inputRecordedForElement.add(elementKey);
                console.log('[Recorder] Calendar/Date input recorded:', currentValue);
            }
            // For regular inputs
            else if (currentValue && currentValue !== lastValue && !inputRecordedForElement.has(elementKey)) {
                // Record as 'click_and_input' to indicate combined action
                recordAction('click_and_input', target, currentValue);
                lastInputValues.set(target, currentValue);
                inputRecordedForElement.add(elementKey);
            }
            
            // Clear active element
            activeInputElement = null;
        }
    }, true);

    // Capture click events
    document.addEventListener('click', function(e) {
        const target = e.target;
        
        // Log ALL clicks for debugging (before early returns)
        console.log('[Recorder] 🖱️ CLICK:', target.tagName, 
                    'ID:', target.id || '(none)', 
                    'Class:', target.className || '(none)',
                    'Text:', target.textContent?.substring(0, 30) || '(none)',
                    'Recording:', isRecording, 
                    'Paused:', isPaused);
        
        if (!isRecording || isPaused) {
            console.log('[Recorder] ⏸️ Click ignored - not recording');
            return;
        }
        
        // Note: We NO LONGER prevent default on submit buttons or links
        // This allows navigation to happen naturally (e.g., login forms)
        // The form submission handler will record the action before navigation
        
        console.log('[Recorder] Click detected on:', target.tagName, 'ID:', target.id, 'Class:', target.className);
        
        // Ignore recorder controls and sticky popup
        if (target.closest('#recorderControls') || 
            target.id === 'sticky-close' || 
            target.closest('#sticky-close') ||
            target.closest('.sticky-popup')) {
            console.log('[Recorder] ❌ Skipped: Recorder controls or sticky popup');
            return;
        }
        
        // Skip buttons/elements that trigger file inputs (like "Select File", "Choose File", "Browse" buttons)
        // Check if this element or any parent will trigger a file input
        const triggersFileInput = target.tagName === 'LABEL' && target.getAttribute('for') && 
            document.getElementById(target.getAttribute('for'))?.type === 'file';
        
        const hasFileInputChild = target.querySelector('input[type="file"]') !== null;
        const parentTriggersFile = target.closest('label')?.getAttribute('for') && 
            document.getElementById(target.closest('label').getAttribute('for'))?.type === 'file';
        
        // Also check if this is a button that programmatically clicks a file input
        if (target.tagName === 'BUTTON' || target.closest('button')) {
            const buttonText = (target.textContent || '').toLowerCase();
            if (buttonText.includes('select file') || buttonText.includes('choose file') || 
                buttonText.includes('browse') || buttonText.includes('upload file')) {
                // Mark that a file input might be triggered next
                fileInputTriggered = true;
                console.log('[Recorder] ❌ Skipped: Button that triggers file input');
                return;
            }
        }
        
        if (triggersFileInput || hasFileInputChild || parentTriggersFile) {
            console.log('[Recorder] ❌ Skipped: Element triggers file input');
            fileInputTriggered = true;
            return;
        }
        
        // Ignore clicks on input fields and textareas (they will be captured as click_and_input on focusout)
        if (target.tagName === 'INPUT' && (target.type === 'text' || target.type === 'password' || target.type === 'email' || target.type === 'number' || target.type === 'tel' || target.type === 'url' || target.type === 'search')) {
            console.log('[Recorder] ❌ Skipped: Text input field');
            return;
        }
        
        if (target.tagName === 'TEXTAREA') {
            console.log('[Recorder] ❌ Skipped: Textarea');
            return;
        }
        
        // Skip hidden checkbox/radio inputs - the change event will handle them
        if (target.tagName === 'INPUT' && (target.type === 'checkbox' || target.type === 'radio')) {
            console.log('[Recorder] ❌ Skipped: Checkbox/radio - change event will handle it');
            return;
        }
        
        // Ignore ALL labels - they either trigger inputs (handled by change event) or are non-functional
        if (target.tagName === 'LABEL' || target.classList.contains('custom-control-label')) {
            console.log('[Recorder] ❌ Skipped: Label element');
            return;
        }
        
        // Skip common container/layout elements that aren't actually interactive
        const className = target.className || '';
        const classNameStr = typeof className === 'string' ? className : className.toString();
        
        // Always skip these patterns regardless of event handlers
        const alwaysSkipClasses = [
            'custom-control-label',  // Bootstrap custom control labels
            'col-12', 'col-md-', 'col-lg-', 'col-sm-', 'col-xs-', 'col-',  // Bootstrap grid columns
            'row', 'container', 'container-fluid',  // Bootstrap containers
            '__value-container', '__control', '__menu', '__option',  // React Select parts
            'subjects-auto-complete',  // Autocomplete containers
        ];
        
        const shouldAlwaysSkip = alwaysSkipClasses.some(cls => classNameStr.includes(cls));
        if (shouldAlwaysSkip) {
            console.log('[Recorder] Skipping known non-interactive element:', classNameStr);
            return;
        }
        
        // Skip other container/layout elements only if they don't have event handlers
        const conditionalSkipClasses = [
            'form-group', 'form-row', 'form-control',
            '-container', '-wrapper', '-group', '-section',
            'css-', // Emotion/styled-components
            'MuiBox', 'MuiGrid', 'MuiPaper', // Material-UI
        ];
        
        const hasConditionalSkipClass = conditionalSkipClasses.some(cls => classNameStr.includes(cls));
        if (hasConditionalSkipClass && !target.onclick && !target.getAttribute('onclick')) {
            console.log('[Recorder] Skipping container/layout element click:', classNameStr);
            return;
        }
        
        // Use Smart Detector for framework detection and click deduplication
        const framework = smartDetector.detectFrameworkElements(target);
        if (framework !== 'vanilla') {
            console.log(`[Recorder] 🎯 Detected ${framework} framework element`);
        }
        
        // Use Smart Detector to check if we should skip this element
        if (smartDetector.shouldSkipFrameworkElement(target)) {
            console.log('[Recorder] Skipping framework-specific element via Smart Detector');
            return;
        }
        
        // Deduplicate rapid clicks using Smart Detector
        const shouldRecord = smartDetector.handleClick(target, (element) => {
            // Record the actual click action
            recordAction('click', element);
        });
        
        if (!shouldRecord) {
            return; // Smart Detector prevented duplicate/unwanted click
        }
        
        // Skip clicks on date picker SELECT elements (month/year dropdowns)
        if (target.tagName === 'SELECT') {
            const isDatePickerSelect = 
                target.getAttribute('aria-label')?.toLowerCase().includes('month') ||
                target.getAttribute('aria-label')?.toLowerCase().includes('year') ||
                target.getAttribute('aria-label')?.toLowerCase().includes('day') ||
                target.getAttribute('aria-label')?.toLowerCase().includes('date') ||
                target.classList.contains('ui-datepicker-month') ||
                target.classList.contains('ui-datepicker-year') ||
                target.closest('.datepicker') !== null ||
                target.closest('.ui-datepicker') !== null ||
                target.closest('[class*="date-picker"]') !== null ||
                target.closest('[class*="datepicker"]') !== null;
            
            if (isDatePickerSelect) {
                console.log('[Recorder] ❌ Skipped: Date picker SELECT (month/year dropdown) - will capture final date value');
                return;
            }
        }
        
        // ULTRA STRICT: Only record clicks on ACTUAL actionable elements
        // Absolutely NO divs, spans, or decorative elements
        
        // First check: Is this an actual interactive HTML element?
        const isRealButton = target.tagName === 'BUTTON';
        const isRealLink = target.tagName === 'A' && target.hasAttribute('href');
        const isRealInput = target.tagName === 'INPUT' && (target.type === 'button' || target.type === 'submit');
        const isRealSelect = target.tagName === 'SELECT';
        
        // If it's one of the above REAL elements, record it
        if (isRealButton || isRealLink || isRealInput || isRealSelect) {
            console.log('[Recorder] ✅ Recording REAL interactive element:', target.tagName, target.id || target.className);
            // Continue to record this
        }
        // If it's an icon/svg/img inside a button/link, traverse up
        else if (target.tagName === 'I' || target.tagName === 'SVG' || target.tagName === 'IMG' || target.tagName === 'SPAN' || target.tagName === 'PATH') {
            // Look for parent button/link
            const parentButton = target.closest('button');
            const parentLink = target.closest('a[href]');
            
            if (!parentButton && !parentLink) {
                console.log('[Recorder] ❌ BLOCKED: Icon/span without button/link parent -', target.tagName, target.className);
                return; // Do NOT record standalone icons/spans
            }
            console.log('[Recorder] ✅ Icon inside button/link, will traverse up');
            // Continue to traverse logic below
        }
        // Everything else (divs, spans without button parents, etc.) - BLOCK
        else {
            console.log('[Recorder] ⛔ BLOCKED non-interactive element:', {
                tag: target.tagName,
                class: target.className,
                id: target.id,
                text: target.textContent?.substring(0, 30)
            });
            return;
        }

        // Update last click tracking
        lastClickTime = currentTime;

        // Check if this is a message/toast/alert element
        const messageSelectors = [
            '.toast', '.toastr', '.notification', '.alert', '.message',
            '.success', '.error', '.warning', '.info',
            '[role="alert"]', '[role="status"]',
            '.swal2-container', '.Toastify', '.snackbar',
            '.flash-message', '.banner', '.callout'
        ];
        
        let isMessage = false;
        for (const selector of messageSelectors) {
            if (target.matches(selector) || target.closest(selector)) {
                isMessage = true;
                break;
            }
        }
        
        if (isMessage) {
            // User clicked on a message - capture it for verification
            const messageElement = target.closest(messageSelectors.join(',')) || target;
            console.log('[Recorder] ✅ User clicked on message element - capturing for verification');
            captureMessage(messageElement);
            return; // Don't record as a regular click
        }

        // If clicked on an icon/SVG/img/span inside a button/link, traverse up to find the button
        let clickTarget = target;
        if (target.tagName === 'I' || target.tagName === 'SVG' || target.tagName === 'IMG' || target.tagName === 'SPAN') {
            // Look up to 3 levels for a button
            let current = target;
            let depth = 0;
            while (current && depth < 3) {
                if (current.tagName === 'BUTTON' || 
                    current.tagName === 'A' ||
                    current.classList.contains('btn') ||
                    current.classList.contains('button') ||
                    current.role === 'button') {
                    clickTarget = current;
                    console.log('[Recorder] ✅ Found clickable parent:', clickTarget.tagName, clickTarget.id || clickTarget.className);
                    break;
                }
                current = current.parentElement;
                depth++;
            }
            if (clickTarget === target) {
                console.log('[Recorder] ⚠️ No clickable parent found, recording span/icon directly');
            }
        }
        
        // isActionable check already done earlier in the handler
        // Removed duplicate check to prevent re-declaration error
        
        console.log('[Recorder] ✅ Recording click on:', clickTarget.tagName, clickTarget.id || clickTarget.className);
        
        recordAction('click', clickTarget);
    }, true);

    // Special handler for date picker interactions
    // Detect when user clicks on date picker day cells or when picker closes
    document.addEventListener('click', function(e) {
        if (!isRecording || isPaused) return;
        
        const target = e.target;
        
        // Comprehensive check if this is a date picker related click
        const isDatePickerElement = 
            // Day cells
            target.classList.contains('ui-state-default') || // jQuery UI datepicker
            target.classList.contains('day') || // Bootstrap datepicker
            target.classList.contains('calendar-day') ||
            target.hasAttribute('data-day') ||
            target.hasAttribute('data-date') ||
            target.closest('.ui-datepicker-calendar') !== null ||
            target.closest('.datepicker-days') !== null ||
            target.closest('.datepicker-table') !== null ||
            target.closest('[class*="calendar"]') !== null ||
            target.closest('.react-datepicker__day') !== null ||
            target.closest('.flatpickr-day') !== null ||
            // Calendar container/popup
            target.closest('.ui-datepicker') !== null ||
            target.closest('.datepicker') !== null ||
            target.closest('[class*="date-picker"]') !== null ||
            target.closest('.react-datepicker') !== null ||
            target.closest('.flatpickr-calendar') !== null ||
            // Calendar icon/button
            target.classList.contains('calendar-icon') ||
            target.classList.contains('date-icon') ||
            target.closest('[aria-label*="calendar"]') !== null ||
            target.closest('[aria-label*="date"]') !== null;
        
        if (isDatePickerElement) {
            console.log('[Recorder] Date picker element clicked:', target.className, target.tagName);
            
            // Wait for the input field to update
            setTimeout(() => {
                // Try to find the input field that was just updated
                const dateInputs = document.querySelectorAll(
                    'input[type="date"], ' +
                    'input[type="text"][class*="date"], ' +
                    'input[class*="datepicker"], ' +
                    'input[data-provide="datepicker"], ' +
                    'input[id*="date"], ' +
                    'input[name*="date"]'
                );
                
                for (const input of dateInputs) {
                    const currentValue = input.value;
                    const lastValue = lastInputValues.get(input) || '';
                    
                    if (currentValue && currentValue !== lastValue) {
                        // Found the input that was updated
                        console.log('[Recorder] ✅ Capturing final date value from picker:', currentValue);
                        recordAction('click_and_input', input, currentValue);
                        lastInputValues.set(input, currentValue);
                        const elementKey = `${input.id || input.name || input.className}_${currentValue}`;
                        inputRecordedForElement.add(elementKey);
                        break;
                    }
                }
            }, 300); // Increased delay to allow calendar widgets time to update
        }
    }, true);

    // Capture select, checkbox, and radio events
    document.addEventListener('change', function(e) {
        if (!isRecording || isPaused) return;
        
        const target = e.target;
        
        if (target.tagName === 'SELECT') {
            // Check if this SELECT is part of a date picker widget
            const isDatePickerSelect = 
                target.getAttribute('aria-label')?.toLowerCase().includes('month') ||
                target.getAttribute('aria-label')?.toLowerCase().includes('year') ||
                target.getAttribute('aria-label')?.toLowerCase().includes('day') ||
                target.getAttribute('aria-label')?.toLowerCase().includes('date') ||
                target.classList.contains('ui-datepicker-month') ||
                target.classList.contains('ui-datepicker-year') ||
                target.closest('.datepicker') !== null ||
                target.closest('.ui-datepicker') !== null ||
                target.closest('[class*="date-picker"]') !== null ||
                target.closest('[class*="datepicker"]') !== null;
            
            if (isDatePickerSelect) {
                console.log('[Recorder] Date picker SELECT detected - skipping (will capture final date value):', target.getAttribute('aria-label') || target.id);
                // Don't record date picker select interactions
                return;
            }
            
            console.log('[Recorder] Select changed:', target.id || target.name);
            recordAction('select', target, target.options[target.selectedIndex].text);
        } else if (target.type === 'checkbox') {
            // Record checkbox state change
            console.log('[Recorder] Checkbox changed:', target.id, target.checked);
            recordAction('click', target, target.checked ? 'checked' : 'unchecked');
        } else if (target.type === 'radio') {
            // Record radio button selection
            console.log('[Recorder] Radio changed:', target.id, target.value);
            recordAction('click', target, target.value || 'selected');
        } else if (target.type === 'date' || target.type === 'datetime-local' || 
                   target.type === 'month' || target.type === 'week' || target.type === 'time') {
            // For date/calendar inputs, only track the value change here
            // The final value will be recorded by the focusout handler when user leaves the field
            const currentValue = target.value;
            const lastValue = lastInputValues.get(target) || '';
            
            if (currentValue && currentValue !== lastValue) {
                // Just update the last value - don't record yet
                lastInputValues.set(target, currentValue);
                console.log('[Recorder] Date picker value changed (will record on focusout):', target.id || target.name, currentValue);
            }
        }
    }, true);

    // Capture file upload events
    document.addEventListener('change', function(e) {
        if (!isRecording || isPaused) return;
        
        const target = e.target;
        
        if (target.tagName === 'INPUT' && target.type === 'file') {
            console.log('[Recorder] File input detected:', target.id || target.name);
            if (target.files && target.files.length > 0) {
                // Support multiple files
                const fileCount = target.files.length;
                const fileNames = Array.from(target.files).map(f => f.name).join(', ');
                
                // Record with placeholder - will be replaced at execution time
                // For multiple files, use pipe separator: {{FILE_UPLOAD_1|FILE_UPLOAD_2}}
                const placeholders = [];
                for (let i = 0; i < fileCount; i++) {
                    placeholders.push(`{{FILE_UPLOAD_${actionCount + 1}_${i + 1}}}`);
                }
                const placeholder = placeholders.join('|');
                
                recordAction('upload_file', target, placeholder);
                
                const message = fileCount > 1 
                    ? `${fileCount} files uploaded: ${fileNames} (paths will be provided at execution)`
                    : `File upload recorded: ${fileNames} (path will be provided at execution)`;
                showNotification(message, '#10b981');
                
                // Clear the file input trigger flag
                fileInputTriggered = false;
            }
        }
    }, true);

    // Capture custom calendar library events (jQuery datepicker, flatpickr, etc.)
    // These libraries often use custom events or direct value updates
    document.addEventListener('input', function(e) {
        if (!isRecording || isPaused) return;
        
        const target = e.target;
        
        // Check if this is a calendar/datepicker field
        const isCalendarField = target.classList.contains('datepicker') ||
                               target.classList.contains('flatpickr') ||
                               target.hasAttribute('data-provide') === 'datepicker' ||
                               target.hasAttribute('data-date') ||
                               target.closest('.datepicker') !== null ||
                               target.closest('.flatpickr') !== null;
        
        if (isCalendarField && target.tagName === 'INPUT') {
            const currentValue = target.value;
            const lastValue = lastInputValues.get(target) || '';
            
            // Only update the last value, actual recording happens on focusout
            // This ensures we capture the final selected date, not intermediate states
            if (currentValue && currentValue !== lastValue) {
                console.log('[Recorder] Calendar field value changed (input event):', currentValue);
                // Don't record here - let focusout or change event handle it
                // Just update the tracking so we know it changed
                lastInputValues.set(target, currentValue);
            }
        }
    }, true);

    // Capture drag and drop events
    let draggedElement = null;
    
    document.addEventListener('dragstart', function(e) {
        if (!isRecording || isPaused) return;
        draggedElement = e.target;
        console.log('[Recorder] Drag started:', draggedElement);
    }, true);
    
    document.addEventListener('drop', function(e) {
        if (!isRecording || isPaused || !draggedElement) return;
        
        e.preventDefault();
        const dropTarget = e.target;
        
        console.log('[Recorder] Drop detected:', dropTarget);
        
        // Record drag and drop action
        recordActionWithTarget('drag_and_drop', draggedElement, dropTarget);
        draggedElement = null;
    }, true);
    
    document.addEventListener('dragover', function(e) {
        if (isRecording) {
            e.preventDefault(); // Allow drop
        }
    }, true);

    // Capture form submission during recording - Record but allow navigation
    document.addEventListener('submit', function(e) {
        if (!isRecording || isPaused) {
            return; // Not recording, allow normal submission
        }
        
        console.log('[Recorder] ✅ Form submission detected - Recording and allowing navigation');
        
        // Record the form submission action
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]') || 
                           document.activeElement;
        
        // Find the actual submit button that was clicked
        let clickedSubmit = submitButton;
        if (submitButton && submitButton.form === form) {
            clickedSubmit = submitButton;
        }
        
        // Record the submit button click
        if (clickedSubmit && (clickedSubmit.type === 'submit' || clickedSubmit.tagName === 'BUTTON')) {
            console.log('[Recorder] 📝 Recording submit button click:', clickedSubmit);
            recordAction('click', clickedSubmit, 'submit');
        } else {
            // Fallback: record the form submission directly
            console.log('[Recorder] 📝 Recording form submission');
            recordAction('submit', form, 'form_submit');
        }
        
        // Allow the form to submit normally (navigation will happen)
        // The recording will be saved before the page unloads
        console.log('[Recorder] ✅ Allowing form submission to proceed - page will navigate');
        
    }, true);

    // ============== SCROLL EVENT RECORDING ==============
    let scrollTimeout;
    let lastScrollY = window.scrollY;
    let lastScrollX = window.scrollX;
    
    window.addEventListener('scroll', function(e) {
        console.log('[Recorder] 🔍 SCROLL EVENT FIRED - isRecording:', isRecording, 'isPaused:', isPaused, 'scrollY:', window.scrollY);
        if (!isRecording || isPaused) {
            console.log('[Recorder] ⚠️ Scroll ignored - isRecording:', isRecording, 'isPaused:', isPaused);
            return;
        }
        
        // Debounce scroll events - only record when user stops scrolling
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            const currentScrollY = window.scrollY;
            const currentScrollX = window.scrollX;
            
            console.log('[Recorder] 🔍 SCROLL DEBOUNCE COMPLETE:', {
                currentY: currentScrollY,
                currentX: currentScrollX,
                lastY: lastScrollY,
                lastX: lastScrollX
            });
            
            // Only record if scroll position changed significantly (more than 50px)
            const deltaY = Math.abs(currentScrollY - lastScrollY);
            const deltaX = Math.abs(currentScrollX - lastScrollX);
            
            console.log('[Recorder] 🔍 DELTA:', { deltaY, deltaX, threshold: 50, willRecord: (deltaY > 50 || deltaX > 50) });
            
            if (deltaY > 50 || deltaX > 50) {
                console.log('[Recorder] 📜 Scroll detected:', { x: currentScrollX, y: currentScrollY, deltaY, deltaX });
                
                // Record scroll action with position
                recordAction('scroll', document.body, JSON.stringify({
                    x: currentScrollX,
                    y: currentScrollY,
                    deltaY: deltaY,
                    deltaX: deltaX
                }));
                
                lastScrollY = currentScrollY;
                lastScrollX = currentScrollX;
            } else {
                console.log('[Recorder] ⚠️ Scroll too small - threshold not met (need >50px)', { deltaY, deltaX });
            }
        }, 500); // Wait 500ms after user stops scrolling
    }, { passive: true });

    // Keyboard shortcuts for recorder control
    document.addEventListener('keydown', function(e) {
        // Ctrl+Shift+R - Toggle recording on/off
        if (e.ctrlKey && e.shiftKey && e.key === 'R') {
            e.preventDefault();
            if (isRecording) {
                window.stopRecorderCapture();
                showNotification('Recording Stopped', '#ef4444');
            } else {
                window.startRecorderCapture();
                showNotification('Recording Started', '#10b981');
            }
        }
        
        // Ctrl+Shift+P - Pause/Resume recording
        if (e.ctrlKey && e.shiftKey && e.key === 'P') {
            e.preventDefault();
            if (!isRecording) return;
            
            isPaused = !isPaused;
            const indicator = document.getElementById('recordingIndicator');
            const text = document.getElementById('recordingText');
            
            if (isPaused) {
                if (indicator) indicator.style.background = '#f59e0b';
                if (text) text.textContent = 'Paused...';
                showNotification('Recording Paused', '#f59e0b');
            } else {
                if (indicator) indicator.style.background = '#ef4444';
                if (text) text.textContent = 'Recording...';
                showNotification('Recording Resumed', '#10b981');
            }
        }
        
        // Ctrl+Shift+H - Show/Hide recorder controls
        if (e.ctrlKey && e.shiftKey && e.key === 'H') {
            e.preventDefault();
            const controls = document.getElementById('recorderControls');
            if (controls) {
                controls.style.display = controls.style.display === 'none' ? 'block' : 'none';
            }
        }
        
        // Ctrl+Shift+K - Show keyboard shortcuts help
        if (e.ctrlKey && e.shiftKey && e.key === 'K') {
            e.preventDefault();
            showKeyboardHelp();
        }
    });
    
    // Show notification
    function showNotification(message, color) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 10px;
            background: ${color};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            z-index: 1000000;
            font-family: Arial, sans-serif;
            font-size: 14px;
            font-weight: 600;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
    
    // Show keyboard shortcuts help
    function showKeyboardHelp() {
        const existingHelp = document.getElementById('recorderKeyboardHelp');
        if (existingHelp) {
            existingHelp.remove();
            return;
        }
        
        const helpPanel = document.createElement('div');
        helpPanel.id = 'recorderKeyboardHelp';
        helpPanel.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            color: #333;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            z-index: 1000001;
            font-family: Arial, sans-serif;
            min-width: 400px;
        `;
        
        helpPanel.innerHTML = `
            <h3 style="margin: 0 0 15px 0; color: #667eea; font-size: 18px;">⌨️ Keyboard Shortcuts</h3>
            <div style="font-size: 14px; line-height: 1.8;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <kbd style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-family: monospace;">Ctrl+Shift+R</kbd>
                    <span>Start/Stop Recording</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <kbd style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-family: monospace;">Ctrl+Shift+P</kbd>
                    <span>Pause/Resume Recording</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <kbd style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-family: monospace;">Ctrl+Shift+H</kbd>
                    <span>Hide/Show Controls</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <kbd style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-family: monospace;">Ctrl+Shift+K</kbd>
                    <span>Show This Help</span>
                </div>
            </div>
            <button onclick="document.getElementById('recorderKeyboardHelp').remove()" 
                    style="margin-top: 15px; width: 100%; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
                Got it!
            </button>
        `;
        
        document.body.appendChild(helpPanel);
        
        // Close on Escape
        const closeOnEscape = (e) => {
            if (e.key === 'Escape') {
                helpPanel.remove();
                document.removeEventListener('keydown', closeOnEscape);
            }
        };
        document.addEventListener('keydown', closeOnEscape);
    }

    // Create recorder control panel
    function createRecorderControls() {
        const controls = document.createElement('div');
        controls.id = 'recorderControls';
        controls.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            z-index: 999999;
            font-family: Arial, sans-serif;
            font-size: 14px;
            cursor: move;
            user-select: none;
        `;

        controls.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div id="recordingIndicator" style="width: 12px; height: 12px; background: #ef4444; border-radius: 50%; animation: pulse 1.5s infinite;"></div>
                <span id="recordingText">Recording...</span>
                <span id="actionCounter" style="background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px; font-weight: bold;">0</span>
            </div>
            <button id="stopRecordingBtn" style="width: 100%; padding: 8px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; margin-bottom: 8px; font-size: 13px;">
                ⏹️ Stop Recording (Ctrl+Shift+R)
            </button>
            <div style="font-size: 11px; opacity: 0.8; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 8px;">
                Press <kbd style="background: rgba(255,255,255,0.2); padding: 2px 5px; border-radius: 3px; font-family: monospace;">Ctrl+Shift+K</kbd> for shortcuts
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.3; }
                }
            </style>
        `;

        // Make the panel draggable
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        controls.addEventListener('mousedown', function(e) {
            // Don't start drag if clicking on the stop button
            if (e.target.id === 'stopRecordingBtn' || e.target.closest('#stopRecordingBtn')) {
                return;
            }
            
            isDragging = true;
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
            controls.style.cursor = 'grabbing';
            e.preventDefault();
        });

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                xOffset = currentX;
                yOffset = currentY;
                
                // Update position
                controls.style.transform = `translate(${currentX}px, ${currentY}px)`;
            }
        });

        document.addEventListener('mouseup', function(e) {
            if (isDragging) {
                isDragging = false;
                controls.style.cursor = 'move';
            }
        });

        // Add click handler for stop button
        setTimeout(() => {
            const stopBtn = document.getElementById('stopRecordingBtn');
            if (stopBtn) {
                stopBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    window.stopRecorderCapture();
                });
            }
        }, 100);

        document.body.appendChild(controls);
        
        return controls;
    }

    // Start recording
    window.startRecorderCapture = function() {
        isRecording = true;
        window.isRecording = true;
        actionCount = 0;
        observedMessages.clear();
        
        // Reset scroll tracking when recording starts
        lastScrollY = window.scrollY;
        lastScrollX = window.scrollX;
        console.log('[Recorder] 🔄 Scroll tracking reset to current position:', { x: lastScrollX, y: lastScrollY });
        
        createRecorderControls();
        startMessageObserver();
        startDateInputMonitoring(); // Start monitoring date inputs
        
        // Reset Smart Detector for new session
        smartDetector.reset();
        
        console.log('='.repeat(60));
        console.log('[Recorder] ✅ RECORDING STARTED');
        console.log('[Recorder] Recording state:', {
            isRecording: isRecording,
            apiUrl: API_URL,
            pageUrl: window.location.href,
            eventListeners: 'focusin, focusout, input, click, change, submit'
        });
        console.log('[Recorder] 📝 Interact with the page - all actions will be captured');
        console.log('[Recorder] 🔍 Check console for "🎯", "⌨️", "👋", "📝" emojis to see events');
        console.log('[Recorder] 🧠 Smart Detection: ENABLED (debouncing, framework detection, pattern recognition)');
        console.log('='.repeat(60));
    };

    // Stop recording
    window.stopRecorderCapture = function() {
        if (!isRecording) {
            console.log('[Recorder] Already stopped');
            return;
        }
        
        isRecording = false;
        window.isRecording = false;
        isPaused = false;
        stopDateInputMonitoring(); // Stop monitoring date inputs
        
        const controls = document.getElementById('recorderControls');
        if (controls) {
            controls.remove();
        }
        
        // Stop message observer
        stopMessageObserver();
        
        // Clear tracking data
        activeInputElement = null;
        inputRecordedForElement.clear();
        lastInputValues.clear();
        observedMessages.clear();
        
        // Clear Smart Detector and log stats
        const stats = smartDetector.getStats();
        console.log('[Recorder] 📊 Smart Detector Stats:', stats);
        if (smartDetector.actionGroups.length > 0) {
            console.log('[Recorder] 🎯 Detected Action Patterns:', smartDetector.actionGroups.map(p => p.pattern));
        }
        smartDetector.reset();
        
        console.log(`[Recorder] Stopped. Total actions recorded: ${actionCount}`);
        
        // Notify server to stop recording (synchronize with main UI)
        try {
            fetch(`${API_URL}/recorder/stop`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                mode: 'cors'
            }).then(response => response.json())
              .then(data => {
                  console.log('[Recorder] Server notified of stop:', data);
              })
              .catch(error => {
                  console.error('[Recorder] Failed to notify server:', error);
              });
        } catch (error) {
            console.error('[Recorder] Error notifying server:', error);
        }
        
        // Show notification
        if (typeof showNotification === 'function') {
            showNotification('Recording Stopped', '#ef4444');
        }
    };

    // Observe messages, toasts, alerts
    function startMessageObserver() {
        // Message auto-capture is disabled
        // Messages will only be captured when user explicitly clicks on them
        console.log('[Recorder] Message auto-capture disabled - click on messages to verify them');
    }

    function stopMessageObserver() {
        // No observer to stop since auto-capture is disabled
        console.log('[Recorder] Message observer stopped');
    }

    async function captureMessage(element) {
        // Clone the element to manipulate without affecting the DOM
        const clone = element.cloneNode(true);
        
        // Remove buttons, links, and close icons from the clone
        const buttonsAndLinks = clone.querySelectorAll('button, a, .close, .dismiss, [role="button"], .btn');
        buttonsAndLinks.forEach(el => el.remove());
        
        // Get message text after removing interactive elements
        const messageText = clone.textContent.trim();
        
        // Avoid duplicates and empty messages or very short messages (like single words)
        if (!messageText || messageText.length < 5) {
            console.log('[Recorder] Skipping message - too short or empty:', messageText);
            return;
        }
        
        // Skip if message is just common button text
        const commonButtonTexts = ['hide this', 'close', 'dismiss', 'ok', 'cancel', 'x', '×'];
        if (commonButtonTexts.includes(messageText.toLowerCase())) {
            console.log('[Recorder] Skipping common button text:', messageText);
            return;
        }
        
        const messageKey = `${messageText}_${element.className}`;
        if (observedMessages.has(messageKey)) return;
        
        observedMessages.add(messageKey);

        // Determine message type
        let messageType = 'info';
        const classList = element.className.toLowerCase();
        const role = element.getAttribute('role');
        
        if (classList.includes('error') || classList.includes('danger') || classList.includes('fail')) {
            messageType = 'error';
        } else if (classList.includes('success')) {
            messageType = 'success';
        } else if (classList.includes('warning') || classList.includes('warn')) {
            messageType = 'warning';
        } else if (role === 'alert') {
            messageType = 'alert';
        }

        console.log(`[Recorder] Captured ${messageType} message:`, messageText);

        // Record as verify action
        try {
            const response = await fetch(`${API_URL}/recorder/record-action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action_type: 'verify_message',
                    element: {
                        tagName: element.tagName.toLowerCase(),
                        className: element.className,
                        xpath: getXPath(element)
                    },
                    value: messageText,
                    message_type: messageType
                }),
                mode: 'cors'
            });

            const data = await response.json();
            
            if (data.total_actions !== undefined) {
                actionCount = data.total_actions;
                // Update the counter display in browser controls
                const counterElement = document.getElementById('actionCounter');
                if (counterElement) {
                    counterElement.textContent = actionCount;
                }
            }

            // Visual feedback
            element.style.outline = '3px solid #10b981';
            setTimeout(() => {
                element.style.outline = '';
            }, 1000);

        } catch (error) {
            console.error('[Recorder] Error recording message:', error);
        }
    }

    // Update action counter
    setInterval(() => {
        const counter = document.getElementById('actionCounter');
        if (counter) {
            counter.textContent = actionCount;
        }
    }, 100);

    console.log('[Recorder] Injection script loaded. Use window.startRecorderCapture() to begin.');
})();
