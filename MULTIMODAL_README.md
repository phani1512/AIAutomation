# 📸 Multi-modal AI Test Generator

## Overview

Generate automated test code from UI screenshots using computer vision and AI. This feature enables you to create tests by simply uploading screenshots of your application.

## Features

✨ **Visual Element Detection**
- Automatically detects buttons, input fields, and text regions
- Uses OpenCV for computer vision analysis
- Provides bounding box coordinates for each element

🤖 **AI-Powered Code Generation**
- Generates complete Selenium test code from screenshots
- Understands user intent (e.g., "test login flow")
- Creates locator strategies for detected elements

🎨 **Visual Annotations**
- Annotates screenshots with detected elements
- Color-coded bounding boxes (green=buttons, blue=inputs, red=text)
- Helps verify detection accuracy

📊 **Multi-Screenshot Flows**
- Generate tests from sequences of screenshots
- Captures complete user journeys
- Creates unified test code for entire flows

## Installation

### Required Dependencies

```bash
pip install opencv-python pillow numpy
```

Add to your `requirements.txt`:
```
opencv-python==4.8.1.78
pillow==10.1.0
numpy==1.24.3
```

## Usage

### 1. Web Interface

Navigate to: `http://localhost:5002/screenshot-generator.html`

**Steps:**
1. Upload or drag-drop a screenshot
2. Enter test intent (e.g., "Test login with valid credentials")
3. Click "Analyze Screenshot" to detect elements
4. Click "Generate Test Code" to create automation code
5. Click "Show Element Detection" to see annotated screenshot

### 2. API Endpoints

#### Analyze Screenshot
```bash
POST /screenshot/analyze
Content-Type: application/json

{
  "screenshot": "base64_encoded_image_data",
  "intent": "Test login flow"
}
```

**Response:**
```json
{
  "elements": {
    "buttons": [...],
    "inputs": [...],
    "text_regions": [...]
  },
  "suggested_actions": [...],
  "total_elements": 10
}
```

#### Generate Code
```bash
POST /screenshot/generate-code
Content-Type: application/json

{
  "screenshot": "base64_encoded_image_data",
  "intent": "Test login flow",
  "test_name": "LoginTest"
}
```

**Response:**
```json
{
  "code": "# Generated Python test code...",
  "elements_detected": 10,
  "actions_generated": 5
}
```

#### Annotate Screenshot
```bash
POST /screenshot/annotate
Content-Type: application/json

{
  "screenshot": "base64_encoded_image_data"
}
```

**Response:**
```json
{
  "annotated_screenshot": "base64_annotated_image",
  "elements": {...}
}
```

### 3. Python API

```python
from visual_element_detector import VisualElementDetector
from multimodal_generator import MultiModalCodeGenerator

# Initialize
detector = VisualElementDetector()
generator = MultiModalCodeGenerator(detector)

# Analyze screenshot
analysis = generator.analyze_screenshot(
    screenshot_data="path/to/screenshot.png",
    user_intent="Test login flow"
)

# Generate test code
code = generator.generate_test_code_from_screenshot(
    screenshot_data="path/to/screenshot.png",
    user_intent="Test login flow",
    test_name="LoginTest"
)

print(code)
```

## Architecture

### Components

**1. visual_element_detector.py**
- Core computer vision module
- Detects UI elements using OpenCV
- Methods:
  - `detect_buttons()` - Identifies button elements
  - `detect_input_fields()` - Finds input fields
  - `detect_text_regions()` - Locates text areas
  - `annotate_screenshot()` - Adds visual annotations

**2. multimodal_generator.py**
- AI-powered code generation
- Translates visual elements into test code
- Methods:
  - `analyze_screenshot()` - Complete screenshot analysis
  - `generate_test_code_from_screenshot()` - Creates test code
  - `generate_from_screenshot_sequence()` - Multi-step flows

**3. screenshot_handler.py**
- Flask API endpoints
- Handles HTTP requests for screenshot processing
- Routes:
  - `/screenshot/analyze` - Element detection
  - `/screenshot/generate-code` - Code generation
  - `/screenshot/annotate` - Visual annotation

**4. screenshot-generator.html**
- User interface
- Drag-and-drop screenshot upload
- Real-time analysis and code display

## Element Detection Algorithm

### Buttons
- Aspect ratio: 1.5 - 6.0
- Area: 1,000 - 50,000 pixels
- Detection: Edge detection + contour analysis

