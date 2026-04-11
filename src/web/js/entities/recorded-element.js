/**
 * RecordedElement Entity
 * Represents a DOM element with multiple locator strategies and context information
 */

class RecordedElement {
    constructor(element) {
        // Handle both DOM elements and plain objects
        if (element instanceof Element || (element && element.nodeType === 1)) {
            this.fromDOMElement(element);
        } else if (typeof element === 'object' && element !== null) {
            this.fromObject(element);
        } else {
            this.initEmpty();
        }
    }

    /**
     * Initialize from a DOM element
     */
    fromDOMElement(element) {
        this.tagName = element.tagName?.toLowerCase();
        this.attributes = this.extractAttributes(element);
        this.text = this.extractText(element);
        this.xpath = this.generateXPath(element);
        this.cssSelector = this.generateCSSSelector(element);
        this.locators = this.generateAllLocators(element);
        this.context = this.getElementContext(element);
        this.framework = this.detectFramework(element);
        this.position = this.getPosition(element);
    }

    /**
     * Initialize from plain object
     */
    fromObject(obj) {
        this.tagName = obj.tagName;
        this.attributes = obj.attributes || {};
        this.text = obj.text;
        this.xpath = obj.xpath;
        this.cssSelector = obj.cssSelector;
        this.locators = obj.locators || {};
        this.context = obj.context || {};
        this.framework = obj.framework || 'vanilla';
        this.position = obj.position || {};
    }

    /**
     * Initialize empty element
     */
    initEmpty() {
        this.tagName = '';
        this.attributes = {};
        this.text = '';
        this.xpath = '';
        this.cssSelector = '';
        this.locators = {};
        this.context = {};
        this.framework = 'vanilla';
        this.position = {};
    }

    /**
     * Extract all relevant attributes
     */
    extractAttributes(element) {
        const attrs = {};
        
        // Standard attributes
        if (element.id) attrs.id = element.id;
        if (element.name) attrs.name = element.name;
        if (element.className) attrs.className = element.className;
        if (element.type) attrs.type = element.type;
        if (element.href) attrs.href = element.href;
        if (element.src) attrs.src = element.src;
        if (element.value) attrs.value = element.value;
        if (element.placeholder) attrs.placeholder = element.placeholder;
        if (element.title) attrs.title = element.title;
        if (element.alt) attrs.alt = element.alt;
        
        // ARIA attributes
        if (element.getAttribute('aria-label')) attrs.ariaLabel = element.getAttribute('aria-label');
        if (element.getAttribute('aria-labelledby')) attrs.ariaLabelledby = element.getAttribute('aria-labelledby');
        if (element.getAttribute('aria-describedby')) attrs.ariaDescribedby = element.getAttribute('aria-describedby');
        if (element.role) attrs.role = element.role;
        
        // Data attributes
        if (element.dataset) {
            Object.keys(element.dataset).forEach(key => {
                attrs[`data-${key}`] = element.dataset[key];
            });
        }
        
        return attrs;
    }

    /**
     * Extract text content safely
     */
    extractText(element) {
        const text = element.textContent?.trim() || '';
        const innerText = element.innerText?.trim() || '';
        
        // Return the shorter one (usually more relevant)
        if (text.length > 0 && innerText.length > 0) {
            return text.length < innerText.length ? text : innerText;
        }
        return text || innerText || '';
    }

    /**
     * Generate XPath for element
     */
    generateXPath(element) {
        // Prioritize ID if available
        if (element.id) {
            return `//*[@id="${element.id}"]`;
        }
        
        // Generate path from root
        const segments = [];
        let currentElement = element;
        
        while (currentElement && currentElement.nodeType === Node.ELEMENT_NODE) {
            let index = 0;
            let sibling = currentElement.previousSibling;
            
            while (sibling) {
                if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === currentElement.tagName) {
                    index++;
                }
                sibling = sibling.previousSibling;
            }
            
            const tagName = currentElement.tagName.toLowerCase();
            const pathIndex = index > 0 ? `[${index + 1}]` : '';
            segments.unshift(`${tagName}${pathIndex}`);
            
            currentElement = currentElement.parentElement;
        }
        
