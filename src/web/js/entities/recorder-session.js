/**
 * RecorderSession Entity
 * Represents a complete recording session with all actions and metadata
 */

class RecorderSession {
    constructor(config) {
        this.id = config.id || this.generateUUID();
        this.name = config.name || `Test_${Date.now()}`;
        this.module = config.module || 'default';
        this.url = config.url;
        this.actions = config.actions || [];
        this.metadata = {
            browser: config.browser || 'chrome',
            viewport: config.viewport || { width: window.innerWidth, height: window.innerHeight },
            userAgent: navigator.userAgent,
            createdAt: config.createdAt || Date.now(),
            updatedAt: Date.now(),
            duration: config.duration || 0,
            status: config.status || 'active' // active, paused, stopped, completed
        };
        this.tags = config.tags || [];
        this.variables = new Map(config.variables || []); // Store dynamic variables
        this.screenshots = config.screenshots || [];
    }

    /**
     * Add an action to the session
     */
    addAction(actionConfig) {
        const action = new RecorderAction({
            ...actionConfig,
            sessionId: this.id,
            step: this.actions.length + 1
        });
        
        this.actions.push(action);
        this.metadata.updatedAt = Date.now();
        return action;
    }

    /**
     * Remove an action by step number
     */
    removeAction(step) {
        this.actions = this.actions.filter(a => a.step !== step);
        this.reindexSteps();
        this.metadata.updatedAt = Date.now();
    }

    /**
     * Update an action
     */
    updateAction(step, updates) {
        const action = this.actions.find(a => a.step === step);
        if (action) {
            Object.assign(action, updates);
            this.metadata.updatedAt = Date.now();
        }
        return action;
    }

    /**
     * Reindex all action steps sequentially
     */
    reindexSteps() {
        this.actions.forEach((action, index) => {
            action.step = index + 1;
        });
    }

    /**
     * Get action by step number
     */
    getAction(step) {
        return this.actions.find(a => a.step === step);
    }

    /**
     * Get all actions of a specific type
     */
    getActionsByType(type) {
        return this.actions.filter(a => a.type === type);
    }

    /**
     * Calculate session duration
     */
    calculateDuration() {
        if (this.actions.length === 0) return 0;
        const firstAction = this.actions[0];
        const lastAction = this.actions[this.actions.length - 1];
        return lastAction.metadata.timestamp - firstAction.metadata.timestamp;
    }

    /**
     * Update session status
     */
    setStatus(status) {
        this.metadata.status = status;
        this.metadata.updatedAt = Date.now();
        
        if (status === 'completed' || status === 'stopped') {
            this.metadata.duration = this.calculateDuration();
        }
    }

    /**
     * Export session in specified format
     */
    export(format = 'java') {
        const exporters = {
            java: () => this.exportJava(),
            python: () => this.exportPython(),
            javascript: () => this.exportJavaScript(),
            cypress: () => this.exportCypress(),
            json: () => this.exportJSON()
        };
        
        const exporter = exporters[format];
        if (!exporter) {
            throw new Error(`Unsupported export format: ${format}`);
        }
        
        return exporter();
    }

    /**
     * Export as Java TestNG
     */
    exportJava() {
        const className = this.toPascalCase(this.name);
        const methodName = this.toCamelCase(this.name);
        
        let code = `package com.automation.tests.${this.module};\n\n`;
        code += `import org.testng.annotations.*;\n`;
        code += `import org.openqa.selenium.*;\n`;
        code += `import org.openqa.selenium.chrome.ChromeDriver;\n\n`;
        code += `public class ${className} {\n`;
        code += `    private WebDriver driver;\n\n`;
        code += `    @BeforeMethod\n`;
        code += `    public void setUp() {\n`;
        code += `        driver = new ChromeDriver();\n`;
        code += `        driver.manage().window().maximize();\n`;
        code += `    }\n\n`;
        code += `    @Test\n`;
        code += `    public void ${methodName}() {\n`;
        code += `        driver.get("${this.url}");\n`;
        
        this.actions.forEach(action => {
            const actionCode = this.generateJavaCode(action);
            code += `        ${actionCode}\n`;
        });
        
        code += `    }\n\n`;
        code += `    @AfterMethod\n`;
        code += `    public void tearDown() {\n`;
        code += `        if (driver != null) {\n`;
        code += `            driver.quit();\n`;
        code += `        }\n`;
        code += `    }\n`;
        code += `}\n`;
        
        return code;
    }

    /**
     * Export as Python Pytest
     */
    exportPython() {
        const testName = this.toSnakeCase(this.name);
        
        let code = `import pytest\n`;
        code += `from selenium import webdriver\n`;
        code += `from selenium.webdriver.common.by import By\n`;
        code += `from selenium.webdriver.support.ui import WebDriverWait\n`;
        code += `from selenium.webdriver.support import expected_conditions as EC\n\n`;
        code += `@pytest.fixture\n`;
        code += `def driver():\n`;
        code += `    driver = webdriver.Chrome()\n`;
        code += `    driver.maximize_window()\n`;
        code += `    yield driver\n`;
        code += `    driver.quit()\n\n`;
        code += `def test_${testName}(driver):\n`;
        code += `    driver.get("${this.url}")\n`;
        
        this.actions.forEach(action => {
            const actionCode = this.generatePythonCode(action);
            code += `    ${actionCode}\n`;
        });
        
        return code;
    }

