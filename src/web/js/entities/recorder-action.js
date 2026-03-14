/**
 * RecorderAction Entity
 * Represents a single user action captured during recording
 */

class RecorderAction {
    constructor(config) {
        this.id = config.id || this.generateUUID();
        this.sessionId = config.sessionId;
        this.step = config.step;
        this.type = config.type; // click, input, select, navigate, scroll, hover, etc.
        this.element = config.element instanceof RecordedElement 
            ? config.element 
            : new RecordedElement(config.element || {});
        this.value = config.value;
        this.metadata = {
            timestamp: config.timestamp || Date.now(),
            duration: config.duration || 0,
            frameId: config.frameId || null,
            scrollPosition: config.scrollPosition || { x: window.scrollX, y: window.scrollY },
            viewport: config.viewport || { width: window.innerWidth, height: window.innerHeight }
        };
        this.assertions = config.assertions || [];
        this.screenshot = config.screenshot || null;
        this.notes = config.notes || '';
    }

    /**
     * Add an assertion/verification to this action
     */
    addAssertion(assertion) {
        this.assertions.push({
            type: assertion.type, // contains, equals, visible, enabled, etc.
            expected: assertion.expected,
            actual: assertion.actual,
            timestamp: Date.now()
        });
    }

    /**
     * Generate code for this action in specified format
     */
    toCode(format = 'java', options = {}) {
        const generators = {
            java: () => this.generateJavaCode(options),
            python: () => this.generatePythonCode(options),
            javascript: () => this.generateJavaScriptCode(options),
            playwright: () => this.generatePlaywrightCode(options),
            cypress: () => this.generateCypressCode(options)
        };

        const generator = generators[format];
        if (!generator) {
            return `// Unsupported format: ${format}`;
        }

        return generator();
    }

    /**
     * Generate Java/Selenium code
     */
    generateJavaCode(options = {}) {
        const locator = this.element.getBestLocator('java');
        const timeout = options.timeout || 10;

        let code = '';
        
        // Add wait if configured
        if (options.useExplicitWait) {
            code += `wait.until(ExpectedConditions.presenceOfElementLocated(${locator}));\n        `;
        }

        switch (this.type) {
            case 'click':
                code += `driver.findElement(${locator}).click();`;
                break;
            
            case 'input':
            case 'click_and_input':
                code += `driver.findElement(${locator}).clear();\n        `;
                code += `driver.findElement(${locator}).sendKeys("${this.escapeString(this.value)}");`;
                break;
            
            case 'select':
                code += `new Select(driver.findElement(${locator})).selectByVisibleText("${this.escapeString(this.value)}");`;
                break;
            
            case 'navigate':
                code += `driver.get("${this.value}");`;
                break;
            
            case 'hover':
                code += `new Actions(driver).moveToElement(driver.findElement(${locator})).perform();`;
                break;
            
            case 'drag_and_drop':
                code += `new Actions(driver).dragAndDrop(driver.findElement(${locator}), driver.findElement(${this.metadata.targetLocator})).perform();`;
                break;
            
            case 'scroll':
                code += `((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView(true);", driver.findElement(${locator}));`;
                break;
            
            case 'verify_message':
            case 'assertion':
                code += `Assert.assertTrue(driver.findElement(${locator}).getText().contains("${this.escapeString(this.value)}"));`;
                break;
            
            default:
                code += `// ${this.type}: ${this.value || ''}`;
        }

        // Add assertions if present
        this.assertions.forEach(assertion => {
            code += `\n        ${this.generateJavaAssertion(assertion, locator)}`;
        });

        return code;
    }

    /**
     * Generate Python/Selenium code
     */
    generatePythonCode(options = {}) {
        const locator = this.element.getBestLocator('python');

        let code = '';

        if (options.useExplicitWait) {
            code += `WebDriverWait(driver, 10).until(EC.presence_of_element_located((${locator})))\n    `;
        }

        switch (this.type) {
            case 'click':
                code += `driver.find_element(${locator}).click()`;
                break;
            
            case 'input':
            case 'click_and_input':
                code += `element = driver.find_element(${locator})\n    `;
                code += `element.clear()\n    `;
                code += `element.send_keys("${this.escapeString(this.value)}")`;
                break;
            
            case 'select':
                code += `Select(driver.find_element(${locator})).select_by_visible_text("${this.escapeString(this.value)}")`;
                break;
            
            case 'navigate':
                code += `driver.get("${this.value}")`;
                break;
            
            case 'hover':
                code += `ActionChains(driver).move_to_element(driver.find_element(${locator})).perform()`;
                break;
            
            case 'scroll':
                code += `driver.execute_script("arguments[0].scrollIntoView(true);", driver.find_element(${locator}))`;
                break;
            
            case 'verify_message':
            case 'assertion':
                code += `assert "${this.escapeString(this.value)}" in driver.find_element(${locator}).text`;
                break;
            
            default:
                code += `# ${this.type}: ${this.value || ''}`;
        }

        return code;
    }

