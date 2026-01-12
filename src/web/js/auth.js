// User Authentication and Account Management

// Helper function for authenticated API calls
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('session_token');
    
    if (!token) {
        // Redirect to login page instead of showing modal
        showLoginPage();
        throw new Error('Authentication required');
    }
    
    options.headers = options.headers || {};
    options.headers['Authorization'] = token;
    options.credentials = 'include';
    
    try {
        const response = await fetch(url, options);
        
        if (response.status === 401) {
            localStorage.removeItem('session_token');
            localStorage.removeItem('username');
            // Redirect to login page instead of showing modal
            showLoginPage();
            throw new Error('Session expired. Please login again.');
        }
        
        return response;
    } catch (error) {
        console.error('Authenticated fetch error:', error);
        throw error;
    }
}

function getCurrentUser() {
    const userData = localStorage.getItem('currentUser');
    return userData ? JSON.parse(userData) : null;
}

function getAllUsers() {
    const users = localStorage.getItem('users');
    return users ? JSON.parse(users) : [];
}

function saveUser(user) {
    let users = getAllUsers();
    const existingIndex = users.findIndex(u => u.email === user.email);
    
    if (existingIndex >= 0) {
        users[existingIndex] = user;
    } else {
        users.push(user);
    }
    
    localStorage.setItem('users', JSON.stringify(users));
}

function showLoginModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">🔐 Login Required</h3>
            <div class="form-group">
                <label for="loginUsername">Username:</label>
                <input type="text" id="loginUsername" placeholder="Enter username">
            </div>
            <div class="form-group">
                <label for="loginPassword">Password:</label>
                <input type="password" id="loginPassword" placeholder="Enter password">
            </div>
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button class="btn" onclick="loginUser()" style="flex: 1;">Login</button>
                <button class="btn" onclick="document.querySelector('.modal-overlay').remove()" style="flex: 1; background: var(--error);">Cancel</button>
            </div>
            <p style="text-align: center; margin-top: 15px; color: var(--text-secondary);">
                Don't have an account? <a href="#" onclick="event.preventDefault(); document.querySelector('.modal-overlay').remove(); showRegisterModal();" style="color: var(--primary);">Register</a>
            </p>
        </div>
    `;
    document.body.appendChild(modal);
    
    document.getElementById('loginPassword').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') loginUser();
    });
}

function showRegisterModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">📝 Register Account</h3>
            <div class="form-group">
                <label for="registerUsername">Username:</label>
                <input type="text" id="registerUsername" placeholder="Choose a username">
            </div>
            <div class="form-group">
                <label for="registerEmail">Email:</label>
                <input type="email" id="registerEmail" placeholder="Enter email">
            </div>
            <div class="form-group">
                <label for="registerPassword">Password:</label>
                <input type="password" id="registerPassword" placeholder="Choose a password">
            </div>
            <div class="form-group">
                <label for="registerConfirmPassword">Confirm Password:</label>
                <input type="password" id="registerConfirmPassword" placeholder="Confirm password">
            </div>
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button class="btn" onclick="registerUser()" style="flex: 1;">Register</button>
                <button class="btn" onclick="document.querySelector('.modal-overlay').remove()" style="flex: 1; background: var(--error);">Cancel</button>
            </div>
            <p style="text-align: center; margin-top: 15px; color: var(--text-secondary);">
                Already have an account? <a href="#" onclick="event.preventDefault(); document.querySelector('.modal-overlay').remove(); showLoginModal();" style="color: var(--primary);">Login</a>
            </p>
        </div>
    `;
    document.body.appendChild(modal);
}

