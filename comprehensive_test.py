#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive test script for field-aware suggestions.
This tests the entire flow and shows detailed results.
"""
import requests
import json
import time
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*70)
print("FIELD-AWARE SUGGESTIONS - COMPREHENSIVE TEST")
print("="*70)

# Wait for server to be ready
print("\n[1/5] Waiting for server to initialize...")
time.sleep(5)

# Test server health
print("\n[2/5] Checking server health...")
try:
    health = requests.get("http://localhost:5002/health", timeout=5)
    if health.status_code == 200:
        print(f"  ✓ Server is healthy: {health.json()}")
    else:
        print(f"  ✗ Server returned: {health.status_code}")
        exit(1)
except Exception as e:
    print(f"  ✗ Server not responding: {e}")
    exit(1)

# Check if test case JSON exists
print("\n[3/5] Verifying test case JSON file exists...")
workspace = Path(__file__).parent
json_pattern = "test_suites/**/builder/TC002_variant_2*.json"
json_files = list(workspace.glob(json_pattern))
if json_files:
    print(f"  ✓ Found JSON file: {json_files[0]}")
    with open(json_files[0], 'r') as f:
        test_data = json.load(f)
    print(f"    - Test name: {test_data.get('name')}")
    print(f"    - Has 'actions': {('actions' in test_data)}")
    if 'actions' in test_data:
        print(f"    - Actions count: {len(test_data['actions'])}")
        if test_data['actions']:
            print(f"    - First action: {test_data['actions'][0].get('type', 'unknown')}")
else:
    print(f"  ✗ No JSON files found matching: {json_pattern}")
    print(f"    Searched from: {workspace}")

# Call the API
print("\n[4/5] Calling field-aware suggestions API...")
payload = {"test_case_id": "TC002_variant_2"}
try:
    response = requests.post(
        "http://localhost:5002/ml/field-aware-suggestions",
        json=payload,
        timeout=10
    )
    
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n  ✓ SUCCESS!")
        print(f"    - Test Name: {data.get('test_name')}")
        print(f"    - Input Fields: {data.get('metadata', {}).get('input_fields_found', 0)}")
        print(f"    - Variant Type: {data.get('metadata', {}).get('variant_type', 'none')}")
        print(f"    - Scenarios Count: {data.get('scenarios_count', 0)}")
        
        print(f"\n    Scenarios:")
        for scenario in data.get('scenarios', []):
            priority = "⭐" if scenario.get('is_prioritized') else "  "
            print(f"      {priority} {scenario.get('type').upper()}: {len(scenario.get('suggestions', []))} suggestions")
    else:
        print(f"\n  ✗ ERROR: {response.status_code}")
        try:
            error_data = response.json()
            print(f"    Error: {error_data.get('error', 'Unknown')}")
        except:
            print(f"    Response: {response.text[:200]}")
            
except Exception as e:
    print(f"  ✗ Exception: {e}")

# Show debug log
print("\n[5/5] Reading debug log...")
debug_file = r"c:\Users\valaboph\AIAutomation\debug_field_aware.txt"
if os.path.exists(debug_file):
    print("-"*70)
    with open(debug_file, 'r') as f:
        content = f.read()
        print(content)
    print("-"*70)
else:
    print("  ✗ Debug file not found")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
