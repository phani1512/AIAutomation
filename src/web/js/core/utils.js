// Utility Functions and Helpers

// Saved Prompts Management
let savedPrompts = [];

function loadSavedPrompts() {
    try {
        const saved = localStorage.getItem('savedPrompts');
        savedPrompts = saved ? JSON.parse(saved) : getDefaultPrompts();
        updateSavedPromptsList();
    } catch (error) {
        console.error('Error loading prompts:', error);
        savedPrompts = getDefaultPrompts();
    }
}

function getDefaultPrompts() {
    return [
        {
            name: "Login Test",
            prompt: "Generate a Selenium test that opens a login page, enters username and password, clicks submit, and verifies successful login",
            category: "Authentication"
        },
        {
            name: "Form Validation",
            prompt: "Create a test that validates required fields in a form, checks error messages, and verifies successful submission",
            category: "Forms"
        },
        {
            name: "Navigation Test",
            prompt: "Write a test that navigates through multiple pages, verifies page titles, and checks menu items",
            category: "Navigation"
        },
        {
            name: "Search Functionality",
            prompt: "Generate a test for search functionality with multiple search terms, verify results, and test filters",
            category: "Search"
        },
        {
            name: "Data Entry",
            prompt: "Create a test that fills out a multi-step form with various input types (text, dropdown, checkbox, radio)",
            category: "Forms"
        }
    ];
}

