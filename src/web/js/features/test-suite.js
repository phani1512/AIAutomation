// Test Suite Management

// VERSION CHECK - Force browser to reload if using old cached version
const TEST_SUITE_VERSION = '2.2.0-scenario-count-fix';
console.log('[LOAD-TESTS] Test Suite JS Version:', TEST_SUITE_VERSION);
const storedVersion = localStorage.getItem('test_suite_version');
// Only reload if version exists AND is different (not on first load or after clear)
if (storedVersion && storedVersion !== TEST_SUITE_VERSION) {
    console.log('[LOAD-TESTS] ⚠️ Version changed from', storedVersion, 'to', TEST_SUITE_VERSION, '- reloading...');
    localStorage.setItem('test_suite_version', TEST_SUITE_VERSION);
    window.location.reload(true); // Force reload without cache
} else if (!storedVersion) {
    // First time or after auth clear - just set the version, don't reload
    console.log('[LOAD-TESTS] Setting initial version:', TEST_SUITE_VERSION);
    localStorage.setItem('test_suite_version', TEST_SUITE_VERSION);
}

async function loadTestCases() {
    try {
        console.log('[LOAD-TESTS] ===== Starting loadTestCases =====');
        
        // Clear any lingering selection state before reload
        const selectAllCheckbox = document.getElementById('selectAllTests');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
        const deleteBtn = document.getElementById('deleteSelectedTestsBtn');
        if (deleteBtn) {
            deleteBtn.style.display = 'none';
        }
        
        console.log('[LOAD-TESTS] Fetching from API...');
        console.log('[LOAD-TESTS] API_URL:', typeof API_URL !== 'undefined' ? API_URL : 'UNDEFINED!');
        
        // Check if API_URL is defined
        if (typeof API_URL === 'undefined') {
            const errorMsg = '❌ API_URL is not defined! Server configuration error.';
            console.error('[LOAD-TESTS]', errorMsg);
            showNotification(errorMsg, 'error');
            return;
        }
        
        // Load saved recorder tests AND saved test builder cases
        // Active sessions stay in their respective pages (Recorder/Builder)
        const [savedRecorderTestsResponse, testCasesResponse] = await Promise.all([
            fetch(`${API_URL}/recorder/saved-tests`),  // Only saved recorder tests
            fetch(`${API_URL}/test-suite/test-cases`)   // Only saved builder tests
        ]);
        
        console.log('[LOAD-TESTS] Recorder response status:', savedRecorderTestsResponse.status);
        console.log('[LOAD-TESTS] Builder response status:', testCasesResponse.status);
        
        const savedRecorderTests = await savedRecorderTestsResponse.json();
        const testCasesData = await testCasesResponse.json();
        
        console.log('[LOAD-TESTS] Recorder tests:', savedRecorderTests.success ? savedRecorderTests.test_cases?.length : 'FAILED');
        console.log('[LOAD-TESTS] Builder tests:', testCasesData.success ? testCasesData.test_cases?.length : 'FAILED');
        
        let allSessions = [];
        
        // Add saved recorder test cases (from disk)
        if (savedRecorderTests.success) {
            const savedTests = (savedRecorderTests.test_cases || []).map(tc => {
                // CRITICAL FIX: Normalize timestamp to milliseconds (same as builder tests)
                // Check saved_at and saved_to_suite_at for semantic tests before falling back to Date.now()
                const timestamp = tc.timestamp || tc.created_at || tc.saved_at || tc.saved_to_suite_at || Date.now();
                const timestampMs = String(timestamp).length <= 10 ? timestamp * 1000 : timestamp;
                
                return {
                    ...tc,
                    id: tc.test_case_id,  // Map test_case_id to id for consistency
                    session_id: tc.test_case_id,
                    source: 'recorder',
                    timestamp: timestampMs,        // Normalized timestamp
                    created_at: timestampMs,       // Normalized timestamp
                    actions: tc.actions || [],  // Include actions array from API response
                    tags: tc.tags || [],  // Preserve tags for semantic filtering
                    steps: tc.steps || [],  // Include AI suggestions for semantic tests
                    generated_code: tc.generated_code,  // Include for code parsing fallback
                    generated_by: tc.generated_by,
                    variant_type: tc.variant_type,
                    parent_test_case_id: tc.parent_test_case_id
                };
            });
            allSessions = savedTests;
            console.log('[LOAD-TESTS] Found', savedTests.length, 'saved recorder tests');
        }
        
        // Add saved test cases (from Test Builder)
        // Active sessions remain in Test Builder until user clicks Save
        if (testCasesData.success) {
            const testCases = testCasesData.test_cases || [];
            console.log('[LOAD-TESTS] Processing', testCases.length, 'builder test cases');
            
            // Convert test cases to session format for display
            const convertedTestCases = testCases.map(tc => {
                try {
                    // Handle timestamp - could be seconds or milliseconds or a date string
                    // Check saved_at and saved_to_suite_at for semantic tests before falling back to Date.now()
                    let timestampMs;
                    const timestamp = tc.timestamp || tc.created_at || tc.saved_at || tc.saved_to_suite_at || Date.now();
                    
                    if (typeof timestamp === 'string') {
                        // Parse date string
                        timestampMs = new Date(timestamp).getTime();
                    } else {
                        // If timestamp is in seconds (10 digits or less), convert to milliseconds
                        timestampMs = String(timestamp).length <= 10 ? timestamp * 1000 : timestamp;
                    }
                    
                    // Check if this is a semantic test (has suggestions in steps array)
                    const isSemantic = tc.tags && Array.isArray(tc.tags) && (tc.tags.includes('semantic') || tc.tags.includes('ai-generated'));
                    
                    // For semantic tests: count suggestion scenarios separately
                    // For regular tests: count actual prompts/actions
                    let actionCount = 0;
                    let scenarioCount = 0; // NEW: Track semantic scenarios separately
                    
                    if (isSemantic && tc.steps && Array.isArray(tc.steps)) {
                        // Semantic test - count scenarios but show as 1 executable test
                        scenarioCount = tc.steps.length; // Number of AI scenarios
                        actionCount = 1; // Executed as 1 complete test
                    } else if (tc.prompts && Array.isArray(tc.prompts)) {
                        // Count only prompts with actual content (not empty suggestions)
                        const executablePrompts = tc.prompts.filter(p => p && p.prompt && p.prompt.trim());
                        actionCount = executablePrompts.length || tc.prompts.length;
                    } else {
                        actionCount = tc.prompt_count || tc.actions?.length || 0;
                    }
                    
                    const converted = {
                        id: tc.test_case_id,
                        session_id: tc.test_case_id,
                        name: tc.name || tc.test_case_id,
                        module: tc.module || (tc.tags && Array.isArray(tc.tags) ? tc.tags.filter(t => !['semantic', 'ai-generated'].includes(t)).join(', ') : 'Test Builder'),
                        url: tc.url || tc.starting_url || 'N/A',
                        action_count: actionCount,
                        scenario_count: scenarioCount, // NEW: Add scenario count
                        timestamp: timestampMs,
                        created_at: timestampMs,
                        prompt_count: actionCount,
                        source: 'test-builder',
                        priority: tc.priority || 'medium',
                        test_case_id: tc.test_case_id,
                        // IMPORTANT: Preserve semantic metadata for filtering
                        tags: tc.tags || [],
                        generated_by: tc.generated_by,
                        variant_type: tc.variant_type,
                        parent_test_case_id: tc.parent_test_case_id,
                        // CRITICAL: Store prompts, steps, and actions for data override modal
                        prompts: tc.prompts || [],
                        steps: tc.steps || [],
                        actions: tc.actions || [],
                        generated_code: tc.generated_code  // Store for semantic tests
                    };
                    
                    return converted;
                } catch (err) {
                    console.error('[LOAD-TESTS] ❌ Error processing test case:', tc.test_case_id, 'Error:', err.message);
                    console.error('[LOAD-TESTS] Test case data:', tc);
                    return null;
                }
            }).filter(tc => tc !== null);  // Remove any failed conversions
            
            console.log('[LOAD-TESTS] Successfully converted', convertedTestCases.length, 'builder tests');
            allSessions = [...allSessions, ...convertedTestCases];
        }
        
        // Sort by timestamp - LATEST FIRST
        allSessions.sort((a, b) => {
            const timeA = a.created_at || a.timestamp || 0;
            const timeB = b.created_at || b.timestamp || 0;
            return timeB - timeA; // Descending order (newest first)
        });
        
        console.log('[LOAD-TESTS] ===== SORTING DEBUG =====');
        console.log('[LOAD-TESTS] First 3 tests after sort:');
        allSessions.slice(0, 3).forEach(test => {
            console.log(`  ${test.source}: ${test.name} - Timestamp: ${test.created_at || test.timestamp} (${new Date(test.created_at || test.timestamp).toLocaleString()})`);
        });
        console.log('[LOAD-TESTS] Last 3 tests after sort:');
        allSessions.slice(-3).forEach(test => {
            console.log(`  ${test.source}: ${test.name} - Timestamp: ${test.created_at || test.timestamp} (${new Date(test.created_at || test.timestamp).toLocaleString()})`);
        });
        console.log('[LOAD-TESTS] ===========================');
        
        console.log('[LOAD-TESTS] Total tests loaded:', allSessions.length);
        console.log('[LOAD-TESTS] ===== loadTestCases completed successfully =====');
        
        window.allTestSessions = allSessions;
        populateModuleFilter(allSessions);
        populateModulesList(allSessions);
        displayTestCases(allSessions);
        updateDashboardFromTestSuite(allSessions);
        
        // Show success notification
        showNotification(`✅ Loaded ${allSessions.length} test cases`, 'success');
        
    } catch (error) {
        console.error('[LOAD-TESTS] ===== ERROR =====');
        console.error('[LOAD-TESTS] Error loading test cases:', error);
        console.error('[LOAD-TESTS] Error stack:', error.stack);
        
        // Show user-friendly error message
        const errorMsg = `❌ Failed to refresh test cases: ${error.message}`;
        showNotification(errorMsg, 'error');
        
        // Also show in alert for visibility
        alert(`Unable to load test cases.\n\nError: ${error.message}\n\nCheck browser console (F12) for details.`);
    }
}

function populateModuleFilter(sessions) {
    const moduleFilter = document.getElementById('moduleFilter');
    
    if (!moduleFilter) {
        return;
    }
    
    const modules = new Set();
    
    sessions.forEach(session => {
        if (session.module) {
            modules.add(session.module);
        }
    });
    
    moduleFilter.innerHTML = '<option value="">All Modules</option>';
    
    Array.from(modules).sort().forEach(module => {
        const option = document.createElement('option');
        option.value = module;
        option.textContent = module;
        moduleFilter.appendChild(option);
    });
}

function populateModulesList(sessions) {
    const modulesList = document.getElementById('moduleFilter');
    
    if (!modulesList) {
        return;
    }
    
    const modules = new Set();
    
    sessions.forEach(session => {
        if (session.module) {
            modules.add(session.module);
        }
    });
    
    // Clear existing options (keep the "All Modules" option)
    while (modulesList.options.length > 1) {
        modulesList.remove(1);
    }
    
    Array.from(modules).sort().forEach(module => {
        const option = document.createElement('option');
        option.value = module;
        option.textContent = module;
        modulesList.appendChild(option);
    });
}

function filterTestsBySource() {
    applyFilters();
}

function filterTestsByModule() {
    applyFilters();
}

function applyFilters() {
    const selectedSource = document.getElementById('testSourceFilter')?.value || 'all';
    const selectedModule = document.getElementById('moduleFilter')?.value || '';
    
    console.log('[Filter] Source:', selectedSource, 'Module:', selectedModule);
    
    if (!window.allTestSessions) {
        console.log('[Filter] No test sessions available');
        return;
    }
    
    console.log('[Filter] Total sessions:', window.allTestSessions.length);
    
    let filteredSessions = window.allTestSessions;
    
    // Apply source filter
    if (selectedSource !== 'all') {
        filteredSessions = filteredSessions.filter(session => {
            if (selectedSource === 'recorder') {
                const isRecorder = !session.source || session.source === 'recorder';
                console.log('[Filter] Session:', session.id, 'Source:', session.source, 'Is Recorder:', isRecorder);
                return isRecorder;
            } else if (selectedSource === 'builder') {
                const isBuilder = session.source === 'test-builder';
                console.log('[Filter] Session:', session.id, 'Source:', session.source, 'Is Builder:', isBuilder);
                return isBuilder;
            } else if (selectedSource === 'semantic') {
                // Filter for semantic/AI-generated tests
                const tags = session.tags || [];
                const isSemantic = tags.includes('semantic') || tags.includes('ai-generated') || session.generated_by === 'semantic-analysis';
                console.log('[Filter] Session:', session.id, 'Tags:', tags, 'Is Semantic:', isSemantic);
                return isSemantic;
            }
            return true;
        });
        console.log('[Filter] After source filter:', filteredSessions.length);
    }
    
    // Apply module filter
    if (selectedModule) {
        filteredSessions = filteredSessions.filter(session => 
            session.module === selectedModule
        );
        console.log('[Filter] After module filter:', filteredSessions.length);
    }
    
    console.log('[Filter] Displaying', filteredSessions.length, 'sessions');
    displayTestCases(filteredSessions);
}

