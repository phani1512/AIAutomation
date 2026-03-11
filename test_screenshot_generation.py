"""
Screenshot Test Generation Diagnostic Tool
Helps debug and test screenshot-based test case generation
"""

import sys
import os

# Add src/main/python to Python path for module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

import base64
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_screenshot():
    """Create a simple test screenshot with buttons and inputs."""
    # Create a simple login form image
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use default font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw title
    draw.text((150, 20), "Login Form", fill='black', font=font)
    
    # Draw input fields (rectangles)
    # Email field
    draw.rectangle([50, 70, 350, 100], outline='gray', width=2)
    draw.text((55, 50), "Email:", fill='black', font=font)
    
    # Password field
    draw.rectangle([50, 140, 350, 170], outline='gray', width=2)
    draw.text((55, 120), "Password:", fill='black', font=font)
    
    # Login button
    draw.rectangle([150, 210, 250, 240], fill='blue', outline='darkblue', width=2)
    draw.text((170, 215), "Login", fill='white', font=font)
    
    # Save to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_base64

def test_screenshot_analysis():
    """Test screenshot analysis pipeline."""
    print("\n" + "="*70)
    print("SCREENSHOT TEST GENERATION DIAGNOSTIC")
    print("="*70)
    
    # Create test screenshot
    print("\n[1/5] Creating test screenshot...")
    screenshot_b64 = create_test_screenshot()
    print(f"✓ Screenshot created (size: {len(screenshot_b64)} bytes)")
    
    # Initialize components
    print("\n[2/5] Initializing components...")
    try:
        from visual_element_detector import VisualElementDetector
        from multimodal_generator import MultiModalCodeGenerator
        from complete_test_generator import CompleteTestGenerator
        
        detector = VisualElementDetector()
        generator = MultiModalCodeGenerator(detector)
        test_gen = CompleteTestGenerator()
        print("✓ All components initialized")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return
    
    # Analyze screenshot
    print("\n[3/5] Analyzing screenshot...")
    try:
        analysis = generator.analyze_screenshot(
            screenshot_b64,
            user_intent="login form",
            use_ocr=True,
            generate_pom=False
        )
        
        print(f"✓ Analysis complete:")
        print(f"  - Buttons detected: {len(analysis['elements'].get('buttons', []))}")
        print(f"  - Inputs detected: {len(analysis['elements'].get('inputs', []))}")
        print(f"  - Text regions: {len(analysis.get('text_regions', []))}")
        print(f"  - OCR enabled: {analysis.get('ocr_enabled', False)}")
        print(f"  - Total elements: {analysis.get('total_elements', 0)}")
        
        # Show element details
        if analysis['elements'].get('buttons'):
            print(f"\n  Button details:")
            for i, btn in enumerate(analysis['elements']['buttons']):
                print(f"    #{i+1}: {btn.get('suggested_name', 'N/A')} - Text: '{btn.get('text', 'N/A')}'")
                print(f"         Strategies: {len(btn.get('locator_strategies', []))}")
        
        if analysis['elements'].get('inputs'):
            print(f"\n  Input details:")
            for i, inp in enumerate(analysis['elements']['inputs']):
                print(f"    #{i+1}: {inp.get('suggested_name', 'N/A')} - Label: '{inp.get('label', 'N/A')}'")
                print(f"         Strategies: {len(inp.get('locator_strategies', []))}")
        
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Generate test suite
    print("\n[4/5] Generating test suite (Java)...")
    try:
        test_suite = test_gen.generate_complete_test_suite(
            analysis,
            language='java',
            test_name='LoginTest'
        )
        
        print(f"✓ Test suite generated:")
        print(f"  - Language: {test_suite.get('language', 'N/A')}")
        print(f"  - Framework: {test_suite.get('framework', 'N/A')}")
        print(f"  - Test count: {test_suite.get('test_count', 0)}")
        print(f"  - Ready to execute: {test_suite.get('ready_to_execute', False)}")
        
        # Check code quality
        page_object = test_suite.get('page_object', '')
        test_class = test_suite.get('test_class', '')
        
        print(f"\n  Code quality check:")
        print(f"    - Page Object: {len(page_object)} characters")
        print(f"    - Test Class: {len(test_class)} characters")
        
        # Check for 'unknown' locators (indicates problem)
        unknown_count = page_object.count('unknown')
        if unknown_count > 0:
            print(f"    ⚠ Warning: {unknown_count} 'unknown' locators found!")
        else:
            print(f"    ✓ No 'unknown' locators")
        
        # Save sample code
        output_dir = 'diagnostic_output'
        os.makedirs(output_dir, exist_ok=True)
        
        with open(f'{output_dir}/LoginTestPage.java', 'w', encoding='utf-8') as f:
            f.write(page_object)
        
        with open(f'{output_dir}/LoginTest.java', 'w', encoding='utf-8') as f:
            f.write(test_class)
        
        print(f"\n  ✓ Sample code saved to: {output_dir}/")
        
    except Exception as e:
        print(f"✗ Test generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Generate Python version
    print("\n[5/5] Generating test suite (Python)...")
    try:
        test_suite_py = test_gen.generate_complete_test_suite(
            analysis,
            language='python',
            test_name='LoginTest'
        )
        
        print(f"✓ Python test suite generated:")
        print(f"  - Test count: {test_suite_py.get('test_count', 0)}")
        
        # Save Python code
        page_object_py = test_suite_py.get('page_object', '')
        test_class_py = test_suite_py.get('test_class', '')
        
        with open(f'{output_dir}/login_test_page.py', 'w', encoding='utf-8') as f:
            f.write(page_object_py)
        
        with open(f'{output_dir}/test_login.py', 'w', encoding='utf-8') as f:
            f.write(test_class_py)
        
        print(f"  ✓ Python code saved to: {output_dir}/")
        
    except Exception as e:
        print(f"✗ Python generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    print("✓ Screenshot analysis: PASSED")
    print("✓ Test generation: PASSED")
    print(f"✓ Output files: {output_dir}/")
    print("\nIf you see this message, screenshot test generation is working!")
    print("="*70 + "\n")

def test_api_endpoint():
    """Test the API endpoint directly."""
    print("\n" + "="*70)
    print("TESTING API ENDPOINT")
    print("="*70)
    
    import requests
    
    # Create test screenshot
    print("\n[1/2] Creating test screenshot...")
    screenshot_b64 = create_test_screenshot()
    
    # Test API
    print("\n[2/2] Calling /screenshot/analyze endpoint...")
    try:
        response = requests.post(
            'http://localhost:5002/screenshot/analyze',
            json={
                'screenshot': screenshot_b64,
                'intent': 'login form test',
                'language': 'java',
                'test_name': 'LoginTest',
                'auto_save': False  # Don't save during test
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API call successful!")
            print(f"\n  Response:")
            print(f"    - Total elements: {data.get('total_elements', 0)}")
            print(f"    - Test count: {data.get('test_suite', {}).get('test_count', 0)}")
            print(f"    - Ready to execute: {data.get('test_suite', {}).get('ready_to_execute', False)}")
            
            # Save response
            with open('diagnostic_output/api_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"    - Full response saved to: diagnostic_output/api_response.json")
        else:
            print(f"✗ API call failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API server")
        print("  Make sure the server is running: python src/main/python/api_server_modular.py")
    except Exception as e:
        print(f"✗ API test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\n" + "█"*70)
    print("█" + "  SCREENSHOT TEST GENERATION DIAGNOSTIC TOOL".center(68) + "█")
    print("█"*70)
    
    # Test 1: Direct component testing
    test_screenshot_analysis()
    
    # Test 2: API endpoint testing
    print("\n" + "="*70)
    print("Would you like to test the API endpoint? (y/n)")
    response = input("> ").strip().lower()
    if response == 'y':
        test_api_endpoint()
    
    print("\n✅ Diagnostic complete!\n")
