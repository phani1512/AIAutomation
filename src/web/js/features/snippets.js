// Code Snippets Management

function showAddSnippetModal(code = '') {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            <h3 style="margin-bottom: 20px;">💾 Save Code Snippet</h3>
            <div class="form-group">
                <label for="snippetTitle">Title:</label>
                <input type="text" id="snippetTitle" placeholder="Enter snippet title" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="snippetLanguage">Language:</label>
                <select id="snippetLanguage" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
                    <option value="java">Java</option>
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="csharp">C#</option>
                </select>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="snippetTags">Tags (comma-separated):</label>
                <input type="text" id="snippetTags" placeholder="test, selenium, automation" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="snippetDescription">Description:</label>
                <textarea id="snippetDescription" rows="2" placeholder="Optional description" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);"></textarea>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="snippetCode">Code:</label>
                <textarea id="snippetCode" rows="10" placeholder="Paste or type your code here" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary); font-family: 'Courier New', monospace;">${code}</textarea>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button class="btn btn-primary" onclick="saveSnippet()" style="flex: 1;">
                    💾 Save Snippet
                </button>
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()" style="flex: 1;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    if (code) {
        const language = detectLanguage(code);
        document.getElementById('snippetLanguage').value = language;
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
    const language = document.getElementById('snippetLanguage').value;
    const tags = document.getElementById('snippetTags').value.trim();
    const description = document.getElementById('snippetDescription').value.trim();
    const code = document.getElementById('snippetCode').value.trim();
    
    if (!title) {
        alert('Please enter a title');
        return;
    }
    
    if (!code) {
        alert('Please enter code');
        return;
    }
    
    const snippet = {
        id: Date.now(),
        title: title,
        language: language,
        tags: tags ? tags.split(',').map(t => t.trim()) : [],
        description: description,
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    document.querySelector('.modal-overlay').remove();
    showNotification('✅ Snippet saved to library!');
    loadSnippets();
}

function loadSnippets() {
    const snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    const listDiv = document.getElementById('snippetsList');
    
    if (!listDiv) {
        return;
    }
    
    if (snippets.length === 0) {
        listDiv.innerHTML = `
            <div style="padding: 20px; text-align: center; color: var(--text-secondary);">
                No snippets yet. Save your first snippet!
            </div>
        `;
        return;
    }
    
    listDiv.innerHTML = snippets.map(snippet => {
        const tags = Array.isArray(snippet.tags) ? snippet.tags : [];
        const tagsString = tags.join(' ');
        
        return `
        <div class="snippet-card" data-language="${snippet.language}" data-tags="${tagsString}" style="background: var(--card-bg); border: 2px solid var(--border-color); border-radius: 8px; padding: 15px; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="display: flex; align-items: start; gap: 12px; flex: 1;">
                    <input type="checkbox" class="snippet-checkbox" data-snippet-id="${snippet.id}" onchange="updateDeleteButton()" style="cursor: pointer; width: 18px; height: 18px; margin-top: 3px;">
                    <div style="flex: 1;">
                        <h4 style="color: var(--text-primary); margin: 0 0 5px 0;">${snippet.title}</h4>
                        <div style="display: flex; gap: 10px; align-items: center; font-size: 0.85em; color: var(--text-tertiary);">
                            <span style="background: var(--primary); color: white; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; font-size: 0.75em;">${snippet.language}</span>
                            <span>📅 ${snippet.date}</span>
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
                    <button onclick="useSnippet(${snippet.id})" class="btn" style="padding: 6px 12px; font-size: 0.85em;">
                        📝 Use
                    </button>
                    <button onclick="viewSnippet(${snippet.id})" class="btn" style="padding: 6px 12px; font-size: 0.85em; background: var(--info);">
                        👁️ View
                    </button>
                    <button onclick="deleteSnippet(${snippet.id})" class="btn" style="padding: 6px 12px; font-size: 0.85em; background: var(--error);">
                        🗑️
                    </button>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

function filterSnippets() {
    const searchTerm = document.getElementById('snippetSearch').value.toLowerCase();
    const languageFilter = document.getElementById('snippetFilter').value;
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

function useSnippet(id) {
    const snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    const snippet = snippets.find(s => s.id === id);
    
    if (snippet) {
        displayResult(snippet.code, 0, 0);
        switchTab('generate');
        showNotification('✅ Snippet loaded into output!');
    }
}

function viewSnippet(id) {
    const snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    const snippet = snippets.find(s => s.id === id);
    
    if (!snippet) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px; max-height: 80vh; overflow: auto;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                <div>
                    <h3 style="margin: 0;">${snippet.title}</h3>
                    <div style="margin-top: 8px; display: flex; gap: 10px; align-items: center; font-size: 0.9em; color: var(--text-tertiary);">
                        <span style="background: var(--primary); color: white; padding: 4px 10px; border-radius: 4px; text-transform: uppercase; font-size: 0.8em;">${snippet.language}</span>
                        <span>📅 ${snippet.date}</span>
                    </div>
                </div>
                <button onclick="this.closest('.modal-overlay').remove()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text-secondary);">×</button>
            </div>
            ${snippet.description ? `<p style="color: var(--text-secondary); margin-bottom: 15px;">${snippet.description}</p>` : ''}
            ${snippet.tags.length > 0 ? `
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
    
    if (typeof Prism !== 'undefined') {
        modal.querySelectorAll('code').forEach(block => Prism.highlightElement(block));
    }
}

function copySnippetCode(id) {
    const snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    const snippet = snippets.find(s => s.id === id);
    
    if (snippet) {
        navigator.clipboard.writeText(snippet.code).then(() => {
            showNotification('✅ Code copied to clipboard!');
        });
    }
}

function deleteSnippet(id) {
    if (!confirm('Are you sure you want to delete this snippet?')) {
        return;
    }
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets = snippets.filter(s => s.id !== id);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    loadSnippets();
    showNotification('🗑️ Snippet deleted');
}

function toggleSelectAllSnippets() {
    const selectAll = document.getElementById('selectAllSnippets');
    const checkboxes = document.querySelectorAll('.snippet-checkbox');
    
    checkboxes.forEach(cb => {
        cb.checked = selectAll.checked;
    });
    
    updateDeleteButton();
}

function updateDeleteButton() {
    const checkboxes = document.querySelectorAll('.snippet-checkbox');
    const checkedBoxes = Array.from(checkboxes).filter(cb => cb.checked);
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    const selectAll = document.getElementById('selectAllSnippets');
    
    if (checkedBoxes.length > 0) {
        deleteBtn.style.display = 'block';
        deleteBtn.textContent = `🗑️ Delete Selected (${checkedBoxes.length})`;
    } else {
        deleteBtn.style.display = 'none';
    }
    
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

function deleteSelectedSnippets() {
    const checkboxes = document.querySelectorAll('.snippet-checkbox:checked');
    const selectedIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.snippetId));
    
    if (selectedIds.length === 0) {
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${selectedIds.length} snippet(s)?`)) {
        return;
    }
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets = snippets.filter(s => !selectedIds.includes(s.id));
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    document.getElementById('selectAllSnippets').checked = false;

    loadSnippets();
    showNotification(`🗑️ ${selectedIds.length} snippet(s) deleted`);
}

// Expose functions to window object
window.showAddSnippetModal = showAddSnippetModal;
window.loadSnippets = loadSnippets;
window.filterSnippets = filterSnippets;
window.useSnippet = useSnippet;
window.viewSnippet = viewSnippet;
window.deleteSnippet = deleteSnippet;
window.toggleSelectAllSnippets = toggleSelectAllSnippets;
window.deleteSelectedSnippets = deleteSelectedSnippets;