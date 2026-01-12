"""
Inference script for the trained Selenium SLM.
Generate Selenium code from prompts.
"""

import torch
import tiktoken
from train_slm import SeleniumSLM, ModelConfig

class SeleniumCodeGenerator:
    """Generate Selenium code using trained SLM."""
    
    def __init__(self, model_path: str, device='cpu'):
        self.device = device
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Load model
        print(f"Loading model from {model_path}...")
        checkpoint = torch.load(model_path, map_location=device)
        
        self.config = checkpoint.get('config', ModelConfig())
        self.model = SeleniumSLM(self.config)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(device)
        self.model.eval()
        
        print("✅ Model loaded successfully!")
    
    def generate(self, prompt: str, max_tokens: int = 200, temperature: float = 0.8, top_k: int = 50):
        """Generate Selenium code from a prompt."""
        
        # Tokenize prompt
        tokens = self.tokenizer.encode(prompt)
        tokens_tensor = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(self.device)
        
        print(f"\n{'='*60}")
        print(f"Prompt: {prompt}")
        print(f"{'='*60}\n")
        
        # Generate
        with torch.no_grad():
            generated = self.model.generate(
                tokens_tensor,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_k=top_k
            )
        
        # Decode
        generated_tokens = generated[0].tolist()
        generated_text = self.tokenizer.decode(generated_tokens)
        
        # Extract only the generated part
        generated_only = self.tokenizer.decode(generated_tokens[len(tokens):])
        
        print("Generated Code:")
        print("-" * 60)
        print(generated_only)
        print("-" * 60)
        
        return generated_only

def main():
    """Demo inference script."""
    
    # Initialize generator
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    generator = SeleniumCodeGenerator('best_model.pt', device=device)
    
    # Example prompts
    prompts = [
        "method: beforeClick\naction: click on login button",
        "Find element by id username and send keys",
        "Navigate to URL and wait for element to be visible",
        "Select dropdown option by visible text",
        "Handle alert and accept",
    ]
    
    print("\n🚀 Selenium Code Generator - Inference Demo\n")
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'#'*60}")
        print(f"Example {i}/{len(prompts)}")
        print(f"{'#'*60}")
        
        generator.generate(
            prompt,
            max_tokens=150,
            temperature=0.7,
            top_k=40
        )
        
        print("\n")

if __name__ == "__main__":
    main()