    /**
     * Generate JavaScript/Playwright code
     */
    generateJavaScriptCode(options = {}) {
        return this.generatePlaywrightCode(options);
    }

    /**
     * Generate Playwright code
     */
    generatePlaywrightCode(options = {}) {
        const locator = this.element.getBestLocator('playwright');

        let code = '';

        switch (this.type) {
            case 'click':
                code += `await page.locator('${locator}').click();`;
                break;
            
            case 'input':
            case 'click_and_input':
                code += `await page.locator('${locator}').fill('${this.escapeString(this.value)}');`;
                break;
            
            case 'select':
                code += `await page.locator('${locator}').selectOption('${this.escapeString(this.value)}');`;
                break;
            
            case 'navigate':
                code += `await page.goto('${this.value}');`;
                break;
            
            case 'hover':
                code += `await page.locator('${locator}').hover();`;
                break;
            
            case 'scroll':
                code += `await page.locator('${locator}').scrollIntoViewIfNeeded();`;
                break;
            
            case 'verify_message':
            case 'assertion':
                code += `await expect(page.locator('${locator}')).toContainText('${this.escapeString(this.value)}');`;
                break;
            
            default:
                code += `// ${this.type}: ${this.value || ''}`;
        }

        return code;
    }

    /**
     * Generate Cypress code
     */
    generateCypressCode(options = {}) {
        const locator = this.element.getBestLocator('cypress');

        let code = '';

        switch (this.type) {
            case 'click':
                code += `cy.get('${locator}').click();`;
                break;
            
            case 'input':
            case 'click_and_input':
                code += `cy.get('${locator}').clear().type('${this.escapeString(this.value)}');`;
                break;
            
            case 'select':
                code += `cy.get('${locator}').select('${this.escapeString(this.value)}');`;
                break;
            
            case 'navigate':
                code += `cy.visit('${this.value}');`;
                break;
            
            case 'hover':
                code += `cy.get('${locator}').trigger('mouseover');`;
                break;
            
            case 'scroll':
                code += `cy.get('${locator}').scrollIntoView();`;
                break;
            
            case 'verify_message':
            case 'assertion':
                code += `cy.get('${locator}').should('contain', '${this.escapeString(this.value)}');`;
                break;
            
            default:
                code += `// ${this.type}: ${this.value || ''}`;
        }

        return code;
    }

    /**
     * Generate Java assertion code
     */
    generateJavaAssertion(assertion, locator) {
        switch (assertion.type) {
            case 'contains':
                return `Assert.assertTrue(driver.findElement(${locator}).getText().contains("${this.escapeString(assertion.expected)}"));`;
            case 'equals':
                return `Assert.assertEquals(driver.findElement(${locator}).getText(), "${this.escapeString(assertion.expected)}");`;
            case 'visible':
                return `Assert.assertTrue(driver.findElement(${locator}).isDisplayed());`;
            case 'enabled':
                return `Assert.assertTrue(driver.findElement(${locator}).isEnabled());`;
            default:
                return `// Unknown assertion type: ${assertion.type}`;
        }
    }

    /**
     * Get a description of this action
     */
    getDescription() {
        switch (this.type) {
            case 'click':
                return `Click ${this.element.getDescription()}`;
            case 'input':
            case 'click_and_input':
                return `Type "${this.value}" into ${this.element.getDescription()}`;
            case 'select':
                return `Select "${this.value}" from ${this.element.getDescription()}`;
            case 'navigate':
                return `Navigate to ${this.value}`;
            case 'hover':
                return `Hover over ${this.element.getDescription()}`;
            case 'scroll':
                return `Scroll to ${this.element.getDescription()}`;
            case 'verify_message':
                return `Verify message: "${this.value}"`;
            default:
                return `${this.type} on ${this.element.getDescription()}`;
        }
    }

    // Helper methods
    generateUUID() {
        return 'action_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    escapeString(str) {
        if (!str) return '';
        return str.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '');
    }

    /**
     * Convert to JSON-serializable object
     */
    toJSON() {
        return {
            id: this.id,
            sessionId: this.sessionId,
            step: this.step,
            type: this.type,
            element: this.element.toJSON ? this.element.toJSON() : this.element,
            value: this.value,
            metadata: this.metadata,
            assertions: this.assertions,
            screenshot: this.screenshot,
            notes: this.notes
        };
    }

    /**
     * Create action from JSON
     */
    static fromJSON(json) {
        return new RecorderAction(json);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RecorderAction;
}