function updateSavedPromptsList() {
    const container = document.getElementById('savedPromptsList');
    
    if (!container) return;
    
    if (savedPrompts.length === 0) {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">No saved prompts</div>';
        return;
    }
    
    // Group by category
    const grouped = {};
    savedPrompts.forEach(prompt => {
        const category = prompt.category || 'Other';
        if (!grouped[category]) {
            grouped[category] = [];
        }
        grouped[category].push(prompt);
    });
    
    let html = '';
    Object.keys(grouped).sort().forEach(category => {
        html += `
            <div style="margin-bottom: 20px;">
                <h4 style="color: var(--text-primary); margin-bottom: 10px; font-size: 0.9em; text-transform: uppercase; opacity: 0.7;">
                    ${category}
                </h4>
                ${grouped[category].map((prompt, idx) => {
                    const globalIdx = savedPrompts.indexOf(prompt);
                    return `
                        <div style="background: var(--bg-secondary); padding: 12px; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1; cursor: pointer;" onclick="loadSavedPrompt(${globalIdx})">
                                <strong style="color: var(--text-primary); display: block; margin-bottom: 4px;">${prompt.name}</strong>
                                <div style="color: var(--text-secondary); font-size: 0.85em; line-height: 1.4;">
                                    ${prompt.prompt.substring(0, 80)}${prompt.prompt.length > 80 ? '...' : ''}
                                </div>
                            </div>
                            <div style="display: flex; gap: 5px; margin-left: 10px;">
                                <button onclick="editSavedPrompt(${globalIdx})" style="background: var(--info); color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                                    ✏️
                                </button>
                                <button onclick="deleteSavedPrompt(${globalIdx})" style="background: var(--error); color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                                    🗑️
                                </button>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function loadSavedPrompt(index) {
    const prompt = savedPrompts[index];
    if (prompt) {
        document.getElementById('promptInput').value = prompt.prompt;
        navigateTo('generator');
        showNotification('✅ Prompt loaded!');
    }
}

function editSavedPrompt(index) {
    const prompt = savedPrompts[index];
    if (!prompt) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    modal.innerHTML = `
        <div class="modal" style="max-width: 600px;">
            <div class="modal-header">
                <h3 class="modal-title">✏️ Edit Saved Prompt</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Name:</label>
                    <input type="text" id="editPromptName" value="${prompt.name}" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Category:</label>
                    <input type="text" id="editPromptCategory" value="${prompt.category || ''}" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Prompt:</label>
                    <textarea id="editPromptText" rows="5" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">${prompt.prompt}</textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn" style="background: var(--color-gray-500); flex: 1;" onclick="this.closest('.modal-overlay').remove()">
                    Cancel
                </button>
                <button class="btn" style="background: var(--color-success-600); flex: 1;" onclick="updateSavedPrompt(${index})">
                    💾 Update
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function updateSavedPrompt(index) {
    const name = document.getElementById('editPromptName').value.trim();
    const category = document.getElementById('editPromptCategory').value.trim();
    const prompt = document.getElementById('editPromptText').value.trim();
    
    if (!name || !prompt) {
        alert('Name and prompt are required');
        return;
    }
    
    savedPrompts[index] = { name, category: category || 'Other', prompt };
    localStorage.setItem('savedPrompts', JSON.stringify(savedPrompts));
    updateSavedPromptsList();
    document.querySelector('.modal-overlay').remove();
    showNotification('✅ Prompt updated!');
}

function deleteSavedPrompt(index) {
    if (!confirm('Delete this prompt?')) return;
    
    savedPrompts.splice(index, 1);
    localStorage.setItem('savedPrompts', JSON.stringify(savedPrompts));
    updateSavedPromptsList();
    showNotification('🗑️ Prompt deleted');
}

function showAddPromptModal() {
    const currentPrompt = document.getElementById('promptInput')?.value.trim() || '';
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    modal.innerHTML = `
        <div class="modal" style="max-width: 600px;">
            <div class="modal-header">
                <h3 class="modal-title">➕ Save Prompt</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Name:</label>
                    <input type="text" id="newPromptName" placeholder="e.g., Login Test" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Category:</label>
                    <input type="text" id="newPromptCategory" placeholder="e.g., Authentication" value="Other" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Prompt:</label>
                    <textarea id="newPromptText" rows="5" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">${currentPrompt}</textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn" style="background: var(--color-gray-500); flex: 1;" onclick="this.closest('.modal-overlay').remove()">
                    Cancel
                </button>
                <button class="btn" style="background: var(--color-success-600); flex: 1;" onclick="saveNewPrompt()">
                    💾 Save
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function saveNewPrompt() {
    const name = document.getElementById('newPromptName').value.trim();
    const category = document.getElementById('newPromptCategory').value.trim();
    const prompt = document.getElementById('newPromptText').value.trim();
    
    if (!name || !prompt) {
        alert('Name and prompt are required');
        return;
    }
    
    savedPrompts.push({ name, category: category || 'Other', prompt });
    localStorage.setItem('savedPrompts', JSON.stringify(savedPrompts));
    updateSavedPromptsList();
    document.querySelector('.modal-overlay').remove();
    showNotification('✅ Prompt saved!');
}

// Test Runner Utilities
function runAllTests() {
    if (testCases.length === 0) {
        alert('No test cases to run');
        return;
    }
    
    executeTestSuite();
}

function runSingleTest(testId) {
    const test = testCases.find(t => t.id === testId);
    if (!test) return;
    
    showLoading(true);
    
    // Simulate test execution
    setTimeout(() => {
        const success = Math.random() > 0.3; // 70% success rate for demo
        const duration = Math.floor(Math.random() * 3000) + 1000;
        
        addTestResult(
            test.name || 'Test',
            success ? 'passed' : 'failed',
            duration,
            success ? null : 'Assertion failed: Element not found'
        );
        
        showLoading(false);
        showNotification(success ? '✅ Test passed!' : '❌ Test failed!');
    }, 2000);
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to generate
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const promptInput = document.getElementById('promptInput');
            if (promptInput && document.activeElement === promptInput) {
                e.preventDefault();
                generateCode();
            }
        }
        
        // Ctrl/Cmd + K to clear
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const promptInput = document.getElementById('promptInput');
            if (promptInput) {
                promptInput.value = '';
                promptInput.focus();
            }
        }
        
        // Esc to close modals
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal-overlay');
            if (modal) {
                modal.remove();
            }
        }
    });
}

