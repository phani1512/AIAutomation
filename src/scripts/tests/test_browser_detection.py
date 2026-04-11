#!/usr/bin/env python
"""
Smart Browser Detection Test
Tests the auto-detection and fallback capabilities
"""

import sys
import os

# Add src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from smart_browser_manager import SmartBrowserManager

def test_browser_detection():
    """Test browser detection and WebDriver auto-install"""
    
    print("\n" + "="*60)
    print("SMART BROWSER MANAGER TEST")
    print("="*60 + "\n")
    
    manager = SmartBrowserManager()
    
    # Test 1: Detect available browsers
    print("📋 Test 1: Detecting available browsers...")
    print("-" * 60)
    browsers = manager.detect_available_browsers()
    
    if browsers:
        print(f"✅ Found {len(browsers)} browser(s):")
        for browser in browsers:
            print(f"   • {browser['name'].capitalize()}: {browser['path']}")
            print(f"     Version: {browser.get('version', 'Unknown')}")
    else:
        print("❌ No browsers detected")
    print()
    
    # Test 2: Get best available browser
    print("🏆 Test 2: Finding best available browser...")
    print("-" * 60)
    best = manager.get_best_available_browser()
    
    if best:
        print(f"✅ Best browser: {best['name'].capitalize()}")
        print(f"   Path: {best['path']}")
        print(f"   Version: {best.get('version', 'Unknown')}")
    else:
        print("❌ No suitable browser found")
    print()
    
    # Test 3: Try to initialize browser (auto mode)
    print("🚀 Test 3: Auto-initializing browser...")
    print("-" * 60)
    result = manager.initialize_browser_auto(headless=True)
    
    if result['success']:
        print(f"✅ Successfully initialized: {result['browser_name'].capitalize()}")
        print(f"   WebDriver: {result.get('driver_info', 'Installed')}")
        
        # Try to navigate to a test page
        try:
            driver = result['browser']
            driver.get("https://www.google.com")
            print(f"   Navigation test: ✅ Successfully loaded Google")
            
            # Clean up
            driver.quit()
            print(f"   Cleanup: ✅ Browser closed")
        except Exception as e:
            print(f"   Navigation test: ❌ Error - {str(e)}")
    else:
        print(f"❌ Initialization failed: {result['message']}")
        if 'suggestion' in result:
            print(f"\n💡 Suggestion:\n{result['suggestion']}")
    print()
    
    # Test 4: Try specific browser (if Edge fails, shows fallback)
    print("🔄 Test 4: Testing fallback to available browser...")
    print("-" * 60)
    # Try Edge first (might not be installed)
    edge_result = manager.initialize_browser_auto(preferred_browser="edge", headless=True)
    
    if edge_result['success']:
        print(f"✅ Edge initialized successfully")
        edge_result['browser'].quit()
    else:
        print(f"⚠️  Edge not available: {edge_result['message']}")
        print(f"   Fallback: Using {best['name'] if best else 'No fallback'}")
    print()
    
    print("="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_browser_detection()
