// Browser Control and Execution Functions

let browser = null;

async function initializeBrowser() {
    const browserType = document.getElementById('browserType');
    const headlessCheckbox = document.getElementById('headlessMode');
    
    const browserValue = browserType ? browserType.value : 'chrome';
    const headless = headlessCheckbox ? headlessCheckbox.checked : false;
    
    window.showLoading(true);
    
    try {
        const response = await fetch(`${window.API_URL}/browser/initialize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ browser: browserValue, headless })
        });
        
        const data = await response.json();
        
        if (data.success) {
            browser = 'initialized'; // Set browser state
            const statusEl = document.getElementById('browserStatus');
            const closeBtnEl = document.getElementById('closeBrowserBtn');
            
            if (statusEl) {
                statusEl.textContent = '✅ Browser Ready';
                statusEl.style.color = 'var(--success)';
            }
            if (closeBtnEl) {
                closeBtnEl.style.display = 'inline-block';
            }
            
            window.showNotification('✅ Browser initialized successfully!', 'success');
        } else {
            throw new Error(data.message || data.error || 'Failed to initialize browser');
        }
    } catch (error) {
        console.error('[BROWSER] Initialization error:', error);
        const statusEl = document.getElementById('browserStatus');
        if (statusEl) {
            statusEl.textContent = '❌ Browser Error';
            statusEl.style.color = 'var(--error)';
        }
        window.showNotification('❌ Error: ' + error.message, 'error');
    } finally {
        window.showLoading(false);
    }
}

async function executeInBrowser() {
    if (!browser) {
        alert('Please initialize browser first');
        return;
    }
    
    // Get prompt from browser control textarea
    const promptEl = document.getElementById('browserPrompt');
    const prompt = promptEl ? promptEl.value.trim() : '';
    
    if (!prompt) {
        alert('Please enter a test prompt (e.g., "click login button")');
        return;
    }
    
    window.showLoading(true);
    
    try {
        // First, generate code from the prompt using AI
        const generateResponse = await fetch(`${window.API_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                prompt: prompt,
                language: 'python',
                execute: false
            })
        });
        
        const generateData = await generateResponse.json();
        
        // The API returns either {success: true, generated: code} or {code: code, tokens_generated: X}
        const code = generateData.code || generateData.generated;
        
        if (!code || code.trim() === '') {
            console.error('Generate API response:', generateData);
            throw new Error(generateData.error || 'No code was generated from the prompt');
        }
        
        window.showNotification('✅ Code generated, now executing...', 'info');
        
        // Now execute the generated code
        const response = await fetch(`${window.API_URL}/browser/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.showNotification('✅ Code executed successfully!', 'success');
            displayExecutionResults(data);
        } else {
            throw new Error(data.error || data.message || 'Execution failed');
        }
    } catch (error) {
        console.error('[BROWSER] Execution error:', error);
        window.showNotification('❌ Execution Error: ' + error.message, 'error');
    } finally {
        window.showLoading(false);
    }
}

async function closeBrowser() {
    if (!browser) {
        return;
    }
    
    try {
        const response = await fetch(`${window.API_URL}/browser/close`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        browser = null;
        
        const statusEl = document.getElementById('browserStatus');
        const closeBtnEl = document.getElementById('closeBrowserBtn');
        
        if (statusEl) {
            statusEl.textContent = '⭕ Browser Closed';
            statusEl.style.color = 'var(--text-secondary)';
        }
        if (closeBtnEl) {
            closeBtnEl.style.display = 'none';
        }
        
        window.showNotification('Browser closed', 'success');
    } catch (error) {
        console.error('[BROWSER] Error closing browser:', error);
        // Still clear the state even if close failed
        browser = null;
    }
}

function displayExecutionResults(data) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">✅ Execution Results</h3>
            
            <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <strong style="color: var(--text-primary);">Status:</strong>
                <span style="color: var(--success); margin-left: 10px;">${data.status}</span>
            </div>
            
            ${data.output ? `
                <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: var(--text-primary); display: block; margin-bottom: 10px;">Output:</strong>
                    <pre style="margin: 0; color: var(--text-secondary); white-space: pre-wrap; word-wrap: break-word;">${data.output}</pre>
                </div>
            ` : ''}
            
            ${data.screenshot ? `
                <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: var(--text-primary); display: block; margin-bottom: 10px;">Screenshot:</strong>
                    <img src="${data.screenshot}" style="max-width: 100%; border-radius: 6px;" alt="Execution Screenshot">
                </div>
            ` : ''}
            
            ${data.duration ? `
                <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: var(--text-primary);">Duration:</strong>
                    <span style="color: var(--text-secondary); margin-left: 10px;">${data.duration}ms</span>
                </div>
            ` : ''}
            
            <button class="btn" onclick="this.closest('.modal-overlay').remove()" style="width: 100%;">
                Close
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Expose functions to global scope for HTML onclick handlers
window.initializeBrowser = initializeBrowser;
window.executeInBrowser = executeInBrowser;
window.closeBrowser = closeBrowser;
window.displayExecutionResults = displayExecutionResults;