// Theme Colors
function updateThemeColors() {
    const isDark = document.body.classList.contains('dark-mode');
    
    const colors = {
        '--primary': isDark ? '#1a1a2e' : '#ffffff',
        '--secondary': isDark ? '#16213e' : '#f8f9fa',
        '--accent': isDark ? '#0f4c75' : '#3b82f6',
        '--text-primary': isDark ? '#eee' : '#1a1a2e',
        '--text-secondary': isDark ? '#bbb' : '#666',
        '--border': isDark ? '#333' : '#ddd',
        '--success': '#10b981',
        '--error': '#ef4444',
        '--warning': '#f59e0b',
        '--info': '#3b82f6',
        '--bg-primary': isDark ? '#0f0f23' : '#ffffff',
        '--bg-secondary': isDark ? '#1a1a2e' : '#f8f9fa',
        '--bg-tertiary': isDark ? '#16213e' : '#e5e7eb'
    };
    
    Object.keys(colors).forEach(key => {
        document.documentElement.style.setProperty(key, colors[key]);
    });
}

// Format Code
function formatCode(code, language) {
    // Basic code formatting
    let formatted = code.trim();
    
    // Add line breaks after semicolons for readability
    if (language === 'java' || language === 'javascript' || language === 'csharp') {
        formatted = formatted.replace(/;(?!\n)/g, ';\n');
    }
    
    return formatted;
}

// Debounce Helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize Search with Debounce
function initializeSearch() {
    const snippetSearch = document.getElementById('snippetSearch');
    if (snippetSearch) {
        snippetSearch.addEventListener('input', debounce(filterSnippets, 300));
    }
}

// Export All Data
function exportAllData() {
    const data = {
        version: '1.0',
        exportDate: new Date().toISOString(),
        snippets: snippets,
        savedPrompts: savedPrompts,
        testCases: testCases,
        stats: stats
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `web-automation-backup-${new Date().toISOString().split('T')[0]}.json`;
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('✅ All data exported!');
}

// Import All Data
function importAllData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const imported = JSON.parse(event.target.result);
                
                if (imported.snippets) {
                    snippets = imported.snippets;
                    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
                }
                
                if (imported.savedPrompts) {
                    savedPrompts = imported.savedPrompts;
                    localStorage.setItem('savedPrompts', JSON.stringify(savedPrompts));
                }
                
                if (imported.testCases) {
                    testCases = imported.testCases;
                }
                
                if (imported.stats) {
                    stats = imported.stats;
                }
                
                // Refresh UI
                displaySnippets();
                updateSavedPromptsList();
                updateTestCasesList();
                updateDashboardStats();
                
                showNotification('✅ Data imported successfully!');
            } catch (error) {
                alert('Error importing data: ' + error.message);
            }
        };
        reader.readAsText(file);
    };
    
    input.click();
}

// Initialize Utilities
function initializeUtils() {
    setupKeyboardShortcuts();
    updateThemeColors();
    initializeSearch();
    loadSavedPrompts();
}

function runTestWithRunner() {
    const testFile = document.getElementById('runnerTestFile')?.value || '';
    const testClass = document.getElementById('runnerTestClass')?.value || '';
    const testMethod = document.getElementById('runnerTestMethod')?.value || '';
    
    if (!testFile) {
        alert('Please enter a test file path');
        return;
    }
    
    window.showNotification(`✅ Running test: ${testFile}...`);
    // Implementation would execute the test
}

function generateRunCommand() {
    const testFile = document.getElementById('runnerTestFile')?.value || '';
    const testClass = document.getElementById('runnerTestClass')?.value || '';
    const testMethod = document.getElementById('runnerTestMethod')?.value || '';
    const framework = document.getElementById('runnerFramework')?.value || 'pytest';
    
    if (!testFile) {
        alert('Please enter a test file path');
        return;
    }
    
    let command = '';
    if (framework === 'pytest') {
        command = `pytest ${testFile}`;
        if (testClass) command += `::${testClass}`;
        if (testMethod) command += `::${testMethod}`;
    } else if (framework === 'unittest') {
        command = `python -m unittest ${testFile}`;
    } else if (framework === 'junit') {
        command = `mvn test -Dtest=${testClass || testFile}`;
    }
    
    const output = document.getElementById('runnerOutput');
    if (output) {
        output.textContent = command;
        output.style.display = 'block';
    }
    
    window.showNotification('✅ Command generated!');
}

