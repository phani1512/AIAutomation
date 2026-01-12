# Modular JavaScript Architecture

## Overview
The Smart Test Generator application has been restructured into a modular JavaScript architecture for better maintainability, scalability, and code organization.

## Directory Structure

```
src/web/js/
├── core/                           # Core functionality
│   ├── api.js                      # API configuration and helper functions
│   ├── navigation.js               # Page navigation and routing
│   ├── ui.js                       # UI helper functions and utilities
│   ├── dashboard.js                # Dashboard statistics and updates
│   └── authentication.js           # User authentication and session management
│
├── features/                       # Feature modules
│   ├── code-generation.js          # Code generation features
│   ├── validation.js               # Code validation features
│   ├── locator-suggestions.js      # Element locator suggestions
│   ├── action-suggestions.js       # Action suggestions
│   ├── test-recorder.js            # Test recording features
│   ├── test-suite.js               # Test suite management
│   ├── browser-control.js          # Browser initialization and control
│   ├── semantic-analysis.js        # Semantic analysis and AI suggestions
│   └── snippets.js                 # Code snippets management
│
└── app.js                          # Main application initialization
```

## Module Descriptions

### Core Modules

#### `core/api.js`
- **Purpose**: Centralized API configuration and communication
- **Key Functions**:
  - `API_URL` - API endpoint configuration
  - `authenticatedFetch()` - Helper for authenticated API calls
  - `checkConnection()` - Verify API server connection
  - `showConnectionError()` - Display connection error state

#### `core/navigation.js`
- **Purpose**: Application routing and navigation
- **Key Functions**:
  - `navigateTo(page)` - Navigate between pages
  - `toggleSidebar()` - Toggle mobile sidebar
  - `toggleDarkMode()` - Switch between light/dark themes
  - `loadDarkModePreference()` - Load theme preference
  - `switchTab(tabName)` - Switch between tabs within pages

#### `core/ui.js`
- **Purpose**: Common UI helper functions
- **Key Functions**:
  - `showLoading(show)` - Show/hide loading indicator
  - `showNotification(message)` - Display toast notifications
  - `escapeHtml(text)` - Sanitize HTML content
  - `setPrompt(text)` - Set prompt input value

#### `core/dashboard.js`
- **Purpose**: Dashboard statistics and activity tracking
- **Key Functions**:
  - `updateDashboardStats()` - Update dashboard metrics
  - `addTestResult(name, status, duration, details)` - Add test result
  - `updateRecentTestResults()` - Refresh recent test results list
  - `updateActivityTimeline()` - Update activity timeline

#### `core/authentication.js`
- **Purpose**: User authentication and session management
- **Key Functions**:
  - `checkAuthentication()` - Verify user session
  - `loginUser(event)` - Handle user login
  - `registerUser(event)` - Handle user registration
  - `logoutUser()` - Handle user logout
  - `updateUserInterface()` - Update UI with user info
  - `showUserMenu()` - Toggle user menu dropdown

### Feature Modules

#### `features/code-generation.js`
- **Purpose**: AI-powered code generation
- **Key Functions**:
  - `generateCode()` - Generate test code from prompt
  - `displayResult(text, timeMs, tokens)` - Display generated code
  - `copyResult()` - Copy code to clipboard
  - `exportCode()` - Export code to file
  - `saveToSnippets()` - Save code to snippets library

#### `features/validation.js`
- **Purpose**: Code validation and quality checks
- **Key Functions**:
  - `validateCode()` - Validate generated code
  - `performValidation(code, language)` - Run validation rules
  - `displayValidationResults(results)` - Show validation feedback

#### `features/locator-suggestions.js`
- **Purpose**: Element locator generation
- **Key Functions**:
  - `suggestLocator()` - Generate element locators
  - `displayLocatorResult(text, timeMs)` - Display locator suggestions
  - `copyLocatorResult()` - Copy locator to clipboard
  - `saveLocatorToSnippets()` - Save locator as snippet

#### `features/action-suggestions.js`
- **Purpose**: Action recommendation system
- **Key Functions**:
  - `suggestAction()` - Suggest actions for element type
  - `displayActionResult(text, timeMs)` - Display action suggestions
  - `copyActionResult()` - Copy action code
  - `saveActionToSnippets()` - Save action as snippet

#### `features/test-recorder.js`
- **Purpose**: Interactive test recording
- **Key Functions**:
  - `startRecording()` - Start recording user interactions
  - `stopRecording()` - Stop recording session
  - `startNewTestCase()` - Start a new test case
  - `generateTestFromRecording()` - Generate code from recorded actions
  - `updateRecordedActionsList()` - Update actions display
  - `editRecorderOutput()` - Edit generated recorder code
  - `saveRecorderEditedCode()` - Save edited recorder code

