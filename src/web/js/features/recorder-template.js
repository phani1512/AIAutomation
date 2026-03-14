/**
 * RecorderTemplate - Template System
 * Pre-defined templates for common test patterns
 * Version: 1.0
 */

class RecorderTemplate {
    constructor() {
        this.templates = this.initializeTemplates();
    }

    /**
     * Initialize built-in templates
     */
    initializeTemplates() {
        return {
            login: {
                id: 'login',
                name: 'Login Flow',
                description: 'Standard login form with username/email and password',
                icon: '🔐',
                category: 'authentication',
                steps: [
                    { type: 'navigate', description: 'Navigate to login page' },
                    { type: 'input', target: 'username', description: 'Enter username/email', required: true },
                    { type: 'input', target: 'password', description: 'Enter password', required: true },
                    { type: 'click', target: 'submit', description: 'Click login button', required: true },
                    { type: 'verify', target: 'success', description: 'Verify successful login', required: false }
                ],
                variables: ['username', 'password'],
                estimatedTime: '10-15 seconds'
            },

            formFill: {
                id: 'formFill',
                name: 'Form Fill',
                description: 'Complete a multi-field form with various input types',
                icon: '📝',
                category: 'forms',
                steps: [
                    { type: 'navigate', description: 'Navigate to form page' },
                    { type: 'input', target: 'text_fields', description: 'Fill text fields', required: true },
                    { type: 'select', target: 'dropdowns', description: 'Select dropdown values', required: false },
                    { type: 'click', target: 'checkboxes', description: 'Check/uncheck boxes', required: false },
                    { type: 'click', target: 'radio', description: 'Select radio buttons', required: false },
                    { type: 'click', target: 'submit', description: 'Submit form', required: true },
                    { type: 'verify', target: 'confirmation', description: 'Verify submission', required: false }
                ],
                variables: [],
                estimatedTime: '20-30 seconds'
            },

            search: {
                id: 'search',
                name: 'Search Flow',
                description: 'Search for content and verify results',
                icon: '🔍',
                category: 'navigation',
                steps: [
                    { type: 'navigate', description: 'Navigate to search page' },
                    { type: 'input', target: 'search_box', description: 'Enter search query', required: true },
                    { type: 'click', target: 'search_button', description: 'Click search button', required: true },
                    { type: 'verify', target: 'results', description: 'Verify search results appear', required: true },
                    { type: 'click', target: 'result_item', description: 'Click on result', required: false }
                ],
                variables: ['searchQuery'],
                estimatedTime: '10-15 seconds'
            },

            registration: {
                id: 'registration',
                name: 'User Registration',
                description: 'Complete user registration with validation',
                icon: '📋',
                category: 'authentication',
                steps: [
                    { type: 'navigate', description: 'Navigate to registration page' },
                    { type: 'input', target: 'email', description: 'Enter email', required: true },
                    { type: 'input', target: 'username', description: 'Enter username', required: true },
                    { type: 'input', target: 'password', description: 'Enter password', required: true },
                    { type: 'input', target: 'confirm_password', description: 'Confirm password', required: true },
                    { type: 'click', target: 'terms', description: 'Accept terms', required: false },
                    { type: 'click', target: 'submit', description: 'Submit registration', required: true },
                    { type: 'verify', target: 'success', description: 'Verify registration success', required: true }
                ],
                variables: ['email', 'username', 'password'],
                estimatedTime: '20-30 seconds'
            },

            checkout: {
                id: 'checkout',
                name: 'E-commerce Checkout',
                description: 'Complete checkout process with payment',
                icon: '🛒',
                category: 'ecommerce',
                steps: [
                    { type: 'navigate', description: 'Navigate to cart' },
                    { type: 'click', target: 'checkout', description: 'Start checkout', required: true },
                    { type: 'input', target: 'shipping_info', description: 'Enter shipping info', required: true },
                    { type: 'click', target: 'continue', description: 'Continue to payment', required: true },
                    { type: 'input', target: 'payment_info', description: 'Enter payment details', required: true },
                    { type: 'click', target: 'place_order', description: 'Place order', required: true },
                    { type: 'verify', target: 'confirmation', description: 'Verify order confirmation', required: true }
                ],
                variables: ['shippingAddress', 'paymentMethod'],
                estimatedTime: '30-45 seconds'
            },

            navigation: {
                id: 'navigation',
                name: 'Multi-page Navigation',
                description: 'Navigate through multiple pages',
                icon: '🗺️',
                category: 'navigation',
                steps: [
                    { type: 'navigate', description: 'Navigate to home page' },
                    { type: 'click', target: 'menu_item_1', description: 'Click first menu item', required: true },
                    { type: 'verify', target: 'page_1', description: 'Verify page loaded', required: true },
                    { type: 'click', target: 'menu_item_2', description: 'Click second menu item', required: false },
                    { type: 'verify', target: 'page_2', description: 'Verify page loaded', required: false }
                ],
                variables: [],
                estimatedTime: '15-20 seconds'
            },

            crud: {
                id: 'crud',
                name: 'CRUD Operations',
                description: 'Create, Read, Update, Delete operations',
                icon: '⚙️',
                category: 'data',
                steps: [
                    { type: 'navigate', description: 'Navigate to data page' },
                    { type: 'click', target: 'create', description: 'Click create button', required: true },
                    { type: 'input', target: 'fields', description: 'Fill in data fields', required: true },
                    { type: 'click', target: 'save', description: 'Save new item', required: true },
                    { type: 'verify', target: 'created', description: 'Verify item created', required: true },
                    { type: 'click', target: 'edit', description: 'Click edit', required: false },
                    { type: 'input', target: 'update_fields', description: 'Update fields', required: false },
                    { type: 'click', target: 'update', description: 'Save updates', required: false },
                    { type: 'click', target: 'delete', description: 'Delete item', required: false },
                    { type: 'verify', target: 'deleted', description: 'Verify deletion', required: false }
                ],
                variables: [],
                estimatedTime: '30-40 seconds'
            },

            fileUpload: {
                id: 'fileUpload',
                name: 'File Upload',
                description: 'Upload and verify file',
                icon: '📎',
                category: 'forms',
                steps: [
                    { type: 'navigate', description: 'Navigate to upload page' },
                    { type: 'click', target: 'upload_button', description: 'Click upload button', required: true },
                    { type: 'input', target: 'file_input', description: 'Select file', required: true },
                    { type: 'click', target: 'submit', description: 'Submit upload', required: true },
                    { type: 'verify', target: 'success', description: 'Verify upload success', required: true }
                ],
                variables: ['filePath'],
                estimatedTime: '10-15 seconds'
            },

            modal: {
                id: 'modal',
                name: 'Modal Interaction',
                description: 'Open, interact with, and close modals',
                icon: '🪟',
                category: 'ui',
                steps: [
                    { type: 'click', target: 'open_modal', description: 'Open modal', required: true },
                    { type: 'verify', target: 'modal_visible', description: 'Verify modal opened', required: true },
                    { type: 'input', target: 'modal_fields', description: 'Fill modal fields', required: false },
                    { type: 'click', target: 'modal_action', description: 'Perform action', required: true },
                    { type: 'click', target: 'close_modal', description: 'Close modal', required: false },
                    { type: 'verify', target: 'modal_closed', description: 'Verify modal closed', required: true }
                ],
                variables: [],
                estimatedTime: '10-15 seconds'
            },

            table: {
                id: 'table',
                name: 'Table Operations',
                description: 'Sort, filter, and interact with tables',
                icon: '📊',
                category: 'data',
                steps: [
                    { type: 'navigate', description: 'Navigate to table page' },
                    { type: 'click', target: 'sort_column', description: 'Click column header to sort', required: false },
                    { type: 'input', target: 'filter', description: 'Enter filter criteria', required: false },
                    { type: 'verify', target: 'filtered_results', description: 'Verify filtered data', required: false },
                    { type: 'click', target: 'row_action', description: 'Click row action', required: true },
                    { type: 'verify', target: 'action_result', description: 'Verify action result', required: true }
                ],
                variables: ['filterText'],
                estimatedTime: '15-20 seconds'
            }
        };
    }