function displayTestCases(sessions) {
    const listDiv = document.getElementById('testCasesList');
    
    if (!listDiv) {
        return;
    }
    
    if (sessions.length === 0) {
        listDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">No test cases yet. Use the Recorder tab to create your first test!</div>';
        return;
    }
    
    let html = '';
    sessions.forEach(session => {
        // Handle timestamp - check ALL timestamp fields including semantic test fields
        // Priority: timestamp > created_at > saved_at > saved_to_suite_at > Date.now()
        let timestamp = session.timestamp || session.created_at || session.saved_at || session.saved_to_suite_at || Date.now();
        // If timestamp is in seconds (10 digits or less), convert to milliseconds
        if (String(timestamp).length <= 10) {
            timestamp = timestamp * 1000;
        }
        const date = new Date(timestamp).toLocaleString();
        
        // Create compact inline tags
        const moduleTags = session.module ? session.module.split(',').map(m => 
            `<span style="background: rgba(124, 58, 237, 0.08); color: #7C3AED; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: 500;">${m.trim()}</span>`
        ).join(' ') : '';
        
        const sourceTag = session.source === 'test-builder' 
            ? '<span style="background: rgba(34, 197, 94, 0.08); color: #22c55e; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: 500;">Test Builder</span>' 
            : '<span style="background: rgba(239, 68, 68, 0.08); color: #ef4444; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: 500;">Recorder</span>';
        
        // Check if test is semantic-generated
        const tags = session.tags || [];
        const isSemantic = tags.includes('semantic') || tags.includes('ai-generated') || session.generated_by === 'semantic-analysis';
        const semanticBadge = isSemantic 
            ? '<span style="background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: 600;">✨ AI-Generated</span>'
            : '';
        
        // Get variant type badge if available
        const variantBadge = session.variant_type && isSemantic
            ? `<span style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: 500;">${session.variant_type}</span>`
            : '';
        
        html += `
            <div class="test-case-card" data-test-id="${session.id}" style="padding: 18px 20px; margin-bottom: 12px; background: var(--stat-bg); border: 2px solid var(--border-color); border-radius: 12px; transition: all 0.2s ease; overflow: visible; position: relative;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <input type="checkbox" class="test-checkbox" data-test-id="${session.id}" data-source="${session.source || 'recorder'}" onchange="updateDeleteTestsButton()" style="cursor: pointer; width: 18px; height: 18px; margin: 0;">
                    <div style="flex: 1; min-width: 0; overflow: visible;">
                        <!-- Title Row with Action Buttons -->
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; gap: 16px; overflow: visible;">
                            <h4 style="margin: 0; font-size: 16px; font-weight: 600; flex: 1; color: #6366f1;">${session.name}</h4>
                            
                            <!-- Action Buttons on Right -->
                            <div style="display: flex; gap: 8px; align-items: center; flex-shrink: 0; overflow: visible;">
                                <button class="btn-icon" onclick="viewTestCase('${session.id}')" style="padding: 8px 12px; font-size: 16px; background: transparent; border: 1px solid var(--border-color); border-radius: 6px; cursor: pointer; min-width: 40px; height: 36px; display: flex; align-items: center; justify-content: center;" title="View test code">
                                    👁️
                                </button>
                                <button class="btn-icon" onclick="showDataOverrideModal('${session.id}', '${session.source || 'recorder'}')" style="padding: 8px 12px; font-size: 16px; background: #7C3AED; color: white; border: none; border-radius: 6px; cursor: pointer; min-width: 40px; height: 36px; display: flex; align-items: center; justify-content: center;" title="Execute test">
                                    ▶️
                                </button>
                                <div class="dropdown" style="position: relative; overflow: visible;">
                                    <button class="btn-icon" onclick="toggleTestMenu('${session.id}')" style="padding: 8px 12px; font-size: 18px; background: transparent; border: 1px solid var(--border-color); border-radius: 6px; cursor: pointer; min-width: 40px; height: 36px; display: flex; align-items: center; justify-content: center;" title="More actions">
                                        ⋮
                                    </button>
                                    <div id="menu-${session.id}" class="dropdown-menu" style="display: none; position: absolute; right: 0; top: calc(100% + 4px); background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 6px; box-shadow: 0 8px 24px rgba(0,0,0,0.35); min-width: 170px; z-index: 99999; padding: 6px 0; white-space: nowrap;">
                                        <div onclick="editTestName('${session.id}', '${session.name.replace(/'/g, "\\'").replace(/"/g, '&quot;')}', '${session.source || 'recorder'}'); toggleTestMenu('${session.id}')" style="width: 100%; padding: 12px 16px; cursor: pointer; font-size: 14px; color: var(--text-primary); display: flex; align-items: center; gap: 8px; transition: background 0.15s;" onmouseover="this.style.background='var(--bg-tertiary)'" onmouseout="this.style.background='transparent'">
                                            ✏️ Edit Name
                                        </div>
                                        <div onclick="deleteSingleTest('${session.id}', '${session.source || 'recorder'}'); toggleTestMenu('${session.id}')" style="width: 100%; padding: 12px 16px; cursor: pointer; font-size: 14px; color: #ef4444; display: flex; align-items: center; gap: 8px; transition: background 0.15s;" onmouseover="this.style.background='rgba(239, 68, 68, 0.1)'" onmouseout="this.style.background='transparent'">
                                            🗑️ Delete Test
                                        </div>
                                        <div onclick="exportSingleTest('${session.id}'); toggleTestMenu('${session.id}')" style="width: 100%; padding: 12px 16px; cursor: pointer; font-size: 14px; color: var(--text-primary); display: flex; align-items: center; gap: 8px; transition: background 0.15s;" onmouseover="this.style.background='var(--bg-tertiary)'" onmouseout="this.style.background='transparent'">
                                            💾 Export
                                        </div>
                                        <div onclick="duplicateTest('${session.id}'); toggleTestMenu('${session.id}')" style="width: 100%; padding: 12px 16px; cursor: pointer; font-size: 14px; color: var(--text-primary); display: flex; align-items: center; gap: 8px; transition: background 0.15s;" onmouseover="this.style.background='var(--bg-tertiary)'" onmouseout="this.style.background='transparent'">
                                            📋 Duplicate
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Metadata Row with inline tags -->
                        <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.8; display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                            <span>${sourceTag}</span>
                            ${semanticBadge ? `<span>${semanticBadge}</span>` : ''}
                            ${variantBadge ? `<span>${variantBadge}</span>` : ''}
                            ${moduleTags ? `<span>${moduleTags}</span>` : ''}
                            <span style="color: var(--text-secondary);">•</span>
                            <span>📅 ${date}</span>
                            ${session.url && session.url !== 'N/A' ? `<span style="color: var(--text-secondary);">•</span><span>🌐 ${session.url}</span>` : ''}
                            <span style="color: var(--text-secondary);">•</span>
                            ${session.scenario_count > 0 
                                ? `<span>🎯 Scenarios: ${session.scenario_count}</span>`
                                : `<span>📊 ${session.source === 'test-builder' ? 'Steps' : 'Actions'}: ${session.action_count || 0}</span>`
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    listDiv.innerHTML = html;
}

async function viewTestCase(sessionId) {
    try {
        // Find the test in allTestSessions to determine its source
        const session = window.allTestSessions?.find(s => s.id === sessionId || s.session_id === sessionId);
        const source = session?.source || 'recorder';
        
        console.log('[VIEW CODE] Session ID:', sessionId, 'Source:', source);
        console.log('[VIEW CODE] Session data:', session);
        
        let response, data;
        
        if (source === 'test-builder') {
            // Check if this is already a saved test case (has test_case_id in memory)
            if (session && session.test_case_id) {
                console.log('[VIEW CODE] Loading saved test case:', session.test_case_id);
                
                try {
                    const testCaseResponse = await fetch(`${API_URL}/test-suite/test-cases/${session.test_case_id}`);
                    const testCaseData = await testCaseResponse.json();
                    
                    if (testCaseData.success && testCaseData.test_case) {
                        const testCase = testCaseData.test_case;
                        const pythonCode = testCase.generated_code?.python || '# No Python code generated';
                        
                        console.log('[VIEW CODE] Displaying saved test case code');
                        displayTestSuiteCode(pythonCode, sessionId, source);
                        return;
                    }
                } catch (error) {
                    console.error('[VIEW CODE] Error fetching test case:', error);
                    // Fall through to session view
                }
            }
            
            // Try fetching as active session (for unsaved tests)
            try {
                response = await fetch(`${API_URL}/test-suite/session/${sessionId}`);
                
                if (response.ok) {
                    data = await response.json();
                    
                    if (data.success && data.session) {
                        console.log('[VIEW CODE] Session data:', data.session);
                        
                        // Show steps view for the session
                        if (data.session.prompts) {
                            console.log('[VIEW CODE] Showing step-by-step code for session');
                            displayTestBuilderSteps(data.session, sessionId);
                            return;
                        }
                    }
                }
            } catch (error) {
                console.error('[VIEW CODE] Error fetching session:', error);
            }
            
            // If all else fails, show error
            console.error('[VIEW CODE] Could not load test data');
            showNotification('❌ Could not load test code. Session may not exist.', 'error');
            return;
        }
        
        // For Recorder tests, load saved test case and use pre-generated code
        try {
            console.log('[VIEW CODE] Loading saved recorder test:', sessionId);
            const testResponse = await fetch(`${API_URL}/recorder/test/${sessionId}`);
            
            if (testResponse.ok) {
                const testData = await testResponse.json();
                
                if (testData.success && testData.session_data) {
                    // Check if we have pre-generated code (saved during test save)
                    const savedCode = testData.session_data.generated_code?.python;
                    
                    if (savedCode) {
                        console.log('[VIEW CODE] Using pre-generated code from saved test');
                        displayTestSuiteCode(savedCode, sessionId, source);
                    } else {
                        // Fallback: generate code if not saved (old tests)
                        console.log('[VIEW CODE] No saved code, generating...');
                        response = await fetch(`${API_URL}/recorder/generate-test`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                session_id: sessionId,
                                session_data: testData.session_data,
                                test_name: testData.session_data.name || 'GeneratedTest',
                                compact_mode: true
                            })
                        });
                        
                        data = await response.json();
                        
                        if (data.success) {
                            displayTestSuiteCode(data.code, sessionId, source);
                        } else {
                            console.error('[VIEW CODE] Code generation failed:', data.error);
                            showNotification('❌ Failed to generate code: ' + data.error, 'error');
                        }
                    }
                } else {
                    console.error('[VIEW CODE] Test data not found');
                    alert('⚠️ Test case data not found');
                }
            } else {
                console.error('[VIEW CODE] Failed to load test:', testResponse.status);
                alert('⚠️ Failed to load test case');
            }
        } catch (error) {
            console.error('[VIEW CODE] Error:', error);
            alert('⚠️ Error loading test: ' + error.message);
        }
    } catch (error) {
        console.error('Error loading test case:', error);
        alert('Error loading test case: ' + error.message);
    }
}

function displayTestBuilderSteps(session, sessionId) {
    // Create a detailed view showing each step with its prompt and generated code
    const prompts = session.prompts || [];
    
    let stepsView = `/* Test: ${session.name || sessionId} */\n`;
    stepsView += `/* Description: ${session.description || 'No description'} */\n`;
    stepsView += `/* Steps: ${prompts.length} */\n`;
    stepsView += `/* Created: ${new Date(session.created_at).toLocaleString()} */\n\n`;
    
    prompts.forEach((step, index) => {
        stepsView += `// ==================== Step ${step.step}: ${step.prompt} ====================\n`;
        if (step.url) {
            stepsView += `// URL: ${step.url}\n`;
        }
        stepsView += `${step.generated_code || '// No code generated'}\n\n`;
    });
    
    displayTestSuiteCode(stepsView, sessionId, 'test-builder');
}

function displayTestSuiteCode(code, sessionId, source = 'recorder') {
    // Create and show full-screen modal
    openCodeModal(code, sessionId, source);
}

