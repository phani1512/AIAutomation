"""
🚀 Browser Control + AI Prompts - Interactive Demo Script

This script demonstrates how to use the web interface to test complete workflows
using Browser Control combined with AI-generated prompts.

Run this demo to see the workflow in action!
"""

import requests
import time
import json

# API Configuration
API_URL = "http://localhost:5001"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, description):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}STEP {step_num}: {description}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

def print_prompt(prompt):
    print(f"{Colors.YELLOW}📝 AI Prompt:{Colors.ENDC} {Colors.BOLD}{prompt}{Colors.ENDC}")

def print_code(code):
    print(f"{Colors.BLUE}💻 Generated Code:{Colors.ENDC}")
    print(f"{Colors.CYAN}{code}{Colors.ENDC}")

def print_result(success, message):
    color = Colors.GREEN if success else Colors.RED
    icon = "✅" if success else "❌"
    print(f"{color}{icon} {message}{Colors.ENDC}")

def wait_for_user():
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")

def initialize_browser():
    """Step 1: Initialize the browser"""
    print_step(1, "Initialize Browser")
    
    print("🌐 Initializing Chrome browser (non-headless)...")
    
    try:
        response = requests.post(
            f"{API_URL}/browser/initialize",
            json={
                "browser": "chrome",
                "headless": False
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.ok:
            print_result(True, "Browser initialized successfully!")
            print(f"{Colors.GREEN}Browser window should now be visible{Colors.ENDC}")
            return True
        else:
            print_result(False, f"Failed to initialize browser: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error initializing browser: {str(e)}")
        return False

def generate_code_from_prompt(prompt):
    """Generate code using AI prompt"""
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"}
        )
        
        if response.ok:
            data = response.json()
            if data.get("success"):
                return data.get("code", "")
        return None
    except Exception as e:
        print(f"Error generating code: {str(e)}")
        return None

def execute_code(code):
    """Execute code in the browser"""
    try:
        response = requests.post(
            f"{API_URL}/browser/execute",
            json={"code": code},
            headers={"Content-Type": "application/json"}
        )
        
        if response.ok:
            data = response.json()
            if data.get("success"):
                return True, data.get("result", "Executed successfully")
            else:
                return False, data.get("error", "Unknown error")
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def execute_workflow_step(step_num, description, prompt, wait=2):
    """Execute a single workflow step: Generate + Execute"""
    print_step(step_num, description)
    
    # Show the prompt
    print_prompt(prompt)
    
    # Generate code
    print(f"\n{Colors.BLUE}🤖 Generating code with AI...{Colors.ENDC}")
    code = generate_code_from_prompt(prompt)
    
    if not code:
        print_result(False, "Failed to generate code")
        return False
    
    print_code(code)
    
    # Execute code
    print(f"\n{Colors.BLUE}▶️  Executing code in browser...{Colors.ENDC}")
    success, result = execute_code(code)
    
    if success:
        print_result(True, f"Step completed successfully!")
        if result and result != "Executed successfully":
            print(f"{Colors.GREEN}Result: {result}{Colors.ENDC}")
    else:
        print_result(False, f"Execution failed: {result}")
        return False
    
    # Wait between steps
    time.sleep(wait)
    return True

def close_browser():
    """Close the browser"""
    print_step("FINAL", "Close Browser")
    
    try:
        response = requests.post(
            f"{API_URL}/browser/close",
            headers={"Content-Type": "application/json"}
        )
        
        if response.ok:
            print_result(True, "Browser closed successfully!")
            return True
        else:
            print_result(False, f"Failed to close browser: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error closing browser: {str(e)}")
        return False

def run_demo_workflow():
    """Run the complete demo workflow"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🚀 Browser Control + AI Prompts - Live Demo Workflow        ║")
    print("║                                                                ║")
    print("║   This demo will test a complete login-to-purchase flow       ║")
    print("║   on https://www.saucedemo.com                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    print(f"{Colors.YELLOW}📋 Workflow Overview:{Colors.ENDC}")
    print("  1. Initialize Browser")
    print("  2. Navigate to website")
    print("  3. Login")
    print("  4. Sort products by price")
    print("  5. Add product to cart")
    print("  6. Verify cart badge")
    print("  7. Go to cart")
    print("  8. Proceed to checkout")
    print("  9. Fill checkout form")
    print(" 10. Verify checkout overview")
    print(" 11. Complete order")
    print(" 12. Close browser")
    
    wait_for_user()
    
    # Step 1: Initialize Browser
    if not initialize_browser():
        print(f"\n{Colors.RED}❌ Demo failed at browser initialization{Colors.ENDC}")
        return
    
    wait_for_user()
    
    # Step 2: Navigate to website
    if not execute_workflow_step(
        2,
        "Navigate to Website",
        "navigate to https://www.saucedemo.com"
    ):
        return
    
    wait_for_user()
    
    # Step 3: Login
    if not execute_workflow_step(
        3,
        "Login to Application",
        "enter standard_user in username field with id user-name and secret_sauce in password field with id password then click button with id login-button"
    ):
        return
    
    wait_for_user()
    
    # Step 4: Sort products
    if not execute_workflow_step(
        4,
        "Sort Products by Price",
        "select Price (low to high) from dropdown with class product_sort_container"
    ):
        return
    
    wait_for_user()
    
    # Step 5: Add to cart
    if not execute_workflow_step(
        5,
        "Add First Product to Cart",
        "click first add to cart button"
    ):
        return
    
    wait_for_user()
    
    # Step 6: Verify cart badge
    if not execute_workflow_step(
        6,
        "Verify Cart Badge",
        "verify shopping cart badge shows 1"
    ):
        return
    
    wait_for_user()
    
    # Step 7: Go to cart
    if not execute_workflow_step(
        7,
        "Navigate to Shopping Cart",
        "click shopping cart icon"
    ):
        return
    
    wait_for_user()
    
    # Step 8: Checkout
    if not execute_workflow_step(
        8,
        "Proceed to Checkout",
        "click checkout button with id checkout"
    ):
        return
    
    wait_for_user()
    
    # Step 9: Fill checkout form
    if not execute_workflow_step(
        9,
        "Fill Checkout Information",
        "enter John in field with id first-name and Doe in field with id last-name and 12345 in field with id postal-code then click button with id continue"
    ):
        return
    
    wait_for_user()
    
    # Step 10: Verify overview
    if not execute_workflow_step(
        10,
        "Verify Checkout Overview",
        "verify current url contains checkout-step-two"
    ):
        return
    
    wait_for_user()
    
    # Step 11: Complete order
    if not execute_workflow_step(
        11,
        "Complete the Order",
        "click finish button with id finish"
    ):
        return
    
    wait_for_user()
    
    # Step 12: Close browser
    close_browser()
    
    # Success summary
    print(f"\n{Colors.GREEN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║               ✅ DEMO WORKFLOW COMPLETED SUCCESSFULLY!         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    print(f"{Colors.CYAN}🎉 Summary:{Colors.ENDC}")
    print(f"  • {Colors.GREEN}12 steps executed{Colors.ENDC}")
    print(f"  • {Colors.GREEN}All prompts converted to working code{Colors.ENDC}")
    print(f"  • {Colors.GREEN}Complete E2E flow in single browser session{Colors.ENDC}")
    print(f"  • {Colors.GREEN}No manual code writing required!{Colors.ENDC}")
    
    print(f"\n{Colors.YELLOW}💡 Next Steps:{Colors.ENDC}")
    print(f"  1. Try this workflow in the web interface (http://localhost:5001)")
    print(f"  2. Create your own workflows with different prompts")
    print(f"  3. Check AI_PROMPTS_GUIDE.html for 100+ prompt examples")
    print(f"  4. Read BROWSER_AI_WORKFLOW_GUIDE.md for more patterns")

def check_server():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.ok
    except:
        return False

if __name__ == "__main__":
    # Check if server is running
    print(f"\n{Colors.BLUE}Checking API server...{Colors.ENDC}")
    
    if not check_server():
        print(f"{Colors.RED}❌ API server is not running!{Colors.ENDC}")
        print(f"\n{Colors.YELLOW}Please start the server first:{Colors.ENDC}")
        print(f"  python src/main/python/api_server_improved.py")
        print(f"\nOr use the VS Code task: 'Start API Server'")
        exit(1)
    
    print(f"{Colors.GREEN}✅ API server is running at {API_URL}{Colors.ENDC}")
    
    # Run the demo
    try:
        run_demo_workflow()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Demo interrupted by user{Colors.ENDC}")
        print(f"{Colors.BLUE}Attempting to close browser...{Colors.ENDC}")
        try:
            close_browser()
        except:
            pass
    except Exception as e:
        print(f"\n{Colors.RED}❌ Demo failed with error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