    /**
     * Get all templates
     */
    getAllTemplates() {
        return Object.values(this.templates);
    }

    /**
     * Get template by ID
     */
    getTemplate(templateId) {
        return this.templates[templateId] || null;
    }

    /**
     * Get templates by category
     */
    getTemplatesByCategory(category) {
        return Object.values(this.templates).filter(t => t.category === category);
    }

    /**
     * Get all categories
     */
    getCategories() {
        const categories = new Set();
        Object.values(this.templates).forEach(t => categories.add(t.category));
        return Array.from(categories);
    }

    /**
     * Detect which template matches recorded actions
     */
    detectTemplate(actions) {
        if (!actions || actions.length === 0) {
            return null;
        }

        const scores = {};
        
        // Score each template based on action pattern match
        for (const [id, template] of Object.entries(this.templates)) {
            scores[id] = this.calculateMatchScore(actions, template);
        }

        // Find best match
        const bestMatch = Object.entries(scores)
            .sort((a, b) => b[1] - a[1])[0];

        // Return if score is significant (> 50%)
        if (bestMatch[1] > 0.5) {
            return {
                template: this.templates[bestMatch[0]],
                confidence: bestMatch[1],
                matchedSteps: this.getMatchedSteps(actions, this.templates[bestMatch[0]])
            };
        }

        return null;
    }