function openCodeModal(code, sessionId, source = 'recorder') {
    // Remove existing modal if any
    const existingModal = document.getElementById('testCodeModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    window.currentTestSuiteSessionId = sessionId;
    window.currentTestSuiteCode = code;
    window.currentTestSuiteSource = source;
    
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    // Create full-screen modal
    const modal = document.createElement('div');
    modal.id = 'testCodeModal';
    modal.className = 'modal-overlay';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.85);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(5px);
    `;
    
    modal.innerHTML = `
        <div style="width: 90%; max-width: 1200px; height: 90vh; background: var(--bg-secondary); border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow: hidden;">
            <!-- Modal Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 2px solid var(--border-color);">
                <h3 style="margin: 0; color: var(--text-primary); font-size: 18px; font-weight: 600;">
                    📄 Generated Test Code
                </h3>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <button onclick="executeViewedTestModal()" style="padding: 8px 16px; background: #7C3AED; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                        ▶ Run
                    </button>
                    <button onclick="editCodeModal()" style="padding: 8px 16px; background: #f59e0b; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                        ✏️ Edit
                    </button>
                    <button onclick="copyCodeModal()" style="padding: 8px 16px; background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                        Copy
                    </button>
                    <button onclick="exportCodeModal()" style="padding: 8px 16px; background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                        Export
                    </button>
                    <button onclick="saveCodeModal()" style="padding: 8px 16px; background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                        💾 Save
                    </button>
                    <button onclick="closeCodeModal()" style="padding: 8px 16px; background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 18px; font-weight: 600; line-height: 1;">
                        ✕
                    </button>
                </div>
            </div>
            
            <!-- Modal Body: Code Viewer -->
            <div class="code-modal-body" style="flex: 1; overflow: auto; padding: 0;">
                <pre style="margin: 0; padding: 24px; height: 100%;"><code id="modalCodeContent" class="language-${language}" style="font-size: 14px; line-height: 1.6; display: block; white-space: pre;">${escapeHtml(code)}</code></pre>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Apply syntax highlighting if available
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(document.getElementById('modalCodeContent'));
    }
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeCodeModal();
        }
    });
}

function closeCodeModal() {
    const modal = document.getElementById('testCodeModal');
    if (modal) {
        modal.remove();
    }
}

function executeViewedTestModal() {
    if (window.currentTestSuiteSessionId) {
        showDataOverrideModal(window.currentTestSuiteSessionId, window.currentTestSuiteSource || 'recorder');
    }
}

function copyCodeModal() {
    if (window.currentTestSuiteCode) {
        navigator.clipboard.writeText(window.currentTestSuiteCode);
        showNotification('Code copied to clipboard!', 'success');
    }
}

