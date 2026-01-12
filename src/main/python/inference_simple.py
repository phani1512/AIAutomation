"""
Inference script for trained Selenium n-gram language model.
Generate Selenium code patterns from trained model.
"""

import pickle
import tiktoken
from train_simple import NGramLanguageModel

class SeleniumCodeGenerator:
    """Generate Selenium code using trained n-gram model."""
    
    def __init__(self, model_path: str = 'selenium_ngram_model.pkl'):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        print(f"Loading model from {model_path}...")
        self.model = NGramLanguageModel()
        self.model.load(model_path)
        
        print(f"Model ready!")
        print(f"  Vocabulary size: {len(self.model.vocab):,}")
        print(f"  Unique contexts: {len(self.model.ngrams):,}")
        print()
    
    def generate_from_prompt(self, prompt: str, max_tokens: int = 50, temperature: float = 0.7):
        """Generate code from text prompt."""
        
        print("="*60)
        print(f"Prompt: {prompt}")
        print("="*60)
        
        # Tokenize prompt
        tokens = self.tokenizer.encode(prompt)
        print(f"Input tokens: {tokens[:10]}..." if len(tokens) > 10 else f"Input tokens: {tokens}")
        
        # Generate
        generated_tokens = self.model.generate(
            tokens,
            max_length=max_tokens,
            temperature=temperature
        )
        
        # Decode
        generated_text = self.tokenizer.decode(generated_tokens)
        
        print(f"\nGenerated Output:")
        print("-"*60)
        print(generated_text)
        print("-"*60)
        print()
        
        return generated_text
    
    def generate_selenium_patterns(self):
        """Generate common Selenium code patterns."""
        
        print("\n" + "="*60)
        print("🎯 SELENIUM CODE GENERATION EXAMPLES")
        print("="*60 + "\n")
        
        examples = [
            {
                "name": "Click Button Pattern",
                "prompt": "action: click\nmethod: beforeClick\nelement_type: button",
                "tokens": 40
            },
            {
                "name": "Send Keys Pattern",
                "prompt": "action: sendKeys\nmethod: beforeSendKeys\nelement_type: input",
                "tokens": 40
            },
            {
                "name": "Locator Pattern",
                "prompt": "locator: By.id\naction: find",
                "tokens": 40
            },
            {
                "name": "Navigation Pattern",
                "prompt": "method: beforeGet\naction: navigate",
                "tokens": 40
            },
            {
                "name": "Wait Pattern",
                "prompt": "category: Waits_ExpectedConditions\nmethod: visibilityOfElementLocated",
                "tokens": 50
            }
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n{'#'*60}")
            print(f"Example {i}: {example['name']}")
            print(f"{'#'*60}\n")
            
            self.generate_from_prompt(
                example['prompt'],
                max_tokens=example['tokens'],
                temperature=0.7
            )
    
    def interactive_mode(self):
        """Interactive generation mode."""
        
        print("\n" + "="*60)
        print("🤖 INTERACTIVE SELENIUM CODE GENERATOR")
        print("="*60)
        print("Enter prompts to generate Selenium code patterns")
        print("Commands:")
        print("  'quit' or 'exit' - Exit interactive mode")
        print("  'examples' - Show example generations")
        print("="*60 + "\n")
        
        while True:
            try:
                prompt = input("Enter prompt (or 'quit'): ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if prompt.lower() == 'examples':
                    self.generate_selenium_patterns()
                    continue
                
                if not prompt:
                    continue
                
                self.generate_from_prompt(prompt, max_tokens=60, temperature=0.7)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

def main():
    """Main execution."""
    
    print("\n" + "="*60)
    print("🚀 SELENIUM CODE GENERATOR")
    print("="*60)
    print("Trained on Selenium WebDriver methods and patterns")
    print("="*60 + "\n")
    
    # Initialize generator
    generator = SeleniumCodeGenerator('selenium_ngram_model.pkl')
    
    # Show examples
    generator.generate_selenium_patterns()
    
    # Interactive mode
    print("\n" + "="*60)
    response = input("Enter interactive mode? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        generator.interactive_mode()
    else:
        print("\n✨ Demo complete!")

if __name__ == "__main__":
    main()
