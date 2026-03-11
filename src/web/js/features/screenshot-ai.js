// Screenshot AI Features - Professional Screenshot Test Generator
// Handles screenshot upload, analysis, and test code generation with OCR support

let currentScreenshotData = null;

// Initialize Screenshot AI functionality
function initializeScreenshotAI() {
    const uploadAreaScreenshot = document.getElementById('uploadAreaScreenshot');
    const screenshotInput = document.getElementById('screenshotInput');
    
    if (!uploadAreaScreenshot || !screenshotInput) {
        // Elements not loaded yet - this is normal during initial page load
        return;
    }
    
    const screenshotPreview = document.getElementById('screenshotPreview');

    // Upload area click handler
    uploadAreaScreenshot.addEventListener('click', () => screenshotInput.click());

    // Drag and drop handlers
    uploadAreaScreenshot.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadAreaScreenshot.style.background = 'var(--bg-primary)';
        uploadAreaScreenshot.style.borderColor = 'var(--primary)';
    });

    uploadAreaScreenshot.addEventListener('dragleave', () => {
        uploadAreaScreenshot.style.background = 'var(--bg-secondary)';
        uploadAreaScreenshot.style.borderColor = 'var(--border-color)';
    });

    uploadAreaScreenshot.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadAreaScreenshot.style.background = 'var(--bg-secondary)';
        uploadAreaScreenshot.style.borderColor = 'var(--border-color)';
        const file = e.dataTransfer.files[0];
        if (file) handleScreenshotUpload(file);
    });

    screenshotInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleScreenshotUpload(file);
    });

    // Clipboard paste support
    document.addEventListener('paste', (e) => {
        if (document.getElementById('screenshotPage')?.classList.contains('active')) {
            const items = e.clipboardData.items;
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const blob = items[i].getAsFile();
                    handleScreenshotUpload(blob);
                    break;
                }
            }
        }
    });
    
    console.log('[Screenshot AI] Initialized successfully');
}

function handleScreenshotUpload(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        currentScreenshotData = e.target.result;
        const screenshotPreview = document.getElementById('screenshotPreview');
        screenshotPreview.src = currentScreenshotData;
        document.getElementById('screenshotPreviewContainer').style.display = 'block';
        console.log('[Screenshot AI] Image uploaded successfully');
    };
    reader.readAsDataURL(file);
}

async function analyzeScreenshotAI() {
    if (!currentScreenshotData) {
        showNotification('⚠️ Please upload a screenshot first', 'error');
        return;
    }

    const loading = document.getElementById('screenshotLoadingIndicator');
    loading.style.display = 'block';
    document.getElementById('screenshotAnalysisResults').style.display = 'none';

    try {
        const language = document.getElementById('pomLanguage').value;
        const testName = document.getElementById('screenshotTestIntent').value.split(' ')[0] || 'ScreenshotTest';
        
        const response = await fetch('/screenshot/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                screenshot: currentScreenshotData,
                intent: document.getElementById('screenshotTestIntent').value,
                language: language,
                test_name: testName
            })
        });

        const data = await response.json();
        
        console.log('[ANALYZE] Complete response:', data);
        
        // Check for error response
        if (data.error) {
            loading.style.display = 'none';
            let errorMsg = data.error;
            
            // Add debug info if available
            if (data.debug) {
                console.log('[ANALYZE] Debug info:', data.debug);
                errorMsg += `<br><br>📊 Detection Results:`;
                errorMsg += `<br>• Dimensions: ${data.debug.dimensions || 'N/A'}`;
                errorMsg += `<br>• Buttons found: ${data.debug.buttons || 0}`;
                errorMsg += `<br>• Inputs found: ${data.debug.inputs || 0}`;
                errorMsg += `<br>• Text regions: ${data.debug.text_regions || 0}`;
            }
            
            // Add suggestion
            if (data.suggestion) {
                errorMsg += `<br><br>💡 Suggestion: ${data.suggestion}`;
            }
            
            showNotification(`❌ ${errorMsg}`, 'error');
            return;
        }
        
        // Check if response has required data
        if (!response.ok || !data.summary) {
            loading.style.display = 'none';
            showNotification(`❌ Analysis failed: ${data.message || 'Invalid response from server'}`, 'error');
            return;
        }
        
        // Display summary
        displayScreenshotAnalysis(data);
        
        // Display complete test suite
        if (data.test_suite) {
            displayCompleteTestSuite(data.test_suite);
        }
        
        // Display test data
        if (data.test_data) {
            displayTestData(data.test_data);
        }
        
        // Display saved files info
        if (data.saved_files && data.saved_files.status === 'success') {
            displaySavedFilesInfo(data.saved_files);
            const testCases = data.summary?.test_cases_generated || 0;
            const filesCount = data.saved_files.files_count || Object.keys(data.saved_files.files || {}).length;
            showNotification(`✅ Generated ${testCases} test cases and saved ${filesCount} files!`);
        } else if (data.summary?.test_cases_generated) {
            showNotification(`✅ Generated ${data.summary.test_cases_generated} test cases with locators!`);
        } else {
            showNotification(`✅ Analysis complete!`);
        }
    } catch (error) {
        console.error('[Screenshot AI] Analysis error:', error);
        showNotification('❌ Error: ' + error.message, 'error');
    } finally {
        loading.style.display = 'none';
    }
}

