"""
Demo script to test browser execution integration.
This script demonstrates how to use the browser execution API programmatically.
"""

import requests
import time

API_URL = "http://localhost:5000"

def test_browser_execution():
    """Test the complete browser execution workflow."""
    
    print("=" * 60)
    print("🧪 Testing Browser Execution Integration")
    print("=" * 60)
    
    # Step 1: Health check
    print("\n1️⃣ Checking API health...")
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print("✅ API is healthy")
        print(f"   Response: {response.json()}")
    else:
        print("❌ API health check failed")
        return
    
    # Step 2: Initialize browser
    print("\n2️⃣ Initializing Chrome browser...")
    response = requests.post(f"{API_URL}/browser/initialize", json={
        "browser": "chrome",
        "headless": False  # Set to True for headless mode
    })
    result = response.json()
    print(f"   Status: {result.get('message')}")
    
    if not result.get('success'):
        print("❌ Browser initialization failed")
        return
    
    time.sleep(2)  # Brief pause
    
    # Step 3: Generate and execute code
    print("\n3️⃣ Generating code and executing in browser...")
    test_cases = [
        {
            "prompt": "navigate to https://www.example.com",
            "url": "https://www.example.com"
        },
        {
            "prompt": "verify page title",
            "url": ""
        }
    ]
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n   Test {idx}: {test['prompt']}")
        response = requests.post(f"{API_URL}/generate", json={
            "prompt": test['prompt'],
            "execute": True,
            "url": test.get('url', '')
        })
        
        result = response.json()
        print(f"   Generated Code:\n{result['generated']}")
        
        if 'execution' in result:
            execution = result['execution']
            if execution.get('success'):
                print(f"   ✅ Execution successful!")
                print(f"   Current URL: {execution.get('current_url')}")
                print(f"   Page Title: {execution.get('page_title')}")
            else:
                print(f"   ❌ Execution failed: {execution.get('error')}")
        
        time.sleep(2)  # Pause between tests
    
    # Step 4: Get browser info
    print("\n4️⃣ Getting browser info...")
    response = requests.get(f"{API_URL}/browser/info")
    if response.status_code == 200:
        info = response.json()
        print(f"   Current URL: {info.get('url')}")
        print(f"   Page Title: {info.get('title')}")
        print(f"   Page Source Length: {info.get('page_source_length')} bytes")
    
    # Step 5: Take screenshot
    print("\n5️⃣ Taking screenshot...")
    response = requests.post(f"{API_URL}/browser/screenshot", json={
        "filename": "demo_screenshot.png"
    })
    result = response.json()
    if result.get('success'):
        print(f"   ✅ Screenshot saved: {result.get('filepath')}")
    else:
        print(f"   ❌ Screenshot failed: {result.get('error')}")
    
    # Step 6: Close browser
    print("\n6️⃣ Closing browser...")
    response = requests.post(f"{API_URL}/browser/close")
    result = response.json()
    print(f"   {result.get('message')}")
    
    print("\n" + "=" * 60)
    print("✅ Browser execution test completed!")
    print("=" * 60)

def test_code_generation_only():
    """Test code generation without browser execution."""
    
    print("\n" + "=" * 60)
    print("🧪 Testing Code Generation (No Execution)")
    print("=" * 60)
    
    prompts = [
        "click login button",
        "enter username in input field",
        "select country from dropdown",
        "verify success message"
    ]
    
    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        response = requests.post(f"{API_URL}/generate", json={
            "prompt": prompt,
            "execute": False
        })
        
        result = response.json()
        print(f"Generated:\n{result['generated']}")
        print(f"Tokens: {result.get('tokens_generated', 0)}")

if __name__ == "__main__":
    print("\n🚀 Selenium SLM Browser Integration Demo")
    print("Make sure the API server is running on http://localhost:5000\n")
    
    choice = input("Select test:\n1. Browser Execution Test\n2. Code Generation Only\n3. Both\n\nChoice (1-3): ")
    
    try:
        if choice == "1":
            test_browser_execution()
        elif choice == "2":
            test_code_generation_only()
        elif choice == "3":
            test_code_generation_only()
            print("\n" + "=" * 60)
            input("\nPress Enter to start browser execution test...")
            test_browser_execution()
        else:
            print("Invalid choice")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure the API server is running!")