    /**
     * Export as JavaScript/Playwright  
     */
    exportJavaScript() {
        const testName = this.toCamelCase(this.name);
        
        let code = `const { test, expect } = require('@playwright/test');\n\n`;
        code += `test('${testName}', async ({ page }) => {\n`;
        code += `    await page.goto('${this.url}');\n`;
        
        this.actions.forEach(action => {
            const actionCode = this.generateJavaScriptCode(action);
            code += `    ${actionCode}\n`;
        });
        
        code += `});\n`;
        
        return code;
    }

    /**
     * Export as Cypress
     */
    exportCypress() {
        const testName = this.name;
        
        let code = `describe('${testName}', () => {\n`;
        code += `    it('should complete the test', () => {\n`;
        code += `        cy.visit('${this.url}');\n`;
        
        this.actions.forEach(action => {
            const actionCode = this.generateCypressCode(action);
            code += `        ${actionCode}\n`;
        });
        
        code += `    });\n`;
        code += `});\n`;
        
        return code;
    }

    /**
     * Export as JSON
     */
    exportJSON() {
        return JSON.stringify({
            id: this.id,
            name: this.name,
            module: this.module,
            url: this.url,
            actions: this.actions.map(a => a.toJSON()),
            metadata: {
                ...this.metadata,
                viewport: this.metadata.viewport
            },
            tags: this.tags,
            variables: Array.from(this.variables.entries())
        }, null, 2);
    }

    /**
     * Generate Java code for an action
     */
    generateJavaCode(action) {
        const locator = action.element.getBestLocator('java');
        
        switch (action.type) {
            case 'click':
                return `driver.findElement(${locator}).click();`;
            case 'input':
            case 'click_and_input':
                return `driver.findElement(${locator}).sendKeys("${this.escapeString(action.value)}");`;
            case 'select':
                return `new Select(driver.findElement(${locator})).selectByVisibleText("${this.escapeString(action.value)}");`;
            case 'navigate':
                return `driver.get("${action.value}");`;
            case 'verify_message':
                return `Assert.assertTrue(driver.findElement(${locator}).getText().contains("${this.escapeString(action.value)}"));`;
            default:
                return `// ${action.type}: ${action.value || ''}`;
        }
    }

    /**
     * Generate Python code for an action
     */
    generatePythonCode(action) {
        const locator = action.element.getBestLocator('python');
        
        switch (action.type) {
            case 'click':
                return `driver.find_element(${locator}).click()`;
            case 'input':
            case 'click_and_input':
                return `driver.find_element(${locator}).send_keys("${this.escapeString(action.value)}")`;
            case 'select':
                return `Select(driver.find_element(${locator})).select_by_visible_text("${this.escapeString(action.value)}")`;
            case 'navigate':
                return `driver.get("${action.value}")`;
            case 'verify_message':
                return `assert "${this.escapeString(action.value)}" in driver.find_element(${locator}).text`;
            default:
                return `# ${action.type}: ${action.value || ''}`;
        }
    }

    /**
     * Generate JavaScript/Playwright code for an action
     */
    generateJavaScriptCode(action) {
        const locator = action.element.getBestLocator('playwright');
        
        switch (action.type) {
            case 'click':
                return `await page.locator('${locator}').click();`;
            case 'input':
            case 'click_and_input':
                return `await page.locator('${locator}').fill('${this.escapeString(action.value)}');`;
            case 'select':
                return `await page.locator('${locator}').selectOption('${this.escapeString(action.value)}');`;
            case 'navigate':
                return `await page.goto('${action.value}');`;
            case 'verify_message':
                return `await expect(page.locator('${locator}')).toContainText('${this.escapeString(action.value)}');`;
            default:
                return `// ${action.type}: ${action.value || ''}`;
        }
    }

    /**
     * Generate Cypress code for an action
     */
    generateCypressCode(action) {
        const locator = action.element.getBestLocator('cypress');
        
        switch (action.type) {
            case 'click':
                return `cy.get('${locator}').click();`;
            case 'input':
            case 'click_and_input':
                return `cy.get('${locator}').type('${this.escapeString(action.value)}');`;
            case 'select':
                return `cy.get('${locator}').select('${this.escapeString(action.value)}');`;
            case 'navigate':
                return `cy.visit('${action.value}');`;
            case 'verify_message':
                return `cy.get('${locator}').should('contain', '${this.escapeString(action.value)}');`;
            default:
                return `// ${action.type}: ${action.value || ''}`;
        }
    }

    // Helper methods
    generateUUID() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    toPascalCase(str) {
        return str.replace(/\w+/g, w => w[0].toUpperCase() + w.slice(1).toLowerCase()).replace(/\s+/g, '');
    }

    toCamelCase(str) {
        const pascal = this.toPascalCase(str);
        return pascal[0].toLowerCase() + pascal.slice(1);
    }

    toSnakeCase(str) {
        return str.replace(/\s+/g, '_').toLowerCase();
    }

    escapeString(str) {
        if (!str) return '';
        return str.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');
    }

    /**
     * Convert to JSON-serializable object
     */
    toJSON() {
        return {
            id: this.id,
            name: this.name,
            module: this.module,
            url: this.url,
            actions: this.actions.map(a => a.toJSON ? a.toJSON() : a),
            metadata: this.metadata,
            tags: this.tags,
            variables: Array.from(this.variables.entries()),
            screenshots: this.screenshots
        };
    }

    /**
     * Create session from JSON
     */
    static fromJSON(json) {
        const config = {
            ...json,
            variables: new Map(json.variables || [])
        };
        return new RecorderSession(config);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RecorderSession;
}
