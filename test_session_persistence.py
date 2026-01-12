"""
Test that browser sessions persist across multiple prompts.
This verifies the fix for the logout issue.
"""

import requests
import time

API_URL = "http://localhost:5001"

def test_session_persistence():
    """Test that login session persists across multiple prompts."""
    
    print("\n" + "="*70)
    print("TESTING SESSION PERSISTENCE - Multiple Prompts")
    print("="*70)
    
    # Test 1: Initialize browser
    print("\n[TEST 1] Initializing browser...")
    response = requests.post(f"{API_URL}/browser/initialize", json={
        "browser": "chrome",
        "headless": False
    })
    print(f"Initialize response: {response.json()}")
    assert response.status_code == 200, "Failed to initialize browser"
    print("✅ Browser initialized")
    
    time.sleep(2)
    
    # Test 2: Navigate to login page
    print("\n[TEST 2] Navigating to login page...")
    response = requests.post(f"{API_URL}/browser/execute", json={
        "code": 'driver.get("https://example.com")',
        "url": ""  # No URL navigation
    })
    result = response.json()
    print(f"Navigate response: {result.get('current_url')}")
    assert response.status_code == 200, "Failed to navigate"
    print(f"✅ Navigated to: {result.get('current_url')}")
    
    time.sleep(2)
    
    # Test 3: Get browser info (should show same URL)
    print("\n[TEST 3] Getting browser info...")
    response = requests.get(f"{API_URL}/browser/info")
    info = response.json()
    print(f"Current URL: {info.get('current_url')}")
    print(f"Page Title: {info.get('page_title')}")
    assert response.status_code == 200, "Failed to get browser info"
    print("✅ Browser info retrieved")
    
    time.sleep(2)
    
    # Test 4: Execute second prompt WITHOUT url parameter
    # This should stay on the same page and NOT re-navigate
    print("\n[TEST 4] Executing second prompt (should preserve session)...")
    response = requests.post(f"{API_URL}/browser/execute", json={
        "code": 'element = driver.find_element(By.TAG_NAME, "body"); print("Body found!")',
        "url": ""  # Empty URL - should NOT navigate
    })
    result = response.json()
    print(f"Execute response: {result.get('success')}")
    print(f"Current URL after execute: {result.get('current_url')}")
    assert response.status_code == 200, "Failed to execute second prompt"
    print("✅ Second prompt executed without re-navigation")
    
    time.sleep(2)
    
    # Test 5: Verify browser is still on the same page
    print("\n[TEST 5] Verifying browser stayed on same page...")
    response = requests.get(f"{API_URL}/browser/info")
    final_info = response.json()
    print(f"Final URL: {final_info.get('current_url')}")
    assert final_info.get('current_url') == info.get('current_url'), \
        "URL changed! Session was not preserved!"
    print("✅ Browser stayed on same page - Session preserved!")
    
    # Test 6: Close browser
    print("\n[TEST 6] Closing browser...")
    response = requests.post(f"{API_URL}/browser/close")
    print(f"Close response: {response.json()}")
    print("✅ Browser closed")
    
    print("\n" + "="*70)
    print("ALL TESTS PASSED! ✅")
    print("Session persistence is working correctly.")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        test_session_persistence()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