function exportCodeModal() {
    if (window.currentTestSuiteCode) {
        const blob = new Blob([window.currentTestSuiteCode], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `test_${window.currentTestSuiteSessionId || 'code'}.java`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showNotification('Code exported!', 'success');
    }
}

function saveCodeModal() {
    const code = window.currentTestSuiteCode;
    
    if (!code) {
        showNotification('No code to save. Please view a test case first.', 'error');
        return;
    }
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    // Prompt for snippet details
    const title = prompt('Enter a title for this snippet:', 'Test Suite Code');
    if (!title) return;
    
    const description = prompt('Enter a description (optional):', 'Generated test suite code');
    const tags = prompt('Enter tags (comma-separated, optional):', 'test-suite, automated');
    
    const snippet = {
        id: Date.now(),
        title: title,
        language: language,
        tags: tags ? tags.split(',').map(t => t.trim()) : [],
        description: description || '',
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    // Load existing snippets from localStorage
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    
    // Save to localStorage
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    showNotification('Snippet saved to Code Snippet Library!', 'success');
    
    // Reload snippets if on that page
    if (typeof loadSnippets === 'function') {
        loadSnippets();
    }
}

function editCodeModal() {
    const codeBodyDiv = document.querySelector('.code-modal-body');
    const currentCode = window.currentTestSuiteCode;
    
    if (!codeBodyDiv || !currentCode) {
        showNotification('Cannot enter edit mode', 'error');
        return;
    }
    
    // Check if already in edit mode
    if (document.getElementById('codeEditTextarea')) {
        showNotification('Already in edit mode', 'info');
        return;
    }
    
    // Save original state for cancel
    window.originalTestSuiteCode = currentCode;
    
    // Replace code viewer with editable textarea
    codeBodyDiv.innerHTML = `
        <div style="padding: 16px; height: 100%; display: flex; flex-direction: column;">
            <div style="margin-bottom: 12px; padding: 12px; background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; border-radius: 6px;">
                <div style="font-size: 14px; color: var(--text-primary); line-height: 1.5;">
                    ✏️ <strong>Edit Mode:</strong> Make your changes below. Click <strong>Save Changes</strong> to update or <strong>Cancel</strong> to discard.
                </div>
            </div>
            <textarea 
                id="codeEditTextarea" 
                style="flex: 1; width: 100%; padding: 16px; background: var(--bg-primary); color: var(--text-primary); border: 2px solid var(--border-color); border-radius: 8px; font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 14px; line-height: 1.6; resize: none; outline: none;"
                spellcheck="false"
            >${escapeHtml(currentCode)}</textarea>
            <div style="display: flex; gap: 12px; margin-top: 16px; justify-content: flex-end;">
                <button onclick="cancelEditCodeModal()" style="padding: 10px 20px; background: transparent; border: 2px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s;">
                    ❌ Cancel
                </button>
                <button onclick="saveEditedCodeModal()" style="padding: 10px 20px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s;">
                    ✅ Save Changes
                </button>
            </div>
        </div>
    `;
    
    // Focus on textarea
    setTimeout(() => {
        const textarea = document.getElementById('codeEditTextarea');
        if (textarea) {
            textarea.focus();
            // Place cursor at the end
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        }
    }, 100);
}

function saveEditedCodeModal() {
    const textarea = document.getElementById('codeEditTextarea');
    if (!textarea) {
        showNotification('No edits to save', 'error');
        return;
    }
    
    const editedCode = textarea.value;
    
    // Update the current code
    window.currentTestSuiteCode = editedCode;
    
    // Exit edit mode and show updated code
    const sessionId = window.currentTestSuiteSessionId;
    const source = window.currentTestSuiteSource;
    
    // Re-render modal with updated code
    closeCodeModal();
    openCodeModal(editedCode, sessionId, source);
    
    showNotification('Code updated successfully! Changes are in memory only.', 'success');
}

function cancelEditCodeModal() {
    // Restore original code
    if (window.originalTestSuiteCode) {
        window.currentTestSuiteCode = window.originalTestSuiteCode;
    }
    
    // Exit edit mode and show original code
    const sessionId = window.currentTestSuiteSessionId;
    const source = window.currentTestSuiteSource;
    const code = window.currentTestSuiteCode;
    
    closeCodeModal();
    openCodeModal(code, sessionId, source);
    
    showNotification('Edit cancelled', 'info');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Keep old function for backward compatibility
function displayTestSuiteCodeOld(code, sessionId, source = 'recorder') {
    const codeElement = document.getElementById('testSuiteCodeContent');
    if (!codeElement) return;
    
    codeElement.textContent = code;
    
    window.currentTestSuiteSessionId = sessionId;
    window.currentTestSuiteCode = code;
    window.currentTestSuiteSource = source;
    
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    codeElement.className = `language-${language}`;
    
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(codeElement);
    }
    
    // Show all action buttons including Execute
    document.getElementById('executeViewedTestBtn').style.display = 'block';
    document.getElementById('copyTestSuiteBtn').style.display = 'block';
    document.getElementById('exportTestSuiteBtn').style.display = 'block';
    document.getElementById('saveTestSuiteSnippetBtn').style.display = 'block';
}

function copyTestSuiteCode() {
    const code = document.getElementById('testSuiteCodeContent').textContent;
    navigator.clipboard.writeText(code).then(() => {
        showNotification('✅ Code copied to clipboard!');
    });
}

function exportTestSuiteCode() {
    const code = document.getElementById('testSuiteCodeContent').textContent;
    
    let extension = '.java';
    if (code.includes('from selenium') || code.includes('import pytest')) {
        extension = '.py';
    } else if (code.includes('const ') || code.includes('let ')) {
        extension = '.js';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        extension = '.cs';
    }
    
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `TestSuite_${Date.now()}${extension}`;
    a.click();
    
    showNotification('✅ Code exported successfully!');
}

function saveTestSuiteSnippet() {
    const code = document.getElementById('testSuiteCodeContent').textContent;
    
    if (!code || code === 'Select a test case from the list to view its code here...') {
        alert('No code to save. Please select a test case first.');
        return;
    }
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    const title = prompt('Enter a title for this snippet:', 'Test Suite Code');
    if (!title) return;
    
    const description = prompt('Enter a description (optional):', 'Generated test suite code');
    const tags = prompt('Enter tags (comma-separated, optional):', 'test-suite, automated');
    
    const snippet = {
        id: Date.now(),
        title: title,
        language: language,
        tags: tags ? tags.split(',').map(t => t.trim()) : [],
        description: description || '',
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    // Load existing snippets from localStorage
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    
    // Save to localStorage
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    showNotification('✅ Snippet saved to Code Snippet Library!');
    
    // Reload snippets if on that page
    if (typeof loadSnippets === 'function') {
        loadSnippets();
    }
}

function toggleSelectAllTests() {
    const selectAll = document.getElementById('selectAllTests');
    const checkboxes = document.querySelectorAll('.test-checkbox');
    
    checkboxes.forEach(cb => {
        cb.checked = selectAll.checked;
    });
    
    updateDeleteTestsButton();
}

function updateDeleteTestsButton() {
    const checkboxes = document.querySelectorAll('.test-checkbox');
    const checkedBoxes = Array.from(checkboxes).filter(cb => cb.checked);
    const deleteBtn = document.getElementById('deleteSelectedTestsBtn');
    const selectAll = document.getElementById('selectAllTests');
    
    // Guard: Exit if elements don't exist (not on test suite tab)
    if (!deleteBtn || !selectAll) {
        return;
    }
    
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

async function deleteSelectedTests() {
    const checkboxes = document.querySelectorAll('.test-checkbox:checked');
    const selectedTests = Array.from(checkboxes).map(cb => ({
        id: cb.dataset.testId,
        source: cb.dataset.source || 'recorder'
    }));
    
    if (selectedTests.length === 0) {
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${selectedTests.length} test case(s)?`)) {
        return;
    }
    
    let deletedCount = 0;
    let failedCount = 0;
    
    for (const test of selectedTests) {
        try {
            let response;
            
            if (test.source === 'test-builder') {
                // Delete Test Builder test case
                response = await fetch(`${API_URL}/test-suite/test-cases/${test.id}`, {
                    method: 'DELETE'
                });
            } else {
                // Delete Recorder session
                response = await fetch(`${API_URL}/recorder/delete-session`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: test.id })
                });
            }
            
            const data = await response.json();
            
            if (data.success) {
                deletedCount++;
            } else {
                failedCount++;
                console.error(`Failed to delete ${test.source} test ${test.id}:`, data.error);
            }
        } catch (error) {
            failedCount++;
            console.error('Delete error:', error);
        }
    }
    
    // Clear current test view if element exists
    const codeElement = document.getElementById('testSuiteCodeContent');
    if (codeElement) {
        codeElement.textContent = 'Select a test case from the list to view its code here...';
        codeElement.className = 'language-java';
    }
    
    // Hide buttons if they exist
    const copyBtn = document.getElementById('copyTestSuiteBtn');
    const exportBtn = document.getElementById('exportTestSuiteBtn');
    const saveBtn = document.getElementById('saveTestSuiteSnippetBtn');
    if (copyBtn) copyBtn.style.display = 'none';
    if (exportBtn) exportBtn.style.display = 'none';
    if (saveBtn) saveBtn.style.display = 'none';
    
    // Reload test cases first to rebuild the checkbox list
    await loadTestCases();
    
    // Reset selection state AFTER reload completes
    const selectAllCheckbox = document.getElementById('selectAllTests');
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    }
    
    const deleteBtn = document.getElementById('deleteSelectedTestsBtn');
    if (deleteBtn) {
        deleteBtn.style.display = 'none';
    }
    
    // Force update button state with new checkboxes
    updateDeleteTestsButton();
    
    if (deletedCount > 0) {
        showNotification(`🗑️ ${deletedCount} test case(s) deleted successfully`);
    }
    if (failedCount > 0) {
        alert(`⚠️ Failed to delete ${failedCount} test case(s)`);
    }
}

async function deleteSingleTest(sessionId, source = 'recorder') {
    if (!confirm('Are you sure you want to delete this test case?')) {
        return;
    }
    
    try {
        let response;
        
        if (source === 'test-builder') {
            // Delete Test Builder test case
            response = await fetch(`${API_URL}/test-suite/test-cases/${sessionId}`, {
                method: 'DELETE'
            });
        } else {
            // Delete Recorder session
            response = await fetch(`${API_URL}/recorder/delete-session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            if (window.currentTestSuiteSessionId === sessionId) {
                const codeElement = document.getElementById('testSuiteCodeContent');
                if (codeElement) {
                    codeElement.textContent = 'Select a test case from the list to view its code here...';
                    codeElement.className = 'language-java';
                }
                const copyBtn = document.getElementById('copyTestSuiteBtn');
                const exportBtn = document.getElementById('exportTestSuiteBtn');
                const saveBtn = document.getElementById('saveTestSuiteSnippetBtn');
                if (copyBtn) copyBtn.style.display = 'none';
                if (exportBtn) exportBtn.style.display = 'none';
                if (saveBtn) saveBtn.style.display = 'none';
            }
            
            showNotification('🗑️ Test case deleted successfully');
            
            // Reload test cases first
            await loadTestCases();
            
            // Reset selection state AFTER reload completes
            const selectAllCheckbox = document.getElementById('selectAllTests');
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            }
            
            // Force update button state
            updateDeleteTestsButton();
        } else {
            alert('❌ Failed to delete test case: ' + data.error);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('Error deleting test case: ' + error.message);
    }
}

function updateDashboardFromTestSuite(sessions) {
    const totalTests = sessions.length;
    
    console.log('[Test Suite] 📊 Updating dashboard with', totalTests, 'tests');
    
    // Update the global stats object directly
    if (typeof window.stats !== 'undefined') {
        console.log('[Test Suite] 📝 Before update - window.stats.totalRequests:', window.stats.totalRequests);
        
        // Update total requests on the SAME object reference
        window.stats.totalRequests = totalTests;
        
        console.log('[Test Suite] ✏️ After update - window.stats.totalRequests:', window.stats.totalRequests);
        console.log('[Test Suite] 📦 Full window.stats:', JSON.stringify(window.stats));
        
        // Save to localStorage
        if (typeof window.saveStats === 'function') {
            window.saveStats();
            
            // Verify the save
            const savedData = localStorage.getItem('dashboardStats');
            if (savedData) {
                const parsed = JSON.parse(savedData);
                console.log('[Test Suite] ✅ VERIFIED Save - totalRequests in localStorage:', parsed.totalRequests);
            }
        }
        
        // Update the dashboard UI if on dashboard page
        if (typeof window.updateDashboardStats === 'function') {
            window.updateDashboardStats();
        }
    } else {
        console.error('[Test Suite] ❌ window.stats is undefined!');
    }
    
    // Directly update dashboard element if it exists (backup for immediate update)
    const dashboardTotalEl = document.getElementById('dashboardTotalRequests');
    if (dashboardTotalEl) {
        dashboardTotalEl.textContent = totalTests;
        console.log('[Test Suite] 🖥️ Updated dashboardTotalRequests element to:', totalTests);
    }
}

function updateDashboardWithExecutionResults(suiteData) {
    // Update test results with execution status
    if (typeof window.stats !== 'undefined' && suiteData.results) {
        suiteData.results.forEach(result => {
            let testResult = window.stats.testResults.find(r => r.name === result.test_name);
            
            if (testResult) {
                testResult.status = result.passed ? 'passed' : 'failed';
                testResult.details = result.passed ? 
                    `Executed ${result.steps_executed}/${result.total_steps} steps successfully` :
                    `Failed at step ${result.steps_executed}/${result.total_steps}${result.error ? ': ' + result.error : ''}`;
                testResult.timestamp = new Date().toLocaleString();
            } else {
                window.stats.testResults.unshift({
                    name: result.test_name,
                    status: result.passed ? 'passed' : 'failed',
                    duration: 0,
                    details: result.passed ? 
                        `Executed ${result.steps_executed}/${result.total_steps} steps successfully` :
                        `Failed at step ${result.steps_executed}/${result.total_steps}${result.error ? ': ' + result.error : ''}`,
                    timestamp: new Date().toLocaleString()
                });
            }
        });
        
        if (window.stats.testResults.length > 10) {
            window.stats.testResults = window.stats.testResults.slice(0, 10);
        }
        
        // Save stats to localStorage
        if (typeof window.saveStats === 'function') {
            window.saveStats();
        }
        
        if (typeof window.updateDashboardStats === 'function') {
            window.updateDashboardStats();
        }
        if (typeof window.updateRecentTestResults === 'function') {
            window.updateRecentTestResults();
        }
        if (typeof window.updateActivityTimeline === 'function') {
            window.updateActivityTimeline();
        }
    }
}

async function executeTestSuite() {
    const resultsDiv = document.getElementById('executionResults');
    const resultsList = document.getElementById('executionResultsList');
    const currentlyExecutingDiv = document.getElementById('currentlyExecutingTest');
    const currentExecutingTestName = document.getElementById('currentExecutingTestName');
    const selectedModule = document.getElementById('moduleFilter').value;
    const selectedBrowser = document.getElementById('browserSelect').value; // Get browser selection
    const selectedHealingMode = document.getElementById('healingModeSelect')?.value || 'v1'; // Get healing mode (default v1)
    
    if (!resultsDiv || !resultsList) {
        showNotification('⚠️ Test execution UI not found');
        return;
    }
    
    resultsDiv.style.display = 'block';
    if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'block';
    
    // Show healing mode in execution message
    const healingLabel = selectedHealingMode === 'v2' ? ' with Advanced Healing ✨' : '';
    
    if (selectedModule) {
        resultsList.innerHTML = `<div style="color: #f59e0b;">⏳ Executing tests from module: ${selectedModule} on ${selectedBrowser.toUpperCase()}${healingLabel}...</div>`;
        if (currentExecutingTestName) currentExecutingTestName.textContent = `Module: ${selectedModule} (${selectedBrowser.toUpperCase()})`;
    } else {
        resultsList.innerHTML = `<div style="color: #f59e0b;">⏳ Executing all test cases on ${selectedBrowser.toUpperCase()}${healingLabel}...</div>`;
        if (currentExecutingTestName) currentExecutingTestName.textContent = `Test Suite (${selectedBrowser.toUpperCase()})`;
    }
    
    try {
        const response = await fetch(`${API_URL}/recorder/sessions`);
        const data = await response.json();
        
        if (!data.success || data.sessions.length === 0) {
            resultsList.innerHTML = '<div style="color: #ef4444;">❌ No test cases to execute</div>';
            if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
            return;
        }
        
        let sessionsToExecute = data.sessions;
        if (selectedModule) {
            sessionsToExecute = data.sessions.filter(s => s.module === selectedModule);
            
            if (sessionsToExecute.length === 0) {
                resultsList.innerHTML = `<div style="color: #ef4444;">❌ No test cases found in module: ${selectedModule}</div>`;
                if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
                return;
            }
        }
        
        const suiteResponse = await fetch(`${API_URL}/recorder/execute-suite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                module: selectedModule || null,
                browser: selectedBrowser,  // Send browser selection
                healing_mode: selectedHealingMode  // Send healing mode (v1 or v2)
            })
        });
        
        const suiteData = await suiteResponse.json();
        
        if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
        
        if (suiteData.success) {
            // Detect dark mode for summary colors
            const isDarkMode = document.body.classList.contains('dark-mode');
            const summaryBorderColor = suiteData.all_passed ? '#10b981' : '#ef4444';
            const summaryText = isDarkMode ? (suiteData.all_passed ? '#6ee7b7' : '#fca5a5') : (suiteData.all_passed ? '#065f46' : '#991b1b');
            const summaryMuted = isDarkMode ? '#f3f4f6' : (suiteData.all_passed ? '#047857' : '#7f1d1d');
            
            let html = `
                <div style="margin-bottom: 15px; padding: 10px; border-left: 4px solid ${summaryBorderColor}; border-radius: 6px;">
                    <div style="font-weight: bold; font-size: 1.1em; color: ${summaryText};">
                        ${suiteData.all_passed ? '✅ All Tests Passed' : '⚠️ Some Tests Failed'}
                    </div>
                    <div style="margin-top: 5px; color: ${summaryMuted};">
                        Passed: ${suiteData.passed_count} / ${suiteData.total_count} on ${selectedBrowser.toUpperCase()}
                    </div>
                </div>
            `;
            
            suiteData.results.forEach(result => {
                // Simple color scheme - no backgrounds, just borders and text
                const resultBorderColor = result.passed ? '#10b981' : '#ef4444';
                const resultTextColor = isDarkMode ? (result.passed ? '#6ee7b7' : '#fca5a5') : (result.passed ? '#065f46' : '#991b1b');
                const resultMutedColor = isDarkMode ? '#f3f4f6' : '#6b7280';
                
                // Build screenshot HTML if there are any
                let screenshotHtml = '';
                if (result.screenshots && result.screenshots.length > 0) {
                    screenshotHtml = `
                        <div style="margin-top: 8px; padding: 8px; border-left: 3px solid #f59e0b; border-radius: 4px;">
                            <div style="font-weight: bold; color: ${isDarkMode ? '#fbbf24' : '#92400e'}; margin-bottom: 5px;">📸 Error Screenshot${result.screenshots.length > 1 ? 's' : ''}:</div>
                            ${result.screenshots.map(s => {
                                const path = s.path || s.filepath || s.screenshot_path || '';
                                const step = s.step || s.step_number || 'Unknown';
                                const error = s.error || s.error_message || s.description || 'View Screenshot';
                                return `<a href="${path}" target="_blank" style="color: ${isDarkMode ? '#60a5fa' : '#3b82f6'}; text-decoration: underline; display: block; margin-top: 3px;">Step ${step}: ${error}</a>`;
                            }).join('')}
                        </div>`;
                }
                
                html += `
                    <div style="padding: 10px; margin-bottom: 10px; border-left: 4px solid ${resultBorderColor}; border-radius: 6px;">
                        <div style="font-weight: bold; color: ${resultTextColor};">
                            ${result.passed ? '✅' : '❌'} ${result.test_name}
                        </div>
                        <div style="font-size: 0.9em; color: ${resultMutedColor}; margin-top: 5px;">
                            Steps: ${result.steps_executed} / ${result.total_steps}
                        </div>
                        ${result.error ? `<div style="font-size: 0.9em; color: ${isDarkMode ? '#fca5a5' : '#991b1b'}; margin-top: 5px;">Error: ${result.error}</div>` : ''}
                        ${screenshotHtml}
                    </div>
                `;
            });
            
            resultsList.innerHTML = html;
            updateDashboardWithExecutionResults(suiteData);
        } else {
            resultsList.innerHTML = `<div style="color: #ef4444;">❌ Suite execution failed: ${suiteData.error}</div>`;
        }
    } catch (error) {
        if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
        resultsList.innerHTML = `<div style="color: #ef4444;">❌ Error: ${error.message}</div>`;
    }
}

async function clearTestSuite() {
    if (!confirm('Are you sure you want to clear all test cases? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/recorder/clear-sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ All test cases cleared successfully');
            loadTestCases();
            
            const executionResults = document.getElementById('executionResults');
            if (executionResults) executionResults.style.display = 'none';
            
            // Reset dashboard metrics
            const dashboardTotalEl = document.getElementById('dashboardTotalRequests');
            if (dashboardTotalEl) dashboardTotalEl.textContent = '0';
            
            if (typeof window.stats !== 'undefined') {
                window.stats.testResults = [];
                if (typeof window.updateRecentTestResults === 'function') window.updateRecentTestResults();
                if (typeof window.updateActivityTimeline === 'function') window.updateActivityTimeline();
            }
        } else {
            alert('❌ Failed to clear test cases: ' + data.error);
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// Helper function to generate placeholder text based on AI suggestion
function getPlaceholderForSuggestion(suggestion) {
    const lowerSuggestion = suggestion.toLowerCase();
    
    if (lowerSuggestion.includes('empty') || lowerSuggestion.includes('0 character')) {
        return 'Leave empty or enter ""';
    } else if (lowerSuggestion.includes('1 character') || lowerSuggestion.includes('minimum')) {
        return 'Enter 1 character (e.g., "a")';
    } else if (lowerSuggestion.includes('maximum') && lowerSuggestion.includes('+ 1')) {
        return 'Enter text exceeding max length';
    } else if (lowerSuggestion.includes('maximum')) {
        return 'Enter text at maximum length';
    } else if (lowerSuggestion.includes('special character')) {
        return 'Enter special chars (e.g., @#$%)';
    } else if (lowerSuggestion.includes('numeric') || lowerSuggestion.includes('number')) {
        return 'Enter numbers (e.g., 12345)';
    } else if (lowerSuggestion.includes('invalid')) {
        return 'Enter invalid data';
    } else if (lowerSuggestion.includes('valid')) {
        return 'Enter valid data';
    }
    
    return 'Enter test data based on suggestion';
}

// Helper function to show semantic suggestions modal (used by both builder and recorder)
function showSemanticSuggestionsModal(suggestions, sessionId, source) {
    const suggestionModal = `
        <div class="modal-overlay" id="semanticSuggestionModal" style="display: flex; position: fixed; inset: 0; background: rgba(0,0,0,0.7); align-items: center; justify-content: center; z-index: 10000;">
            <div class="modal" style="max-width: 600px; background: var(--bg-primary); border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
                <div class="modal-header">
                    <h3 class="modal-title">✨ AI-Generated Test Scenarios</h3>
                </div>
                <div class="modal-body">
                    <p style="margin-bottom: 16px; color: var(--text-secondary);">This test will execute the following boundary scenarios:</p>
                    <div style="background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; padding: 16px; border-radius: 8px;">
                        ${suggestions.map((s, i) => `<div style="margin-bottom: 8px; display: flex; gap: 8px;"><span style="color: #8b5cf6; font-weight: 600;">${i + 1}.</span><span>${s}</span></div>`).join('')}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn" style="background: var(--color-gray-500); flex: 1;" onclick="document.getElementById('semanticSuggestionModal').remove()">Cancel</button>
                    <button class="btn" style="background: var(--color-success-600); flex: 1;" onclick="document.getElementById('semanticSuggestionModal').remove(); executeTestCase('${sessionId}', {}, '${source}')">▶️ Execute Test</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', suggestionModal);
}

// Helper function to handle semantic test logic (used by both builder and recorder)
async function handleSemanticTest(sessionData, sessionId, source) {
    console.log(`[Data Override] 🎯 SEMANTIC ${source.toUpperCase()} TEST - Showing suggestions as guidance`);
    
    const suggestions = sessionData.steps || [];
    
    if (suggestions.length === 0) {
        console.log('[Data Override] No suggestions, executing semantic test directly');
        executeTestCase(sessionId, {}, source);
        return null;
    }
    
    // Store suggestions for display
    window.currentSemanticSuggestions = suggestions;
    
    if (source === 'test-builder') {
        // For semantic tests: Find the PARENT/BASE test to get original input fields
        // Semantic variants are named like: TC002_variant_1, TC002_variant_2, etc.
        // Base test is: TC002
        
        let originalPrompts = [];
        
        // Strategy 1: Try to extract base test ID from variant name
        const testId = sessionData.test_case_id || sessionId;
        const variantMatch = testId.match(/^(.+)_variant_\d+$/);
        
        if (variantMatch) {
            const baseTestId = variantMatch[1];
            console.log('[Data Override] Detected variant test:', testId);
            console.log('[Data Override] Extracting base test ID:', baseTestId);
            
            try {
                const baseTestResponse = await fetch(`${API_URL}/test-suite/test-cases/${baseTestId}`);
                const baseTestData = await baseTestResponse.json();
                
                if (baseTestData.success && baseTestData.test_case && baseTestData.test_case.prompts) {
                    originalPrompts = baseTestData.test_case.prompts;
                    console.log('[Data Override] ✓ Fetched', originalPrompts.length, 'prompts from base test:', baseTestId);
                }
            } catch (error) {
                console.error('[Data Override] Error fetching base test:', error);
            }
        }
        
        // Strategy 2: If parent_test_id is set, use it
        if (originalPrompts.length === 0 && sessionData.parent_test_id) {
            console.log('[Data Override] Using parent_test_id:', sessionData.parent_test_id);
            
            try {
                const parentResponse = await fetch(`${API_URL}/test-suite/test-cases/${sessionData.parent_test_id}`);
                const parentData = await parentResponse.json();
                
                if (parentData.success && parentData.test_case && parentData.test_case.prompts) {
                    originalPrompts = parentData.test_case.prompts;
                    console.log('[Data Override] ✓ Fetched', originalPrompts.length, 'prompts from parent test');
                }
            } catch (error) {
                console.error('[Data Override] Error fetching parent test:', error);
            }
        }
        
        // Strategy 3: If no parent found, try to use current test's prompts
        if (originalPrompts.length === 0) {
            console.log('[Data Override] No parent test found, fetching current test prompts');
            
            try {
                const testResponse = await fetch(`${API_URL}/test-suite/test-cases/${testId}`);
                const testData = await testResponse.json();
                
                if (testData.success && testData.test_case) {
                    originalPrompts = testData.test_case.prompts || [];
                    console.log('[Data Override] Fetched', originalPrompts.length, 'prompts from current test');
                }
            } catch (error) {
                console.error('[Data Override] Error fetching test case:', error);
            }
        }
        
        // Filter for actual input fields (not action steps)
        let inputFieldPrompts = originalPrompts.filter(p => 
            p && p.prompt && p.prompt.trim() &&
            !p.prompt.toLowerCase().includes('click') &&
            !p.prompt.toLowerCase().includes('navigate') &&
            !p.prompt.toLowerCase().includes('verify') &&
            !p.prompt.toLowerCase().includes('wait')
        );
        
        console.log('[Data Override] Filtered to', inputFieldPrompts.length, 'input field prompts');
        
        // If no input fields found from prompts, check if this is a semantic test with generated code
        // Parse the generated code to extract field information
        if (inputFieldPrompts.length === 0) {
            console.log('[Data Override] No prompts found, checking generated code for fields...');
            
            try {
                const testResponse = await fetch(`${API_URL}/test-suite/test-cases/${testId}`);
                const testData = await testResponse.json();
                
                if (testData.success && testData.test_case && testData.test_case.generated_code) {
                    const code = testData.test_case.generated_code.python || testData.test_case.generated_code.java || '';
                    console.log('[Data Override] Analyzing generated code...');
                    
                    // Extract send_keys / sendKeys calls from code
                    const sendKeysPattern = /(?:send_keys|sendKeys)\s*\(\s*["']([^"']+)["']\s*\)/g;
                    const matches = [...code.matchAll(sendKeysPattern)];
                    
                    if (matches.length > 0) {
                        console.log('[Data Override] Found', matches.length, 'input fields in generated code');
                        
                        // Create input items from extracted values
                        inputFieldPrompts = matches.map((match, index) => {
                            const currentValue = match[1];
                            // Try to determine field name from context
                            const fieldName = `Input Field ${index + 1}`;
                            
                            return {
                                prompt: fieldName,
                                value: currentValue,
                                step: index + 1
                            };
                        });
                    } else {
                        console.log('[Data Override] No send_keys found in generated code');
                    }
                }
            } catch (error) {
                console.error('[Data Override] Error parsing generated code:', error);
            }
        }
        
        // If still no fields, show suggestions-only modal
        if (inputFieldPrompts.length === 0) {
            console.log('[Data Override] No input fields - showing suggestions-only modal');
            showSemanticSuggestionsModal(suggestions, sessionId, source);
            return null;
        }
        
        // Create input items from the original test's input fields
        const inputItems = inputFieldPrompts.map((prompt, index) => ({
            index: index,
            step: prompt.step || (index + 1),
            prompt: prompt.prompt,
            value: prompt.value || '',
            hasValue: true,
            isSemanticTest: true
        }));
        
        console.log('[Data Override] Created', inputItems.length, 'input fields from original test');
        return inputItems;
        
    } else {
        // For recorder semantic tests: Use actions from the semantic test itself
        // The semantic test already has the original actions copied from parent
        let actions = sessionData.actions || [];
        console.log('[Data Override] Semantic recorder test has', actions.length, 'actions');
        
        // Filter for input actions only (not clicks, navigates, etc.)
        let inputActions = actions.filter(action => 
            action.action_type === 'input' || 
            action.action_type === 'click_and_input' || 
            action.action_type === 'select'
        );
        
        console.log('[Data Override] Filtered to', inputActions.length, 'input/select actions');
        
        // If no input actions found, try parsing generated code (same as builder)
        if (inputActions.length === 0) {
            console.log('[Data Override] No actions found, checking generated code for fields...');
            
            try {
                const testResponse = await fetch(`${API_URL}/recorder/test/${sessionId}`);
                const testData = await testResponse.json();
                
                if (testData.success && testData.session_data && testData.session_data.generated_code) {
                    const code = testData.session_data.generated_code.python || 
                                testData.session_data.generated_code.java || 
                                testData.session_data.generated_code.javascript || '';
                    console.log('[Data Override] Analyzing generated code...');
                    
                    // Extract send_keys / sendKeys calls from code
                    const sendKeysPattern = /(?:send_keys|sendKeys)\s*\(\s*["']([^"']+)["']\s*\)/g;
                    const matches = [...code.matchAll(sendKeysPattern)];
                    
                    if (matches.length > 0) {
                        console.log('[Data Override] ✓ Found', matches.length, 'input fields in generated code');
                        
                        // Create input actions from extracted values
                        inputActions = matches.map((match, index) => ({
                            action_type: 'input',
                            step: index + 1,
                            action: `Input Field ${index + 1}`,
                            value: match[1]
                        }));
                    } else {
                        console.log('[Data Override] No send_keys found in generated code');
                    }
                }
            } catch (error) {
                console.error('[Data Override] Error parsing generated code:', error);
            }
        }
        
        // If still no input actions, show suggestions-only modal
        if (inputActions.length === 0) {
            console.log('[Data Override] No input fields - showing suggestions-only modal');
            showSemanticSuggestionsModal(suggestions, sessionId, source);
            return null;
        }
        
        // Create input items from the original session's input actions
        const inputItems = inputActions.map((action, index) => ({
            index: index,
            step: action.step,
            prompt: action.action || action.prompt || `Step ${action.step}`,
            actionType: action.action_type === 'select' ? 'Select' : 'Input',
            value: action.value || '',
            originalValue: action.value,
            isSemanticTest: true
        }));
        
        console.log('[Data Override] ✓ Created', inputItems.length, 'input fields for recorder test');
        return inputItems;
    }
}

async function showDataOverrideModal(sessionId, source = 'recorder') {
    console.log('[Data Override] ==== START ====');
    console.log('[Data Override] Session ID:', sessionId);
    console.log('[Data Override] Source:', source);
    
    // Store source for later use
    window.currentTestSource = source;
    
    try {
        let inputItems = [];
        
        // Handle Test Builder tests
        if (source === 'test-builder') {
            console.log('[Data Override] Processing Test Builder test');
            // Fetch session data for Test Builder
            const sessionData = window.allTestSessions?.find(s => s.id === sessionId || s.session_id === sessionId);
            
            if (!sessionData) {
                console.log('[Data Override] ❌ Session not found');
                executeTestCase(sessionId, {}, source);
                return;
            }
            
            console.log('[Data Override] ===== SESSION DATA DEBUG =====');
            console.log('[Data Override] Test name:', sessionData.name);
            console.log('[Data Override] Tags:', sessionData.tags);
            console.log('[Data Override] Parent test ID:', sessionData.parent_test_id);
            console.log('[Data Override] Test case ID:', sessionData.test_case_id);
            console.log('[Data Override] Prompts count:', sessionData.prompts?.length);
            console.log('[Data Override] Steps/Suggestions count:', sessionData.steps?.length);
            if (sessionData.prompts && sessionData.prompts.length > 0) {
                console.log('[Data Override] First 3 prompts:');
                sessionData.prompts.slice(0, 3).forEach((p, i) => {
                    console.log(`  ${i + 1}. "${p.prompt}" (step ${p.step}, value: "${p.value}")`);
                });
            }
            console.log('[Data Override] =====================================');
            
            // Check if this is a semantic test
            const isSemantic = sessionData.tags && (sessionData.tags.includes('semantic') || sessionData.tags.includes('ai-generated'));
            
            if (isSemantic) {
                // Use shared semantic test handler
                const semanticInputItems = await handleSemanticTest(sessionData, sessionId, source);
                if (semanticInputItems === null) return; // Modal shown or executing
                inputItems = semanticInputItems;
            } else {
                // Regular Test Builder test - fetch prompts
                let prompts = [];
            
                // Check if this is a saved test case
                if (sessionData && sessionData.test_case_id) {
                    console.log('[Data Override] Fetching saved test case:', sessionData.test_case_id);
                    
                    // CRITICAL FIX: Check if prompts are already in sessionData (from test list)
                    if (sessionData.prompts && sessionData.prompts.length > 0) {
                        prompts = sessionData.prompts;
                        console.log('[Data Override] ✓ Using prompts from cached session data:', prompts.length);
                    } else {
                        // Fetch saved test case to get prompts
                        try {
                            const testCaseResponse = await fetch(`${API_URL}/test-suite/test-cases/${sessionData.test_case_id}`);
                            const testCaseData = await testCaseResponse.json();
                            
                            if (testCaseData.success && testCaseData.test_case) {
                                prompts = testCaseData.test_case.prompts || [];
                                console.log('[Data Override] Loaded prompts from saved test case:', prompts.length);
                            }
                        } catch (error) {
                            console.error('[Data Override] Error fetching test case:', error);
                        }
                    }
                } else {
                    // Fetch active session to get prompts
                    const response = await fetch(`${API_URL}/test-suite/session/${sessionId}`);
                    const data = await response.json();
                    
                    if (data.success && data.session && data.session.prompts) {
                        prompts = data.session.prompts;
                        console.log('[Data Override] Loaded prompts from active session');
                    }
                }
                
                if (prompts.length === 0) {
                    console.log('[Data Override] No prompts found');
                    executeTestCase(sessionId, {}, source);
                    return;
                }
                
                // Extract prompts with values (input data)
                inputItems = prompts.map((prompt, index) => ({
                    index: index,
                    step: prompt.step || (index + 1),
                    prompt: prompt.prompt || 'Step ' + (index + 1),
                    value: prompt.value || '',
                    hasValue: !!prompt.value
                })).filter(item => item.hasValue); // Only show prompts that have values
                
                if (inputItems.length === 0) {
                    console.log('[Data Override] No prompts with values found, executing without override');
                    executeTestCase(sessionId, {}, source);
                    return;
                }
            }
        } else {
            // Handle Recorder tests - Same approach as Test Builder
            console.log('[Data Override] Processing Recorder test');
            
            // Get session data from already-loaded Test Suite data (same as Test Builder)
            let sessionData = window.allTestSessions?.find(s => s.id === sessionId || s.session_id === sessionId);
            
            console.log('[Data Override] Session data from Test Suite:', sessionData);
            
            if (!sessionData) {
                console.log('[Data Override] ❌ Session not found in Test Suite data');
                showNotification('⚠️ Test not found. Please refresh Test Suite.', 'warning');
                executeTestCase(sessionId, {}, source);
                return;
            }
            
            // Check if this is a semantic test (same logic as builder tests)
            const isSemantic = sessionData.tags && (sessionData.tags.includes('semantic') || sessionData.tags.includes('ai-generated'));
            
            if (isSemantic) {
                // Use shared semantic test handler
                const semanticInputItems = await handleSemanticTest(sessionData, sessionId, source);
                if (semanticInputItems === null) return; // Modal shown or executing
                inputItems = semanticInputItems;
            } else {
                // Regular recorder test - check if we have actions in the session data
                // Usually loaded with test list, but fetch if missing
                if (!sessionData.actions || sessionData.actions.length === 0) {
                    console.log('[Data Override] Actions not in cached data, fetching from API...');
                    
                    try {
                        // Use the new endpoint that loads full test data with actions
                        const fullDataResponse = await fetch(`${API_URL}/recorder/test/${sessionId}`);
                        const fullData = await fullDataResponse.json();
                        
                        if (fullData.success && fullData.session_data && fullData.session_data.actions) {
                            console.log('[Data Override] ✓ Loaded full test data with', fullData.session_data.actions.length, 'actions');
                            sessionData.actions = fullData.session_data.actions;
                        } else {
                            console.log('[Data Override] ⚠️ Failed to load actions:', fullData.error || 'No actions in response');
                        }
                    } catch (error) {
                        console.error('[Data Override] Error fetching full test data:', error);
                    }
                } else {
                    console.log('[Data Override] ✓ Actions already loaded:', sessionData.actions.length);
                }
                
                // Final check - do we have actions now?
                if (!sessionData || !sessionData.actions || sessionData.actions.length === 0) {
                    console.log('[Data Override] ⚠️ No actions available even after API fetch');
                    showNotification('ℹ️ No actions in test. Executing directly.', 'info');
                    executeTestCase(sessionId, {}, source);
                    return;
                }
                
                console.log('[Data Override] ✓ Found session with', sessionData.actions.length, 'actions');
                
                // Filter for input/select actions
                const inputActions = sessionData.actions.filter(a => 
                    a.action_type === 'input' || 
                    a.action_type === 'click_and_input' || 
                    a.action_type === 'select'
                );
                
                console.log('[Data Override] Found', inputActions.length, 'input/select actions');
                
                if (inputActions.length === 0) {
                    console.log('[Data Override] ℹ️ No input actions found - executing without overrides');
                    showNotification('ℹ️ No input/select actions in test. Executing directly.', 'info');
                    executeTestCase(sessionId, {}, source);
                    return;
                }
                
                // Convert actions to inputItems format
                inputItems = inputActions.map((action, index) => ({
                    index: index,
                    step: action.step,
                    prompt: action.action || action.prompt || `Step ${action.step}`,
                    actionType: action.action_type === 'select' ? 'Select' : 'Input',
                    value: action.value || '',
                    originalValue: action.value
                }));
                
                console.log('[Data Override] ✓ Prepared', inputItems.length, 'input items for modal');
            }
        }
        
        console.log('[Data Override] ✓ Showing modal with', inputItems.length, 'items');
        
        // Check if this is a semantic test
        const isSemanticTest = inputItems.length > 0 && inputItems[0].isSemanticTest;
        
        // If semantic test, fetch field-aware suggestions
        if (isSemanticTest && window.fieldAwareSuggestions) {
            console.log('[Data Override] 🎯 Fetching field-aware suggestions for semantic test');
            try {
                await window.fieldAwareSuggestions.fetchSuggestions(sessionId);
                console.log('[Data Override] ✓ Field-aware suggestions loaded');
            } catch (error) {
                console.error('[Data Override] ⚠️ Failed to fetch field-aware suggestions:', error);
                // Continue anyway with fallback to generic suggestions
            }
        }
        
        // Build form fields from inputItems
        const modal = document.createElement('div');
        modal.id = 'dataOverrideModal';
        modal.className = 'modal-overlay';
        
        let formFields = '';
        inputItems.forEach((item, index) => {
            const stepLabel = `Step ${item.step}`;
            const itemLabel = source === 'test-builder' 
                ? item.prompt
                : `${item.actionType || 'Input'} - ${item.prompt}`;
            
            // For semantic tests, show field-aware AI suggestions inline  
            let inlineSuggestions = '';
            if (item.isSemanticTest) {
                // Use field-aware suggestions module
                const inputElementId = `override_${item.index}`;
                inlineSuggestions = window.fieldAwareSuggestions 
                    ? window.fieldAwareSuggestions.renderFieldSuggestions(item.index, inputElementId, sessionId)
                    : '';
                
                // Fallback to generic suggestions if field-aware not available
                if (!inlineSuggestions) {
                    const semanticSuggestions = window.currentSemanticSuggestions || [];
                    if (semanticSuggestions.length > 0) {
                        inlineSuggestions = `<div style="margin-top: 10px; padding: 12px; background: rgba(139, 92, 246, 0.08); border-left: 3px solid #8b5cf6; border-radius: 4px;">
                               <div style="font-size: 12px; font-weight: 600; color: #8b5cf6; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                                   <span>💡</span>
                                   <span>AI Test Scenarios:</span>
                               </div>
                               <div style="display: flex; flex-direction: column; gap: 6px;">
                                   ${semanticSuggestions.map((s, i) => `
                                       <div style="font-size: 11px; color: var(--text-primary); padding: 4px 8px; background: rgba(139, 92, 246, 0.05); border-radius: 3px; line-height: 1.4;">
                                           <span style="color: #8b5cf6; font-weight: 600;">${i + 1}.</span> ${s}
                                       </div>
                                   `).join('')}
                               </div>
                           </div>`;
                    }
                }
            }
            
            // For regular tests (non-semantic), show suggestion as additional help
            const suggestionHint = !item.isSemanticTest && item.suggestion 
                ? `<div style="margin-top: 8px; padding: 10px; background: rgba(124, 58, 237, 0.1); border-left: 3px solid #7c3aed; border-radius: 4px;">
                       <div style="font-size: 12px; font-weight: 600; color: #7c3aed; margin-bottom: 4px;">💡 Suggested Implementation:</div>
                       <div style="font-size: 12px; color: var(--text-primary); line-height: 1.5;">${item.suggestion}</div>
                   </div>`
                : '';
            
            const placeholder = item.isSemanticTest ? 'Enter value based on scenario above' : 'Enter test data';
            
            formFields += `
                <div style="margin-bottom: 20px; padding: 15px; background: var(--bg-secondary); border-radius: 8px; border: 1px solid var(--border-color);">
                    <label style="display: block; margin-bottom: 8px; color: var(--text-primary); font-weight: 600; font-size: 14px;">
                        ${item.isSemanticTest ? itemLabel : `${stepLabel}: ${itemLabel}`}
                    </label>
                    <input 
                        type="text" 
                        id="override_${item.index}" 
                        data-step="${item.step}"
                        data-prompt-index="${item.index}"
                        placeholder="${placeholder}"
                        value="${item.value || ''}"
                        style="width: 100%; padding: 12px; border: 2px solid var(--border-color); border-radius: 6px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; background: var(--input-bg); color: var(--text-primary);"
                        onfocus="this.style.borderColor='#8b5cf6'; this.style.outline='none';"
                        onblur="this.style.borderColor='var(--border-color)';"
                    />
                    ${inlineSuggestions}
                    ${suggestionHint}
                    ${!item.isSemanticTest ? `<div style="font-size: 12px; color: var(--text-secondary); margin-top: 6px; font-style: italic;">📝 Original value: "${item.value || 'N/A'}"</div>` : ''}
                </div>
            `;
        });
        
        // Get semantic suggestions for display (isSemanticTest already declared earlier)
        const semanticSuggestions = window.currentSemanticSuggestions || [];
        
        // For semantic tests, show a brief header instead of duplicating all suggestions
        // (Full suggestions are shown inline with each field)
        const suggestionsBox = isSemanticTest && semanticSuggestions.length > 0
            ? `<div style="margin-bottom: 20px; padding: 14px; background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; border-radius: 8px;">
                   <div style="font-size: 14px; font-weight: 600; color: #8b5cf6; margin-bottom: 6px;">✨ AI Boundary Testing</div>
                   <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
                       This test includes ${semanticSuggestions.length} AI-generated scenarios. Review the suggestions below each field and enter appropriate test values.
                   </div>
               </div>`
            : '';
        
        const modalTitle = isSemanticTest ? '✨ AI Boundary Test - Enter Test Data' : '🔧 Override Test Data';
        const modalDescription = isSemanticTest 
            ? 'Each field below shows AI-generated test scenarios. Choose a scenario and enter the corresponding test value:'
            : 'Modify the input values below to run the test with different data';
        const tipBox = !isSemanticTest
            ? `<div style="margin-bottom: 25px; padding: 14px; background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; border-radius: 6px;">
                   <div style="font-size: 14px; color: var(--text-primary); line-height: 1.5;">
                       💡 <strong>Tip:</strong> Leave fields unchanged to use recorded values, or enter new data to override them during execution.
                   </div>
               </div>`
            : '';
        
        modal.innerHTML = `
            <div class="modal" style="max-width: ${isSemanticTest ? '750px' : '650px'};">
                <div class="modal-header">
                    <h3 class="modal-title">${modalTitle}</h3>
                    <button class="modal-close" onclick="closeDataOverrideModal()">&times;</button>
                </div>
                <div class="modal-body" style="max-height: 60vh; overflow-y: auto;">
                    <p style="color: var(--text-secondary); margin-bottom: 20px; font-size: 14px;">
                        ${modalDescription}
                    </p>
                    ${suggestionsBox}
                    ${tipBox}
                    <form id="dataOverrideForm">
                        ${formFields}
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn" style="background: var(--color-gray-500); flex: 1;" onclick="closeDataOverrideModal()">
                        ❌ Cancel
                    </button>
                    <button type="submit" form="dataOverrideForm" class="btn" style="background: var(--color-success-600); flex: 1;">
                        ▶️ ${isSemanticTest ? 'Execute Test' : 'Execute with Data'}
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('dataOverrideForm').addEventListener('submit', (e) => {
            e.preventDefault();
            
            const overrides = {};
            inputItems.forEach((item) => {
                const input = document.getElementById(`override_${item.index}`);
                const newValue = input.value.trim();
                
                // Check if value changed
                if (newValue !== item.value) {
                    if (source === 'test-builder') {
                        // For Test Builder: index by prompt index (0-based)
                        overrides[item.index] = newValue;
                    } else {
                        // For Recorder: index by step number
                        overrides[item.step] = newValue;
                    }
                }
            });
            
            console.log('[Data Override] Overrides:', overrides);
            closeDataOverrideModal();
            executeTestCase(sessionId, overrides, source);
        });
        
    } catch (error) {
        console.error('Error showing data override modal:', error);
        executeTestCase(sessionId, {}, source);
    }
}

function closeDataOverrideModal() {
    const modal = document.getElementById('dataOverrideModal');
    if (modal) {
        modal.remove();
    }
}

async function executeTestCase(sessionId, dataOverrides = {}, source = 'recorder') {
    // Prevent double execution
    if (window.isExecutingTest) {
        console.log('[Test Suite] ⚠️ Test already executing, ignoring duplicate call');
        return;
    }
    window.isExecutingTest = true;
    
    // Close any sticky popup before executing test
    const stickyPopup = document.getElementById('sticky-close');
    if (stickyPopup) {
        stickyPopup.style.display = 'none';
        stickyPopup.remove();
    }
    
    const resultsDiv = document.getElementById('executionResults');
    const resultsList = document.getElementById('executionResultsList');
    const currentlyExecutingDiv = document.getElementById('currentlyExecutingTest');
    const currentExecutingTestName = document.getElementById('currentExecutingTestName');
    
    if (!resultsDiv || !resultsList) {
        window.isExecutingTest = false;
        showNotification('⚠️ Test execution UI not found');
        return;
    }
    
    resultsDiv.style.display = 'block';
    if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'block';
    
    // Get test name from window.allTestSessions
    let testName = sessionId; // Default to ID if not found
    if (window.allTestSessions && Array.isArray(window.allTestSessions)) {
        const session = window.allTestSessions.find(s => s.id === sessionId || s.session_id === sessionId);
        if (session && session.name) {
            testName = session.name;
        }
    }
    
    // Set test name
    if (currentExecutingTestName) {
        currentExecutingTestName.textContent = testName;
    }
    
    resultsList.innerHTML = '<div style="color: #f59e0b;">⏳ Executing test case...</div>';
    
    try {
        let response;
        
        // Get selected healing mode and browser from UI
        const selectedHealingMode = document.getElementById('healingModeSelect')?.value || 'v1';
        const selectedBrowser = document.getElementById('browserSelect')?.value || 'chrome';
        
        // Find the session data to determine execution type
        const sessionData = window.allTestSessions?.find(s => s.id === sessionId || s.session_id === sessionId);
        
        // Use different endpoint based on source
        if (source === 'test-builder') {
            // Check if this is a saved test case or an active session
            const isSavedTestCase = sessionData && sessionData.test_case_id;
            
            if (isSavedTestCase) {
                // Saved test case: use /test-suite/execute/{test_case_id}
                console.log('[Test Suite] Executing saved test case:', sessionData.test_case_id);
                response = await fetch(`${API_URL}/test-suite/execute/${sessionData.test_case_id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        headless: false,
                        data_overrides: dataOverrides,
                        browser: selectedBrowser,
                        healing_mode: selectedHealingMode
                    })
                });
            } else {
                // Active session (not saved): use /test-suite/session/{session_id}/execute
                console.log('[Test Suite] Executing active session:', sessionId);
                response = await fetch(`${API_URL}/test-suite/session/${sessionId}/execute`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        headless: false,
                        data_overrides: dataOverrides,
                        browser: selectedBrowser,
                        healing_mode: selectedHealingMode
                    })
                });
            }
        } else {
            // Recorder tests use /recorder/execute-test
            response = await fetch(`${API_URL}/recorder/execute-test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    session_id: sessionId,
                    data_overrides: dataOverrides,
                    browser: selectedBrowser,
                    healing_mode: selectedHealingMode
                })
            });
        }
        
        const data = await response.json();
        
        // Normalize Test Builder response to match Recorder format
        if (source === 'test-builder') {
            if (data.result) {
                // Test Builder wraps result in 'result' object
                const result = data.result;
                data.passed = result.status === 'passed';
                data.test_name = result.test_name;
                data.duration = result.duration || 0;
                data.steps_executed = result.steps ? result.steps.filter(s => s.status === 'passed').length : 0;
                data.total_steps = result.steps ? result.steps.length : 0;
                data.error = result.error_message || null;
                data.output = result.logs ? result.logs.map(l => `[${l.level}] ${l.message}`).join('\n') : null;
            } else if (data.error) {
                // Test Builder error response
                data.passed = false;
                data.test_name = sessionId;
                data.duration = 0;
                data.steps_executed = 0;
                data.total_steps = 0;
            }
        }
        
        console.log('[Test Suite] 🎯 RAW RESPONSE:', JSON.stringify(data, null, 2));
        console.log('[Test Suite] Response validation:', {
            hasSuccess: 'success' in data,
            hasPassed: 'passed' in data,
            hasTestName: 'test_name' in data,
            hasDuration: 'duration' in data,
            successValue: data.success,
            passedValue: data.passed,
            durationValue: data.duration
        });
        
        if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
        
        // CRITICAL: Record test results for BOTH passed and failed tests
        if (data.success !== undefined && ('passed' in data || data.error)) {
            // Detect dark mode
            const isDarkMode = document.body.classList.contains('dark-mode');
            
            // Simple color scheme - no backgrounds, just text and borders
            let borderColor, textColor, mutedColor;
            if (data.passed) {
                borderColor = '#10b981';
                textColor = isDarkMode ? '#6ee7b7' : '#065f46';
                mutedColor = isDarkMode ? '#f3f4f6' : '#6b7280';
            } else {
                borderColor = '#ef4444';
                textColor = isDarkMode ? '#fca5a5' : '#991b1b';
                mutedColor = isDarkMode ? '#f3f4f6' : '#6b7280';
            }
            
            // Get screenshots from response - try multiple possible locations
            const screenshots = data.screenshots || data.result?.screenshots || data.execution_result?.screenshots || [];
            console.log('[Test Suite] 📸 Screenshots found:', screenshots.length, screenshots);
            
            // Build screenshot HTML if there are any
            let screenshotHtml = '';
            if (screenshots && screenshots.length > 0) {
                screenshotHtml = `
                    <div style="margin-top: 10px; padding: 10px; border-left: 3px solid #f59e0b; border-radius: 4px;">
                        <div style="font-weight: bold; color: ${isDarkMode ? '#fbbf24' : '#92400e'}; margin-bottom: 8px;">📸 Error Screenshot${screenshots.length > 1 ? 's' : ''} Captured:</div>
                        ${screenshots.map(s => {
                            const path = s.path || s.filepath || s.screenshot_path || '';
                            const step = s.step || s.step_number || 'Unknown';
                            const error = s.error || s.error_message || s.description || 'View Screenshot';
                            return `<div style="margin-top: 5px;"><a href="${path}" target="_blank" style="color: ${isDarkMode ? '#60a5fa' : '#3b82f6'}; text-decoration: underline; font-size: 0.95em;">Step ${step}: ${error}</a></div>`;
                        }).join('')}
                    </div>`;
            }
            
            const result = `
                <div style="padding: 10px; margin-bottom: 10px; border-left: 4px solid ${borderColor}; border-radius: 6px;">
                    <div style="font-weight: bold; color: ${textColor};">
                        ${data.passed ? '✅ Test Passed' : '❌ Test Failed'}
                    </div>
                    ${data.is_edited_code ? '<div style="font-size: 0.9em; color: #a78bfa; margin-top: 5px; font-weight: bold;">⚡ Executed edited code</div>' : `<div style="font-size: 0.9em; color: ${mutedColor}; margin-top: 5px;">Steps executed: ${data.steps_executed} / ${data.total_steps}</div>`}
                    ${Object.keys(dataOverrides).length > 0 ? '<div style="font-size: 0.9em; color: #60a5fa; margin-top: 5px;">🔧 Executed with overridden data</div>' : ''}
                    ${screenshotHtml}
                    ${data.output ? `<details style="margin-top: 10px;"><summary style="cursor: pointer; color: ${mutedColor}; font-size: 0.9em;">📋 View Output</summary><pre style="background: ${isDarkMode ? '#374151' : '#1f2937'}; color: #e5e7eb; padding: 10px; border-radius: 4px; overflow-x: auto; margin-top: 5px; font-size: 0.85em;">${data.output}</pre></details>` : ''}
                    ${data.error && !data.output ? `<div style="font-size: 0.9em; color: ${isDarkMode ? '#ffffff' : '#fca5a5'}; margin-top: 5px;">Error: ${data.error}</div>` : ''}
                </div>
            `;
            resultsList.innerHTML = result;
            
            // Fetch and display screenshots for failed tests
            if (!data.passed && sessionId) {
                fetchAndDisplayScreenshots(sessionId, resultsList);
            }
            
            // Update dashboard with test result (for both passed and failed tests)
            const isPassed = data.passed === true;
            const testName = data.test_name || 'Test Case';
            const duration = data.duration || 0;
            
            console.log('[Test Suite] 📈 Processing test result:', {
                passed: isPassed,
                test_name: testName,
                duration: duration,
                steps: data.steps_executed ? `${data.steps_executed}/${data.total_steps}` : 'N/A',
                hasError: !!data.error,
                timestamp: new Date().toISOString()
            });
            
            if (typeof addTestResult === 'function') {
                const details = isPassed ? 
                    `Executed ${data.steps_executed || 0}/${data.total_steps || 0} steps successfully` :
                    `Failed${data.step ? ' at step ' + data.step : ''}${data.error ? ': ' + data.error.substring(0, 100) : ''}`;
                
                console.log('[Test Suite] 📞 CALLING addTestResult NOW:', { testName, status: isPassed ? 'passed' : 'failed', duration, details });
                
                // Call addTestResult
                addTestResult(testName, isPassed ? 'passed' : 'failed', duration, details);
                
                console.log('[Test Suite] ✅ addTestResult called - waiting 200ms for save...');
                
                // Force dashboard update after a delay to ensure save completed
                setTimeout(() => {
                    console.log('[Test Suite] 🔄 Forcing dashboard update NOW');
                    if (typeof updateDashboardStats === 'function') {
                        updateDashboardStats();
                    }
                    // Double-check localStorage
                    const stats = localStorage.getItem('dashboardStats');
                    console.log('[Test Suite] 📊 Dashboard stats after update:', stats ? JSON.parse(stats) : 'NO DATA');
                }, 200);
            } else {
                console.error('[Test Suite] ❌ CRITICAL: addTestResult function not found!');
                console.log('[Test Suite] Available window functions:', Object.keys(window).filter(k => k.includes('Test') || k.includes('Dashboard')));
            }
            
            // Show bug report modal for semantic tests (after results displayed)
            const sessionData = window.allTestSessions?.find(s => s.id === sessionId || s.session_id === sessionId);
            const isSemantic = sessionData?.tags?.includes('semantic') || sessionData?.tags?.includes('ai-generated');
            
            if (isSemantic && window.feedbackManager && Object.keys(dataOverrides).length > 0) {
                console.log('[Test Suite] 🎯 Semantic test completed - showing feedback modal');
                setTimeout(() => {
                    feedbackManager.showBugReportModal(sessionId, Object.keys(dataOverrides));
                }, 1500); // Delay to let results display first
            }
        } else {
            const errorHtml = `
                <div style="color: #ef4444; padding: 10px; background: #fee2e2; border-radius: 6px; border-left: 4px solid #ef4444;">
                    <div style="font-weight: bold;">❌ Execution failed</div>
                    <div style="margin-top: 5px; font-size: 0.9em;">${data.error}</div>
                    ${data.hint ? `<div style="margin-top: 8px; padding: 8px; background: #fef3c7; color: #92400e; border-radius: 4px; font-size: 0.9em;">💡 Hint: ${data.hint}</div>` : ''}
                </div>
            `;
            resultsList.innerHTML = errorHtml;
        }
    } catch (error) {
        if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
        resultsList.innerHTML = `<div style="color: #ef4444;">❌ Error: ${error.message}</div>`;
    } finally {
        // Reset execution flag
        window.isExecutingTest = false;
    }
}

async function executeCurrentTest() {
    alert('This will execute the currently displayed test code. Feature coming soon!');
}

async function executeViewedTest() {
    if (!window.currentTestSuiteSessionId) {
        showNotification('⚠️ No test selected. Please view a test first.', 'warning');
        return;
    }
    
    const sessionId = window.currentTestSuiteSessionId;
    const source = window.currentTestSuiteSource || 'recorder';
    
    console.log('[Test Suite] Executing viewed test:', { sessionId, source });
    
    // Show data override modal for the test
    showDataOverrideModal(sessionId, source);
}

function editTestSuiteCode() {
    const code = document.getElementById('testSuiteCodeContent').textContent;
    const editArea = document.getElementById('testSuiteCodeEditArea');
    const editor = document.getElementById('testSuiteCodeEditor');
    const viewer = document.getElementById('testSuiteCodeViewer');
    
    if (!editArea || !editor || !viewer) {
        showNotification('⚠️ Edit UI not found');
        return;
    }
    
    editArea.value = code;
    viewer.style.display = 'none';
    editor.style.display = 'block';
}

async function saveEditedTestCode() {
    const editedCode = document.getElementById('testSuiteCodeEditArea').value;
    const sessionId = window.currentTestSuiteSessionId;
    
    if (!sessionId) {
        alert('No test case selected to save');
        return;
    }
    
    if (typeof showLoading === 'function') showLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/recorder/update-test-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId,
                code: editedCode
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.currentTestSuiteCode = editedCode;
            displayTestSuiteCode(editedCode, sessionId);
            cancelEditTestCode();
            alert('✅ Test code updated successfully!');
        } else {
            alert('❌ Failed to save: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Error saving test code: ' + error.message);
    } finally {
        if (typeof showLoading === 'function') showLoading(false);
    }
}

function cancelEditTestCode() {
    const editor = document.getElementById('testSuiteCodeEditor');
    const viewer = document.getElementById('testSuiteCodeViewer');
    
    if (editor && viewer) {
        editor.style.display = 'none';
        viewer.style.display = 'block';
    }
}

// Expose functions to window object
window.loadTestCases = loadTestCases;
window.viewTestCase = viewTestCase;
window.displayTestCases = displayTestCases;
window.displayTestSuiteCode = displayTestSuiteCode;
window.filterTestsBySource = filterTestsBySource;
window.filterTestsByModule = filterTestsByModule;
window.applyFilters = applyFilters;
window.populateModuleFilter = populateModuleFilter;
window.populateModulesList = populateModulesList;
window.toggleSelectAllTests = toggleSelectAllTests;
// Toggle three-dot dropdown menu
function toggleTestMenu(sessionId) {
    const menu = document.getElementById(`menu-${sessionId}`);
    if (!menu) return;
    
    // Close all other menus first and remove active class from cards
    document.querySelectorAll('.dropdown-menu').forEach(m => {
        if (m.id !== `menu-${sessionId}`) {
            m.style.display = 'none';
            // Remove active class from parent card
            const parentCard = m.closest('.test-case-card');
            if (parentCard) {
                parentCard.classList.remove('dropdown-active');
            }
        }
    });
    
    // Toggle this menu
    const isOpening = menu.style.display === 'none';
    menu.style.display = isOpening ? 'block' : 'none';
    
    // Add/remove active class to parent card
    const parentCard = menu.closest('.test-case-card');
    if (parentCard) {
        if (isOpening) {
            parentCard.classList.add('dropdown-active');
        } else {
            parentCard.classList.remove('dropdown-active');
        }
    }
}

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            m.style.display = 'none';
            // Remove active class from parent card
            const parentCard = m.closest('.test-case-card');
            if (parentCard) {
                parentCard.classList.remove('dropdown-active');
            }
        });
    }
});

// Export single test
async function exportSingleTest(sessionId) {
    try {
        const session = window.allTestSessions?.find(s => s.id === sessionId);
        if (!session) {
            alert('Test not found');
            return;
        }
        
        const response = await fetch(`${API_URL}/test-suite/test-cases/${sessionId}/code`);
        const data = await response.json();
        
        if (data.code) {
            const blob = new Blob([data.code], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${session.name.replace(/[^a-z0-9]/gi, '_')}.java`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Test exported successfully!', 'success');
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('Failed to export test');
    }
}