async function loginUser() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        alert('Please enter both username and password');
        return;
    }
    
    try {
        const response = await fetch(`${window.API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem('session_token', data.session_token);
            localStorage.setItem('username', username);
            document.querySelector('.modal-overlay').remove();
            updateUserInterface();
            showNotification('✅ Login successful!');
        } else {
            alert('❌ Login failed: ' + (data.error || 'Invalid credentials'));
        }
    } catch (error) {
        alert('❌ Error during login: ' + error.message);
    }
}

async function registerUser() {
    const username = document.getElementById('registerUsername').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    
    if (!username || !password) {
        alert('Please fill in all required fields');
        return;
    }
    
    if (username.length < 3) {
        alert('Username must be at least 3 characters long');
        return;
    }
    
    if (password.length < 6) {
        alert('Password must be at least 6 characters long');
        return;
    }
    
    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }
    
    try {
        const response = await fetch(`${window.API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.querySelector('.modal-overlay').remove();
            showNotification('✅ Registration successful! Please login.');
            showLoginModal();
        } else {
            alert('❌ Registration failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Error during registration: ' + error.message);
    }
}

async function logoutUser() {
    try {
        await fetch(`${window.API_URL}/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': localStorage.getItem('session_token')
            }
        });
        
        localStorage.removeItem('session_token');
        localStorage.removeItem('username');
        localStorage.removeItem('currentUser');
        
        showNotification('👋 Logged out successfully');
        updateUserInterface();
        showLoginPage();
    } catch (error) {
        console.error('Logout error:', error);
    }
}

function updateUserInterface() {
    const username = localStorage.getItem('username');
    const loginBtn = document.getElementById('loginBtn');
    const userProfileSection = document.getElementById('userProfileSection');
    
    if (username) {
        loginBtn.style.display = 'none';
        userProfileSection.style.display = 'block';
        
        const userName = document.getElementById('userName');
        const userAvatar = document.getElementById('userAvatar');
        
        userName.textContent = username;
        userAvatar.textContent = username.charAt(0).toUpperCase();
    } else {
        loginBtn.style.display = 'block';
        userProfileSection.style.display = 'none';
    }
}

function showUserMenu() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 300px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">👤 User Menu</h3>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <button class="btn" onclick="document.querySelector('.modal-overlay').remove();">
                    ⚙️ Settings
                </button>
                <button class="btn" onclick="document.querySelector('.modal-overlay').remove(); showSavedPrompts();">
                    💾 Saved Prompts
                </button>
                <button class="btn" onclick="document.querySelector('.modal-overlay').remove(); logoutUser();" style="background: var(--error);">
                    🚪 Logout
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function checkAuthentication() {
    const token = localStorage.getItem('session_token');
    console.log('[AUTH] Checking authentication, token:', token ? 'exists' : 'none');
    
    if (token) {
        showMainApp();
    } else {
        showLoginPage();
    }
}

function showLoginPage() {
    console.log('[UI] Showing login page');
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('appContainer').style.display = 'none';
}

function showMainApp() {
    console.log('[UI] Showing main app');
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('appContainer').style.display = 'flex';
    updateUserInterface();
}

function showRegisterPage() {
    const loginPage = document.getElementById('loginPage');
    const loginContainer = loginPage.querySelector('.login-container');
    
    loginContainer.innerHTML = `
        <div class="login-header">
            <div class="login-logo">🤖</div>
            <h2 class="login-title">Create Account</h2>
            <p class="login-subtitle">Join AI Test Automation Studio</p>
        </div>
        <form class="login-form" onsubmit="handleRegister(event)">
            <div class="login-input-group">
                <label class="login-label" for="registerPageUsername">Username</label>
                <input class="login-input" type="text" id="registerPageUsername" placeholder="Enter username" required>
            </div>
            <div class="login-input-group">
                <label class="login-label" for="registerPageEmail">Email</label>
                <input class="login-input" type="email" id="registerPageEmail" placeholder="Enter email" required>
            </div>
            <div class="login-input-group">
                <label class="login-label" for="registerPagePassword">Password</label>
                <input class="login-input" type="password" id="registerPagePassword" placeholder="Create password" required>
            </div>
            <div class="login-input-group">
                <label class="login-label" for="registerPageConfirmPassword">Confirm Password</label>
                <input class="login-input" type="password" id="registerPageConfirmPassword" placeholder="Confirm password" required>
            </div>
            <button type="submit" class="login-button">Create Account</button>
        </form>
        <div class="login-footer">
            Already have an account? <a href="#" class="login-link" onclick="event.preventDefault(); showLoginPageForm();">Sign in</a>
        </div>
    `;
}

function showLoginPageForm() {
    const loginPage = document.getElementById('loginPage');
    const loginContainer = loginPage.querySelector('.login-container');
    
    loginContainer.innerHTML = `
        <div class="login-header">
            <div class="login-logo">🤖</div>
            <h2 class="login-title">Welcome Back</h2>
            <p class="login-subtitle">Sign in to AI Test Automation Studio</p>
        </div>
        <form class="login-form" onsubmit="handleLogin(event)">
            <div class="login-input-group">
                <label class="login-label" for="loginPageUsername">Username</label>
                <input class="login-input" type="text" id="loginPageUsername" placeholder="Enter your username" required>
            </div>
            <div class="login-input-group">
                <label class="login-label" for="loginPagePassword">Password</label>
                <input class="login-input" type="password" id="loginPagePassword" placeholder="Enter your password" required>
            </div>
            <button type="submit" class="login-button" onclick="window.userClickedLogin = true">Sign In</button>
        </form>
        <div class="login-footer">
            Don't have an account? <a href="#" class="login-link" onclick="event.preventDefault(); showRegisterPage();">Create one</a>
        </div>
    `;
    
    setTimeout(() => {
        window.loginFormReady = true;
        console.log('[LOGIN] Form ready for input');
    }, 500);
}

// Global state variables (will be exposed to window later)
let userClickedLogin = false;
let pageFullyLoaded = false;
let loginFormReady = true;  // Start as true since form exists in initial HTML

async function handleLogin(event) {
    event.preventDefault();
    
    console.log('[LOGIN] Form submitted. Ready:', window.loginFormReady, 'UserClicked:', window.userClickedLogin);
    console.log('[LOGIN] API_URL:', API_URL);
    console.log('[LOGIN] Form element IDs:', document.getElementById('loginPageUsername'), document.getElementById('loginPagePassword'));
    
    const errorDiv = document.getElementById('loginError');
    if (errorDiv) errorDiv.style.display = 'none';
    
    if (!window.loginFormReady) {
        console.log('[LOGIN] Form not ready yet, preventing submit');
        return;
    }
    
    if (!window.userClickedLogin) {
        console.log('[LOGIN] Auto-submit prevented - user must click button');
        return;
    }
    
    window.userClickedLogin = false;
    
    const username = document.getElementById('loginPageUsername').value.trim();
    const password = document.getElementById('loginPagePassword').value;
    
    console.log('[LOGIN] Username:', username, 'Password length:', password?.length);
    
    if (!username || !password) {
        const msg = 'Please enter both username and password';
        if (errorDiv) {
            errorDiv.textContent = msg;
            errorDiv.style.display = 'block';
        }
        alert(msg);
        return;
    }
    
    try {
        console.log('[LOGIN] Fetching:', `${window.API_URL}/auth/login`);
        const response = await fetch(`${window.API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        console.log('[LOGIN] Response status:', response.status);
        const data = await response.json();
        console.log('[LOGIN] Response data:', data);
        
        if (data.success) {
            localStorage.setItem('session_token', data.session_token);
            localStorage.setItem('username', username);
            console.log('[LOGIN] Showing main app...');
            showMainApp();
            if (typeof showNotification === 'function') {
                showNotification('✅ Login successful!');
            }
        } else {
            const msg = '❌ Login failed: ' + (data.error || 'Invalid credentials');
            if (errorDiv) {
                errorDiv.textContent = msg;
                errorDiv.style.display = 'block';
            }
            console.error('[LOGIN]', msg);
            alert(msg);
        }
    } catch (error) {
        const msg = '❌ Error during login: ' + error.message;
        if (errorDiv) {
            errorDiv.textContent = msg;
            errorDiv.style.display = 'block';
        }
        console.error('[LOGIN] Exception:', error);
        alert(msg);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerPageUsername').value.trim();
    const email = document.getElementById('registerPageEmail').value.trim();
    const password = document.getElementById('registerPagePassword').value;
    const confirmPassword = document.getElementById('registerPageConfirmPassword').value;
    
    if (!username || !password) {
        alert('Please fill in all required fields');
        return;
    }
    
    if (username.length < 3) {
        alert('Username must be at least 3 characters long');
        return;
    }
    
    if (password.length < 6) {
        alert('Password must be at least 6 characters long');
        return;
    }
    
    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }
    
    try {
        const response = await fetch(`${window.API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Registration successful! Please login.');
            showLoginPageForm();
        } else {
            alert('❌ Registration failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Error during registration: ' + error.message);
    }
}

// Expose functions to global scope for HTML onclick handlers
window.authenticatedFetch = authenticatedFetch;
window.getCurrentUser = getCurrentUser;
window.getAllUsers = getAllUsers;
window.saveUser = saveUser;
window.showLoginModal = showLoginModal;
window.showRegisterModal = showRegisterModal;
window.showUserMenu = showUserMenu;
window.loginUser = loginUser;
window.registerUser = registerUser;
window.logoutUser = logoutUser;
window.updateUserInterface = updateUserInterface;
window.checkAuthentication = checkAuthentication;
window.showRegisterPage = showRegisterPage;
window.showLoginPageForm = showLoginPageForm;
window.showMainApp = showMainApp;
window.showLoginPage = showLoginPage;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;

// Global state variables - initialize on window object
if (typeof window.userClickedLogin === 'undefined') {
    window.userClickedLogin = false;
}
if (typeof window.pageFullyLoaded === 'undefined') {
    window.pageFullyLoaded = false;
}
if (typeof window.loginFormReady === 'undefined') {
    window.loginFormReady = true;  // Set to true initially since form is already in HTML
}

