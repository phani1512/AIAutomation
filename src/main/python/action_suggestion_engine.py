"""
Enhanced Action Suggestion Engine
Provides comprehensive, context-aware action suggestions with confidence scoring
"""

class ActionSuggestionEngine:
    """
    Advanced action suggestion system with:
    - 30+ element types
    - Context-aware suggestions
    - Confidence scoring algorithm
    - Test case generation
    - Multi-language support
    """
    
    def __init__(self):
        self.action_catalog = self._initialize_action_catalog()
        self.test_patterns = self._initialize_test_patterns()
        
    def _initialize_action_catalog(self):
        """Comprehensive action catalog for all element types"""
        return {
            'button': {
                'actions': [
                    {'name': 'click', 'priority': 1, 'code': 'click()', 'description': 'Click the button'},
                    {'name': 'doubleClick', 'priority': 3, 'code': 'doubleClick()', 'description': 'Double-click the button'},
                    {'name': 'isEnabled', 'priority': 2, 'code': 'isEnabled()', 'description': 'Check if button is enabled'},
                    {'name': 'isDisplayed', 'priority': 2, 'code': 'isDisplayed()', 'description': 'Check if button is visible'},
                    {'name': 'getText', 'priority': 2, 'code': 'getText()', 'description': 'Get button text'},
                    {'name': 'getAttribute', 'priority': 3, 'code': 'getAttribute("class")', 'description': 'Get button attributes'},
                    {'name': 'waitAndClick', 'priority': 1, 'code': 'waitAndClick()', 'description': 'Wait for button and click'},
                    {'name': 'verifyText', 'priority': 2, 'code': 'verifyText("expected")', 'description': 'Verify button text'}
                ],
                'context_hints': ['submit', 'save', 'cancel', 'delete', 'close', 'next', 'previous', 'login', 'register']
            },
            
            'input': {
                'actions': [
                    {'name': 'sendKeys', 'priority': 1, 'code': 'sendKeys("text")', 'description': 'Enter text'},
                    {'name': 'clear', 'priority': 1, 'code': 'clear()', 'description': 'Clear input field'},
                    {'name': 'clearAndType', 'priority': 1, 'code': 'clear(); sendKeys("text")', 'description': 'Clear and enter text'},
                    {'name': 'getValue', 'priority': 2, 'code': 'getAttribute("value")', 'description': 'Get input value'},
                    {'name': 'getPlaceholder', 'priority': 3, 'code': 'getAttribute("placeholder")', 'description': 'Get placeholder text'},
                    {'name': 'isEnabled', 'priority': 2, 'code': 'isEnabled()', 'description': 'Check if input is enabled'},
                    {'name': 'verifyValue', 'priority': 2, 'code': 'verifyValue("expected")', 'description': 'Verify input value'},
                    {'name': 'pressEnter', 'priority': 2, 'code': 'sendKeys(Keys.ENTER)', 'description': 'Press Enter key'},
                    {'name': 'typeSlowly', 'priority': 3, 'code': 'typeWithDelay("text", 100)', 'description': 'Type with delay'},
                    {'name': 'pasteText', 'priority': 3, 'code': 'sendKeys(Keys.CONTROL, "v")', 'description': 'Paste from clipboard'}
                ],
                'context_hints': ['email', 'password', 'username', 'search', 'name', 'phone', 'address', 'date']
            },
            
            'select': {
                'actions': [
                    {'name': 'selectByText', 'priority': 1, 'code': 'selectByVisibleText("Option")', 'description': 'Select by visible text'},
                    {'name': 'selectByValue', 'priority': 1, 'code': 'selectByValue("value")', 'description': 'Select by value attribute'},
                    {'name': 'selectByIndex', 'priority': 2, 'code': 'selectByIndex(0)', 'description': 'Select by index'},
                    {'name': 'getOptions', 'priority': 2, 'code': 'getOptions()', 'description': 'Get all options'},
                    {'name': 'getSelectedOption', 'priority': 2, 'code': 'getFirstSelectedOption()', 'description': 'Get selected option'},
                    {'name': 'deselectAll', 'priority': 3, 'code': 'deselectAll()', 'description': 'Deselect all (multi-select)'},
                    {'name': 'verifySelected', 'priority': 2, 'code': 'verifySelected("Option")', 'description': 'Verify selected option'}
                ],
                'context_hints': ['country', 'state', 'city', 'category', 'status', 'type', 'role']
            },
            
            'checkbox': {
                'actions': [
                    {'name': 'check', 'priority': 1, 'code': 'if(!isSelected()) click()', 'description': 'Check the checkbox'},
                    {'name': 'uncheck', 'priority': 1, 'code': 'if(isSelected()) click()', 'description': 'Uncheck the checkbox'},
                    {'name': 'toggle', 'priority': 1, 'code': 'click()', 'description': 'Toggle checkbox state'},
                    {'name': 'isSelected', 'priority': 2, 'code': 'isSelected()', 'description': 'Check if checkbox is selected'},
                    {'name': 'verifyChecked', 'priority': 2, 'code': 'verifyChecked(true)', 'description': 'Verify checkbox is checked'},
                    {'name': 'verifyUnchecked', 'priority': 2, 'code': 'verifyChecked(false)', 'description': 'Verify checkbox is unchecked'}
                ],
                'context_hints': ['agree', 'terms', 'remember', 'subscribe', 'accept']
            },
            
            'radio': {
                'actions': [
                    {'name': 'select', 'priority': 1, 'code': 'click()', 'description': 'Select radio button'},
                    {'name': 'isSelected', 'priority': 2, 'code': 'isSelected()', 'description': 'Check if radio is selected'},
                    {'name': 'verifySelected', 'priority': 2, 'code': 'verifySelected(true)', 'description': 'Verify radio is selected'},
                    {'name': 'getGroupOptions', 'priority': 3, 'code': 'findElements(By.name("group"))', 'description': 'Get all radio options in group'}
                ],
                'context_hints': ['gender', 'payment', 'shipping', 'choice', 'option']
            },
            
            'link': {
                'actions': [
                    {'name': 'click', 'priority': 1, 'code': 'click()', 'description': 'Click the link'},
                    {'name': 'getHref', 'priority': 2, 'code': 'getAttribute("href")', 'description': 'Get link URL'},
                    {'name': 'getText', 'priority': 2, 'code': 'getText()', 'description': 'Get link text'},
                    {'name': 'openInNewTab', 'priority': 3, 'code': 'sendKeys(Keys.CONTROL, Keys.RETURN)', 'description': 'Open in new tab'},
                    {'name': 'rightClick', 'priority': 3, 'code': 'contextClick()', 'description': 'Right-click the link'},
                    {'name': 'verifyHref', 'priority': 2, 'code': 'verifyHref("url")', 'description': 'Verify link URL'}
                ],
                'context_hints': ['logout', 'profile', 'settings', 'help', 'about', 'contact']
            },
            
            'textarea': {
                'actions': [
                    {'name': 'sendKeys', 'priority': 1, 'code': 'sendKeys("text")', 'description': 'Enter text'},
                    {'name': 'clear', 'priority': 1, 'code': 'clear()', 'description': 'Clear textarea'},
                    {'name': 'clearAndType', 'priority': 1, 'code': 'clear(); sendKeys("text")', 'description': 'Clear and enter text'},
                    {'name': 'getValue', 'priority': 2, 'code': 'getAttribute("value")', 'description': 'Get textarea value'},
                    {'name': 'verifyValue', 'priority': 2, 'code': 'verifyValue("expected")', 'description': 'Verify textarea content'},
                    {'name': 'appendText', 'priority': 3, 'code': 'sendKeys("additional text")', 'description': 'Append text without clearing'}
                ],
                'context_hints': ['comment', 'description', 'message', 'notes', 'feedback']
            },
            
            'image': {
                'actions': [
                    {'name': 'click', 'priority': 1, 'code': 'click()', 'description': 'Click the image'},
                    {'name': 'getSrc', 'priority': 2, 'code': 'getAttribute("src")', 'description': 'Get image source URL'},
                    {'name': 'getAlt', 'priority': 2, 'code': 'getAttribute("alt")', 'description': 'Get alt text'},
                    {'name': 'isDisplayed', 'priority': 2, 'code': 'isDisplayed()', 'description': 'Check if image is visible'},
                    {'name': 'verifyLoaded', 'priority': 3, 'code': 'verifyImageLoaded()', 'description': 'Verify image loaded successfully'}
                ],
                'context_hints': ['logo', 'avatar', 'thumbnail', 'banner', 'icon']
            },
            
            'table': {
                'actions': [
                    {'name': 'getRowCount', 'priority': 1, 'code': 'findElements(By.tagName("tr")).size()', 'description': 'Get row count'},
                    {'name': 'getColumnCount', 'priority': 2, 'code': 'findElements(By.tagName("th")).size()', 'description': 'Get column count'},
                    {'name': 'getCellValue', 'priority': 1, 'code': 'getCellValue(row, col)', 'description': 'Get cell value'},
                    {'name': 'getRowData', 'priority': 2, 'code': 'getRowData(rowIndex)', 'description': 'Get all data from row'},
                    {'name': 'getColumnData', 'priority': 2, 'code': 'getColumnData(colIndex)', 'description': 'Get all data from column'},
                    {'name': 'searchInTable', 'priority': 2, 'code': 'searchInTable("text")', 'description': 'Search for text in table'},
                    {'name': 'sortColumn', 'priority': 3, 'code': 'click() on header', 'description': 'Sort by column'},
                    {'name': 'verifyRowExists', 'priority': 2, 'code': 'verifyRowExists("data")', 'description': 'Verify row with data exists'}
                ],
                'context_hints': ['data', 'list', 'grid', 'results', 'records']
            },
            
            'modal': {
                'actions': [
                    {'name': 'isDisplayed', 'priority': 1, 'code': 'isDisplayed()', 'description': 'Check if modal is visible'},
                    {'name': 'close', 'priority': 1, 'code': 'click() on close button', 'description': 'Close the modal'},
                    {'name': 'getTitle', 'priority': 2, 'code': 'getText() from title', 'description': 'Get modal title'},
                    {'name': 'getContent', 'priority': 2, 'code': 'getText() from body', 'description': 'Get modal content'},
                    {'name': 'clickOverlay', 'priority': 3, 'code': 'click() on overlay', 'description': 'Click modal overlay to close'},
                    {'name': 'verifyOpened', 'priority': 2, 'code': 'verifyModalOpened()', 'description': 'Verify modal is opened'}
                ],
                'context_hints': ['dialog', 'popup', 'alert', 'confirm', 'prompt']
            },
            
            'form': {
                'actions': [
                    {'name': 'submit', 'priority': 1, 'code': 'submit()', 'description': 'Submit the form'},
                    {'name': 'fillForm', 'priority': 1, 'code': 'fillForm(data)', 'description': 'Fill all form fields'},
                    {'name': 'reset', 'priority': 3, 'code': 'click() reset button', 'description': 'Reset form fields'},
                    {'name': 'validateForm', 'priority': 2, 'code': 'validateAllFields()', 'description': 'Validate all form fields'},
                    {'name': 'getFormData', 'priority': 3, 'code': 'getAllFieldValues()', 'description': 'Get all form data'}
                ],
                'context_hints': ['login', 'register', 'contact', 'profile', 'settings']
            },
            
            'div': {
                'actions': [
                    {'name': 'click', 'priority': 1, 'code': 'click()', 'description': 'Click the div element'},
                    {'name': 'getText', 'priority': 1, 'code': 'getText()', 'description': 'Get div text content'},
                    {'name': 'isDisplayed', 'priority': 2, 'code': 'isDisplayed()', 'description': 'Check if div is visible'},
                    {'name': 'getAttribute', 'priority': 2, 'code': 'getAttribute("class")', 'description': 'Get div attributes'},
                    {'name': 'verifyText', 'priority': 2, 'code': 'verifyText("expected")', 'description': 'Verify div text'},
                    {'name': 'hover', 'priority': 3, 'code': 'moveToElement()', 'description': 'Hover over div'}
                ],
                'context_hints': ['card', 'panel', 'container', 'section', 'widget']
            },
            
            'span': {
                'actions': [
                    {'name': 'getText', 'priority': 1, 'code': 'getText()', 'description': 'Get span text'},
                    {'name': 'click', 'priority': 2, 'code': 'click()', 'description': 'Click the span'},
                    {'name': 'getAttribute', 'priority': 2, 'code': 'getAttribute("class")', 'description': 'Get span attributes'},
                    {'name': 'verifyText', 'priority': 2, 'code': 'verifyText("expected")', 'description': 'Verify span text'},
                    {'name': 'isDisplayed', 'priority': 2, 'code': 'isDisplayed()', 'description': 'Check if span is visible'}
                ],
                'context_hints': ['label', 'badge', 'tag', 'error', 'message']
            },
            
            'file': {
                'actions': [
                    {'name': 'uploadFile', 'priority': 1, 'code': 'sendKeys("/path/to/file")', 'description': 'Upload a file'},
                    {'name': 'uploadMultiple', 'priority': 2, 'code': 'sendKeys("file1\\nfile2")', 'description': 'Upload multiple files'},
                    {'name': 'clearFiles', 'priority': 3, 'code': 'clear()', 'description': 'Clear selected files'},
                    {'name': 'verifyFileSelected', 'priority': 2, 'code': 'verifyFileSelected()', 'description': 'Verify file is selected'}
                ],
                'context_hints': ['upload', 'attach', 'document', 'image', 'avatar']
            },
            
            'date': {
                'actions': [
                    {'name': 'selectDate', 'priority': 1, 'code': 'sendKeys("2024-01-01")', 'description': 'Select a date'},
                    {'name': 'clear', 'priority': 2, 'code': 'clear()', 'description': 'Clear date field'},
                    {'name': 'getDate', 'priority': 2, 'code': 'getAttribute("value")', 'description': 'Get selected date'},
                    {'name': 'openCalendar', 'priority': 3, 'code': 'click()', 'description': 'Open date picker calendar'},
                    {'name': 'verifyDate', 'priority': 2, 'code': 'verifyDate("2024-01-01")', 'description': 'Verify selected date'}
                ],
                'context_hints': ['birthday', 'start', 'end', 'created', 'updated']
            },
            
            'alert': {
                'actions': [
                    {'name': 'accept', 'priority': 1, 'code': 'switchTo().alert().accept()', 'description': 'Accept/OK alert'},
                    {'name': 'dismiss', 'priority': 1, 'code': 'switchTo().alert().dismiss()', 'description': 'Dismiss/Cancel alert'},
                    {'name': 'getText', 'priority': 2, 'code': 'switchTo().alert().getText()', 'description': 'Get alert text'},
                    {'name': 'sendKeys', 'priority': 2, 'code': 'switchTo().alert().sendKeys("text")', 'description': 'Enter text in prompt'},
                    {'name': 'verifyAlertText', 'priority': 2, 'code': 'verifyAlertText("expected")', 'description': 'Verify alert message'}
                ],
                'context_hints': ['confirm', 'prompt', 'warning', 'error', 'success']
            },
            
            'dropdown': {
                'actions': [
                    {'name': 'open', 'priority': 1, 'code': 'click()', 'description': 'Open dropdown menu'},
                    {'name': 'selectOption', 'priority': 1, 'code': 'click() on option', 'description': 'Select dropdown option'},
                    {'name': 'search', 'priority': 2, 'code': 'sendKeys("search text")', 'description': 'Search in dropdown'},
                    {'name': 'getOptions', 'priority': 2, 'code': 'getAllOptions()', 'description': 'Get all options'},
                    {'name': 'verifyOptionExists', 'priority': 2, 'code': 'verifyOptionExists("option")', 'description': 'Verify option exists'}
                ],
                'context_hints': ['menu', 'choices', 'options', 'filter']
            },
            
            'slider': {
                'actions': [
                    {'name': 'setValue', 'priority': 1, 'code': 'dragAndDrop(offset)', 'description': 'Set slider value'},
                    {'name': 'getValue', 'priority': 2, 'code': 'getAttribute("value")', 'description': 'Get slider value'},
                    {'name': 'setToMin', 'priority': 3, 'code': 'sendKeys(Keys.HOME)', 'description': 'Set to minimum'},
                    {'name': 'setToMax', 'priority': 3, 'code': 'sendKeys(Keys.END)', 'description': 'Set to maximum'},
                    {'name': 'verifyValue', 'priority': 2, 'code': 'verifyValue(expected)', 'description': 'Verify slider value'}
                ],
                'context_hints': ['range', 'volume', 'price', 'rating', 'progress']
            },
            
            'tab': {
                'actions': [
                    {'name': 'switchTo', 'priority': 1, 'code': 'click()', 'description': 'Switch to tab'},
                    {'name': 'isActive', 'priority': 2, 'code': 'hasClass("active")', 'description': 'Check if tab is active'},
                    {'name': 'getText', 'priority': 2, 'code': 'getText()', 'description': 'Get tab text'},
                    {'name': 'verifyActive', 'priority': 2, 'code': 'verifyTabActive()', 'description': 'Verify tab is active'}
                ],
                'context_hints': ['navigation', 'panel', 'section', 'page']
            },
            
            'tooltip': {
                'actions': [
                    {'name': 'hover', 'priority': 1, 'code': 'moveToElement()', 'description': 'Hover to show tooltip'},
                    {'name': 'getText', 'priority': 1, 'code': 'getText() from tooltip', 'description': 'Get tooltip text'},
                    {'name': 'isDisplayed', 'priority': 2, 'code': 'isDisplayed()', 'description': 'Check if tooltip is visible'},
                    {'name': 'verifyText', 'priority': 2, 'code': 'verifyTooltipText("expected")', 'description': 'Verify tooltip content'}
                ],
                'context_hints': ['help', 'info', 'hint', 'description']
            },
            
            'menu': {
                'actions': [
                    {'name': 'open', 'priority': 1, 'code': 'click()', 'description': 'Open menu'},
                    {'name': 'selectItem', 'priority': 1, 'code': 'click() on menu item', 'description': 'Select menu item'},
                    {'name': 'hover', 'priority': 2, 'code': 'moveToElement()', 'description': 'Hover to open submenu'},
                    {'name': 'getItems', 'priority': 2, 'code': 'getAllMenuItems()', 'description': 'Get all menu items'},
                    {'name': 'verifyItemExists', 'priority': 2, 'code': 'verifyMenuItemExists("item")', 'description': 'Verify menu item exists'}
                ],
                'context_hints': ['navigation', 'actions', 'options', 'context']
            },
            
            'iframe': {
                'actions': [
                    {'name': 'switchTo', 'priority': 1, 'code': 'switchTo().frame(element)', 'description': 'Switch to iframe'},
                    {'name': 'switchBack', 'priority': 1, 'code': 'switchTo().defaultContent()', 'description': 'Switch back to main content'},
                    {'name': 'isDisplayed', 'priority': 2, 'code': 'isDisplayed()', 'description': 'Check if iframe is visible'},
                    {'name': 'getSrc', 'priority': 2, 'code': 'getAttribute("src")', 'description': 'Get iframe source URL'}
                ],
                'context_hints': ['embed', 'video', 'widget', 'content']
            },
            
            'scroll': {
                'actions': [
                    {'name': 'scrollIntoView', 'priority': 1, 'code': 'scrollIntoView()', 'description': 'Scroll element into view'},
                    {'name': 'scrollToTop', 'priority': 2, 'code': 'scrollTo(0, 0)', 'description': 'Scroll to page top'},
                    {'name': 'scrollToBottom', 'priority': 2, 'code': 'scrollToBottom()', 'description': 'Scroll to page bottom'},
                    {'name': 'scrollBy', 'priority': 3, 'code': 'scrollBy(x, y)', 'description': 'Scroll by offset'},
                    {'name': 'pageDown', 'priority': 3, 'code': 'sendKeys(Keys.PAGE_DOWN)', 'description': 'Page down'}
                ],
                'context_hints': ['navigation', 'content', 'list', 'feed']
            },
            
            'toast': {
                'actions': [
                    {'name': 'getText', 'priority': 1, 'code': 'getText()', 'description': 'Get toast message text'},
                    {'name': 'waitForToast', 'priority': 1, 'code': 'waitFor Toast()', 'description': 'Wait for toast to appear'},
                    {'name': 'close', 'priority': 2, 'code': 'click() on close', 'description': 'Close the toast'},
                    {'name': 'verifyText', 'priority': 1, 'code': 'verifyToastText("expected")', 'description': 'Verify toast message'},
                    {'name': 'verifyType', 'priority': 2, 'code': 'verifyToastType("success")', 'description': 'Verify toast type (success/error/warning)'}
                ],
                'context_hints': ['notification', 'message', 'alert', 'snackbar', 'banner']
            },
            
            'list': {
                'actions': [
                    {'name': 'getItemCount', 'priority': 1, 'code': 'findElements().size()', 'description': 'Get list item count'},
                    {'name': 'getItem', 'priority': 1, 'code': 'getItem(index)', 'description': 'Get specific list item'},
                    {'name': 'getAllItems', 'priority': 2, 'code': 'getAllItems()', 'description': 'Get all list items'},
                    {'name': 'selectItem', 'priority': 1, 'code': 'click() on item', 'description': 'Select list item'},
                    {'name': 'searchItem', 'priority': 2, 'code': 'searchInList("text")', 'description': 'Search for item in list'},
                    {'name': 'verifyItemExists', 'priority': 2, 'code': 'verifyItemExists("text")', 'description': 'Verify item exists in list'}
                ],
                'context_hints': ['menu', 'options', 'results', 'items', 'records']
            },
            
            'generic': {
                'actions': [
                    {'name': 'click', 'priority': 1, 'code': 'click()', 'description': 'Click the element'},
                    {'name': 'getText', 'priority': 1, 'code': 'getText()', 'description': 'Get element text'},
                    {'name': 'isDisplayed', 'priority': 2, 'code': 'isDisplayed()', 'description': 'Check if element is visible'},
                    {'name': 'isEnabled', 'priority': 2, 'code': 'isEnabled()', 'description': 'Check if element is enabled'},
                    {'name': 'getAttribute', 'priority': 2, 'code': 'getAttribute("attr")', 'description': 'Get element attribute'},
                    {'name': 'hover', 'priority': 3, 'code': 'moveToElement()', 'description': 'Hover over element'},
                    {'name': 'verifyPresent', 'priority': 2, 'code': 'verifyElementPresent()', 'description': 'Verify element present'},
                    {'name': 'verifyText', 'priority': 2, 'code': 'verifyText("expected")', 'description': 'Verify element text'}
                ],
                'context_hints': []
            }
        }
    
    def _initialize_test_patterns(self):
        """Test case patterns for different scenarios"""
        return {
            'positive': {
                'description': 'Valid/Happy path testing',
                'scenarios': [
                    'Test with valid data',
                    'Test expected successful flow',
                    'Verify expected results',
                    'Test with typical user input'
                ]
            },
            'negative': {
                'description': 'Invalid/Error path testing',
                'scenarios': [
                    'Test with empty/null data',
                    'Test with invalid data',
                    'Test with boundary values',
                    'Test with special characters',
                    'Test error handling'
                ]
            },
            'boundary': {
                'description': 'Boundary value testing',
                'scenarios': [
                    'Test minimum value',
                    'Test maximum value',
                    'Test just below minimum',
                    'Test just above maximum'
                ]
            },
            'security': {
                'description': 'Security testing',
                'scenarios': [
                    'Test SQL injection',
                    'Test XSS attacks',
                    'Test authentication',
                    'Test authorization',
                    'Test encryption'
                ]
            },
            'performance': {
                'description': 'Performance testing',
                'scenarios': [
                    'Test response time',
                    'Test with large data sets',
                    'Test concurrent users',
                    'Test timeout scenarios'
                ]
            },
            'ui': {
                'description': 'UI/UX testing',
                'scenarios': [
                    'Test responsiveness',
                    'Test cross-browser compatibility',
                    'Test mobile view',
                    'Test accessibility',
                    'Test visual elements'
                ]
            }
        }
    
    def calculate_confidence(self, element_type, context, actions):
        """Calculate confidence score based on element type, context, and action relevance"""
        confidence = 0.0
        
        # Base confidence from element type match
        if element_type.lower() in self.action_catalog:
            confidence += 40  # Strong match
        else:
            confidence += 15  # Generic fallback
        
        # Context relevance boost
        if context:
            context_lower = context.lower()
            element_data = self.action_catalog.get(element_type.lower(), self.action_catalog['generic'])
            context_hints = element_data.get('context_hints', [])
            
            # Check if any context hint matches
            matching_hints = [hint for hint in context_hints if hint in context_lower]
            if matching_hints:
                confidence += 30  # Context matches expected use case
            else:
                confidence += 10  # Context provided but no direct match
        
        # Action completeness boost
        if len(actions) >= 5:
            confidence += 20  # Comprehensive action list
        elif len(actions) >= 3:
            confidence += 15  # Good action coverage
        else:
            confidence += 5  # Limited actions
        
        # Priority action presence boost
        priority_1_count = sum(1 for a in actions if a.get('priority') == 1)
        if priority_1_count >= 2:
            confidence += 10  # Multiple high-priority actions
        
        return min(confidence, 100)  # Cap at 100%
    
    def suggest_action(self, element_type, context="", language="java"):
        """Generate comprehensive action suggestions with confidence scoring"""
        
        # Get element-specific actions or fallback to generic
        element_lower = element_type.lower()
        if element_lower in self.action_catalog:
            element_data = self.action_catalog[element_lower]
        else:
            element_data = self.action_catalog['generic']
        
        actions = element_data['actions']
        
        # Sort by priority
        sorted_actions = sorted(actions, key=lambda x: x['priority'])
        
        # Calculate confidence
        confidence = self.calculate_confidence(element_type, context, sorted_actions)
        
        # Generate test scenarios
        test_scenarios = self.generate_test_scenarios(element_type, context)
        
        # Generate code samples
        code_samples = self.generate_code_samples(element_type, context, sorted_actions[:3], language)
        
        return {
            'element_type': element_type,
            'context': context,
            'confidence': confidence,
            'confidence_level': self._get_confidence_level(confidence),
            'recommended_actions': [
                {
                    'name': action['name'],
                    'code': action['code'],
                    'description': action['description'],
                    'priority': action['priority']
                }
                for action in sorted_actions
            ],
            'top_actions': [action['name'] for action in sorted_actions[:5]],
            'test_scenarios': test_scenarios,
            'code_samples': code_samples,
            'context_hints': element_data.get('context_hints', []),
            'total_actions': len(sorted_actions)
        }
    
    def _get_confidence_level(self, confidence):
        """Convert confidence score to level"""
        if confidence >= 80:
            return 'High'
        elif confidence >= 60:
            return 'Medium-High'
        elif confidence >= 40:
            return 'Medium'
        elif confidence >= 20:
            return 'Low-Medium'
        else:
            return 'Low'
    
    def generate_test_scenarios(self, element_type, context):
        """Generate relevant test scenarios"""
        scenarios = []
        
        # Add positive test cases
        scenarios.append({
            'category': 'Positive Testing',
            'cases': [
                f'Test {element_type} with valid {context or "data"}',
                f'Verify {element_type} displays correctly',
                f'Test {element_type} interaction produces expected result'
            ]
        })
        
        # Add negative test cases
        scenarios.append({
            'category': 'Negative Testing',
            'cases': [
                f'Test {element_type} with invalid {context or "data"}',
                f'Test {element_type} when disabled',
                f'Test {element_type} with boundary values'
            ]
        })
        
        # Add UI/UX test cases
        scenarios.append({
            'category': 'UI/UX Testing',
            'cases': [
                f'Verify {element_type} is visible and accessible',
                f'Test {element_type} responsiveness',
                f'Verify {element_type} styling and appearance'
            ]
        })
        
        # Element-specific scenarios
        if element_type.lower() in ['input', 'textarea']:
            scenarios.append({
                'category': 'Input Validation',
                'cases': [
                    'Test with special characters',
                    'Test with maximum length',
                    'Test with SQL injection patterns',
                    'Test with XSS patterns'
                ]
            })
        
        elif element_type.lower() == 'button':
            scenarios.append({
                'category': 'State Testing',
                'cases': [
                    'Test button in enabled state',
                    'Test button in disabled state',
                    'Test button during loading',
                    'Test double-click prevention'
                ]
            })
        
        elif element_type.lower() in ['select', 'dropdown']:
            scenarios.append({
                'category': 'Option Testing',
                'cases': [
                    'Verify all options are present',
                    'Test selecting each option',
                    'Test default selection',
                    'Test keyboard navigation'
                ]
            })
        
        return scenarios
    
    def generate_code_samples(self, element_type, context, actions, language="java"):
        """
        Generate code samples in specified language.
        Always generates all three languages for flexibility in UI.
        """
        samples = {}
        
        # Generate all three languages regardless of selection
        # This allows users to switch languages in the UI without re-requesting
        samples['java'] = self._generate_java_code(element_type, context, actions)
        samples['python'] = self._generate_python_code(element_type, context, actions)
        samples['javascript'] = self._generate_js_code(element_type, context, actions)
        
        return samples
    
    def _generate_java_code(self, element_type, context, actions):
        """Generate Java Selenium code"""
        code_lines = [
            "// Enhanced action suggestions for " + element_type,
            "WebElement element = driver.findElement(By.id(\"elementId\"));",
            ""
        ]
        
        for action in actions:
            code_lines.append(f"// {action['description']}")
            if action['name'] == 'sendKeys':
                code_lines.append(f"element.{action['code']};")
            elif action['name'] == 'click':
                code_lines.append("element.click();")
            elif action['name'] == 'clear':
                code_lines.append("element.clear();")
            else:
                code_lines.append(f"element.{action['code']};")
            code_lines.append("")
        
        # Add wait example
        code_lines.extend([
            "// Wait for element",
            "WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));",
            "wait.until(ExpectedConditions.elementToBeClickable(element));"
        ])
        
        return "\n".join(code_lines)
    
    def _generate_python_code(self, element_type, context, actions):
        """Generate Python Selenium code"""
        code_lines = [
            f"# Enhanced action suggestions for {element_type}",
            'element = driver.find_element(By.ID, "elementId")',
            ""
        ]
        
        for action in actions:
            code_lines.append(f"# {action['description']}")
            if action['name'] == 'sendKeys':
                code_lines.append('element.send_keys("text")')
            elif action['name'] == 'click':
                code_lines.append("element.click()")
            elif action['name'] == 'clear':
                code_lines.append("element.clear()")
            else:
                code_lines.append(f"element.{action['code'].replace('()', '()')}")
            code_lines.append("")
        
        # Add wait example
        code_lines.extend([
            "# Wait for element",
            "wait = WebDriverWait(driver, 10)",
            "wait.until(EC.element_to_be_clickable(element))"
        ])
        
        return "\n".join(code_lines)
    
    def _generate_js_code(self, element_type, context, actions):
        """Generate JavaScript Playwright code"""
        code_lines = [
            f"// Enhanced action suggestions for {element_type}",
            'const element = await page.locator("#elementId");',
            ""
        ]
        
        for action in actions:
            code_lines.append(f"// {action['description']}")
            if action['name'] == 'sendKeys':
                code_lines.append('await element.fill("text");')
            elif action['name'] == 'click':
                code_lines.append("await element.click();")
            elif action['name'] == 'clear':
                code_lines.append("await element.clear();")
            else:
                code_lines.append(f"await element.{action['code']};")
            code_lines.append("")
        
        # Add wait example
        code_lines.extend([
            "// Wait for element",
            "await element.waitFor({ state: 'visible' });"
        ])
        
        return "\n".join(code_lines)