        return segments.length > 0 ? '/' + segments.join('/') : '';
    }

    /**
     * Generate CSS selector for element
     */
    generateCSSSelector(element) {
        // ID selector (highest priority)
        if (element.id) {
            return `#${CSS.escape(element.id)}`;
        }
        
        // Try to build a unique selector
        const segments = [];
        let current = element;
        
        while (current && current !== document.documentElement) {
            let selector = current.tagName.toLowerCase();
            
            // Add class if available and not too generic
            if (current.className && typeof current.className === 'string') {
                const classes = current.className.trim().split(/\s+/).filter(c => 
                    c && !c.startsWith('ng-') && !c.startsWith('v-') && !c.startsWith('react-')
                );
                if (classes.length > 0) {
                    selector += '.' + classes.map(c => CSS.escape(c)).join('.');
                }
            }
            
            // Add name attribute if available
            if (current.name) {
                selector += `[name="${CSS.escape(current.name)}"]`;
            }
            
            segments.unshift(selector);
            
            // Stop if we have a unique selector
            if (current.id || (current.name && current.tagName === 'INPUT')) {
                break;
            }
            
            current = current.parentElement;
        }
        
        return segments.join(' > ');
    }

    /**
     * Generate all possible locators
     */
    generateAllLocators(element) {
        const locators = {};
        
        // ID locator
        if (this.attributes.id) {
            locators.id = this.attributes.id;
            locators.idFull = `By.id("${this.attributes.id}")`;
        }
        
        // Name locator
        if (this.attributes.name) {
            locators.name = this.attributes.name;
            locators.nameFull = `By.name("${this.attributes.name}")`;
        }
        
        // Class locator (smart)
        if (this.attributes.className) {
            const smartClass = this.smartClassSelector(element);
            if (smartClass) {
                locators.className = smartClass;
                locators.classNameFull = `By.className("${smartClass}")`;
            }
        }
        
        // XPath locator
        locators.xpath = this.xpath;
        locators.xpathFull = `By.xpath("${this.escapeString(this.xpath)}")`;
        
        // CSS selector
        locators.cssSelector = this.cssSelector;
        locators.cssSelectorFull = `By.cssSelector("${this.escapeString(this.cssSelector)}")`;
        
        // Link text (for links)
        if (this.tagName === 'a' && this.text) {
            locators.linkText = this.text;
            locators.linkTextFull = `By.linkText("${this.escapeString(this.text)}")`;
            
            if (this.text.length > 20) {
                const partial = this.text.substring(0, 15);
                locators.partialLinkText = partial;
                locators.partialLinkTextFull = `By.partialLinkText("${this.escapeString(partial)}")`;
            }
        }
        
        // ARIA label
        if (this.attributes.ariaLabel) {
            locators.ariaLabel = this.attributes.ariaLabel;
            locators.ariaLabelFull = `By.cssSelector("[aria-label='${this.escapeString(this.attributes.ariaLabel)}']")`;
        }
        
        // Data test ID
        if (this.attributes['data-testid']) {
            locators.dataTestId = this.attributes['data-testid'];
            locators.dataTestIdFull = `By.cssSelector("[data-testid='${this.attributes['data-testid']}']")`;
        }
        
        // Button/input by text
        if ((this.tagName === 'button' || this.tagName === 'input') && this.text) {
            locators.byText = `By.xpath("//${this.tagName}[contains(normalize-space(.), '${this.escapeString(this.text)}')]")`;
        }
        
        return locators;
    }

    /**
     * Get smart class selector (filter out framework classes)
     */
    smartClassSelector(element) {
        if (!element.className || typeof element.className !== 'string') return null;
        
        const classes = element.className.trim().split(/\s+/).filter(c => {
            // Filter out framework-specific and dynamic classes
            return c && 
                !c.startsWith('ng-') && 
                !c.startsWith('v-') && 
                !c.startsWith('react-') &&
                !c.match(/^[a-f0-9]{6,}$/) && // Likely hash
                !c.includes('active') &&
                !c.includes('selected') &&
                !c.includes('hover');
        });
        
        return classes.length > 0 ? classes.join('.') : null;
    }

    /**
     * Get element context (parent, siblings)
     */
    getElementContext(element) {
        return {
            parent: element.parentElement ? {
                tagName: element.parentElement.tagName?.toLowerCase(),
                id: element.parentElement.id,
                className: element.parentElement.className
            } : null,
            previousSibling: element.previousElementSibling ? {
                tagName: element.previousElementSibling.tagName?.toLowerCase()
            } : null,
            nextSibling: element.nextElementSibling ? {
                tagName: element.nextElementSibling.tagName?.toLowerCase()
            } : null
        };
    }

    /**
     * Detect framework (React, Vue, Angular, etc.)
     */
    detectFramework(element) {
        let current = element;
        
        while (current) {
            // Check for React
            if (current.hasOwnProperty('_reactRootContainer') || 
                current.hasOwnProperty('__reactInternalInstance') ||
                Object.keys(current).some(key => key.startsWith('__react'))) {
                return 'react';
            }
            
            // Check for Vue
            if (current.__vue__ || current.hasAttribute('data-v-')) {
                return 'vue';
            }
            
            // Check for Angular
            if (current.hasAttribute('ng-version') || 
                Array.from(current.attributes || []).some(attr => attr.name.startsWith('ng-'))) {
                return 'angular';
            }
            
            current = current.parentElement;
        }
        
        return 'vanilla';
    }

    /**
     * Get element position
     */
    getPosition(element) {
        const rect = element.getBoundingClientRect();
        return {
            x: rect.left + window.scrollX,
            y: rect.top + window.scrollY,
            width: rect.width,
            height: rect.height
        };
    }

    /**
     * Get best locator based on format and priority
     */
    getBestLocator(format = 'java') {
        // Priority order
        const priorities = [
            'dataTestIdFull',
            'idFull',
            'ariaLabelFull',
            'nameFull',
            'linkTextFull',
            'classNameFull',
            'cssSelectorFull',
            'xpathFull'
        ];
        
        // For playwright/cypress, prefer CSS selectors
        if (format === 'playwright' || format === 'cypress') {
            if (this.locators.dataTestId) return `[data-testid="${this.locators.dataTestId}"]`;
            if (this.attributes.id) return `#${this.attributes.id}`;
            if (this.locators.ariaLabel) return `[aria-label="${this.escapeString(this.locators.ariaLabel)}"]`;
            return this.cssSelector;
        }
        
        // For Python
        if (format === 'python') {
            for (const key of priorities) {
                if (this.locators[key]) {
                    return this.locators[key].replace('By.', 'By.');
                }
            }
        }
        
        // For Java (default)
        for (const key of priorities) {
            if (this.locators[key]) {
                return this.locators[key];
            }
        }
        
        return this.locators.xpathFull || `By.xpath("${this.xpath}")`;
    }

    /**
     * Get best locator as an object with type and value properties
     * Used for code generation where we need to construct locators programmatically
     * 
     * @returns {Object} Object with 'type' (e.g., 'ID', 'XPATH', 'CSS_SELECTOR') and 'value' properties
     */
    getBestLocatorObject() {
        // Priority order: prefer more stable locators
        if (this.locators.dataTestId) {
            return { type: 'CSS_SELECTOR', value: `[data-testid="${this.locators.dataTestId}"]` };
        }
        
        if (this.attributes.id) {
            return { type: 'ID', value: this.attributes.id };
        }
        
        if (this.attributes.ariaLabel) {
            return { type: 'CSS_SELECTOR', value: `[aria-label="${this.escapeString(this.attributes.ariaLabel)}"]` };
        }
        
        if (this.attributes.name) {
            return { type: 'NAME', value: this.attributes.name };
        }
        
        if (this.locators.linkText) {
            return { type: 'LINK_TEXT', value: this.locators.linkText };
        }
        
        if (this.locators.className) {
            return { type: 'CLASS_NAME', value: this.locators.className };
        }
        
        if (this.cssSelector) {
            return { type: 'CSS_SELECTOR', value: this.cssSelector };
        }
        
        // Fallback to XPath
        return { type: 'XPATH', value: this.xpath || '//*' };
    }

    /**
     * Get a human-readable description
     */
    getDescription() {
        if (this.attributes.id) return `element with ID "${this.attributes.id}"`;
        if (this.attributes.name) return `${this.tagName} with name "${this.attributes.name}"`;
        if (this.text) return `${this.tagName} with text "${this.text.substring(0, 30)}"`;
        if (this.attributes.ariaLabel) return `element with aria-label "${this.attributes.ariaLabel}"`;
        return `${this.tagName} element`;
    }

    /**
     * Escape string for code generation
     */
    escapeString(str) {
        if (!str) return '';
        return str.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');
    }

    /**
     * Convert to JSON-serializable object
     */
    toJSON() {
        return {
            tagName: this.tagName,
            attributes: this.attributes,
            text: this.text,
            xpath: this.xpath,
            cssSelector: this.cssSelector,
            locators: this.locators,
            context: this.context,
            framework: this.framework,
            position: this.position
        };
    }

    /**
     * Create element from JSON
     */
    static fromJSON(json) {
        return new RecordedElement(json);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RecordedElement;
}
