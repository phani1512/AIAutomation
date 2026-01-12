"""
Debug test to trace exactly what's happening with session persistence.
"""

import requests
import time

API_URL = "http://localhost:5001"

def test_session_with_logging():
    """Test session persistence with detailed logging."""
    
    print("\n" + "="*80)
    print("SESSION PERSISTENCE DEBUG TEST")
    print("="*80)
    
    # Step 1: Initialize browser
    print("\n[STEP 1] Initializing browser...")
    response = requests.post(f"{API_URL}/browser/initialize", json={
        "browser": "chrome",
        "headless": False
    })
    print(f"Response: {response.json()}")
    time.sleep(2)
    
    # Step 2: First prompt WITH URL
    print("\n[STEP 2] First prompt - Navigate to URL and enter email...")
    test_url = "https://httpbin.org/forms/post"  # Test site
    response = requests.post(f"{API_URL}/generate", json={
        "prompt": "enter test@example.com in custname field",
        "execute": True,
        "url": test_url
    })
    result = response.json()
    print(f"Success: {result.get('execution', {}).get('success')}")
    print(f"Current URL: {result.get('execution', {}).get('current_url')}")
    print(f"Page Title: {result.get('execution', {}).get('page_title')}")
    
    time.sleep(3)
    
    # Step 3: Get browser info
    print("\n[STEP 3] Getting browser info...")
    response = requests.get(f"{API_URL}/browser/info")
    info = response.json()
    print(f"Current URL: {info.get('current_url')}")
    print(f"Page Title: {info.get('page_title')}")
    
    time.sleep(2)
    
    # Step 4: Second prompt WITH SAME URL (should NOT navigate)
    print("\n[STEP 4] Second prompt - Same URL (should skip navigation)...")
    response = requests.post(f"{API_URL}/generate", json={
        "prompt": "enter comments in comments field",
        "execute": True,
        "url": test_url  # SAME URL
    })
    result = response.json()
    print(f"Success: {result.get('execution', {}).get('success')}")
    print(f"Current URL: {result.get('execution', {}).get('current_url')}")
    
    time.sleep(2)
    
    # Step 5: Third prompt WITHOUT URL
    print("\n[STEP 5] Third prompt - No URL (should skip navigation)...")
    response = requests.post(f"{API_URL}/generate", json={
        "prompt": "enter 1234567890 in custtel field",
        "execute": True,
        "url": ""  # EMPTY URL
    })
    result = response.json()
    print(f"Success: {result.get('execution', {}).get('success')}")
    print(f"Current URL: {result.get('execution', {}).get('current_url')}")
    
    time.sleep(2)
    
    # Step 6: Verify still on same page
    print("\n[STEP 6] Final verification...")
    response = requests.get(f"{API_URL}/browser/info")
    final_info = response.json()
    print(f"Final URL: {final_info.get('current_url')}")
    print(f"Expected URL: {test_url}")
    
    if final_info.get('current_url') == test_url or final_info.get('current_url').startswith(test_url):
        print("\n✅ SUCCESS! Browser stayed on the same page throughout all prompts!")
    else:
        print(f"\n❌ FAILED! URL changed unexpectedly to: {final_info.get('current_url')}")
    
    # Cleanup
    print("\n[CLEANUP] Closing browser...")
    requests.post(f"{API_URL}/browser/close")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        test_session_with_logging()
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
