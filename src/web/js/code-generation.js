// Code Generation Functions
// FIXED VERSION - with null checks

async function generateCode() {
    console.log('[DEBUG] generateCode() called');
    const promptInput = document.getElementById('promptInput');
    
    if (!promptInput) {
        console.error('[ERROR] promptInput element not found!');
        alert('Error: Prompt input field not found. Please refresh the page.');
        return;
    }
    
    const prompt = promptInput.value.trim();
    const languageSelector = document.getElementById('languageSelector');
    const language = languageSelector ? languageSelector.value : 'python';
    const executeCheckbox = document.getElementById('executeCheckbox');
    const execute = executeCheckbox ? executeCheckbox.checked : false;

    if (!prompt) {
        alert('Please enter a test description');
        return;
    }

    const outputDiv = document.getElementById('generatedCode');
    if (!outputDiv) {
        console.error('[ERROR] generatedCode element not found!');
        return;
    }

    outputDiv.textContent = 'Generating code...';

    try {
        const response = await fetch(API_URL + '/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, language, execute })
        });

        if (!response.ok) {
            throw new Error('Failed to generate code');
        }

        const data = await response.json();
        outputDiv.textContent = data.code || 'No code generated';
        window.showNotification('Code generated successfully', 'success');
    } catch (error) {
        console.error('[ERROR]', error);
        outputDiv.textContent = 'Error: ' + error.message;
        window.showNotification('Failed to generate code', 'error');
    }
}
