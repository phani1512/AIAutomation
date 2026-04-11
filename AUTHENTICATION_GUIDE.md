# 🔐 Authentication System Documentation

## Overview
The application now requires users to register and login before using any features. This implements session-based authentication with secure password hashing and multi-user support.

## Features

### ✨ Core Features
- **User Registration**: New users must create an account with username and password
- **User Login**: Secure login with session token generation
- **Session Management**: 7-day session expiration with automatic renewal
- **Password Security**: SHA-256 password hashing (passwords never stored in plain text)
- **Protected Endpoints**: All main features require authentication
- **Multi-User Support**: Each user has their own data (sessions, snippets, stats)

### 🔒 Security Features
- HTTP-only cookies for session tokens
- SameS ite=Lax cookie policy
- Authorization header support
- Automatic session expiration check
- Session invalidation on logout
- Password minimum length enforcement (6 characters)
- Username minimum length enforcement (3 characters)

## API Endpoints

### Authentication Endpoints

#### 1. Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",  // Optional
  "password": "mypassword123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Registration successful",
  "username": "john_doe"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Username must be at least 3 characters"
}
```

#### 2. Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "mypassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "username": "john_doe",
  "email": "john@example.com",
  "session_token": "abc123...xyz"
}
```

Sets HTTP-only cookie: `session_token=abc123...xyz; Max-Age=604800; HttpOnly; SameS ite=Lax`

#### 3. Logout
```http
POST /auth/logout
Authorization: <session_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### 4. Check Authentication Status
```http
GET /auth/check
Authorization: <session_token>
```

**Response (200 OK):**
```json
{
  "authenticated": true,
  "username": "john_doe",
  "email": "john@example.com"
}
```

#### 5. Get User Profile
```http
GET /auth/profile
Authorization: <session_token>
```

**Response (200 OK):**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00",
  "stats": {
    "total_requests": 45,
    "tests_passed": 12,
    "tests_failed": 3
  }
}
```

### Protected Endpoints

All the following endpoints now require authentication via the `Authorization` header:

- `POST /generate` - Generate Selenium code
- (More endpoints will be protected as needed)

## Frontend Integration

### Login Flow

1. **Page Load**: 
   - Check if `session_token` exists in localStorage
   - Call `/auth/check` to verify session validity
   - If invalid/expired, show login modal

2. **Registration**:
   - User fills registration form (username, email, password)
   - Submit to `/auth/register`
   - On success, redirect to login modal

3. **Login**:
   - User enters username and password
   - Submit to `/auth/login`
   - Store `session_token` in localStorage
   - Update UI to show user profile

4. **Using Protected Features**:
   - All API calls include `Authorization: <session_token>` header
   - If 401 response, redirect to login

5. **Logout**:
   - Call `/auth/logout` endpoint
   - Clear localStorage
   - Update UI to show login button

### Code Example - Frontend

```javascript
// Login
async function loginUser() {
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
        updateUserInterface();
    }
}

// Authenticated API Call
async function generateCode() {
    const token = localStorage.getItem('session_token');
    
    const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token
        },
        credentials: 'include',
        body: JSON.stringify({ prompt })
    });
    
    if (response.status === 401) {
        // Session expired
        showLoginModal();
        return;
    }
    
    const data = await response.json();
    // Process response...
}
```

## Data Structure

### User Database (In-Memory)
```python
users_db = {
    "username": {
        "password_hash": "sha256_hash",
        "email": "user@example.com",
        "created_at": "2024-01-15T10:30:00",
        "sessions": {},      # User's test recordings
        "snippets": [],      # User's saved code snippets
        "stats": {
            "total_requests": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }
    }
}
```

### Session Database (In-Memory)
```python
sessions_db = {
    "session_token_hash": {
        "username": "john_doe",
        "created_at": "2024-01-15T10:30:00",
        "expires_at": datetime(2024, 1, 22, 10, 30, 0)  # 7 days later
    }
}
```

## Testing

### Manual Testing via Web Interface

1. Start the server:
   ```bash
   python src/main/python/api_server_improved.py
   ```

2. Open `http://localhost:5002` in browser

3. Click "Login" button

4. Click "Register here" to create new account

5. Fill in registration form:
   - Username: testuser (min 3 chars)
   - Email: test@example.com (optional)
   - Password: testpass123 (min 6 chars)
   - Confirm Password: testpass123

6. Click "Register"

7. Login with your credentials

8. Try generating code - should work with authentication

9. Refresh page - should auto-login with stored session

10. Click user profile → Logout

### Automated Testing via Script

Run the test script:
```bash
python test_auth.py
```

This will test:
- ✅ User registration
- ✅ User login
- ✅ Authentication check
- ✅ Protected endpoint access
- ✅ Logout

## Error Handling

### Common Errors

| Error Code | Message | Cause |
|------------|---------|-------|
| 400 | "Username must be at least 3 characters" | Username too short |
| 400 | "Password must be at least 6 characters" | Password too short |
| 400 | "Username already exists" | Duplicate username |
| 401 | "Invalid username or password" | Wrong credentials |
| 401 | "Authentication required" | Missing/invalid token |
| 500 | "Internal server error" | Server error |

## Session Expiration

- **Duration**: 7 days from login
- **Auto-renewal**: No (user must re-login after 7 days)
- **Check**: Every protected endpoint call validates session expiry
- **Behavior**: Expired sessions return 401, frontend shows login modal

## Future Enhancements

### Recommended Improvements
- [ ] Database storage (replace in-memory dictionaries)
- [ ] Password reset functionality
- [ ] Email verification
- [ ] Remember me option (longer sessions)
- [ ] Rate limiting on login attempts
- [ ] Two-factor authentication
- [ ] OAuth integration (Google, GitHub)
- [ ] Session refresh tokens
- [ ] Password complexity requirements
- [ ] Account deletion
- [ ] Admin panel for user management

### Production Considerations
- [ ] Change `app.secret_key` to secure random value
- [ ] Use environment variables for configuration
- [ ] Implement HTTPS
- [ ] Add CSRF protection
- [ ] Use bcrypt instead of SHA-256 for passwords
- [ ] Add logging for security events
- [ ] Implement account lockout after failed attempts
- [ ] Add session device tracking
- [ ] Implement proper database with migrations

## Configuration

### Backend Settings
Located in `api_server_improved.py`:
```python
# Secret key for session signing
app.secret_key = 'your-secret-key-change-this-in-production'

# Session duration
SESSION_DURATION = timedelta(days=7)

# Password requirements
MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6
```

### Frontend Settings
Located in `index.html`:
```javascript
// API URL
const API_URL = 'http://localhost:5002';

// Session token storage
localStorage.setItem('session_token', token);
```

## Troubleshooting

### "Cannot connect to server"
- Ensure `api_server_improved.py` is running
- Check if port 5002 is available
- Verify API_URL matches server address

### "Session expired" error
- Session lasted more than 7 days
- Server was restarted (in-memory sessions lost)
- Solution: Login again

### "Authentication required" on first load
- Normal behavior if no session exists
- Click "Login" and enter credentials

### Registration fails
- Check username is at least 3 characters
- Check password is at least 6 characters
- Ensure username is not already taken
- Check server console for error details

## Support

For issues or questions:
1. Check server console for error messages
2. Check browser console for frontend errors
3. Verify all fields meet requirements
4. Try clearing localStorage and re-registering
5. Restart the server if needed

---

**Note**: This system uses in-memory storage. All user data is lost when the server restarts. For production use, implement persistent database storage.
