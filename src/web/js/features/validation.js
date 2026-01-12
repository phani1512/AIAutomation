// Code Validation Features

function validateCode() {
    const code = document.getElementById('resultContent').textContent;
    const resultsDiv = document.getElementById('validationResults');
    const contentDiv = document.getElementById('validationContent');
    
    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<div style="color: #f59e0b;">⏳ Validating code...</div>';
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    const validationResults = performValidation(code, language);
    displayValidationResults(validationResults);
}

function performValidation(code, language) {
    const issues = [];
    const warnings = [];
    const suggestions = [];
    
    // Common validations
    if (code.length < 10) {
        issues.push({
            message: 'Code is too short to be valid',
            fix: 'Generate more complete code with proper structure'
        });
    }
    
    if (language === 'java') {
        // Java-specific validations
        if (!code.includes('import') && code.length > 50) {
            warnings.push({
                message: 'No import statements found - may be missing dependencies',
                fix: `Add required imports at the top:\nimport org.openqa.selenium.WebDriver;\nimport org.openqa.selenium.chrome.ChromeDriver;\nimport org.openqa.selenium.By;`
            });
        }
        if (!code.includes('class ')) {
            issues.push({
                message: 'No class definition found',
                fix: `Add a class structure:\npublic class TestAutomation {\n    public static void main(String[] args) {\n        // Your test code here\n    }\n}`
            });
        }
        if (!code.includes('driver.quit()') && !code.includes('driver.close()')) {
            warnings.push({
                message: 'Missing driver cleanup (driver.quit() or driver.close())',
                fix: `Add cleanup in finally block:\nfinally {\n    if (driver != null) {\n        driver.quit();\n    }\n}`
            });
        }
    } else if (language === 'python') {
        // Python-specific validations
        if (!code.includes('import') && code.length > 50) {
            warnings.push({
                message: 'No import statements found - may be missing dependencies',
                fix: `Add required imports:\nfrom selenium import webdriver\nfrom selenium.webdriver.common.by import By\nfrom selenium.webdriver.support.ui import WebDriverWait`
            });
        }
        if (!code.includes('def ') && !code.includes('class ')) {
            issues.push({
                message: 'No function or class definition found',
                fix: `Add a function structure:\ndef test_automation():\n    driver = webdriver.Chrome()\n    try:\n        # Your test code here\n    finally:\n        driver.quit()`
            });
        }
        if (code.includes('time.sleep')) {
            suggestions.push({
                message: 'time.sleep found - not recommended for Selenium tests',
                fix: `Replace time.sleep with WebDriverWait:\nfrom selenium.webdriver.support.ui import WebDriverWait\nfrom selenium.webdriver.support import expected_conditions as EC\n\nwait = WebDriverWait(driver, 10)\nelement = wait.until(EC.visibility_of_element_located((By.ID, "element-id")))`
            });
        }
    }
    
    return {
        language: language,
        issues: issues,
        warnings: warnings,
        suggestions: suggestions,
        isValid: issues.length === 0
    };
}

function displayValidationResults(results) {
    const contentDiv = document.getElementById('validationContent');
    
    let html = `<div style="margin-bottom: 15px;">
        <strong>Language:</strong> <span style="color: var(--primary); text-transform: capitalize;">${results.language}</span>
    </div>`;
    
    if (results.isValid && results.warnings.length === 0 && results.suggestions.length === 0) {
        html += `<div style="padding: 12px; background: #d1fae5; border-left: 4px solid #10b981; border-radius: 6px; color: #065f46;">
            <strong>✅ Code validation passed!</strong>
            <p style="margin-top: 5px; font-size: 0.9em;">No issues, warnings, or suggestions found.</p>
        </div>`;
    } else {
        // Display issues
        if (results.issues.length > 0) {
            html += `<div style="margin-bottom: 15px;">
                <div style="padding: 10px; background: #fee2e2; border-left: 4px solid #ef4444; border-radius: 6px;">
                    <strong style="color: #991b1b;">❌ Critical Issues (${results.issues.length})</strong>
                    <div style="margin-top: 10px;">
                        ${results.issues.map((issue, idx) => `
                            <div style="margin-bottom: 15px; padding: 10px; background: white; border-radius: 6px;">
                                <div style="color: #991b1b; font-weight: 500; margin-bottom: 8px;">${idx + 1}. ${issue.message}</div>
                                <div style="margin-top: 8px;">
                                    <strong style="color: #065f46; font-size: 0.9em;">✅ Suggested Fix:</strong>
                                    <pre style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; padding: 10px; margin-top: 5px; overflow-x: auto; font-size: 0.85em; color: #374151;"><code>${escapeHtml(issue.fix)}</code></pre>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>`;
        }
        
        // Display warnings
        if (results.warnings.length > 0) {
            html += `<div style="margin-bottom: 15px;">
                <div style="padding: 10px; background: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 6px;">
                    <strong style="color: #92400e;">⚠️ Warnings (${results.warnings.length})</strong>
                    <div style="margin-top: 10px;">
                        ${results.warnings.map((warning, idx) => `
                            <div style="margin-bottom: 15px; padding: 10px; background: white; border-radius: 6px;">
                                <div style="color: #92400e; font-weight: 500; margin-bottom: 8px;">${idx + 1}. ${warning.message}</div>
                                <div style="margin-top: 8px;">
                                    <strong style="color: #065f46; font-size: 0.9em;">✅ Suggested Fix:</strong>
                                    <pre style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; padding: 10px; margin-top: 5px; overflow-x: auto; font-size: 0.85em; color: #374151;"><code>${escapeHtml(warning.fix)}</code></pre>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>`;
        }
        
        // Display suggestions
        if (results.suggestions.length > 0) {
            html += `<div style="margin-bottom: 15px;">
                <div style="padding: 10px; background: #dbeafe; border-left: 4px solid #3b82f6; border-radius: 6px;">
                    <strong style="color: #1e40af;">💡 Suggestions (${results.suggestions.length})</strong>
                    <div style="margin-top: 10px;">
                        ${results.suggestions.map((suggestion, idx) => `
                            <div style="margin-bottom: 15px; padding: 10px; background: white; border-radius: 6px;">
                                <div style="color: #1e40af; font-weight: 500; margin-bottom: 8px;">${idx + 1}. ${suggestion.message}</div>
                                <div style="margin-top: 8px;">
                                    <strong style="color: #065f46; font-size: 0.9em;">✅ Recommended Code:</strong>
                                    <pre style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; padding: 10px; margin-top: 5px; overflow-x: auto; font-size: 0.85em; color: #374151;"><code>${escapeHtml(suggestion.fix)}</code></pre>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>`;
        }
    }
    
    contentDiv.innerHTML = html;
    
    // Update test result status
    if (stats.testResults.length > 0) {
        const prompt = document.getElementById('promptInput').value.trim();
        const testName = prompt.substring(0, 50) + (prompt.length > 50 ? '...' : '');
        const recentTest = stats.testResults.find(t => t.name === testName);
        
        if (recentTest) {
            if (results.isValid) {
                recentTest.status = 'passed';
                recentTest.details = `Validation passed - ${results.warnings.length} warning(s), ${results.suggestions.length} suggestion(s)`;
            } else {
                recentTest.status = 'failed';
                recentTest.details = `Validation failed - ${results.issues.length} issue(s) found`;
            }
            
            updateDashboardStats();
            updateRecentTestResults();
            updateActivityTimeline();
        }
    }
}

// Expose functions to window object
window.validateCode = validateCode;