function displaySavedFilesInfo(savedFiles) {
    // Create info panel
    const infoPanel = document.createElement('div');
    infoPanel.style.cssText = 'background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 10px; margin-top: 20px;';
    
    let filesHTML = '<h3 style="margin: 0 0 15px 0;">✅ Tests Saved to Project!</h3>';
    filesHTML += '<div style="font-size: 0.9em; line-height: 1.8;">';
    
    for (const [type, path] of Object.entries(savedFiles.files)) {
        const fileName = path.split('\\').pop();
        filesHTML += `<div>📄 ${type}: <strong>${fileName}</strong></div>`;
    }
    
    filesHTML += '</div>';
    filesHTML += '<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.3);">';
    filesHTML += `<div style="font-weight: bold; margin-bottom: 10px;">🚀 Run Tests:</div>`;
    filesHTML += `<div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; font-family: monospace;">${savedFiles.execution.command}</div>`;
    filesHTML += '</div>';
    
    infoPanel.innerHTML = filesHTML;
    
    // Insert at top of analysis results
    const analysisCard = document.getElementById('screenshotAnalysisResults');
    analysisCard.insertBefore(infoPanel, analysisCard.firstChild);
}

function displayCompleteTestSuite(testSuite) {
    // Show Page Object
    document.getElementById('screenshotPOMCode').textContent = testSuite.page_object;
    document.getElementById('pomLanguageLabel').textContent = `${testSuite.language.toUpperCase()} | ${testSuite.test_count} elements`;
    document.getElementById('screenshotPOMResults').style.display = 'block';
    
    // Show Test Class
    document.getElementById('screenshotGeneratedCode').textContent = testSuite.test_class;
    document.getElementById('screenshotCodeResults').style.display = 'block';
    
    console.log('[Screenshot AI] Test suite displayed successfully');
}