function savePromptToAccount() {
    const user = typeof window.getCurrentUser === 'function' ? window.getCurrentUser() : null;
    
    if (!user) {
        window.showNotification('⚠️ Please login to save prompts');
        if (typeof window.showLoginPage === 'function') {
            window.showLoginPage();
        }
        return;
    }
    
    const prompt = document.getElementById('promptInput')?.value.trim();
    
    if (!prompt) {
        alert('Please enter a prompt to save');
        return;
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal" style="max-width: 500px;">
            <div class="modal-header">
                <h3 class="modal-title">💾 Save Prompt</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="promptTitle">Prompt Title:</label>
                    <input type="text" id="promptTitle" placeholder="e.g., Login Test Flow" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
                </div>
                <div class="form-group" style="margin-top: 15px;">
                    <label for="promptCategory">Category (optional):</label>
                    <select id="promptCategory" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
                        <option value="">Select category...</option>
                        <option value="login">Login/Auth</option>
                        <option value="forms">Forms</option>
                        <option value="navigation">Navigation</option>
                        <option value="validation">Validation</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group" style="margin-top: 15px;">
                    <label>Prompt:</label>
                    <textarea readonly style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary); min-height: 100px;">${prompt.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn" style="background: var(--color-gray-500); flex: 1;" onclick="this.closest('.modal-overlay').remove()">
                    Cancel
                </button>
                <button class="btn" style="background: var(--color-primary-600); flex: 1;" onclick="window.confirmSavePrompt('${prompt.replace(/'/g, "\\'")}');">
                    💾 Save
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function confirmSavePrompt(promptText) {
    const user = typeof window.getCurrentUser === 'function' ? window.getCurrentUser() : null;
    const title = document.getElementById('promptTitle')?.value.trim();
    const category = document.getElementById('promptCategory')?.value;
    
    if (!title) {
        alert('Please enter a title for the prompt');
        return;
    }
    
    const savedPrompt = {
        id: Date.now(),
        title: title,
        category: category,
        prompt: promptText,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    if (!user.savedPrompts) {
        user.savedPrompts = [];
    }
    
    user.savedPrompts.unshift(savedPrompt);
    
    if (typeof window.saveUser === 'function') {
        window.saveUser(user);
    }
    localStorage.setItem('currentUser', JSON.stringify(user));
    
    document.querySelector('.modal-overlay')?.remove();
    window.showNotification('✅ Prompt saved successfully!');
}

function showSavedPrompts() {
    const user = typeof window.getCurrentUser === 'function' ? window.getCurrentUser() : null;
    
    if (!user) {
        window.showNotification('⚠️ Please login to view saved prompts');
        if (typeof window.showLoginPage === 'function') {
            window.showLoginPage();
        }
        return;
    }
    
    const prompts = user.savedPrompts || [];
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal modal-lg" style="max-width: 700px;">
            <div class="modal-header">
                <h3 class="modal-title">📚 My Saved Prompts (${prompts.length})</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-body" style="max-height: 60vh; overflow-y: auto;">
                ${prompts.length > 0 ? `
                    <div id="savedPromptsList">
                        ${prompts.map((p, index) => `
                            <div style="padding: 15px; margin-bottom: 10px; background: var(--bg-secondary); border-radius: 8px; border-left: 4px solid var(--primary);">
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                    <strong style="color: var(--text-primary); font-size: 1.1em;">${p.title}</strong>
                                    <div style="display: flex; gap: 8px;">
                                        <button onclick="window.loadSavedPromptToInput(${index}); document.querySelector('.modal-overlay').remove();" class="btn" style="background: var(--color-primary-600); padding: 5px 10px; font-size: 0.9em;">Use</button>
                                        <button onclick="window.deleteSavedAccountPrompt(${index}); document.querySelector('.modal-overlay').remove(); window.showSavedPrompts();" class="btn" style="background: var(--color-error-600); padding: 5px 10px; font-size: 0.9em;">Delete</button>
                                    </div>
                                </div>
                                ${p.category ? `<span style="background: var(--primary); color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 8px;">${p.category}</span>` : ''}
                                <div style="color: var(--text-secondary); font-size: 0.9em; margin-top: 8px;">${p.prompt}</div>
                                <div style="color: var(--text-secondary); font-size: 0.8em; margin-top: 8px;">${p.date}</div>
                            </div>
                        `).join('')}
                    </div>
                ` : '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">No saved prompts yet</p>'}
            </div>
            <div class="modal-footer">
                <button class="btn" style="background: var(--color-gray-500); width: 100%;" onclick="this.closest('.modal-overlay').remove()">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function loadSavedPromptToInput(index) {
    const user = typeof window.getCurrentUser === 'function' ? window.getCurrentUser() : null;
    if (user && user.savedPrompts && user.savedPrompts[index]) {
        const promptInput = document.getElementById('promptInput');
        if (promptInput) {
            promptInput.value = user.savedPrompts[index].prompt;
            window.showNotification('✅ Prompt loaded!');
        }
    }
}

function deleteSavedAccountPrompt(index) {
    const user = typeof window.getCurrentUser === 'function' ? window.getCurrentUser() : null;
    if (user && user.savedPrompts) {
        user.savedPrompts.splice(index, 1);
        if (typeof window.saveUser === 'function') {
            window.saveUser(user);
        }
        localStorage.setItem('currentUser', JSON.stringify(user));
        window.showNotification('✅ Prompt deleted!');
    }
}

// Expose functions to global scope for HTML onclick handlers
window.loadSavedPrompts = loadSavedPrompts;
window.updateSavedPromptsList = updateSavedPromptsList;
window.loadSavedPrompt = loadSavedPrompt;
window.editSavedPrompt = editSavedPrompt;
window.updateSavedPrompt = updateSavedPrompt;
window.deleteSavedPrompt = deleteSavedPrompt;
window.showAddPromptModal = showAddPromptModal;
window.saveNewPrompt = saveNewPrompt;
window.runAllTests = runAllTests;
window.runSingleTest = runSingleTest;
window.setupKeyboardShortcuts = setupKeyboardShortcuts;
window.updateThemeColors = updateThemeColors;
window.formatCode = formatCode;
window.debounce = debounce;
window.initializeSearch = initializeSearch;
window.exportAllData = exportAllData;
window.importAllData = importAllData;
window.initializeUtils = initializeUtils;
window.runTestWithRunner = runTestWithRunner;
window.generateRunCommand = generateRunCommand;
window.savePromptToAccount = savePromptToAccount;
window.confirmSavePrompt = confirmSavePrompt;
window.showSavedPrompts = showSavedPrompts;
window.loadSavedPromptToInput = loadSavedPromptToInput;
window.deleteSavedAccountPrompt = deleteSavedAccountPrompt;

// Additional UI Functions
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('mobile-open');
    }
}

