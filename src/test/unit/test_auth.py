"""
Test the authentication system
"""
import requests
import json

API_URL = "http://localhost:5000"

def test_registration():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

def test_login():
    """Test user login"""
    print("\n=== Testing Login ===")
    
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    return result.get('session_token')

def test_auth_check(token):
    """Test authentication check"""
    print("\n=== Testing Auth Check ===")
    
    headers = {'Authorization': token}
    response = requests.get(f"{API_URL}/auth/check", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    print("\n=== Testing Protected Endpoint ===")
    
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    data = {"prompt": "test selenium code"}
    
    response = requests.post(f"{API_URL}/generate", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Successfully accessed protected endpoint")
    else:
        print(f"❌ Failed: {response.json()}")

def test_logout(token):
    """Test logout"""
    print("\n=== Testing Logout ===")
    
    headers = {'Authorization': token}
    response = requests.post(f"{API_URL}/auth/logout", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    try:
        # Test registration
        reg_result = test_registration()
        
        # Test login
        token = test_login()
        
        if token:
            # Test auth check
            test_auth_check(token)
            
            # Test protected endpoint
            test_protected_endpoint(token)
            
            # Test logout
            test_logout(token)
            
            print("\n✅ All tests completed!")
        else:
            print("\n❌ Login failed, cannot continue tests")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server. Please start the server first.")
        print("Run: python src/main/python/api_server_improved.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