function displayScreenshotAnalysis(data) {
    // Check for errors or invalid data
    if (!data || data.error) {
        console.warn('[Screenshot AI] Invalid data for display:', data);
        return;
    }
    
    const analysisCard = document.getElementById('screenshotAnalysisResults');
    analysisCard.style.display = 'block';
    
    const statsContainer = document.getElementById('screenshotStatsContainer');
    
    // Build stats cards with safe access
    const totalElements = data.total_elements || 0;
    const buttons = (data.elements?.buttons || []).length;
    const inputs = (data.elements?.inputs || []).length;
    
    let statsHTML = `
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2.5em; font-weight: bold;">${totalElements}</div>
            <div style="font-size: 0.9em; opacity: 0.9; margin-top: 5px;">Total Elements</div>
        </div>
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2.5em; font-weight: bold;">${buttons}</div>
            <div style="font-size: 0.9em; opacity: 0.9; margin-top: 5px;">Buttons</div>
        </div>
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2.5em; font-weight: bold;">${inputs}</div>
            <div style="font-size: 0.9em; opacity: 0.9; margin-top: 5px;">Input Fields</div>
        </div>
    `;
    
    // Add OCR indicator if enabled
    if (data.ocr_enabled) {
        statsHTML += `
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <div style="font-size: 2.5em; font-weight: bold;">✓</div>
                <div style="font-size: 0.9em; opacity: 0.9; margin-top: 5px;">OCR Enabled</div>
            </div>
        `;
    }
    
    statsContainer.innerHTML = statsHTML;

    const container = document.getElementById('screenshotElementsContainer');
    container.innerHTML = '<h4 style="margin-top: 20px; color: var(--text-primary);">Detected Elements</h4>';
    
    // Show locator strategies if enabled
    const showLocators = document.getElementById('showLocatorStrategies')?.checked;
    
    if (data.suggested_actions && data.suggested_actions.length > 0) {
        const grid = document.createElement('div');
        grid.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin-top: 20px;';

        data.suggested_actions.forEach((action, idx) => {
            const card = document.createElement('div');
            card.style.cssText = 'background: var(--bg-secondary); padding: 16px; border-radius: 8px; border-left: 4px solid var(--primary);';
            
            let cardHTML = `
                <h4 style="color: var(--primary); margin-bottom: 8px;">Step ${idx + 1}</h4>
                <p style="font-size: 0.9em; color: var(--text-secondary); margin: 4px 0;"><strong>Action:</strong> ${action.action}</p>
                <p style="font-size: 0.9em; color: var(--text-secondary); margin: 4px 0;"><strong>Element:</strong> ${action.element_type}</p>
                <p style="font-size: 0.9em; color: var(--text-secondary); margin: 4px 0;">${action.description || ''}</p>
            `;
            
            // Add OCR text if available
            if (action.text) {
                cardHTML += `<p style="font-size: 0.85em; color: var(--primary); margin: 8px 0;"><strong>📝 Text:</strong> "${action.text}"</p>`;
            }
            
            card.innerHTML = cardHTML;
            grid.appendChild(card);
        });

        container.appendChild(grid);
    }
    
    // Display text regions from OCR
    if (data.text_regions && data.text_regions.length > 0) {
        const textSection = document.createElement('div');
        textSection.innerHTML = '<h4 style="margin-top: 30px; color: var(--text-primary);">📝 Extracted Text (OCR)</h4>';
        
        const textGrid = document.createElement('div');
        textGrid.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin-top: 15px;';
        
        data.text_regions.slice(0, 12).forEach(region => {
            const textCard = document.createElement('div');
            textCard.style.cssText = 'background: var(--bg-primary); padding: 12px; border-radius: 6px; border: 1px solid var(--border-color);';
            textCard.innerHTML = `
                <p style="font-size: 0.85em; color: var(--text-primary); margin: 0;">${region.text}</p>
                <p style="font-size: 0.75em; color: var(--text-secondary); margin-top: 6px;">Confidence: ${Math.round(region.confidence)}%</p>
            `;
            textGrid.appendChild(textCard);
        });
        
        textSection.appendChild(textGrid);
        container.appendChild(textSection);
    }
}

async function generateScreenshotCode() {
    if (!currentScreenshotData) {
        showNotification('⚠️ Please upload a screenshot first', 'error');
        return;
    }

    const loading = document.getElementById('screenshotLoadingIndicator');
    loading.style.display = 'block';
    document.getElementById('screenshotCodeResults').style.display = 'none';

    try {
        const response = await fetch('/screenshot/generate-code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                screenshot: currentScreenshotData,
                intent: document.getElementById('screenshotTestIntent').value,
                test_name: document.getElementById('screenshotTestName').value
            })
        });

        const data = await response.json();
        
        // Check for errors
        if (data.error || !response.ok) {
            showNotification(`❌ ${data.error || 'Failed to generate code'}`, 'error');
            return;
        }
        
        if (data.code) {
            document.getElementById('screenshotGeneratedCode').textContent = data.code;
            document.getElementById('screenshotCodeResults').style.display = 'block';
            showNotification('✅ Test code generated successfully');
        } else {
            showNotification('⚠️ No code was generated', 'error');
        }
        
        if (data.analysis) {
            displayScreenshotAnalysis(data.analysis);
        }
    } catch (error) {
        console.error('[Screenshot AI] Code generation error:', error);
        showNotification('❌ Error generating code: ' + error.message, 'error');
    } finally {
        loading.style.display = 'none';
    }
}