function toggleDarkMode() {
    const body = document.body;
    const slider = document.getElementById('darkModeSlider');
    
    body.classList.toggle('dark-mode');
    
    if (body.classList.contains('dark-mode')) {
        if (slider) slider.textContent = '☀️';
        localStorage.setItem('darkMode', 'enabled');
    } else {
        if (slider) slider.textContent = '🌙';
        localStorage.setItem('darkMode', 'disabled');
    }
}

function showUserMenu() {
    const username = localStorage.getItem('username') || 'User';
    const options = [
        { text: `Logged in as ${username}`, disabled: true },
        { text: 'Profile Settings', action: () => alert('Profile settings coming soon') },
        { text: 'Preferences', action: () => alert('Preferences coming soon') },
        { text: 'Logout', action: logout }
    ];
    
    // Simple menu implementation
    const menu = confirm(`User: ${username}\n\nLogout?`);
    if (menu) {
        logout();
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    if (window.showLoginPage) {
        window.showLoginPage();
    } else {
        location.reload();
    }
}

function copyResult() {
    const resultContent = document.getElementById('resultContent') || document.getElementById('generatedCode');
    if (!resultContent) {
        alert('No result to copy');
        return;
    }
    
    const text = resultContent.textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyBtn');
        if (btn) {
            const originalText = btn.textContent;
            btn.textContent = '✅ Copied!';
            setTimeout(() => btn.textContent = originalText, 2000);
        }
        window.showNotification('Copied to clipboard', 'success');
    }).catch(err => {
        window.showNotification('Failed to copy', 'error');
    });
}

