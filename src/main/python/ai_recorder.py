"""
Enhanced ActionRecorder with AI-powered locator generation.
Integrates with trained SLM for intelligent code generation.
"""

import requests
import json
from typing import List, Dict, Tuple

class AIEnhancedRecorder:
    """
    Recorder with AI capabilities for smart locator selection.
    """
    
    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url
        self.recorded_actions = []
    
    def record_action(self, element_info: Dict, action_type: str, value: str = None):
        """
        Record action with AI-enhanced locator suggestion.
        
        Args:
            element_info: Dictionary with element attributes (id, name, class, tag)
            action_type: Type of action (click, sendKeys, select, etc.)
            value: Value for the action (text to type, option to select, etc.)
        """
        
        # Get AI suggestions for best locator
        suggested_locators = self.get_locator_suggestions(
            element_info.get('tag', 'unknown'),
            action_type,
            element_info
        )
        
        # Select best locator (first suggestion or fallback)
        best_locator = suggested_locators[0] if suggested_locators else self._generate_fallback_locator(element_info)
        
        # Record the action
        action = {
            'step': len(self.recorded_actions) + 1,
            'action': action_type,
            'locator': best_locator,
            'value': value,
            'element_type': element_info.get('tag'),
            'ai_suggested': len(suggested_locators) > 0,
            'alternative_locators': suggested_locators[1:4] if len(suggested_locators) > 1 else []
        }
        
        self.recorded_actions.append(action)
        
        print(f"✓ Recorded: {action_type} on {best_locator}" + (f" with value '{value}'" if value else ""))
        if action['alternative_locators']:
            print(f"  Alternatives: {', '.join(action['alternative_locators'])}")
    
    def get_locator_suggestions(self, element_type: str, action: str, attributes: Dict) -> List[str]:
        """Get AI-powered locator suggestions from the trained model."""
        
        try:
            response = requests.post(
                f"{self.api_url}/suggest-locator",
                json={
                    'element_type': element_type,
                    'action': action,
                    'attributes': attributes
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('suggested_locators', [])
            else:
                print(f"Warning: API returned status {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not connect to AI service: {e}")
            return []
    
    def _generate_fallback_locator(self, element_info: Dict) -> str:
        """Generate locator using traditional priority order."""
        
        if element_info.get('id'):
            return f'By.id("{element_info["id"]}")'
        elif element_info.get('name'):
            return f'By.name("{element_info["name"]}")'
        elif element_info.get('class'):
            classes = element_info['class'].split()
            return f'By.className("{classes[0]}")'
        elif element_info.get('tag'):
            return f'By.tagName("{element_info["tag"]}")'
        else:
            return 'By.xpath("//unknown")'
    
    def generate_test_code(self, test_name: str = "AIGeneratedTest") -> str:
        """Generate complete test code from recorded actions."""
        
        code = f"""package com.testing.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.Select;
import org.testng.annotations.*;

public class {test_name} {{
    private WebDriver driver;
    
    @BeforeMethod
    public void setUp() {{
        driver = new ChromeDriver();
    }}
    
    @Test
    public void aiGeneratedTest() {{
"""
        
        for action in self.recorded_actions:
            code += f"        // Step {action['step']}"
            if action['ai_suggested']:
                code += " (AI-suggested locator)\n"
            else:
                code += "\n"
            
            if action['action'] == 'click':
                code += f"        driver.findElement({action['locator']}).click();\n"
            elif action['action'] == 'sendKeys':
                code += f"        driver.findElement({action['locator']}).sendKeys(\"{action['value']}\");\n"
            elif action['action'] == 'select':
                code += f"        new Select(driver.findElement({action['locator']})).selectByVisibleText(\"{action['value']}\");\n"
            elif action['action'] == 'clear':
                code += f"        driver.findElement({action['locator']}).clear();\n"
            
            code += "\n"
        
        code += """    }
    
    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
"""
        
        return code
    
    def get_action_statistics(self) -> Dict:
        """Get statistics about recorded actions."""
        
        ai_suggested_count = sum(1 for a in self.recorded_actions if a['ai_suggested'])
        
        action_types = {}
        for action in self.recorded_actions:
            action_type = action['action']
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        return {
            'total_actions': len(self.recorded_actions),
            'ai_suggested': ai_suggested_count,
            'traditional': len(self.recorded_actions) - ai_suggested_count,
            'action_breakdown': action_types
        }

# Example usage
if __name__ == "__main__":
    print("="*60)
    print("🤖 AI-Enhanced Action Recorder Demo")
    print("="*60)
    
    recorder = AIEnhancedRecorder()
    
    # Simulate recording actions
    print("\nRecording user actions...\n")
    
    recorder.record_action(
        element_info={'id': 'username', 'name': 'user', 'class': 'form-control', 'tag': 'input'},
        action_type='sendKeys',
        value='testuser'
    )
    
    recorder.record_action(
        element_info={'id': 'password', 'name': 'pass', 'class': 'form-control', 'tag': 'input'},
        action_type='sendKeys',
        value='password123'
    )
    
    recorder.record_action(
        element_info={'id': 'loginBtn', 'class': 'btn btn-primary', 'tag': 'button'},
        action_type='click'
    )
    
    # Generate test code
    print("\n" + "="*60)
    print("Generated Test Code:")
    print("="*60)
    print(recorder.generate_test_code())
    
    # Statistics
    stats = recorder.get_action_statistics()
    print("="*60)
    print("Recording Statistics:")
    print("="*60)
    print(f"Total Actions: {stats['total_actions']}")
    print(f"AI-Suggested: {stats['ai_suggested']}")
    print(f"Traditional: {stats['traditional']}")
    print(f"Action Types: {stats['action_breakdown']}")
    print("="*60)