    /**
     * Calculate match score between actions and template
     */
    calculateMatchScore(actions, template) {
        let score = 0;
        const templateSteps = template.steps;
        let actionIndex = 0;

        for (const step of templateSteps) {
            // Look for matching action type in remaining actions
            const found = actions.slice(actionIndex).find(a => a.type === step.type);
            
            if (found) {
                score += step.required ? 2 : 1;
                actionIndex = actions.indexOf(found) + 1;
            } else if (step.required) {
                score -= 2; // Penalty for missing required step
            }
        }

        // Normalize score
        const maxScore = templateSteps.reduce((sum, s) => sum + (s.required ? 2 : 1), 0);
        return maxScore > 0 ? Math.max(0, score / maxScore) : 0;
    }

    /**
     * Get matched steps between actions and template
     */
    getMatchedSteps(actions, template) {
        const matched = [];
        let actionIndex = 0;

        for (const step of template.steps) {
            const found = actions.slice(actionIndex).find(a => a.type === step.type);
            
            if (found) {
                matched.push({
                    templateStep: step,
                    action: found,
                    matched: true
                });
                actionIndex = actions.indexOf(found) + 1;
            } else {
                matched.push({
                    templateStep: step,
                    action: null,
                    matched: false
                });
            }
        }

        return matched;
    }

    /**
     * Apply template to start recording
     */
    applyTemplate(templateId) {
        const template = this.getTemplate(templateId);
        
        if (!template) {
            throw new Error(`Template not found: ${templateId}`);
        }

        console.log(`[RecorderTemplate] Applying template: ${template.name}`);
        
        return {
            template: template,
            guidance: this.generateGuidance(template),
            nextStep: template.steps[0]
        };
    }

    /**
     * Generate step-by-step guidance for template
     */
    generateGuidance(template) {
        return template.steps.map((step, index) => ({
            stepNumber: index + 1,
            type: step.type,
            description: step.description,
            required: step.required,
            status: 'pending' // pending, completed, skipped
        }));
    }

    /**
     * Validate recorded actions against template
     */
    validateAgainstTemplate(actions, templateId) {
        const template = this.getTemplate(templateId);
        
        if (!template) {
            throw new Error(`Template not found: ${templateId}`);
        }

        const validation = {
            valid: true,
            missingRequired: [],
            extraActions: [],
            warnings: []
        };

        // Check for missing required steps
        for (const step of template.steps) {
            if (step.required) {
                const found = actions.find(a => a.type === step.type);
                if (!found) {
                    validation.valid = false;
                    validation.missingRequired.push(step);
                }
            }
        }

        // Check for unexpected actions
        const templateTypes = new Set(template.steps.map(s => s.type));
        for (const action of actions) {
            if (!templateTypes.has(action.type)) {
                validation.extraActions.push(action);
                validation.warnings.push(`Unexpected action: ${action.type}`);
            }
        }

        return validation;
    }

    /**
     * Create custom template
     */
    createCustomTemplate(config) {
        if (!config.id || !config.name || !config.steps) {
            throw new Error('Template must have id, name, and steps');
        }

        const template = {
            id: config.id,
            name: config.name,
            description: config.description || '',
            icon: config.icon || '📝',
            category: config.category || 'custom',
            steps: config.steps,
            variables: config.variables || [],
            estimatedTime: config.estimatedTime || 'Unknown',
            custom: true
        };

        this.templates[config.id] = template;
        console.log(`[RecorderTemplate] Created custom template: ${template.name}`);
        
        return template;
    }

    /**
     * Export template as JSON
     */
    exportTemplate(templateId) {
        const template = this.getTemplate(templateId);
        
        if (!template) {
            throw new Error(`Template not found: ${templateId}`);
        }

        return JSON.stringify(template, null, 2);
    }

    /**
     * Import template from JSON
     */
    importTemplate(json) {
        try {
            const template = JSON.parse(json);
            return this.createCustomTemplate(template);
        } catch (error) {
            throw new Error(`Failed to import template: ${error.message}`);
        }
    }

    /**
     * Get template statistics
     */
    getStatistics() {
        const templates = Object.values(this.templates);
        
        return {
            total: templates.length,
            byCategory: this.groupByCategory(templates),
            custom: templates.filter(t => t.custom).length,
            builtin: templates.filter(t => !t.custom).length
        };
    }

    /**
     * Group templates by category
     */
    groupByCategory(templates) {
        const grouped = {};
        
        for (const template of templates) {
            if (!grouped[template.category]) {
                grouped[template.category] = [];
            }
            grouped[template.category].push(template);
        }
        
        return grouped;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RecorderTemplate;
}

// Create global instance
if (typeof window !== 'undefined') {
    window.RecorderTemplate = RecorderTemplate;
    window.recorderTemplates = new RecorderTemplate();
}