function exportCode() {
    const resultContent = document.getElementById('resultContent') || document.getElementById('generatedCode');
    if (!resultContent) {
        alert('No code to export');
        return;
    }
    
    const code = resultContent.textContent;
    let extension = '.java';
    let filename = 'GeneratedTest';
    
    if (code.includes('from selenium') || code.includes('import pytest')) {
        extension = '.py';
        filename = 'test_generated';
    } else if (code.includes('const ') || code.includes('let ')) {
        extension = '.js';
        filename = 'test_generated';
    }
    
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename + extension;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    window.showNotification('Code exported successfully', 'success');
}

function saveToSnippets() {
    const resultContent = document.getElementById('resultContent') || document.getElementById('generatedCode');
    if (!resultContent) {
        alert('No code to save');
        return;
    }
    
    const code = resultContent.textContent;
    const promptInput = document.getElementById('promptInput');
    const prompt = promptInput ? promptInput.value.trim() : '';
    const languageSelector = document.getElementById('languageSelector');
    const language = languageSelector ? languageSelector.value : 'java';
    
    const snippet = {
        id: Date.now(),
        title: 'Generated Code',
        language: language,
        tags: ['generated'],
        description: prompt ? `Generated from: ${prompt.substring(0, 50)}...` : 'Generated code',
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    window.showNotification('Saved to Code Snippets', 'success');
    if (window.loadSnippets) window.loadSnippets();
}

async function validateCode() {
    const code = document.getElementById('resultContent').textContent;
    const resultsDiv = document.getElementById('validationResults');
    const contentDiv = document.getElementById('validationContent');
    
    if (!resultsDiv || !contentDiv) {
        alert('Validation UI not found');
        return;
    }
    
    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<div style="color: #f59e0b;">⏳ Validating code...</div>';
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    }
    
    const validationResults = performValidation(code, language);
    displayValidationResults(validationResults);
}

