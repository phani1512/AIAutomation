/**
 * Field-Aware Semantic Suggestions Module
 * 
 * Fetches and displays field-specific boundary test suggestions.
 * Modular design - imported by test-suite.js when needed.
 */

class FieldAwareSuggestionsManager {
    constructor() {
        this.currentSuggestions = null;
        this.currentTestId = null;
    }

    /**
     * Fetch field-aware suggestions from backend
     */
    async fetchSuggestions(testCaseId) {
        try {
            console.log('[FIELD-AWARE] Fetching suggestions for:', testCaseId);
            
            const response = await fetch(`${API_URL}/ml/field-aware-suggestions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ test_case_id: testCaseId })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                console.error('[FIELD-AWARE] Failed to fetch:', data.error);
                return null;
            }
            
            console.log('[FIELD-AWARE] ✓ Fetched', data.scenarios_count, 'scenarios');
            console.log('[FIELD-AWARE] Input fields found:', data.metadata.input_fields_found);
            
            this.currentSuggestions = data;
            this.currentTestId = testCaseId;
            
            return data;
            
        } catch (error) {
            console.error('[FIELD-AWARE] Error fetching suggestions:', error);
            return null;
        }
    }

    /**
     * Get suggestions for a specific field by index
     */
    getSuggestionsForField(fieldIndex) {
        if (!this.currentSuggestions || !this.currentSuggestions.scenarios) {
            return null;
        }

        // Get field suggestions from first scenario (all scenarios have same field_suggestions)
        const scenario = this.currentSuggestions.scenarios[0];
        if (!scenario || !scenario.field_suggestions) {
            return null;
        }

        return scenario.field_suggestions[fieldIndex];
    }

    /**
     * Render field suggestions as HTML
     */
    renderFieldSuggestions(fieldIndex, inputElementId, testCaseId = null) {
        const fieldSuggestions = this.getSuggestionsForField(fieldIndex);
        
        if (!fieldSuggestions || !fieldSuggestions.suggestions) {
            return '';
        }

        const fieldType = fieldSuggestions.field_type;
        const suggestions = fieldSuggestions.suggestions;
        const currentTestId = testCaseId || this.currentTestId;

        // Detect prioritized category from scenarios
        let prioritizedCategory = null;
        if (this.currentSuggestions && this.currentSuggestions.scenarios) {
            const prioritizedScenario = this.currentSuggestions.scenarios.find(s => s.is_prioritized);
            if (prioritizedScenario) {
                prioritizedCategory = prioritizedScenario.type;
                console.log('[FIELD-AWARE] Prioritized category:', prioritizedCategory);
            }
        }

        // Group suggestions by category
        const byCategory = {};
        suggestions.forEach(sugg => {
            const category = sugg.category || 'other';
            if (!byCategory[category]) {
                byCategory[category] = [];
            }
            byCategory[category].push(sugg);
        });

        // Sort categories - prioritized first
        let categoryOrder = Object.keys(byCategory);
        if (prioritizedCategory && byCategory[prioritizedCategory]) {
            categoryOrder = [prioritizedCategory, ...categoryOrder.filter(c => c !== prioritizedCategory)];
        }

        // Define category colors and icons
        const categoryStyles = {
            'invalid': { color: '#EF4444', icon: '❌', label: 'Invalid' },
            'invalid_format': { color: '#EF4444', icon: '❌', label: 'Invalid Format' },
            'weak': { color: '#F59E0B', icon: '⚠️', label: 'Weak' },
            'security': { color: '#DC2626', icon: '🔒', label: 'Security' },
            'boundary': { color: '#3B82F6', icon: '📏', label: 'Boundary' },
            'edge_case': { color: '#8B5CF6', icon: '🎯', label: 'Edge Case' },
            'valid': { color: '#10B981', icon: '✅', label: 'Valid' },
            'i18n': { color: '#EC4899', icon: '🌍', label: 'I18N' }
        };

        let html = `
            <div style="
                background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(99, 102, 241, 0.05) 100%);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 8px;
                padding: 16px;
                margin-top: 12px;
            ">
                <div style="
                    font-weight: 600;
                    font-size: 14px;
                    color: #7C3AED;
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    💡 <span style="text-transform: capitalize;">${fieldType}</span> Field Test Data
                    <span style="
                        font-size: 11px;
                        font-weight: 500;
                        background: rgba(124, 58, 237, 0.1);
                        color: #7C3AED;
                        padding: 2px 8px;
                        border-radius: 12px;
                    ">${suggestions.length} suggestions</span>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 6px;">
        `;

        // Add prioritized category notice if applicable
        if (prioritizedCategory) {
            const prioritizedStyle = categoryStyles[prioritizedCategory] || {};
            html += `
                <div style="
                    padding: 8px 12px;
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(99, 102, 241, 0.08) 100%);
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    border-radius: 6px;
                    margin-bottom: 8px;
                ">
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; color: #7C3AED; font-weight: 600;">
                        <span>⭐</span>
                        <span>Recommended for this test: ${prioritizedCategory.replace('_', ' ').toUpperCase()} ${prioritizedStyle.icon || ''}</span>
                    </div>
                </div>
            `;
        }

        // Render suggestions grouped by category (in sorted order)
        categoryOrder.forEach(category => {
            const categoryData = byCategory[category];
            const style = categoryStyles[category] || { color: '#6B7280', icon: '•', label: category };
            const isPrioritized = (category === prioritizedCategory);

            categoryData.forEach((sugg, idx) => {
                const suggestionId = `sugg-${fieldIndex}-${category}-${idx}`;
                const scenarioKey = `${fieldType}_${category}_${idx}`;
                const escapedValue = String(sugg.value).replace(/'/g, "\\'").replace(/"/g, '&quot;');
                const escapedDescription = String(sugg.description || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                
                // Highlight prioritized suggestions with special styling
                const bgColor = isPrioritized ? 'rgba(139, 92, 246, 0.05)' : 'white';
                const borderColor = isPrioritized ? 'rgba(139, 92, 246, 0.25)' : 'rgba(0,0,0,0.08)';
                const hoverBg = 'rgba(124, 58, 237, 0.1)';
                const hoverBorder = 'rgba(124, 58, 237, 0.4)';
                
                html += `
                    <div 
                        id="${suggestionId}"
                        style="
                            display: flex;
                            align-items: center;
                            gap: 10px;
                            padding: 8px 12px;
                            background: ${bgColor};
                            border: 1.5px solid ${borderColor};
                            border-radius: 6px;
                            cursor: pointer;
                            transition: all 0.2s;
                            ${isPrioritized ? 'box-shadow: 0 1px 3px rgba(139, 92, 246, 0.1);' : ''}
                        "
                        onmouseover="this.style.background='${hoverBg}'; this.style.borderColor='${hoverBorder}';"
                        onmouseout="this.style.background='${bgColor}'; this.style.borderColor='${borderColor}';"
                        onclick="fieldAwareSuggestions.applySuggestion('${inputElementId}', '${escapedValue}', '${suggestionId}', ${fieldIndex}, '${fieldType}', '${category}', '${escapedDescription}')"
                    >
                        ${isPrioritized ? '<span style="font-size: 14px;">⭐</span>' : ''}
                        <span style="font-size: 16px;">${style.icon}</span>
                        <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <code style="
                                    background: rgba(139, 92, 246, 0.08);
                                    color: #7C3AED;
                                    padding: 3px 8px;
                                    border-radius: 4px;
                                    font-size: 13px;
                                    font-family: 'Courier New', monospace;
                                    font-weight: 600;
                                ">${this.escapeHtml(sugg.value)}</code>
                                <span style="
                                    font-size: 12px;
                                    color: #6B7280;
                                ">${sugg.description}</span>
                            </div>
                            ${currentTestId && window.feedbackManager ? `
                                <div onclick="event.stopPropagation();">
                                    ${window.feedbackManager.renderRatingButtons(suggestionId, scenarioKey, currentTestId)}
                                </div>
                            ` : ''}
                        </div>
                        <span style="
                            font-size: 10px;
                            font-weight: 500;
                            color: ${style.color};
                            background: ${style.color}15;
                            padding: 2px 6px;
                            border-radius: 10px;
                            text-transform: uppercase;
                            flex-shrink: 0;
                        ">${style.label}</span>
                    </div>
                `;
            });
        });

        html += `
                </div>
            </div>
        `;

        return html;
    }

    /**
     * Apply suggestion to input field
     */
    applySuggestion(inputElementId, value, suggestionElementId, fieldIndex = null, fieldType = null, category = null, description = null) {
        console.log('[FIELD-AWARE] Applying suggestion:', value, 'to', inputElementId);
        
        const inputElement = document.getElementById(inputElementId);
        if (inputElement) {
            inputElement.value = value;
            
            // Record feedback for this suggestion usage
            if (this.currentTestId && fieldIndex !== null && fieldType && category) {
                this.recordSuggestionUsage(fieldIndex, fieldType, category, value, description);
            }
            
            // Visual feedback
            const suggestionElement = document.getElementById(suggestionElementId);
            if (suggestionElement) {
                suggestionElement.style.background = 'rgba(16, 185, 129, 0.1)';
                suggestionElement.style.borderColor = 'rgba(16, 185, 129, 0.5)';
                
                setTimeout(() => {
                    suggestionElement.style.background = 'white';
                    suggestionElement.style.borderColor = 'rgba(0,0,0,0.08)';
                }, 1500);
            }
        } else {
            console.error('[FIELD-AWARE] Input element not found:', inputElementId);
        }
    }

    /**
     * Record suggestion usage for feedback/analytics
     */
    async recordSuggestionUsage(fieldIndex, fieldType, category, value, description) {
        try {
            console.log('[FIELD-AWARE] Recording suggestion usage feedback');
            
            const response = await fetch(`${API_URL}/ml/feedback/field-suggestion-used`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    test_case_id: this.currentTestId,
                    field_index: fieldIndex,
                    field_type: fieldType,
                    category: category,
                    value: value || '',
                    description: description || ''
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('[FIELD-AWARE] ✓ Suggestion usage recorded');
            } else {
                console.warn('[FIELD-AWARE] Failed to record usage:', data.error);
            }
            
        } catch (error) {
            console.error('[FIELD-AWARE] Error recording suggestion usage:', error);
            // Don't fail the main operation if feedback fails
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Clear cached suggestions
     */
    clear() {
        this.currentSuggestions = null;
        this.currentTestId = null;
    }
}

// Global instance
window.fieldAwareSuggestions = new FieldAwareSuggestionsManager();

console.log('[FIELD-AWARE] Module loaded');
