// Code Snippets Library Functions

let snippets = [];

function saveLocatorToSnippets() {
    const code = document.getElementById('locatorResultContent').textContent;
    const html = document.getElementById('htmlInput').value.trim();
    
    const snippet = {
        id: Date.now(),
        name: 'Locator Suggestions',
        title: 'Locator Suggestions',
        language: 'java',
        tags: ['locator', 'selenium'],
        description: `Locators for: ${html.substring(0, 50)}...`,
        code: code,
        createdAt: new Date().toISOString(),
        created: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    if (typeof showNotification === 'function') {
        showNotification('✅ Saved to Code Snippets!');
    }
    loadSnippets();
}

function saveActionToSnippets() {
    const code = document.getElementById('actionResultContent').textContent;
    const elementType = document.getElementById('elementType').value;
    const context = document.getElementById('contextInput').value.trim();
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    const snippet = {
        id: Date.now(),
        name: `Action Suggestions - ${elementType}`,
        title: `Action Suggestions - ${elementType}`,
        language: language,
        tags: ['action', 'selenium', elementType],
        description: context ? `Actions for ${elementType} in ${context}` : `Actions for ${elementType}`,
        code: code,
        createdAt: new Date().toISOString(),
        created: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    if (typeof showNotification === 'function') {
        showNotification('✅ Saved to Code Snippets!');
    }
    loadSnippets();
}

function saveToSnippets() {
    const code = document.getElementById('resultContent').textContent;
    if (!code || code === 'Your generated code will appear here...') {
        alert('No code to save');
        return;
    }
    
    // Get the detected language from the code element's class
    const codeElement = document.getElementById('resultContent');
    const classNames = codeElement.className.split(' ');
    const languageClass = classNames.find(cls => cls.startsWith('language-'));
    const detectedLanguage = languageClass ? languageClass.replace('language-', '') : 'java';
    
    showAddSnippetModal(code, detectedLanguage);
}

async function loadSnippets() {
    try {
        const saved = localStorage.getItem('codeSnippets');
        snippets = saved ? JSON.parse(saved) : [];
        displaySnippets();
    } catch (error) {
        console.error('Error loading snippets:', error);
    }
}

function displaySnippets() {
    const container = document.getElementById('snippetsList');
    
    if (snippets.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary);">
                <div style="font-size: 3em; margin-bottom: 15px;">📚</div>
                <h3 style="color: var(--text-primary); margin-bottom: 10px;">No Snippets Yet</h3>
                <p>Save code snippets for quick reuse</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = snippets.map((snippet) => {
        // Ensure tags is an array
        const tags = Array.isArray(snippet.tags) ? snippet.tags : [];
        const tagsString = tags.join(' ');
        const snippetTitle = snippet.title || snippet.name || 'Untitled';
        const snippetDate = snippet.date || new Date(snippet.createdAt || snippet.created).toLocaleString() || 'Unknown date';
        
        return `
        <div class="snippet-card" data-language="${snippet.language}" data-tags="${tagsString}" data-snippet-id="${snippet.id}" style="background: var(--card-bg); border: 2px solid var(--border-color); border-radius: 8px; padding: 15px; margin-bottom: 15px; transition: all 0.3s;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                <div style="display: flex; align-items: start; gap: 12px; flex: 1;">
                    <input type="checkbox" class="snippet-checkbox" data-snippet-id="${snippet.id}" onchange="updateDeleteButton()" style="cursor: pointer; width: 18px; height: 18px; margin-top: 3px;">
                    <div style="flex: 1;">
                        <h4 style="color: var(--text-primary); margin: 0 0 5px 0;">${snippetTitle}</h4>
                        <div style="display: flex; gap: 10px; align-items: center; font-size: 0.85em; color: var(--text-tertiary);">
                            <span style="background: var(--primary); color: white; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; font-size: 0.75em;">${snippet.language}</span>
                            <span>📅 ${snippetDate}</span>
                        </div>
                        ${snippet.description ? `<p style="margin: 8px 0 0 0; color: var(--text-secondary); font-size: 0.9em;">${snippet.description}</p>` : ''}
                        ${tags.length > 0 ? `
                            <div style="margin-top: 8px; display: flex; gap: 5px; flex-wrap: wrap;">
                                ${tags.map(tag => `<span style="background: var(--bg-secondary); color: var(--text-secondary); padding: 2px 8px; border-radius: 4px; font-size: 0.75em;">#${tag}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div style="display: flex; gap: 5px;">
                    <button onclick="useSnippet(${snippet.id})" style="background: var(--primary); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85em;" title="Use this snippet">
                        📝 Use
                    </button>
                    <button onclick="viewSnippet(${snippet.id})" style="background: var(--info); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85em;" title="View code">
                        👁️ View
                    </button>
                    <button onclick="deleteSnippet(${snippet.id})" style="background: var(--error); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85em;" title="Delete snippet">
                        🗑️
                    </button>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

function showAddSnippetModal(code = '', language = null) {
    // Use provided language or detect from code
    const detectedLanguage = language || detectLanguage(code);
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <h3 style="margin-bottom: 20px;">💾 Save Code Snippet</h3>
            
            <div style="margin-bottom: 20px; padding: 15px; background: var(--bg-tertiary); border-radius: 8px; border: 2px dashed var(--border-color);">
                <label for="snippetFileUpload" style="display: flex; align-items: center; justify-content: center; gap: 10px; cursor: pointer; color: var(--primary); font-weight: 600;">
                    📎 Upload Snippet from File
                    <input type="file" id="snippetFileUpload" accept=".java,.py,.js,.cs,.txt" style="display: none;">
                </label>
                <div style="text-align: center; font-size: 0.85em; color: var(--text-secondary); margin-top: 8px;">
                    Supported: .java, .py, .js, .cs, .txt
                </div>
            </div>
            
            <div class="form-group">
                <label for="snippetTitle">Title:</label>
                <input type="text" id="snippetTitle" placeholder="e.g., Login Test" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="snippetLanguage">Language:</label>
                <select id="snippetLanguage" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
                    <option value="java" ${detectedLanguage === 'java' ? 'selected' : ''}>Java</option>
                    <option value="python" ${detectedLanguage === 'python' ? 'selected' : ''}>Python</option>
                    <option value="javascript" ${detectedLanguage === 'javascript' ? 'selected' : ''}>JavaScript</option>
                    <option value="csharp" ${detectedLanguage === 'csharp' ? 'selected' : ''}>C#</option>
                </select>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="snippetTags">Tags (comma-separated):</label>
                <input type="text" id="snippetTags" placeholder="e.g., selenium, login, webdriver" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="snippetDescription">Description (optional):</label>
                <textarea id="snippetDescription" placeholder="Brief description of what this snippet does..." style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary); min-height: 60px;"></textarea>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="snippetCode">Code:</label>
                <textarea id="snippetCode" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary); min-height: 200px; font-family: 'JetBrains Mono', monospace;">${escapeHtml(code)}</textarea>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button class="btn" onclick="saveSnippet()" style="flex: 1;">
                    💾 Save Snippet
                </button>
                <button class="btn-secondary" onclick="this.closest('.modal-overlay').remove()" style="flex: 1;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Attach file upload event handler after modal is added to DOM
    const fileInput = document.getElementById('snippetFileUpload');
    if (fileInput) {
        fileInput.addEventListener('change', handleSnippetFileUpload);
    }
}

function handleSnippetFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        
        // Extract filename without extension for title
        const fileName = file.name.replace(/\.[^/.]+$/, '');
        document.getElementById('snippetTitle').value = fileName;
        
        // Detect language from file extension
        const ext = file.name.split('.').pop().toLowerCase();
        const langMap = {
            'java': 'java',
            'py': 'python',
            'js': 'javascript',
            'cs': 'csharp',
            'txt': 'java'
        };
        const detectedLang = langMap[ext] || 'java';
        document.getElementById('snippetLanguage').value = detectedLang;
        
        // Set code content
        document.getElementById('snippetCode').value = content;
        
        // Try to extract metadata from comments if present
        extractMetadataFromCode(content);
        
        if (typeof showNotification === 'function') {
            showNotification(`✅ File "${file.name}" loaded successfully!`);
        }
    };
    
    reader.onerror = function() {
        alert('Error reading file. Please try again.');
    };
    
    reader.readAsText(file);
}

function extractMetadataFromCode(content) {
    // Try to extract title, description, and tags from code comments
    const lines = content.split('\n');
    
    for (let i = 0; i < Math.min(lines.length, 20); i++) {
        const line = lines[i].trim();
        
        // Extract Title
        if (line.includes('Title:')) {
            const title = line.split('Title:')[1].trim().replace(/\*\/|\*|"""/g, '').trim();
            if (title && !document.getElementById('snippetTitle').value) {
                document.getElementById('snippetTitle').value = title;
            }
        }
        
        // Extract Description
        if (line.includes('Description:')) {
            const desc = line.split('Description:')[1].trim().replace(/\*\/|\*|"""/g, '').trim();
            if (desc) {
                document.getElementById('snippetDescription').value = desc;
            }
        }
        
        // Extract Tags
        if (line.includes('Tags:')) {
            const tags = line.split('Tags:')[1].trim().replace(/\*\/|\*|"""/g, '').trim();
            if (tags) {
                document.getElementById('snippetTags').value = tags;
            }
        }
    }
}

function detectLanguage(code) {
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        return 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        return 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        return 'csharp';
    }
    return 'java';
}

function saveSnippet() {
    const title = document.getElementById('snippetTitle').value.trim();
    const description = document.getElementById('snippetDescription').value.trim();
    const language = document.getElementById('snippetLanguage').value;
    const tagsInput = document.getElementById('snippetTags').value.trim();
    const code = document.getElementById('snippetCode').value.trim();
    
    if (!title) {
        alert('Please enter a title');
        return;
    }
    
    if (!code) {
        alert('Please enter code');
        return;
    }
    
    const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];
    
    const snippet = {
        id: Date.now(),
        title: title,
        name: title,
        description,
        language,
        tags,
        code,
        createdAt: new Date().toISOString(),
        created: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    displaySnippets();
    document.querySelector('.modal-overlay').remove();
    window.showNotification('✅ Snippet saved!');
}

function useSnippet(id) {
    const snippet = snippets.find(s => s.id === id);
    if (!snippet) return;
    
    // Display in output
    if (typeof displayResult === 'function') {
        displayResult(snippet.code, 0, 0);
    }
    
    // Switch to generate tab
    if (typeof switchTab === 'function') {
        switchTab('generate');
    }
    
    if (typeof showNotification === 'function') {
        showNotification('✅ Snippet loaded into output!');
    }
}

function editSnippet(id) {
    const snippetIndex = snippets.findIndex(s => s.id === id);
    if (snippetIndex === -1) return;
    const snippet = snippets[snippetIndex];
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">✏️ Edit Snippet</h3>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Snippet Name:</label>
                <input type="text" id="editSnippetName" value="${snippet.name}" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Description:</label>
                <textarea id="editSnippetDescription" rows="2" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">${snippet.description || ''}</textarea>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Language:</label>
                <select id="editSnippetLanguage" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
                    <option value="python" ${snippet.language === 'python' ? 'selected' : ''}>Python</option>
                    <option value="java" ${snippet.language === 'java' ? 'selected' : ''}>Java</option>
                    <option value="javascript" ${snippet.language === 'javascript' ? 'selected' : ''}>JavaScript</option>
                    <option value="csharp" ${snippet.language === 'csharp' ? 'selected' : ''}>C#</option>
                </select>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Tags (comma-separated):</label>
                <input type="text" id="editSnippetTags" value="${snippet.tags ? snippet.tags.join(', ') : ''}" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Code:</label>
                <textarea id="editSnippetCode" rows="10" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary); font-family: monospace;">${snippet.code}</textarea>
            </div>
            
            <div style="display: flex; gap: 10px;">
                <button class="btn" onclick="updateSnippet(${snippetIndex})" style="flex: 1; background: var(--success);">
                    💾 Update
                </button>
                <button class="btn" onclick="this.closest('.modal-overlay').remove()" style="flex: 1;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function updateSnippet(index) {
    const name = document.getElementById('editSnippetName').value.trim();
    const description = document.getElementById('editSnippetDescription').value.trim();
    const language = document.getElementById('editSnippetLanguage').value;
    const tagsInput = document.getElementById('editSnippetTags').value.trim();
    const code = document.getElementById('editSnippetCode').value.trim();
    
    if (!name || !code) {
        alert('Name and code are required');
        return;
    }
    
    const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];
    
    snippets[index] = {
        ...snippets[index],
        name,
        description,
        language,
        tags,
        code
    };
    
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    displaySnippets();
    document.querySelector('.modal-overlay').remove();
    window.showNotification('✅ Snippet updated!');
}

function deleteSnippet(id) {
    if (!confirm('Are you sure you want to delete this snippet?')) {
        return;
    }
    
    snippets = snippets.filter(s => s.id !== id);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    displaySnippets();
    if (typeof showNotification === 'function') {
        showNotification('🗑️ Snippet deleted');
    }
}

function filterSnippets() {
    const searchTerm = document.getElementById('snippetSearch')?.value.toLowerCase().trim() || '';
    const languageFilter = document.getElementById('snippetFilter')?.value || 'all';
    const snippetCards = document.querySelectorAll('.snippet-card');
    
    snippetCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const language = card.getAttribute('data-language');
        const tags = card.getAttribute('data-tags');
        
        const matchesSearch = text.includes(searchTerm) || tags.includes(searchTerm);
        const matchesLanguage = languageFilter === 'all' || language === languageFilter;
        
        card.style.display = matchesSearch && matchesLanguage ? 'block' : 'none';
    });
}

function clearSnippetSearch() {
    document.getElementById('snippetSearch').value = '';
    displaySnippets();
}

function exportSnippets() {
    if (snippets.length === 0) {
        alert('No snippets to export');
        return;
    }
    
    const data = JSON.stringify(snippets, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'code-snippets.json';
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    window.showNotification('✅ Snippets exported!');
}

function importSnippets() {
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
                if (Array.isArray(imported)) {
                    snippets = [...snippets, ...imported];
                    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
                    displaySnippets();
                    window.showNotification(`✅ Imported ${imported.length} snippets`);
                } else {
                    throw new Error('Invalid format');
                }
            } catch (error) {
                alert('Error importing snippets: ' + error.message);
            }
        };
        reader.readAsText(file);
    };
    
    input.click();
}

function deleteSelectedSnippets() {
    const checkboxes = document.querySelectorAll('.snippet-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('No snippets selected');
        return;
    }
    
    if (confirm(`Delete ${checkboxes.length} selected snippet(s)?`)) {
        checkboxes.forEach(cb => {
            const snippetId = parseInt(cb.dataset.snippetId);
            if (!isNaN(snippetId) && typeof deleteSnippet === 'function') {
                deleteSnippet(snippetId);
            }
        });
        window.showNotification(`✅ ${checkboxes.length} snippet(s) deleted!`);
    }
}

// Expose functions to global scope for HTML onclick handlers
window.loadSnippets = loadSnippets;
window.displaySnippets = displaySnippets;
window.showAddSnippetModal = showAddSnippetModal;
window.saveSnippet = saveSnippet;
window.useSnippet = useSnippet;
window.editSnippet = editSnippet;
window.updateSnippet = updateSnippet;
window.deleteSnippet = deleteSnippet;
window.deleteSelectedSnippets = deleteSelectedSnippets;
window.filterSnippets = filterSnippets;
window.clearSnippetSearch = clearSnippetSearch;
window.exportSnippets = exportSnippets;
window.importSnippets = importSnippets;
window.saveLocatorToSnippets = saveLocatorToSnippets;
window.saveActionToSnippets = saveActionToSnippets;
window.saveToSnippets = saveToSnippets;
window.toggleSelectAllSnippets = toggleSelectAllSnippets;
window.updateDeleteButton = updateDeleteButton;
window.viewSnippet = viewSnippet;
window.copySnippetCode = copySnippetCode;
window.handleSnippetFileUpload = handleSnippetFileUpload;
window.extractMetadataFromCode = extractMetadataFromCode;
window.detectLanguage = detectLanguage;

function toggleSelectAllSnippets() {
    const selectAll = document.getElementById('selectAllSnippets');
    const checkboxes = document.querySelectorAll('.snippet-checkbox');
    
    checkboxes.forEach(cb => {
        cb.checked = selectAll.checked;
    });
    
    if (typeof updateDeleteButton === 'function') {
        updateDeleteButton();
    }
}

function updateDeleteButton() {
    const checkboxes = document.querySelectorAll('.snippet-checkbox');
    const checkedBoxes = Array.from(checkboxes).filter(cb => cb.checked);
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    const selectAll = document.getElementById('selectAllSnippets');
    
    if (!deleteBtn || !selectAll) return;
    
    // Show/hide delete button
    if (checkedBoxes.length > 0) {
        deleteBtn.style.display = 'block';
        deleteBtn.textContent = `🗑️ Delete Selected (${checkedBoxes.length})`;
    } else {
        deleteBtn.style.display = 'none';
    }
    
    // Update select all checkbox state
    if (checkedBoxes.length === 0) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
    } else if (checkedBoxes.length === checkboxes.length) {
        selectAll.checked = true;
        selectAll.indeterminate = false;
    } else {
        selectAll.checked = false;
        selectAll.indeterminate = true;
    }
}

function viewSnippet(id) {
    const snippetData = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    const snippet = snippetData.find(s => s.id === id);
    
    if (!snippet) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px; max-height: 80vh; overflow: auto;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                <div>
                    <h3 style="margin: 0;">${snippet.title || snippet.name}</h3>
                    <div style="margin-top: 8px; display: flex; gap: 10px; align-items: center; font-size: 0.9em; color: var(--text-tertiary);">
                        <span style="background: var(--primary); color: white; padding: 4px 10px; border-radius: 4px; text-transform: uppercase; font-size: 0.8em;">${snippet.language}</span>
                        <span>📅 ${snippet.date}</span>
                    </div>
                </div>
                <button onclick="this.closest('.modal-overlay').remove()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text-secondary);">×</button>
            </div>
            ${snippet.description ? `<p style="color: var(--text-secondary); margin-bottom: 15px;">${snippet.description}</p>` : ''}
            ${snippet.tags && snippet.tags.length > 0 ? `
                <div style="margin-bottom: 15px; display: flex; gap: 5px; flex-wrap: wrap;">
                    ${snippet.tags.map(tag => `<span style="background: var(--bg-secondary); color: var(--text-secondary); padding: 4px 10px; border-radius: 4px; font-size: 0.85em;">#${tag}</span>`).join('')}
                </div>
            ` : ''}
            <pre style="background: var(--result-bg); border: 2px solid var(--border-color); border-radius: 8px; padding: 15px; overflow-x: auto;"><code class="language-${snippet.language}">${escapeHtml(snippet.code)}</code></pre>
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button class="btn" onclick="useSnippet(${snippet.id}); this.closest('.modal-overlay').remove();" style="flex: 1;">
                    📝 Use This Snippet
                </button>
                <button class="btn-secondary" onclick="copySnippetCode(${snippet.id})" style="flex: 1;">
                    📋 Copy Code
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Apply syntax highlighting
    if (typeof Prism !== 'undefined') {
        modal.querySelectorAll('code').forEach(block => Prism.highlightElement(block));
    }
}

function copySnippetCode(id) {
    const snippetData = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    const snippet = snippetData.find(s => s.id === id);
    
    if (snippet) {
        navigator.clipboard.writeText(snippet.code).then(() => {
            if (typeof showNotification === 'function') {
                showNotification('✅ Code copied to clipboard!');
            }
        });
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