#### `features/test-suite.js`
- **Purpose**: Test case management
- **Key Functions**:
  - `loadTestCases()` - Load all test cases
  - `displayTestCases(sessions)` - Display test case list
  - `viewTestCase(sessionId)` - View test case code
  - `filterTestsByModule()` - Filter tests by module
  - `deleteSelectedTests()` - Delete multiple test cases
  - `deleteSingleTest(sessionId)` - Delete single test case
  - `copyTestSuiteCode()` - Copy test code
  - `exportTestSuiteCode()` - Export test code

#### `features/browser-control.js`
- **Purpose**: Browser automation control
- **Key Functions**:
  - `initializeBrowser()` - Initialize WebDriver instance
  - `executeInBrowser()` - Execute code in browser
  - `closeBrowser()` - Close browser instance
  - `displayBrowserResult(text)` - Display execution result
  - `showBrowserStatus(message)` - Show status message

#### `features/semantic-analysis.js`
- **Purpose**: AI-powered test scenario generation
- **Key Functions**:
  - `refreshSemanticSessions()` - Refresh session list
  - `loadSemanticAnalysis()` - Analyze test intent
  - `generateSuggestions()` - Generate test suggestions
  - `displaySuggestions(suggestions)` - Display suggestion cards
  - `generateTestFromSuggestionByIndex(index)` - Generate test from suggestion
  - `generateAllHighPriority()` - Bulk generate high priority tests
  - `clearSemanticAnalysis()` - Clear analysis state

#### `features/snippets.js`
- **Purpose**: Code snippet library management
- **Key Functions**:
  - `showAddSnippetModal(code)` - Show add snippet dialog
  - `saveSnippet()` - Save snippet to library
  - `loadSnippets()` - Load and display all snippets
  - `filterSnippets()` - Filter by search/language
  - `useSnippet(id)` - Load snippet into editor
  - `viewSnippet(id)` - View snippet details
  - `deleteSnippet(id)` - Delete snippet
  - `deleteSelectedSnippets()` - Bulk delete snippets
  - `detectLanguage(code)` - Auto-detect code language

## Loading Order

The modules should be loaded in this order in `index.html`:

```html
<!-- Core modules - load first -->
<script src="js/core/api.js"></script>
<script src="js/core/ui.js"></script>
<script src="js/core/navigation.js"></script>
<script src="js/core/dashboard.js"></script>
<script src="js/core/authentication.js"></script>

<!-- Feature modules -->
<script src="js/features/code-generation.js"></script>
<script src="js/features/validation.js"></script>
<script src="js/features/locator-suggestions.js"></script>
<script src="js/features/action-suggestions.js"></script>
<script src="js/features/test-recorder.js"></script>
<script src="js/features/test-suite.js"></script>
<script src="js/features/browser-control.js"></script>
<script src="js/features/semantic-analysis.js"></script>
<script src="js/features/snippets.js"></script>

<!-- Main application initialization - load last -->
<script src="js/app.js"></script>
```

## Global Variables

### Shared State
- `API_URL` - API endpoint URL
- `stats` - Dashboard statistics object
- `isRecording` - Recording state flag
- `currentSessionId` - Active recording session
- `currentSemanticSession` - Active semantic analysis session
- `pageFullyLoaded` - Page load state flag
- `loginFormReady` - Login form ready flag

## Benefits of Modular Architecture

1. **Maintainability**: Each module has a single responsibility, making code easier to understand and maintain
2. **Scalability**: New features can be added as separate modules without affecting existing code
3. **Testability**: Individual modules can be tested in isolation
4. **Reusability**: Functions can be easily reused across different features
5. **Organization**: Clear file structure makes it easy to locate specific functionality
6. **Collaboration**: Multiple developers can work on different modules simultaneously
7. **Performance**: Only load modules that are needed for specific pages (future optimization)

## Development Guidelines

1. **Keep modules focused**: Each module should handle one specific feature or responsibility
2. **Minimize global variables**: Use function parameters and return values instead
3. **Document functions**: Add JSDoc comments for complex functions
4. **Handle errors gracefully**: Use try-catch blocks and provide user feedback
5. **Follow naming conventions**: Use descriptive names for functions and variables
6. **Keep dependencies clear**: Document which modules depend on others

## Future Enhancements

1. **Module bundling**: Use a bundler (Webpack, Rollup) for production optimization
2. **ES6 modules**: Convert to ES6 import/export syntax
3. **TypeScript**: Add type safety with TypeScript
4. **Lazy loading**: Load feature modules on demand
5. **Service workers**: Add offline capability
6. **Unit tests**: Add Jest or Mocha tests for each module