// Duplicate test
async function duplicateTest(sessionId) {
    try {
        const session = window.allTestSessions?.find(s => s.id === sessionId);
        if (!session) {
            alert('Test not found');
            return;
        }
        
        const newTest = {
            ...session,
            id: Date.now().toString(),
            name: `${session.name} (Copy)`,
            timestamp: new Date().toISOString()
        };
        
        // Save duplicate (this would need backend support)
        showNotification('Duplicate test created!', 'success');
        loadTestCases(); // Refresh list
    } catch (error) {
        console.error('Duplicate error:', error);
        alert('Failed to duplicate test');
    }
}

// Edit test name (for semantic tests)
async function editTestName(testCaseId, currentName, source) {
    try {
        console.log('[EDIT NAME] Test ID:', testCaseId, 'Current name:', currentName, 'Source:', source);
        
        // Create modal for editing name
        const modal = document.createElement('div');
        modal.id = 'editNameModal';
        modal.className = 'modal-overlay';
        modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000;';
        
        modal.innerHTML = `
            <div class="modal" style="max-width: 500px; width: 90%; background: var(--bg-primary); border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                <div class="modal-header" style="padding: 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                    <h3 class="modal-title" style="margin: 0; color: var(--text-primary); font-size: 18px; font-weight: 600;">✏️ Edit Test Name</h3>
                    <button class="modal-close" onclick="closeEditNameModal()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text-secondary); padding: 0; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;">&times;</button>
                </div>
                <div class="modal-body" style="padding: 25px;">
                    <p style="color: var(--text-secondary); margin-bottom: 20px; font-size: 14px;">
                        Enter a new name for this test case
                    </p>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: var(--text-primary); font-weight: 600; font-size: 14px;">
                            Test Name
                        </label>
                        <input 
                            type="text" 
                            id="newTestNameInput" 
                            placeholder="Enter new test name"
                            value="${currentName.replace(/"/g, '&quot;')}"
                            style="width: 100%; padding: 12px; border: 2px solid var(--border-color); border-radius: 6px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; background: var(--input-bg); color: var(--text-primary);"
                            onfocus="this.style.borderColor='#667eea'; this.style.outline='none';"
                            onblur="this.style.borderColor='var(--border-color)';"
                        />
                    </div>
                    <div style="padding: 12px; background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; border-radius: 6px; margin-bottom: 20px;">
                        <div style="font-size: 12px; color: var(--text-primary); line-height: 1.5;">
                            💡 <strong>Tip:</strong> Choose a clear, descriptive name that explains what this test does
                        </div>
                    </div>
                </div>
                <div class="modal-footer" style="padding: 15px 25px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; gap: 12px;">
                    <button onclick="closeEditNameModal()" style="padding: 10px 20px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border-color); border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;">
                        Cancel
                    </button>
                    <button onclick="saveTestName('${testCaseId}', '${source}')" style="padding: 10px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;">
                        💾 Save
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Focus on input
        setTimeout(() => {
            const input = document.getElementById('newTestNameInput');
            if (input) {
                input.focus();
                input.select();
            }
        }, 100);
        
        // Close on escape key
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeEditNameModal();
            } else if (e.key === 'Enter') {
                saveTestName(testCaseId, source);
            }
        });
        
    } catch (error) {
        console.error('[EDIT NAME] Error:', error);
        showNotification('❌ Failed to open edit dialog', 'error');
    }
}

function closeEditNameModal() {
    const modal = document.getElementById('editNameModal');
    if (modal) {
        modal.remove();
    }
}

async function saveTestName(testCaseId, source) {
    try {
        const input = document.getElementById('newTestNameInput');
        const newName = input?.value?.trim();
        
        if (!newName) {
            showNotification('⚠️ Test name cannot be empty', 'warning');
            return;
        }
        
        console.log('[SAVE NAME] Updating test:', testCaseId, 'to name:', newName);
        
        // Determine endpoint based on source
        const endpoint = source === 'test-builder' 
            ? `${API_URL}/test-suite/test-cases/${testCaseId}/rename`
            : `${API_URL}/recorder/rename-test/${testCaseId}`;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_name: newName })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Test name updated successfully!', 'success');
            closeEditNameModal();
            
            // Refresh test list to show new name
            await loadTestCases();
        } else {
            showNotification('❌ Failed to update test name: ' + (data.error || 'Unknown error'), 'error');
        }
        
    } catch (error) {
        console.error('[SAVE NAME] Error:', error);
        showNotification('❌ Failed to save test name: ' + error.message, 'error');
    }
}

/**
 * Fetch and display execution results with screenshots for a test case
 */
async function fetchAndDisplayScreenshots(testCaseId, resultsContainer) {
    try {
        console.log('[Screenshots] Fetching execution results for:', testCaseId);
        
        const response = await fetch(`${API_URL}/test-suite/execution-results/${testCaseId}`);
        const data = await response.json();
        
        if (!data.success || !data.execution_results || data.execution_results.length === 0) {
            console.log('[Screenshots] No execution results found');
            return;
        }
        
        // Get the latest execution result (first in array since sorted newest first)
        const latestExecution = data.execution_results[0];
        
        console.log('[Screenshots] Latest execution:', latestExecution);
        
        // Check if there are screenshots
        if (!latestExecution.screenshots || latestExecution.screenshots.length === 0) {
            console.log('[Screenshots] No screenshots in latest execution');
            return;
        }
        
        // Create screenshot gallery HTML
        const screenshotsHtml = `
            <div style="margin-top: 20px; padding: 15px; background: #FEE2E2; border-radius: 8px; border-left: 4px solid #EF4444;">
                <h4 style="color: #991B1B; margin: 0 0 15px 0; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.2em;">🖼️</span>
                    <span>Failure Screenshots (${latestExecution.screenshots.length})</span>
                </h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px;">
                    ${latestExecution.screenshots.map(screenshot => {
                        // Get the screenshot path - handle both 'filepath' and 'path' properties
                        let screenshotPath = screenshot.filepath || screenshot.path || '';
                        
                        // Convert absolute Windows path to relative web path
                        // Handles both:
                        // - Builder: "execution_results/builder/screenshots/test.png"
                        // - Recorder: "execution_results/recorder/screenshots/test.png"
                        if (screenshotPath.includes('execution_results')) {
                            screenshotPath = screenshotPath
                                .replace(/\\/g, '/')  // Convert backslashes to forward slashes
                                .split('execution_results/').pop();  // Get everything after execution_results/
                            screenshotPath = `execution_results/${screenshotPath}`;
                        }
                        
                        // Ensure path starts with / for web access
                        const webPath = screenshotPath.startsWith('/') ? screenshotPath : `/${screenshotPath}`;
                        
                        const source = screenshot.source === 'recorder' ? '🎬 Recorder' : '🧪 Builder';
                        
                        return `
                        <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <div style="padding: 10px; background: #FEF2F2; border-bottom: 2px solid #FCA5A5;">
                                <strong style="color: #991B1B;">${screenshot.description || `Step ${screenshot.step || 'Unknown'}`}</strong>
                                <div style="font-size: 0.85em; color: #B91C1C; margin-top: 4px;">
                                    ${screenshot.error || 'Test failed at this step'}
                                </div>
                                <div style="font-size: 0.8em; color: #9CA3AF; margin-top: 4px;">
                                    ${source} • ${screenshot.timestamp ? new Date(screenshot.timestamp).toLocaleString() : 'No timestamp'}
                                </div>
                            </div>
                            <a href="${webPath}" target="_blank" style="display: block; position: relative; cursor: pointer;">
                                <img src="${webPath}" 
                                     alt="${screenshot.description || 'Test failure screenshot'}" 
                                     style="width: 100%; height: auto; display: block; transition: transform 0.2s;"
                                     onmouseover="this.style.transform='scale(1.05)'"
                                     onmouseout="this.style.transform='scale(1)'">
                                <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 6px 12px; border-radius: 6px; font-size: 0.85em;">
                                    🔍 Click to enlarge
                                </div>
                            </a>
                        </div>
                    `}).join('')}
                </div>
                <div style="margin-top: 15px; padding: 12px; background: white; border-radius: 6px; border-left: 3px solid #3B82F6;">
                    <strong style="color: #1E40AF;">💡 Tip:</strong>
                    <span style="color: #4B5563; font-size: 0.9em;">
                        Screenshots saved to <code style="background: #F3F4F6; padding: 2px 6px; border-radius: 4px;">execution_results/builder/</code> or 
                        <code style="background: #F3F4F6; padding: 2px 6px; border-radius: 4px;">execution_results/recorder/</code> based on test source.
                    </span>
                </div>
            </div>
        `;
        
        // Append to results container
        resultsContainer.insertAdjacentHTML('beforeend', screenshotsHtml);
        
        console.log('[Screenshots] ✅ Displayed', latestExecution.screenshots.length, 'screenshots');
        
    } catch (error) {
        console.error('[Screenshots] Error fetching screenshots:', error);
    }
}

// Show notification helper
function showNotification(message, type = 'info') {
    const colors = {
        success: '#22c55e',
        error: '#ef4444',
        info: '#6366f1'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

window.toggleTestMenu = toggleTestMenu;
window.exportSingleTest = exportSingleTest;
window.duplicateTest = duplicateTest;
window.editTestName = editTestName;
window.closeEditNameModal = closeEditNameModal;
window.saveTestName = saveTestName;
window.showNotification = showNotification;
window.openCodeModal = openCodeModal;
window.closeCodeModal = closeCodeModal;
window.executeViewedTestModal = executeViewedTestModal;
window.copyCodeModal = copyCodeModal;
window.exportCodeModal = exportCodeModal;
window.saveCodeModal = saveCodeModal;
window.updateDeleteTestsButton = updateDeleteTestsButton;
window.deleteSelectedTests = deleteSelectedTests;
window.deleteSingleTest = deleteSingleTest;
window.copyTestSuiteCode = copyTestSuiteCode;
window.exportTestSuiteCode = exportTestSuiteCode;
window.executeTestSuite = executeTestSuite;
window.clearTestSuite = clearTestSuite;
window.showDataOverrideModal = showDataOverrideModal;
window.closeDataOverrideModal = closeDataOverrideModal;
window.executeTestCase = executeTestCase;
window.executeCurrentTest = executeCurrentTest;
window.executeViewedTest = executeViewedTest;
window.editTestSuiteCode = editTestSuiteCode;
window.saveEditedTestCode = saveEditedTestCode;
window.cancelEditTestCode = cancelEditTestCode;
window.saveTestSuiteSnippet = saveTestSuiteSnippet;
window.updateDashboardFromTestSuite = updateDashboardFromTestSuite;
window.updateDashboardWithExecutionResults = updateDashboardWithExecutionResults;

// Toggle execution results visibility
function toggleExecutionResults() {
    const resultsList = document.getElementById('executionResultsList');
    const toggleIcon = document.getElementById('executionResultsToggle');
    
    if (resultsList.style.display === 'none') {
        resultsList.style.display = 'block';
        toggleIcon.textContent = '▼';
    } else {
        resultsList.style.display = 'none';
        toggleIcon.textContent = '▶';
    }
}

// Clear execution results
function clearExecutionResults() {
    const resultsList = document.getElementById('executionResultsList');
    const resultsDiv = document.getElementById('executionResults');
    
    if (confirm('Clear execution results?')) {
        resultsList.innerHTML = '';
        resultsDiv.style.display = 'none';
    }
}

window.toggleExecutionResults = toggleExecutionResults;
window.clearExecutionResults = clearExecutionResults;