function resetScreenshotForm() {
    currentScreenshotData = null;
    document.getElementById('screenshotPreview').src = '';
    document.getElementById('screenshotPreviewContainer').style.display = 'none';
    document.getElementById('screenshotTestIntent').value = '';
    document.getElementById('screenshotTestName').value = '';
    document.getElementById('screenshotCodeResults').style.display = 'none';
    document.getElementById('screenshotPOMResults').style.display = 'none';
    document.getElementById('screenshotTestDataResults').style.display = 'none';
    document.getElementById('screenshotStatsContainer').innerHTML = '';
    document.getElementById('screenshotElementsContainer').innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Upload a screenshot and click "Analyze" to see detected elements</div>';
    const screenshotInput = document.getElementById('screenshotInput');
    if (screenshotInput) screenshotInput.value = '';
    showNotification('🔄 Form reset');
}

function copyScreenshotCode() {
    const code = document.getElementById('screenshotGeneratedCode').textContent;
    navigator.clipboard.writeText(code).then(() => {
        showNotification('📋 Code copied to clipboard!');
    }).catch(err => {
        console.error('[Screenshot AI] Copy error:', err);
        showNotification('❌ Failed to copy code', 'error');
    });
}

function copyPOMCode() {
    const code = document.getElementById('screenshotPOMCode').textContent;
    navigator.clipboard.writeText(code).then(() => {
        showNotification('📋 POM code copied to clipboard!');
    }).catch(err => {
        console.error('[Screenshot AI] Copy error:', err);
        showNotification('❌ Failed to copy POM code', 'error');
    });
}

async function generatePOMCode() {
    if (!currentScreenshotData) {
        showNotification('⚠️ Please upload a screenshot first', 'error');
        return;
    }

    const loading = document.getElementById('screenshotLoadingIndicator');
    loading.style.display = 'block';

    try {
        const language = document.getElementById('pomLanguage').value;
        const pageName = document.getElementById('screenshotTestIntent').value.split(' ')[0] || 'Test';
        
        const response = await fetch('/screenshot/generate-pom', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                screenshot: currentScreenshotData,
                intent: document.getElementById('screenshotTestIntent').value,
                language: language,
                page_name: pageName
            })
        });

        const data = await response.json();
        
        console.log('[Screenshot AI] POM Response received:', data);
        
        // Check for errors
        if (data.error || !response.ok) {
            showNotification(`❌ ${data.error || 'Failed to generate POM'}`, 'error');
            return;
        }
        
        if (data.pom_code) {
            document.getElementById('screenshotPOMCode').textContent = data.pom_code;
            document.getElementById('pomLanguageLabel').textContent = `${language.toUpperCase()} POM`;
            document.getElementById('screenshotPOMResults').style.display = 'block';
            showNotification('✅ POM code generated successfully');
        } else {
            showNotification('⚠️ No POM code in response', 'error');
        }
    } catch (error) {
        console.error('[Screenshot AI] POM generation error:', error);
        showNotification('❌ Error generating POM: ' + error.message, 'error');
    } finally {
        loading.style.display = 'none';
    }
}

function displayTestData(testData) {
    if (!testData || Object.keys(testData).length === 0) return;
    
    const container = document.getElementById('testDataContainer');
    const resultsCard = document.getElementById('screenshotTestDataResults');
    
    let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">';
    
    for (const [category, items] of Object.entries(testData)) {
        html += `
            <div style="background: var(--bg-secondary); padding: 16px; border-radius: 8px; border-left: 4px solid var(--primary);">
                <h4 style="color: var(--primary); margin-bottom: 12px;">${category}</h4>
                <ul style="list-style: none; padding: 0; margin: 0;">
        `;
        
        if (Array.isArray(items)) {
            items.forEach(item => {
                html += `<li style="padding: 6px 0; color: var(--text-primary); font-size: 0.9em;">• ${item}</li>`;
            });
        }
        
        html += '</ul></div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
    resultsCard.style.display = 'block';
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeScreenshotAI);
} else {
    initializeScreenshotAI();
}

console.log('[Screenshot AI] Module loaded');
