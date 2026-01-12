// Browser Control Features

async function initializeBrowser() {
    const browser = document.getElementById('browserType').value;
    const headless = document.getElementById('headlessMode').checked;
    
    showLoading(true);
    showBrowserStatus('Initializing browser...');
    
    try {
        const response = await fetch(`${API_URL}/browser/initialize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ browser, headless })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showBrowserStatus(`✅ ${browser.toUpperCase()} browser initialized successfully!`);
            document.getElementById('initBrowserBtn').textContent = '✅ Browser Ready';
            document.getElementById('initBrowserBtn').style.background = '#10b981';
        } else {
            showBrowserStatus('❌ Failed to initialize browser: ' + data.message);
        }
    } catch (error) {
        showBrowserStatus('❌ Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function executeInBrowser() {
    const url = document.getElementById('browserUrl').value.trim();
    const prompt = document.getElementById('browserPrompt').value.trim();
    
    if (!prompt) {
        alert('Please enter a test prompt');
        return;
    }
    
    showLoading(true);
    showBrowserStatus('Generating code and executing in browser...');
    
    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                prompt,
                execute: true,
                url: url || undefined
            })
        });
        
        const data = await response.json();
        
        let result = `Generated Code:\n${data.generated}\n\n`;
        
        if (data.execution) {
            if (data.execution.success) {
                result += `✅ Execution Result:\n`;
                result += `Status: Success\n`;
                result += `Current URL: ${data.execution.current_url}\n`;
                result += `Page Title: ${data.execution.page_title}\n`;
                
                if (data.execution.result) {
                    result += `Output: ${data.execution.result}\n`;
                }
                
                showBrowserStatus('✅ Code executed successfully!');
            } else {
                result += `❌ Execution Failed:\n`;
                result += `Error: ${data.execution.error}\n`;
                showBrowserStatus('❌ Execution failed!');
            }
        }
        
        displayBrowserResult(result);
    } catch (error) {
        showBrowserStatus('❌ Error: ' + error.message);
        displayBrowserResult(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

async function closeBrowser() {
    showLoading(true);
    showBrowserStatus('Closing browser...');
    
    try {
        const response = await fetch(`${API_URL}/browser/close`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showBrowserStatus('✅ Browser closed successfully!');
            document.getElementById('initBrowserBtn').textContent = 'Initialize Browser';
            document.getElementById('initBrowserBtn').style.background = '';
        } else {
            showBrowserStatus('❌ Failed to close browser: ' + data.message);
        }
    } catch (error) {
        showBrowserStatus('❌ Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayBrowserResult(text) {
    const resultElement = document.getElementById('browserResultContent');
    resultElement.textContent = text;
    resultElement.className = 'language-java';
    
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(resultElement);
    }
    
    document.getElementById('copyBrowserBtn').style.display = 'block';
}

function copyBrowserResult() {
    const text = document.getElementById('browserResultContent').textContent;
    navigator.clipboard.writeText(text).then(() => {
        showNotification('✅ Code copied to clipboard!');
    });
}

function showBrowserStatus(message) {
    const statusDiv = document.getElementById('browserStatus');
    const statusText = document.getElementById('browserStatusText');
    statusDiv.style.display = 'block';
    statusText.textContent = message;
}

// Expose functions to window object
window.initializeBrowser = initializeBrowser;
window.executeInBrowser = executeInBrowser;
window.closeBrowser = closeBrowser;
