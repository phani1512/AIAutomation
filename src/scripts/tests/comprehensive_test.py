#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Functionality Test Suite
Tests all major features after refactoring to ensure nothing broke
"""

import requests
import json
import time
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:5002"

class TestResults:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.errors = 0
    
    def add(self, test_name: str, status: str, details: str = ""):
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "ERROR":
            self.errors += 1
    
    def print_summary(self):
        total = len(self.results)
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*70)
        print("📊 TEST SUMMARY REPORT")
        print("="*70)
        print(f"\n✅ PASSED: {self.passed}/{total}")
        print(f"❌ FAILED: {self.failed}/{total}")
        print(f"⚠️  ERRORS: {self.errors}/{total}")
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if self.failed > 0 or self.errors > 0:
            print("\n⚠️  FAILED/ERROR TESTS:")
            for r in self.results:
                if r["status"] != "PASS":
                    print(f"   • {r['test']}: {r['status']} - {r['details']}")
        
        print("\n" + "="*70)
        if success_rate == 100:
            print("🏆 ALL TESTS PASSED - FUNCTIONALITY FULLY PRESERVED!")
        elif success_rate >= 90:
            print("✅ EXCELLENT - Minor issues detected")
        elif success_rate >= 70:
            print("⚠️  WARNING - Some functionality impaired")
        else:
            print("❌ CRITICAL - Major functionality broken")
        print("="*70)

def test_feature(results: TestResults, name: str, prompt: str, language: str, 
                 validation_fn, comprehensive_mode: bool = False) -> None:
    """Test a specific feature"""
    print(f"\n📋 Testing: {name}")
    try:
        payload = {
            "prompt": prompt,
            "language": language
        }
        if comprehensive_mode:
            payload["comprehensive_mode"] = True
        
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        
        if validation_fn(data):
            print(f"✅ PASS: {name}")
            results.add(name, "PASS", "Validation successful")
        else:
            print(f"❌ FAIL: {name}")
            results.add(name, "FAIL", "Validation failed")
    except Exception as e:
        print(f"❌ ERROR: {name} - {str(e)}")
        results.add(name, "ERROR", str(e))

def main():
    print("\n🔬 COMPREHENSIVE FUNCTIONALITY TEST SUITE")
    print("="*70)
    
    # Check server health
    print("\n🔍 Checking server status...")
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=3)
        health_data = health.json()
        print(f"✅ Server is healthy - Status: {health_data.get('status')}")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        print("Please start the server first!")
        return
    
    time.sleep(1)
    results = TestResults()
    
    # Test 1: Dataset Matching - Click Action
    test_feature(
        results,
        "Dataset Match: Click Button",
        "click login button",
        "python",
        lambda r: "click" in r.get("code", "").lower() and len(r.get("code", "")) > 20
    )
    
    # Test 2: Dataset Matching - Input Action
    test_feature(
        results,
        "Dataset Match: Enter Text",
        "enter username",
        "python",
        lambda r: any(x in r.get("code", "").lower() for x in ["send_keys", "fill", "type"]) and len(r.get("code", "")) > 20
    )
    
    # Test 3: Universal Input Pattern - Email
    test_feature(
        results,
        "Universal: Email Field",
        "enter test@email.com in email field",
        "python",
        lambda r: ("email" in r.get("code", "").lower() or "test@email" in r.get("code", "").lower()) and 
                  any(x in r.get("code", "").lower() for x in ["send_keys", "fill"])
    )
    
    # Test 4: Universal Input Pattern - Username
    test_feature(
        results,
        "Universal: Username Field",
        "type john_doe in username",
        "python",
        lambda r: ("username" in r.get("code", "").lower() or "john_doe" in r.get("code", "").lower()) and
                  any(x in r.get("code", "").lower() for x in ["send_keys", "fill"])
    )
    
    # Test 5: Language Conversion - Java
    test_feature(
        results,
        "Language: Java",
        "click submit button",
        "java",
        lambda r: ("driver." in r.get("code", "") or "findElement" in r.get("code", "") or "click()" in r.get("code", "")) and
                  len(r.get("code", "")) > 20
    )
    
    # Test 6: Language Conversion - JavaScript
    test_feature(
        results,
        "Language: JavaScript",
        "enter password",
        "javascript",
        lambda r: any(x in r.get("code", "").lower() for x in ["await", "const", "page."]) and
                  len(r.get("code", "")) > 20
    )
    
    # Test 7: Language Conversion - C#
    test_feature(
        results,
        "Language: C#",
        "click next button",
        "csharp",
        lambda r: ("driver." in r.get("code", "") or "FindElement" in r.get("code", "") or "Click()" in r.get("code", "")) and
                  len(r.get("code", "")) > 20
    )
    
    # Test 8: Comprehensive Mode
    test_feature(
        results,
        "Comprehensive Mode with Fallbacks",
        "click login button",
        "python",
        lambda r: any(x in r.get("code", "").lower() for x in ["try", "except"]) and len(r.get("code", "")) > 50,
        comprehensive_mode=True
    )
    
    # Test 9: Multi-word Action
    test_feature(
        results,
        "Multi-word: Login Button",
        "click the login button",
        "python",
        lambda r: "click" in r.get("code", "").lower() and "login" in r.get("code", "").lower() and
                  len(r.get("code", "")) > 20
    )
    
    # Test 10: Template Pattern
    test_feature(
        results,
        "Template: Dynamic Field",
        "enter {VALUE} in search box",
        "python",
        lambda r: ("search" in r.get("code", "").lower() or "VALUE" in r.get("code", "") or "{" in r.get("code", "")) and
                  len(r.get("code", "")) > 15
    )
    
    # Test 11: Synonym Matching
    test_feature(
        results,
        "Synonym: Press/Click",
        "press submit button",
        "python",
        lambda r: ("click" in r.get("code", "").lower() or "submit" in r.get("code", "").lower()) and
                  len(r.get("code", "")) > 20
    )
    
    # Test 12: Complex Universal Pattern
    test_feature(
        results,
        "Universal: Complex Input",
        "input hello@world.com in the email address field",
        "python",
        lambda r: ("email" in r.get("code", "").lower() or "hello@world" in r.get("code", "").lower()) and
                  any(x in r.get("code", "").lower() for x in ["send_keys", "fill"])
    )
    
    # Test 13: Java Universal Pattern
    test_feature(
        results,
        "Java Universal Pattern",
        "enter test123 in password field",
        "java",
        lambda r: ("password" in r.get("code", "").lower() or "test123" in r.get("code", "").lower()) and
                  "sendKeys" in r.get("code", "")
    )
    
    # Test 14: JavaScript Universal Pattern
    test_feature(
        results,
        "JavaScript Universal Pattern",
        "type admin in username box",
        "javascript",
        lambda r: ("username" in r.get("code", "").lower() or "admin" in r.get("code", "").lower()) and
                  any(x in r.get("code", "").lower() for x in ["fill", "type"])
    )
    
    # Test 15: C# Universal Pattern
    test_feature(
        results,
        "C# Universal Pattern",
        "enter secure123 in password",
        "csharp",
        lambda r: ("password" in r.get("code", "").lower() or "secure123" in r.get("code", "").lower()) and
                  "SendKeys" in r.get("code", "")
    )
    
    # Test 16: Different Input Keywords
    test_feature(
        results,
        "Various Input Keywords",
        "input myvalue in textfield",
        "python",
        lambda r: any(x in r.get("code", "").lower() for x in ["myvalue", "textfield"]) and
                  any(x in r.get("code", "").lower() for x in ["send_keys", "fill"])
    )
    
    # Test 17: Fallback Strategy Module
    test_feature(
        results,
        "Fallback Strategy Generation",
        "click save button",
        "python",
        lambda r: "click" in r.get("code", "").lower() and "save" in r.get("code", "").lower(),
        comprehensive_mode=True
    )
    
    # Test 18: Language Converter Module (Python)
    test_feature(
        results,
        "Language Converter: Python Code",
        "click delete button",
        "python",
        lambda r: ".click(" in r.get("code", "") and len(r.get("code", "")) > 15
    )
    
    # Test 19: Locator Utils Module
    test_feature(
        results,
        "Locator Extraction",
        "click cancel button",
        "python",
        lambda r: any(x in r.get("code", "") for x in ["By.", "css", "xpath", "id"]) and
                  "click" in r.get("code", "").lower()
    )
    
    # Test 20: Dataset Matcher Module
    test_feature(
        results,
        "Dataset Fuzzy Matching",
        "press the submit button",
        "python",
        lambda r: ("submit" in r.get("code", "").lower() or "click" in r.get("code", "").lower()) and
                  len(r.get("code", "")) > 20
    )
    
    # Print summary
    results.print_summary()

if __name__ == "__main__":
    main()