function performValidation(code, language) {
    const issues = [];
    const warnings = [];
    const suggestions = [];
    
    if (code.length < 10) {
        issues.push({
            message: 'Code is too short to be valid',
            fix: 'Generate more complete code with proper structure'
        });
    }
    
    if (language === 'java') {
        if (!code.includes('import') && code.length > 50) {
            warnings.push({
                message: 'No import statements found',
                fix: 'import org.openqa.selenium.WebDriver;\nimport org.openqa.selenium.chrome.ChromeDriver;'
            });
        }
        if (!code.includes('driver.quit()') && !code.includes('driver.close()')) {
            warnings.push({
                message: 'Missing driver cleanup',
                fix: 'finally {\n    if (driver != null) {\n        driver.quit();\n    }\n}'
            });
        }
        if (code.includes('Thread.sleep')) {
            suggestions.push({
                message: 'Thread.sleep found - use WebDriverWait instead',
                fix: 'WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));'
            });
        }
    } else if (language === 'python') {
        if (!code.includes('import') && code.length > 50) {
            warnings.push({
                message: 'No import statements found',
                fix: 'from selenium import webdriver\nfrom selenium.webdriver.common.by import By'
            });
        }
        if (!code.includes('driver.quit()') && !code.includes('driver.close()')) {
            warnings.push({
                message: 'Missing driver cleanup',
                fix: 'finally:\n    driver.quit()'
            });
        }
        if (code.includes('time.sleep')) {
            suggestions.push({
                message: 'time.sleep found - use WebDriverWait instead',
                fix: 'wait = WebDriverWait(driver, 10)\nelement = wait.until(EC.visibility_of_element_located((By.ID, "id")))'
            });
        }
    }
    
    if (code.includes('password') && code.match(/password\s*=\s*["'][^"']+["']/i)) {
        warnings.push({
            message: 'Hardcoded password detected - security risk',
            fix: 'Use environment variables: os.getenv("TEST_PASSWORD")'
        });
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
    
    // Helper to escape HTML
    const escapeHtml = (text) => {
        return text.replace(/&/g, '&amp;')
                   .replace(/</g, '&lt;')
                   .replace(/>/g, '&gt;')
                   .replace(/"/g, '&quot;');
    };
    
    let html = `<div style="margin-bottom: 15px; color: var(--text-primary);">
        <strong>Language:</strong> <span style="color: var(--primary); text-transform: capitalize;">${results.language}</span>
    </div>`;
    
    if (results.isValid && results.warnings.length === 0 && results.suggestions.length === 0) {
        html += `<div style="padding: 12px; background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; border-radius: 6px; color: var(--text-primary);">
            <strong>✅ Code validation passed!</strong>
            <p style="margin-top: 5px; font-size: 0.9em; color: var(--text-secondary);">No issues found.</p>
        </div>`;
    } else {
        if (results.issues.length > 0) {
            html += `<div style="margin-bottom: 15px; padding: 10px; background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; border-radius: 6px;">
                <strong style="color: #ef4444;">❌ Critical Issues (${results.issues.length})</strong>
                ${results.issues.map((issue, idx) => `
                    <div style="margin: 10px 0; padding: 10px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px;">
                        <div style="color: #ef4444; font-weight: 500; margin-bottom: 5px;">${idx + 1}. ${issue.message}</div>
                        <div style="font-size: 0.85em; color: #10b981; font-weight: 500; margin-top: 8px;">✅ Suggested Fix:</div>
                        <pre style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; padding: 10px; margin-top: 5px; font-size: 0.85em; overflow-x: auto; white-space: pre-wrap; color: var(--text-primary);"><code>${escapeHtml(issue.fix)}</code></pre>
                    </div>
                `).join('')}
            </div>`;
        }
        
        if (results.warnings.length > 0) {
            html += `<div style="margin-bottom: 15px; padding: 10px; background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; border-radius: 6px;">
                <strong style="color: #f59e0b;">⚠️ Warnings (${results.warnings.length})</strong>
                ${results.warnings.map((warning, idx) => `
                    <div style="margin: 10px 0; padding: 10px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px;">
                        <div style="color: #f59e0b; font-weight: 500; margin-bottom: 5px;">${idx + 1}. ${warning.message}</div>
                        <div style="font-size: 0.85em; color: #10b981; font-weight: 500; margin-top: 8px;">✅ Suggested Fix:</div>
                        <pre style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; padding: 10px; margin-top: 5px; font-size: 0.85em; overflow-x: auto; white-space: pre-wrap; color: var(--text-primary);"><code>${escapeHtml(warning.fix)}</code></pre>
                    </div>
                `).join('')}
            </div>`;
        }
        
        if (results.suggestions.length > 0) {
            html += `<div style="padding: 10px; background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; border-radius: 6px;">
                <strong style="color: #3b82f6;">💡 Suggestions (${results.suggestions.length})</strong>
                ${results.suggestions.map((suggestion, idx) => `
                    <div style="margin: 10px 0; padding: 10px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px;">
                        <div style="color: #3b82f6; font-weight: 500; margin-bottom: 5px;">${idx + 1}. ${suggestion.message}</div>
                        <div style="font-size: 0.85em; color: #10b981; font-weight: 500; margin-top: 8px;">✅ Suggested Fix:</div>
                        <pre style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; padding: 10px; margin-top: 5px; font-size: 0.85em; overflow-x: auto; white-space: pre-wrap; color: var(--text-primary);"><code>${escapeHtml(suggestion.fix)}</code></pre>
                    </div>
                `).join('')}
            </div>`;
        }
    }
    
    contentDiv.innerHTML = html;
}

async function executeCurrentTest() {
    const resultContent = document.getElementById('resultContent') || document.getElementById('generatedCode');
    if (!resultContent) {
        alert('No test code to execute');
        return;
    }
    
    const code = resultContent.textContent;
    
    try {
        const response = await fetch(window.API_URL + '/browser/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });
        
        if (!response.ok) {
            throw new Error('Execution failed');
        }
        
        const data = await response.json();
        alert('✅ Test executed successfully!\n\n' + (data.output || 'No output'));
    } catch (error) {
        alert('❌ Execution failed:\n\n' + error.message);
    }
}

function showPromptHistory() {
    alert('Prompt history feature coming soon!');
}

// Additional save to snippets functions
function savePromptToAccount() {
    const promptEl = document.getElementById('promptInput');
    const prompt = promptEl ? promptEl.value : '';
    if (prompt && prompt.trim()) {
        localStorage.setItem('savedPrompt', prompt);
        window.showNotification('✅ Prompt saved to your account', 'success');
    } else {
        alert('Please enter a prompt to save');
    }
}

function saveLocatorToSnippets() {
    const resultEl = document.getElementById('locatorResult');
    const code = resultEl ? resultEl.textContent : '';
    if (code && code.trim() && !code.includes('will appear here')) {
        window.showAddSnippetModal(code);
    } else {
        alert('No locator code to save');
    }
}

function saveActionToSnippets() {
    const resultEl = document.getElementById('actionResult');
    const code = resultEl ? resultEl.textContent : '';
    if (code && code.trim() && !code.includes('will appear here')) {
        window.showAddSnippetModal(code);
    } else {
        alert('No action code to save');
    }
}

async function runTestWithRunner() {
    const scriptEl = document.getElementById('runnerScript');
    const script = scriptEl ? scriptEl.value : '';
    if (!script || script.trim() === '') {
        alert('Please enter a test script to run');
        return;
    }
    
    window.showLoading(true);
    window.showNotification('🚀 Running test...', 'info');
    
    try {
        const response = await fetch(`${window.API_URL}/browser/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: script })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.showNotification('✅ Test completed successfully!', 'success');
            const outputEl = document.getElementById('runnerOutput');
            if (outputEl) {
                outputEl.textContent = data.output || 'Test executed successfully';
            }
        } else {
            throw new Error(data.error || 'Test execution failed');
        }
    } catch (error) {
        window.showNotification('❌ Test execution failed: ' + error.message, 'error');
    } finally {
        window.showLoading(false);
    }
}

// Export new functions
window.toggleSidebar = toggleSidebar;
window.toggleDarkMode = toggleDarkMode;
window.showUserMenu = showUserMenu;
window.logout = logout;
window.copyResult = copyResult;
window.exportCode = exportCode;
window.saveToSnippets = saveToSnippets;
window.validateCode = validateCode;
window.performValidation = performValidation;
window.displayValidationResults = displayValidationResults;
window.executeCurrentTest = executeCurrentTest;
window.showPromptHistory = showPromptHistory;
window.savePromptToAccount = savePromptToAccount;
window.saveLocatorToSnippets = saveLocatorToSnippets;
window.saveActionToSnippets = saveActionToSnippets;
window.runTestWithRunner = runTestWithRunner;

