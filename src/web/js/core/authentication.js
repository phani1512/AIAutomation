// Authentication and User Management

let pageFullyLoaded = false;
let loginFormReady = false;

// Check authentication on page load
async function checkAuthentication() {
    const token = localStorage.getItem('session_token');
    console.log('[AUTH] Checking authentication, token:', token ? 'exists' : 'none');
    
    if (token) {
        try {
            const response = await fetch(`${API_URL}/auth/check`, {
                headers: { 'Authorization': token },
                credentials: 'include'
            });
            
            const data = await response.json();
            console.log('[AUTH] Server response:', data);
            
            if (data.authenticated) {
                console.log('[AUTH] User authenticated, showing main app');
                localStorage.setItem('username', data.username);
                localStorage.setItem('email', data.email || '');
                showMainApp();
            } else {
                // Session expired
                console.log('[AUTH] Session expired, showing login');
                localStorage.removeItem('session_token');
                localStorage.removeItem('username');
                localStorage.removeItem('email');
                showLoginPage();
            }
        } catch (error) {
            console.error('[AUTH] Check error:', error);
            showLoginPage();
        }
    } else {
        console.log('[AUTH] No token found, showing login page');
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
    
    // Load dashboard page and initialize stats after successful login
    if (typeof navigateTo === 'function') {
        setTimeout(() => {
            navigateTo('dashboard');
        }, 100);
    }
}

// Make variables available globally
window.pageFullyLoaded = pageFullyLoaded;
window.loginFormReady = loginFormReady;
window.userClickedLogin = false;

async function handleLogin(event) {
    event.preventDefault();
    
    console.log('[LOGIN] Form submitted. Ready:', window.loginFormReady, 'UserClicked:', window.userClickedLogin);
    
    // Prevent auto-submit - require explicit user action
    if (!window.loginFormReady) {
        console.log('[LOGIN] Form not ready yet, ignoring submit');
        return;
    }
    
    if (!window.userClickedLogin) {
        console.log('[LOGIN] Form auto-submitted by browser, ignoring');
        return;
    }
    
    window.userClickedLogin = false; // Reset flag
    
    const username = document.getElementById('loginPageUsername').value.trim();
    const password = document.getElementById('loginPagePassword').value;
    
    if (!username || !password) {
        alert('Please enter both username and password');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem('session_token', data.session_token);
            localStorage.setItem('username', data.username);
            localStorage.setItem('email', data.email || '');
            
            showMainApp();
            showNotification('✅ Welcome back, ' + data.username + '!');
        } else {
            alert(data.error || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed. Please check if the server is running.');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerPageUsername').value;
    const email = document.getElementById('registerPageEmail').value;
    const password = document.getElementById('registerPagePassword').value;
    const confirmPassword = document.getElementById('registerPageConfirmPassword').value;
    
    if (!username || !password) {
        showNotification('❌ Username and password are required');
        return;
    }
    
    if (password !== confirmPassword) {
        showNotification('❌ Passwords do not match');
        return;
    }
    
    if (password.length < 6) {
        showNotification('❌ Password must be at least 6 characters');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Registration successful! Please login.');
            showLoginPageForm();
        } else {
            showNotification('❌ ' + (data.message || 'Registration failed'));
        }
    } catch (error) {
        showNotification('❌ Registration error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function showLoginPageForm() {
    const loginPage = document.getElementById('loginPage');
    const loginContainer = loginPage.querySelector('.login-container');
    
    loginContainer.innerHTML = `
        <div class="login-header">
            <div class="login-logo">🤖</div>
            <h1 class="login-title">Welcome Back</h1>
            <p class="login-subtitle">Sign in to access your testing workspace</p>
        </div>
        
        <form id="loginForm" class="login-form" onsubmit="handleLogin(event)">
            <div class="login-input-group">
                <label class="login-label" for="loginPageUsername">Username</label>
                <input 
                    type="text" 
                    id="loginPageUsername" 
                    class="login-input" 
                    placeholder="Enter your username"
                    required
                    autocomplete="username"
                />
            </div>
            
            <div class="login-input-group">
                <label class="login-label" for="loginPagePassword">Password</label>
                <input 
                    type="password" 
                    id="loginPagePassword" 
                    class="login-input" 
                    placeholder="Enter your password"
                    required
                    autocomplete="current-password"
                />
            </div>
            
            <button type="submit" class="login-button">
                🔐 Sign In
            </button>
        </form>
        
        <div class="login-footer">
            Don't have an account? 
            <a class="login-link" onclick="showRegisterPage()">Create one</a>
        </div>
    `;
}

function showRegisterPage() {
    const loginPage = document.getElementById('loginPage');
    const loginContainer = loginPage.querySelector('.login-container');
    
    loginContainer.innerHTML = `
        <div class="login-header">
            <div class="login-logo">🤖</div>
            <h1 class="login-title">Create Account</h1>
            <p class="login-subtitle">Join AI Test Automation Studio</p>
        </div>
        
        <form id="registerForm" class="login-form" onsubmit="handleRegister(event)">
            <div class="login-input-group">
                <label class="login-label" for="registerPageUsername">Username</label>
                <input 
                    type="text" 
                    id="registerPageUsername" 
                    class="login-input" 
                    placeholder="Choose a username (min 3 characters)"
                    required
                    autocomplete="username"
                />
            </div>
            
            <div class="login-input-group">
                <label class="login-label" for="registerPageEmail">Email (optional)</label>
                <input 
                    type="email" 
                    id="registerPageEmail" 
                    class="login-input" 
                    placeholder="your.email@example.com"
                    autocomplete="email"
                />
            </div>
            
            <div class="login-input-group">
                <label class="login-label" for="registerPagePassword">Password</label>
                <input 
                    type="password" 
                    id="registerPagePassword" 
                    class="login-input" 
                    placeholder="Create a password (min 6 characters)"
                    required
                    autocomplete="new-password"
                />
            </div>
            
            <div class="login-input-group">
                <label class="login-label" for="registerPageConfirmPassword">Confirm Password</label>
                <input 
                    type="password" 
                    id="registerPageConfirmPassword" 
                    class="login-input" 
                    placeholder="Confirm your password"
                    required
                    autocomplete="new-password"
                />
            </div>
            
            <button type="submit" class="login-button">
                ✨ Create Account
            </button>
        </form>
        
        <div class="login-footer">
            Already have an account? 
            <a class="login-link" onclick="showLoginPageForm()">Sign in</a>
        </div>
    `;
}

function showLoginModal() {
    const loginPage = document.getElementById('loginPage');
    const appContainer = document.getElementById('appContainer');
    if (loginPage) {
        loginPage.classList.add('show');
    }
    if (appContainer) {
        appContainer.classList.add('hidden');
    }
    showLoginPageForm();
}

function updateUserInterface() {
    const username = localStorage.getItem('username');
    const email = localStorage.getItem('email');
    
    const userNameElement = document.getElementById('userName');
    const userEmailElement = document.getElementById('userEmail');
    const userInitialsElement = document.getElementById('userInitials');
    
    if (userNameElement) userNameElement.textContent = username || 'User';
    if (userEmailElement) userEmailElement.textContent = email || 'user@example.com';
    if (userInitialsElement && username) {
        userInitialsElement.textContent = username.charAt(0).toUpperCase();
    }
}

function showUserMenu() {
    const menu = document.getElementById('userMenu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

function logoutUser() {
    if (!confirm('Are you sure you want to logout?')) {
        return;
    }
    
    localStorage.removeItem('session_token');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    
    document.getElementById('loginPage').classList.add('show');
    document.getElementById('appContainer').classList.add('hidden');
    
    const userMenu = document.getElementById('userMenu');
    if (userMenu) userMenu.style.display = 'none';
    
    showNotification('👋 Logged out successfully');
    showLoginPageForm();
}

// Expose functions to global window object for inline onclick handlers
window.checkAuthentication = checkAuthentication;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.showLoginPageForm = showLoginPageForm;
window.showRegisterPage = showRegisterPage;
window.showLoginModal = showLoginModal;
window.updateUserInterface = updateUserInterface;
window.showUserMenu = showUserMenu;
window.logoutUser = logoutUser;

// Close user menu when clicking outside
document.addEventListener('click', function(event) {
    const userProfile = document.querySelector('.user-profile');
    const userMenu = document.getElementById('userMenu');
    
    if (userProfile && userMenu && !userProfile.contains(event.target)) {
        userMenu.style.display = 'none';
    }
});