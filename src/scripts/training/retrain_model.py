"""
Retrain the n-gram model with Page Helper datasets
"""

import json
import pickle
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Tuple

class NGramLanguageModel:
    """N-gram language model for Selenium code generation."""
    
    def __init__(self, n: int = 4):
        self.n = n
        self.ngrams = defaultdict(Counter)
        self.vocab = set()
        self.start_token = '<START>'
        self.end_token = '<END>'
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize code into words and symbols."""
        # Simple tokenization - split on spaces and keep special chars
        tokens = []
        current = ''
        for char in text:
            if char in '();{},."\'':
                if current:
                    tokens.append(current)
                    current = ''
                tokens.append(char)
            elif char == ' ':
                if current:
                    tokens.append(current)
                    current = ''
            else:
                current += char
        if current:
            tokens.append(current)
        return tokens
    
    def train_on_sequence(self, sequence: List[str]):
        """Train on a single sequence."""
        # Add start tokens
        padded = [self.start_token] * (self.n - 1) + sequence + [self.end_token]
        
        # Update vocabulary
        self.vocab.update(sequence)
        
        # Extract n-grams
        for i in range(len(padded) - self.n + 1):
            context = tuple(padded[i:i + self.n - 1])
            next_word = padded[i + self.n - 1]
            self.ngrams[context][next_word] += 1
    
    def train(self, training_data: List[dict]):
        """Train on dataset entries."""
        print(f"[TRAIN] Training on {len(training_data)} examples...")
        
        for i, example in enumerate(training_data):
            if (i + 1) % 50 == 0:
                print(f"[TRAIN] Processed {i + 1}/{len(training_data)} examples")
            
            # Get the code output
            code = example.get('output', '')
            if not code:
                # Try 'code' field for different format
                code = example.get('code', '')
                if not code:
                    # Try code_template for patterns
                    code = example.get('code_template', '')
            
            if code:
                tokens = self.tokenize(code)
                self.train_on_sequence(tokens)
        
        print(f"[TRAIN] Training complete!")
        print(f"[TRAIN] Vocabulary size: {len(self.vocab)}")
        print(f"[TRAIN] N-gram contexts: {len(self.ngrams)}")
    
    def save(self, filename: str):
        """Save model to file."""
        with open(filename, 'wb') as f:
            pickle.dump({
                'n': self.n,
                'ngrams': dict(self.ngrams),
                'vocab': self.vocab
            }, f)
        print(f"[TRAIN] Model saved to {filename}")
    
    def load(self, filename: str):
        """Load model from file."""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            self.n = data['n']
            self.ngrams = defaultdict(Counter, data['ngrams'])
            self.vocab = data['vocab']


def load_datasets():
    """Load all training datasets."""
    datasets = []
    # Get absolute path to resources folder
    script_dir = Path(__file__).parent
    base_path = script_dir / 'src' / 'resources'
    
    dataset_files = [
        'combined-training-dataset.json',
        'page-helper-training-dataset.json',
        'page-helper-patterns-dataset.json',
        'common-web-actions-dataset.json',
    ]
    
    for filename in dataset_files:
        filepath = base_path / filename
        if filepath.exists():
            print(f"[TRAIN] Loading {filename}...")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        datasets.extend(data)
                    print(f"[TRAIN] ✓ Loaded {len(data)} entries from {filename}")
            except Exception as e:
                print(f"[TRAIN] ⚠ Could not load {filename}: {e}")
        else:
            print(f"[TRAIN] ⚠ Not found: {filename}")
    
    return datasets


def main():
    """Main training function."""
    print("="*60)
    print("🚀 RETRAINING N-GRAM MODEL WITH PAGE HELPER DATASETS")
    print("="*60)
    
    # Load all datasets
    print("\n📂 STEP 1: Loading datasets...")
    training_data = load_datasets()
    
    if not training_data:
        print("\n❌ ERROR: No training data found!")
        print("   Make sure you have run: python src/main/python/integrate_page_helper_datasets.py")
        return
    
    print(f"\n✓ Total training examples: {len(training_data)}")
    
    # Initialize model
    print("\n🧠 STEP 2: Initializing model...")
    model = NGramLanguageModel(n=4)
    
    # Train
    print("\n🎓 STEP 3: Training...")
    model.train(training_data)
    
    # Save
    print("\n💾 STEP 4: Saving model...")
    script_dir = Path(__file__).parent
    model_path = script_dir / 'src' / 'resources' / 'selenium_ngram_model.pkl'
    model.save(str(model_path))
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"\n📊 Statistics:")
    print(f"   • Training examples: {len(training_data)}")
    print(f"   • Vocabulary size: {len(model.vocab)} tokens")
    print(f"   • N-gram contexts: {len(model.ngrams)}")
    print(f"\n📁 Model saved to: {model_path}")
    print(f"\n🚀 Next step:")
    print(f"   Restart your API server to use the new model:")
    print(f"   python src/main/python/api_server_modular.py")
    print()


if __name__ == '__main__':
    main()
