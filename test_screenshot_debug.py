"""
Debug script to test screenshot detection issue
"""
import sys
import os
import base64
import json

# Add path
sys.path.insert(0, 'src/main/python')

from visual_element_detector import VisualElementDetector
from multimodal_generator import MultiModalCodeGenerator

# Load a test screenshot (create a simple one for testing)
def create_test_screenshot():
    """Create a simple test screenshot with known elements"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Create white background
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw email input (long rectangle)
    draw.rectangle([50, 100, 400, 140], outline='black', width=2)
    draw.text((60, 80), "Email:", fill='black')
    
    # Draw password input (long rectangle)
    draw.rectangle([50, 180, 400, 220], outline='black', width=2)
    draw.text((60, 160), "Password:", fill='black')
    
    # Draw login button (medium rectangle with color)
    draw.rectangle([50, 260, 200, 300], fill='#4CAF50', outline='black', width=2)
    draw.text((90, 272), "Login", fill='white')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_bytes = buffer.read()
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return f"data:image/png;base64,{img_b64}"

print("=" * 70)
print("SCREENSHOT DETECTION DEBUG TEST")
print("=" * 70)

# Create test screenshot
print("\n[1] Creating test screenshot...")
screenshot_data = create_test_screenshot()
print(f"✓ Screenshot created (length: {len(screenshot_data)} chars)")

# Test visual detector
print("\n[2] Testing VisualElementDetector...")
detector = VisualElementDetector()
elements = detector.detect_all_elements(screenshot_data)

print(f"\n[RESULTS] Detection Results:")
print(f"  - Buttons found: {len(elements.get('buttons', []))}")
print(f"  - Inputs found: {len(elements.get('inputs', []))}")
print(f"  - Text regions found: {len(elements.get('text_regions', []))}")

if elements.get('buttons'):
    print(f"\n  Button details:")
    for i, btn in enumerate(elements['buttons']):
        print(f"    {i+1}. Position: ({btn['x']}, {btn['y']}), Size: {btn['width']}x{btn['height']}")

if elements.get('inputs'):
    print(f"\n  Input details:")
    for i, inp in enumerate(elements['inputs']):
        print(f"    {i+1}. Position: ({inp['x']}, {inp['y']}), Size: {inp['width']}x{inp['height']}, Aspect ratio: {inp.get('aspect_ratio', 'N/A')}")

# Test multimodal generator
print("\n[3] Testing MultiModalCodeGenerator...")
generator = MultiModalCodeGenerator(detector)
analysis = generator.analyze_screenshot(screenshot_data, user_intent="Login test", use_ocr=True)

print(f"\n[RESULTS] Analysis Results:")
print(f"  - Total elements: {analysis.get('total_elements', 0)}")
print(f"  - Test cases suggested: {len(analysis.get('test_scenarios', []))}")
print(f"  - Has elements dict: {analysis.get('elements') is not None}")

if analysis.get('elements'):
    elem_dict = analysis['elements']
    print(f"  - Elements dict buttons: {len(elem_dict.get('buttons', []))}")
    print(f"  - Elements dict inputs: {len(elem_dict.get('inputs', []))}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