### Input Fields
- Aspect ratio: ≥ 3.0 (long and thin)
- Height: ≤ 60 pixels
- Area: 2,000 - 100,000 pixels
- Detection: Adaptive thresholding + morphological operations

### Text Regions
- Variable dimensions
- Morphological dilation for text grouping
- Contour-based region extraction

## Example Output

### Input
- Screenshot of login page
- Intent: "Test login with valid credentials"

### Generated Code
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestLoginTest:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
    
    def teardown_method(self):
        if self.driver:
            self.driver.quit()
    
    def test_logintest(self):
        """Test generated from visual analysis"""
        wait = WebDriverWait(self.driver, 15)
        
        # Step 1: Enter email in first input field
        try:
            elem = wait.until(EC.presence_of_element_located(
                By.xpath("//input[@type='email']")))
            elem.clear()
            elem.send_keys('test@example.com')
        except:
            # Fallback: click at visual coordinates
            self.driver.execute_script('arguments[0].click()', 
                self.driver.find_element(By.TAG_NAME, 'input'))
        time.sleep(0.5)

        # Step 2: Enter password in second input field
        # ... (similar code for password)
        
        # Step 3: Click login button
        # ... (button click code)
```

## Advanced Features

### Multi-Screenshot Flows

```python
screenshots = [
    "base64_screenshot_1",  # Login page
    "base64_screenshot_2",  # Dashboard
    "base64_screenshot_3"   # Profile page
]

descriptions = [
    "Login with credentials",
    "Navigate to dashboard",
    "Open profile settings"
]

code = generator.generate_from_screenshot_sequence(screenshots, descriptions)
```

### Custom Element Templates

```python
detector = VisualElementDetector()

# Add custom element template for matching
detector.element_templates['submit_button'] = {
    'color': [66, 133, 244],  # Blue
    'min_width': 80,
    'min_height': 30
}
```

## Limitations

⚠️ **Current Limitations:**
- Element detection accuracy depends on screenshot quality
- Text extraction (OCR) not yet implemented
- Works best with standard web UI patterns
- May miss custom-styled elements

🚀 **Future Enhancements:**
- OCR integration for text reading
- Machine learning-based element classification
- Support for mobile screenshots
- Integration with GPT-4 Vision API
- Element similarity matching
- Context-aware locator generation

## Troubleshooting

### Issue: No elements detected
**Solution:** 
- Ensure screenshot has clear UI boundaries
- Try higher resolution screenshots
- Check if UI elements have distinct borders

### Issue: Wrong element types detected
**Solution:**
- Adjust detection thresholds in `visual_element_detector.py`
- Use annotated view to verify detections
- Provide clearer user intent

### Issue: Generated code doesn't work
**Solution:**
- Verify locators match actual HTML
- Use self-healing locator mode
- Manually refine generated locators

## Integration with Existing Project

The multi-modal feature integrates seamlessly:

1. **Register Blueprint** in `api_server_modular.py`:
```python
from screenshot_handler import screenshot_bp
app.register_blueprint(screenshot_bp)
```

2. **Use with Recorder**:
- Take screenshot during recording
- Analyze for additional element suggestions
- Enhance recorded tests with visual validation

3. **Combine with Self-Healing**:
- Visual detection provides fallback coordinates
- Self-healing uses visual hints when DOM changes

## API Reference

### VisualElementDetector

```python
class VisualElementDetector:
    def detect_all_elements(screenshot_data: str) -> Dict
    def find_element_at_position(x: int, y: int, elements: Dict) -> Dict
    def annotate_screenshot(elements: Dict, output_path: str) -> np.ndarray
```

### MultiModalCodeGenerator

```python
class MultiModalCodeGenerator:
    def analyze_screenshot(screenshot_data: str, user_intent: str) -> Dict
    def generate_test_code_from_screenshot(
        screenshot_data: str, 
        user_intent: str, 
        test_name: str
    ) -> str
    def generate_from_screenshot_sequence(
        screenshots: List[str], 
        descriptions: List[str]
    ) -> str
```

## Contributing

To enhance the multi-modal feature:

1. **Improve Detection Accuracy**
   - Experiment with different CV techniques
   - Add machine learning classifiers
   - Implement element clustering

2. **Add New Element Types**
   - Checkboxes, radio buttons
   - Dropdowns, modals
   - Custom components

3. **Integrate Advanced AI**
   - GPT-4 Vision API
   - Custom trained models
   - Semantic understanding

## License

Part of WebAutomation project - Same license applies
