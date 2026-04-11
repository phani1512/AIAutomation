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
        code += `import org.openqa.selenium.chrome.ChromeDriver;\n`;
        code += `import org.openqa.selenium.support.ui.Select;\n`;
        code += `import org.openqa.selenium.interactions.Actions;\n\n`;
        code += `public class ${className} {\n`;
        code += `    private WebDriver driver;\n\n`;
        code += `    @BeforeMethod\n`;
        code += `    public void setUp() {\n`;
        code += `        driver = new ChromeDriver();\n`;
        code += `        driver.manage().window().maximize();\n`;
        code += `    }\n\n`;
        code += `    @Test\n`;
        code += `    public void ${methodName}() throws InterruptedException {\n`;
        code += `        driver.get("${this.url}");\n`;
        
        this.actions.forEach((action, index) => {
            const actionCode = this.generateJavaCode(action, index + 1);
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
        code += `import time\n`;
        code += `from selenium import webdriver\n`;
        code += `from selenium.webdriver.common.by import By\n`;
        code += `from selenium.webdriver.support.ui import WebDriverWait\n`;
        code += `from selenium.webdriver.support import expected_conditions as EC\n`;
        code += `from selenium.webdriver.support.ui import Select\n\n`;
        code += `@pytest.fixture\n`;
        code += `def driver():\n`;
        code += `    driver = webdriver.Chrome()\n`;
        code += `    driver.maximize_window()\n`;
        code += `    yield driver\n`;
        code += `    driver.quit()\n\n`;
        code += `def test_${testName}(driver):\n`;
        code += `    driver.get("${this.url}")\n`;
        
        this.actions.forEach((action, index) => {
            const actionCode = this.generatePythonCode(action, index + 1);
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
        
        this.actions.forEach((action, index) => {
            const actionCode = this.generateJavaScriptCode(action, index + 1);
            code += `    ${actionCode}\n`;
        });
        
        code += `});\n`;
        
        return code;
    }

    /**
     * Export as Cypress
     * Note: File upload requires cypress-file-upload plugin
     * Note: Drag and drop requires cypress-drag-drop plugin
     */
    exportCypress() {
        const testName = this.name;
        
        let code = `// This test requires the following Cypress plugins:\n`;
        code += `// - cypress-file-upload (for file uploads)\n`;
        code += `// - cypress-drag-drop (for drag and drop)\n`;
        code += `// Install with: npm install --save-dev cypress-file-upload cypress-drag-drop\n\n`;
        code += `describe('${testName}', () => {\n`;
        code += `    it('should complete the test', () => {\n`;
        code += `        cy.visit('${this.url}');\n`;
        
        this.actions.forEach((action, index) => {
            const actionCode = this.generateCypressCode(action, index + 1);
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
    generateJavaCode(action, stepNum = 1) {
        const locator = action.element.getBestLocator('java');
        const elemVar = `elem${stepNum}`;
        
        switch (action.type) {
            case 'click':
                return `WebElement ${elemVar} = driver.findElement(${locator});\n        // Scroll element into view\n        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar});\n        Thread.sleep(500);\n        // Try regular click, fallback to JavaScript click if intercepted\n        try {\n            ${elemVar}.click();\n        } catch (Exception e) {\n            if (e.getMessage().toLowerCase().contains("intercepted") || e.getMessage().toLowerCase().contains("not clickable")) {\n                System.out.println("Element click intercepted, using JavaScript click");\n                ((JavascriptExecutor) driver).executeScript("arguments[0].click();", ${elemVar});\n            } else {\n                throw e;\n            }\n        }\n        Thread.sleep(500);  // Brief pause after click`;
            case 'input':
                return `WebElement ${elemVar} = driver.findElement(${locator});\n        // Scroll element into view\n        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar});\n        Thread.sleep(500);\n        ${elemVar}.clear();\n        Thread.sleep(200);\n        ${elemVar}.sendKeys("${this.escapeString(action.value)}");`;
            case 'click_and_input':
                return `WebElement ${elemVar} = driver.findElement(${locator});\n        // Scroll element into view\n        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar});\n        Thread.sleep(500);\n        ${elemVar}.click();\n        Thread.sleep(300);\n        ${elemVar}.clear();\n        Thread.sleep(200);\n        ${elemVar}.sendKeys("${this.escapeString(action.value)}");`;
            case 'select':
                return `WebElement ${elemVar} = driver.findElement(${locator});\n        // Scroll element into view\n        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar});\n        Thread.sleep(500);\n        new Select(${elemVar}).selectByVisibleText("${this.escapeString(action.value)}");\n        Thread.sleep(300);  // Wait for selection to register`;
            case 'scroll':
                try {
                    const scrollData = JSON.parse(action.value || '{}');
                    return `// Explicit scroll recorded by user\n        ((JavascriptExecutor) driver).executeScript("window.scrollTo(${scrollData.x || 0}, ${scrollData.y || 0});");\n        Thread.sleep(500);  // Wait for scroll to complete`;
                } catch {
                    return `// Scroll action (unable to parse data)`;
                }
            case 'upload_file':
                if (action.value && action.value.includes('|')) {
                    const paths = action.value.split('|').join('\\n');
                    return `WebElement ${elemVar} = driver.findElement(${locator});\n        // Scroll element into view\n        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar});\n        Thread.sleep(500);\n        ${elemVar}.sendKeys("${this.escapeString(paths)}");`;
                } else {
                    return `WebElement ${elemVar} = driver.findElement(${locator});\n        // Scroll element into view\n        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar});\n        Thread.sleep(500);\n        ${elemVar}.sendKeys("${this.escapeString(action.value)}");`;
                }
            case 'drag_and_drop':
                const targetLocator = action.target_locator || 'By.id("drop-target")';
                return `WebElement source${stepNum} = driver.findElement(${locator});\n        WebElement target${stepNum} = driver.findElement(${targetLocator});\n        // Scroll source element into view\n        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", source${stepNum});\n        Thread.sleep(500);\n        Actions actions = new Actions(driver);\n        actions.dragAndDrop(source${stepNum}, target${stepNum}).perform();`;
            case 'navigate':
                return `driver.get("${action.value}");`;
            case 'verify_message':
                return `WebElement ${elemVar} = driver.findElement(${locator});\n        // Scroll element into view\n        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar});\n        Thread.sleep(500);\n        Assert.assertTrue(${elemVar}.getText().contains("${this.escapeString(action.value)}"));`;
            default:
                return `// ${action.type}: ${action.value || ''}`;
        }
    }

    /**
     * Generate Python code for an action
     */
    generatePythonCode(action, stepNum = 1) {
        // Get locator value without By. prefix for proper quoting
        const locatorObj = action.element.getBestLocatorObject();
        const byType = locatorObj.type;  // 'ID', 'XPATH', 'CSS_SELECTOR', etc.
        const locatorValue = this.escapeString(locatorObj.value);
        const locator = `By.${byType}("${locatorValue}")`;
        const elemVar = `elem${stepNum}`;
        
        switch (action.type) {
            case 'click':
                return `${elemVar} = driver.find_element(${locator})\n# Scroll element into view\ndriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar})\ntime.sleep(0.5)\n# Try regular click, fallback to JavaScript click if intercepted\ntry:\n    ${elemVar}.click()\nexcept Exception as e:\n    if 'intercepted' in str(e).lower() or 'not clickable' in str(e).lower():\n        print('Element click intercepted, using JavaScript click')\n        driver.execute_script('arguments[0].click();', ${elemVar})\n    else:\n        raise\ntime.sleep(0.5)  # Brief pause after click`;
            case 'input':
                return `${elemVar} = driver.find_element(${locator})\n# Scroll element into view\ndriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar})\ntime.sleep(0.5)\n${elemVar}.clear()\ntime.sleep(0.2)\n${elemVar}.send_keys("${this.escapeString(action.value)}")`;
            case 'click_and_input':
                return `${elemVar} = driver.find_element(${locator})\n# Scroll element into view\ndriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar})\ntime.sleep(0.5)\n${elemVar}.click()\ntime.sleep(0.3)\n${elemVar}.clear()\ntime.sleep(0.2)\n${elemVar}.send_keys("${this.escapeString(action.value)}")`;
            case 'select':
                return `${elemVar} = driver.find_element(${locator})\n# Scroll element into view\ndriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar})\ntime.sleep(0.5)\nSelect(${elemVar}).select_by_visible_text("${this.escapeString(action.value)}")\ntime.sleep(0.3)  # Wait for selection to register`;
            case 'scroll':
                try {
                    const scrollData = JSON.parse(action.value || '{}');
                    return `# Explicit scroll recorded by user\ndriver.execute_script('window.scrollTo(${scrollData.x || 0}, ${scrollData.y || 0});')\ntime.sleep(0.5)  # Wait for scroll to complete`;
                } catch {
                    return `# Scroll action (unable to parse data)`;
                }
            case 'upload_file':
                if (action.value && action.value.includes('|')) {
                    const paths = action.value.split('|').join('\\n');
                    return `${elemVar} = driver.find_element(${locator})\n# Scroll element into view\ndriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar})\ntime.sleep(0.5)\n${elemVar}.send_keys("${this.escapeString(paths)}")`;
                } else {
                    return `${elemVar} = driver.find_element(${locator})\n# Scroll element into view\ndriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar})\ntime.sleep(0.5)\n${elemVar}.send_keys("${this.escapeString(action.value)}")`;
                }
            case 'drag_and_drop':
                const targetLocator = action.target_locator || 'By.ID, "drop-target"';
                return `from selenium.webdriver.common.action_chains import ActionChains\nsource${stepNum} = driver.find_element(${locator})\ntarget${stepNum} = driver.find_element(${targetLocator})\n# Scroll source element into view\ndriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", source${stepNum})\ntime.sleep(0.5)\nActionChains(driver).drag_and_drop(source${stepNum}, target${stepNum}).perform()`;
            case 'navigate':
                return `driver.get("${action.value}")`;
            case 'verify_message':
                return `${elemVar} = driver.find_element(${locator})\n# Scroll element into view\ndriver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", ${elemVar})\ntime.sleep(0.5)\nassert "${this.escapeString(action.value)}" in ${elemVar}.text`;
            default:
                return `# ${action.type}: ${action.value || ''}`;
        }
    }

    /**
     * Generate JavaScript/Playwright code for an action
     */
    generateJavaScriptCode(action, stepNum = 1) {
        const locator = action.element.getBestLocator('playwright');
        const elemVar = `elem${stepNum}`;
        
        switch (action.type) {
            case 'click':
                return `const ${elemVar} = page.locator('${locator}');\n// Scroll element into view\nawait ${elemVar}.scrollIntoViewIfNeeded();\nawait page.waitForTimeout(500);\n// Try regular click, fallback to force click if intercepted\ntry {\n    await ${elemVar}.click();\n} catch (e) {\n    if (e.message.includes('intercepted') || e.message.includes('not clickable')) {\n        console.log('Element click intercepted, using JavaScript click');\n        await ${elemVar}.evaluate(el => el.click());\n    } else {\n        throw e;\n    }\n}\nawait page.waitForTimeout(500);  // Brief pause after click`;
            case 'input':
                return `const ${elemVar} = page.locator('${locator}');\n// Scroll element into view\nawait ${elemVar}.scrollIntoViewIfNeeded();\nawait page.waitForTimeout(500);\nawait ${elemVar}.clear();\nawait page.waitForTimeout(200);\nawait ${elemVar}.fill('${this.escapeString(action.value)}');`;
            case 'click_and_input':
                return `const ${elemVar} = page.locator('${locator}');\n// Scroll element into view\nawait ${elemVar}.scrollIntoViewIfNeeded();\nawait page.waitForTimeout(500);\nawait ${elemVar}.click();\nawait page.waitForTimeout(300);\nawait ${elemVar}.clear();\nawait page.waitForTimeout(200);\nawait ${elemVar}.fill('${this.escapeString(action.value)}');`;
            case 'select':
                return `const ${elemVar} = page.locator('${locator}');\n// Scroll element into view\nawait ${elemVar}.scrollIntoViewIfNeeded();\nawait page.waitForTimeout(500);\nawait ${elemVar}.selectOption('${this.escapeString(action.value)}');\nawait page.waitForTimeout(300);  // Wait for selection to register`;
            case 'scroll':
                try {
                    const scrollData = JSON.parse(action.value || '{}');
                    return `// Explicit scroll recorded by user\nawait page.evaluate(() => window.scrollTo(${scrollData.x || 0}, ${scrollData.y || 0}));\nawait page.waitForTimeout(500);  // Wait for scroll to complete`;
                } catch {
                    return `// Scroll action (unable to parse data)`;
                }
            case 'upload_file':
                if (action.value && action.value.includes('|')) {
                    const paths = action.value.split('|').map(p => `'${this.escapeString(p)}'`).join(', ');
                    return `const ${elemVar} = page.locator('${locator}');\n// Scroll element into view\nawait ${elemVar}.scrollIntoViewIfNeeded();\nawait page.waitForTimeout(500);\nawait ${elemVar}.setInputFiles([${paths}]);`;
                } else {
                    return `const ${elemVar} = page.locator('${locator}');\n// Scroll element into view\nawait ${elemVar}.scrollIntoViewIfNeeded();\nawait page.waitForTimeout(500);\nawait ${elemVar}.setInputFiles('${this.escapeString(action.value)}');`;
                }
            case 'drag_and_drop':
                const targetLocator = action.target_locator || '#drop-target';
                return `const source${stepNum} = page.locator('${locator}');\nconst target${stepNum} = page.locator('${targetLocator}');\n// Scroll source element into view\nawait source${stepNum}.scrollIntoViewIfNeeded();\nawait page.waitForTimeout(500);\nawait source${stepNum}.dragTo(target${stepNum});`;
            case 'navigate':
                return `await page.goto('${action.value}');`;
            case 'verify_message':
                return `const ${elemVar} = page.locator('${locator}');\n// Scroll element into view\nawait ${elemVar}.scrollIntoViewIfNeeded();\nawait page.waitForTimeout(500);\nawait expect(${elemVar}).toContainText('${this.escapeString(action.value)}');`;
            default:
                return `// ${action.type}: ${action.value || ''}`;
        }
    }

    /**
     * Generate Cypress code for an action
     */
    generateCypressCode(action, stepNum = 1) {
        const locator = action.element.getBestLocator('cypress');
        
        switch (action.type) {
            case 'click':
                return `// Scroll element into view\ncy.get('${locator}').scrollIntoView().wait(500);\n// Try regular click, fallback to force click if intercepted\ncy.get('${locator}').click({ force: false }).then(null, (err) => {\n    if (err.message.includes('covered') || err.message.includes('not clickable')) {\n        console.log('Element click intercepted, using force click');\n        cy.get('${locator}').click({ force: true });\n    } else {\n        throw err;\n    }\n});\ncy.wait(500);  // Brief pause after click`;
            case 'input':
                return `// Scroll element into view\ncy.get('${locator}').scrollIntoView().wait(500);\ncy.get('${locator}').clear().wait(200);\ncy.get('${locator}').type('${this.escapeString(action.value)}');`;
            case 'click_and_input':
                return `// Scroll element into view\ncy.get('${locator}').scrollIntoView().wait(500);\ncy.get('${locator}').click().wait(300);\ncy.get('${locator}').clear().wait(200);\ncy.get('${locator}').type('${this.escapeString(action.value)}');`;
            case 'select':
                return `// Scroll element into view\ncy.get('${locator}').scrollIntoView().wait(500);\ncy.get('${locator}').select('${this.escapeString(action.value)}').wait(300);  // Wait for selection to register`;
            case 'scroll':
                try {
                    const scrollData = JSON.parse(action.value || '{}');
                    return `// Explicit scroll recorded by user\ncy.scrollTo(${scrollData.x || 0}, ${scrollData.y || 0});\ncy.wait(500);  // Wait for scroll to complete`;
                } catch {
                    return `// Scroll action (unable to parse data)`;
                }
            case 'upload_file':
                if (action.value && action.value.includes('|')) {
                    const paths = action.value.split('|').map(p => `'${this.escapeString(p)}'`).join(', ');
                    return `// Scroll element into view\ncy.get('${locator}').scrollIntoView().wait(500);\ncy.get('${locator}').attachFile([${paths}]);`;
                } else {
                    return `// Scroll element into view\ncy.get('${locator}').scrollIntoView().wait(500);\ncy.get('${locator}').attachFile('${this.escapeString(action.value)}');`;
                }
            case 'drag_and_drop':
                const targetLocator = action.target_locator || '#drop-target';
                return `// Scroll source element into view\ncy.get('${locator}').scrollIntoView().wait(500);\ncy.get('${locator}').drag('${targetLocator}');`;
            case 'navigate':
                return `cy.visit('${action.value}');`;
            case 'verify_message':
                return `// Scroll element into view\ncy.get('${locator}').scrollIntoView().wait(500);\ncy.get('${locator}').should('contain', '${this.escapeString(action.value)}');`;
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
