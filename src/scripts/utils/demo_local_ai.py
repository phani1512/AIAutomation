"""
Demo: Local AI Engine - True AI Understanding Without External APIs
Shows how the tool intelligently understands prompts without calling GPT/Claude
"""

import sys
sys.path.append('src/main/python')

from core.local_ai_engine import LocalAIEngine
from core.inference_improved import ImprovedSeleniumGenerator

def demo_local_ai():
    """Demonstrate the Local AI Engine capabilities."""
    
    print("\n" + "="*80)
    print("🤖 LOCAL AI ENGINE DEMO - NO EXTERNAL API CALLS")
    print("="*80 + "\n")
    
    # Initialize Local AI Engine
    ai = LocalAIEngine()
    
    # Test various natural language prompts
    test_prompts = [
        "go to https://example.com",
        "enter john@example.com in the email field",
        "click on the login button",
        "type 'hello world' into search box",
        "verify that page title contains 'Welcome'",
        "wait for 5 seconds",
        "get text from error message",
        "fill username with admin",
        "press submit",
        "navigate to the home page"
    ]
    
    print("📋 TESTING INTELLIGENT PROMPT UNDERSTANDING:\n")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}: \"{prompt}\"")
        print(f"{'─'*80}")
        
        # Understand the prompt
        result = ai.understand_prompt(prompt)
        
        # Display results
        print(f"✓ Intent: {result['intent']} (confidence: {result['confidence']:.0%})")
        print(f"✓ Entities: {result['entities']}")
        print(f"✓ Execution Plan:")
        for step in result['execution_plan']['steps']:
            print(f"   - {step['action']}: {step}")
        
        if result['execution_plan']['fallbacks']:
            print(f"✓ Fallback Strategies: {len(result['execution_plan']['fallbacks'])} available")
    
    print(f"\n{'='*80}")
    print("📊 LEARNING STATISTICS:")
    print(f"{'='*80}\n")
    
    stats = ai.get_learning_stats()
    print(f"Total executions: {stats['total_executions']}")
    print(f"Learned patterns: {stats['learned_patterns']}")
    print(f"Success rate: {stats['success_rate']:.0%}")

def demo_code_generation():
    """Demonstrate AI-powered code generation."""
    
    print("\n" + "="*80)
    print("💻 LOCAL AI CODE GENERATION DEMO")
    print("="*80 + "\n")
    
    # Initialize generator with Local AI enabled
    gen = ImprovedSeleniumGenerator(silent=True, enable_local_ai=True)
    
    test_cases = [
        ("go to https://google.com", "java"),
        ("enter test@email.com in email", "python"),
        ("click login button", "java"),
        ("wait for 3 seconds", "python")
    ]
    
    print("📝 GENERATING CODE WITH AI UNDERSTANDING:\n")
    
    for i, (prompt, language) in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}: \"{prompt}\" ({language.upper()})")
        print(f"{'─'*80}\n")
        
        # Generate code using Local AI
        code = gen.generate_clean(prompt, language=language)
        
        print(f"Generated Code:")
        print(f"┌{'─'*78}┐")
        for line in code.split('\n'):
            print(f"│ {line:<76} │")
        print(f"└{'─'*78}┘")

def demo_context_awareness():
    """Demonstrate context-aware understanding."""
    
    print("\n" + "="*80)
    print("🧠 CONTEXT-AWARE AI DEMO")
    print("="*80 + "\n")
    
    ai = LocalAIEngine()
    
    # Simulate execution context
    context = {
        'current_url': 'https://example.com/dashboard',
        'available_elements': [
            {'type': 'input', 'id': 'username', 'text': ''},
            {'type': 'input', 'id': 'password', 'text': ''},
            {'type': 'button', 'id': 'login-btn', 'text': 'Login'},
            {'type': 'button', 'id': 'cancel-btn', 'text': 'Cancel'}
        ]
    }
    
    prompt = "click login"
    
    print(f"Prompt: \"{prompt}\"")
    print(f"\nPage Context:")
    print(f"  URL: {context['current_url']}")
    print(f"  Available elements: {len(context['available_elements'])}")
    
    # Understand with context
    result = ai.understand_prompt(prompt, context)
    
    print(f"\n✓ Intent: {result['intent']}")
    print(f"✓ Matched Element: {result.get('enhanced', {}).get('matched_element')}")
    print(f"✓ Execution Plan:")
    for step in result['execution_plan']['steps']:
        print(f"   - {step['action']}: {step}")

def main():
    """Run all demos."""
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  🤖 LOCAL AI ENGINE - INTELLIGENT TESTING WITHOUT EXTERNAL APIs  ".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Run demos
    demo_local_ai()
    demo_code_generation()
    demo_context_awareness()
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE - Your tool IS the AI!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
