"""
Lightweight training script for Selenium SLM using numpy only.
Implements a simple n-gram language model for demonstration.
"""

import numpy as np
import struct
import json
from collections import defaultdict, Counter
from typing import List, Tuple, Dict
import pickle

class NGramLanguageModel:
    """
    N-gram language model for Selenium code generation.
    Uses trigrams (3-grams) for context-aware predictions.
    """
    
    def __init__(self, n: int = 3):
        self.n = n  # N-gram size
        self.ngrams = defaultdict(Counter)
        self.vocab = set()
        self.total_tokens = 0
        
    def train(self, tokens: List[int], epochs: int = 5):
        """Train the n-gram model on token sequences."""
        
        print(f"\n{'='*60}")
        print(f"🚀 TRAINING N-GRAM MODEL (n={self.n})")
        print(f"{'='*60}")
        print(f"Total tokens: {len(tokens):,}")
        print(f"Epochs: {epochs}")
        
        self.total_tokens = len(tokens)
        self.vocab = set(tokens)
        
        print(f"Vocabulary size: {len(self.vocab):,}")
        print(f"Building n-grams...")
        
        # Build n-grams
        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")
            
            for i in range(len(tokens) - self.n):
                # Get context (n-1 tokens) and next token
                context = tuple(tokens[i:i + self.n - 1])
                next_token = tokens[i + self.n - 1]
                
                # Update n-gram counts
                self.ngrams[context][next_token] += 1
                
                if (i + 1) % 1000 == 0:
                    print(f"  Processed {i + 1:,}/{len(tokens) - self.n:,} n-grams", end='\r')
            
            print(f"  Processed {len(tokens) - self.n:,}/{len(tokens) - self.n:,} n-grams ✓")
        
        print(f"\n{'='*60}")
        print(f"✅ Training completed!")
        print(f"Unique contexts: {len(self.ngrams):,}")
        print(f"{'='*60}\n")
    
    def predict_next(self, context: Tuple[int, ...], top_k: int = 10) -> List[Tuple[int, float]]:
        """Predict next token given context."""
        
        if context not in self.ngrams:
            # Fallback to most common tokens
            all_tokens = []
            for counts in self.ngrams.values():
                all_tokens.extend(counts.elements())
            common = Counter(all_tokens).most_common(top_k)
            total = sum(count for _, count in common)
            return [(token, count / total) for token, count in common]
        
        # Get counts for this context
        counts = self.ngrams[context]
        total = sum(counts.values())
        
        # Get top-k predictions with probabilities
        predictions = [(token, count / total) for token, count in counts.most_common(top_k)]
        
        return predictions
    
    def generate(self, start_tokens: List[int], max_length: int = 100, temperature: float = 1.0) -> List[int]:
        """Generate sequence of tokens."""
        
        generated = list(start_tokens)
        
        for _ in range(max_length):
            # Get context
            context = tuple(generated[-(self.n - 1):])
            
            # Predict next token
            predictions = self.predict_next(context, top_k=20)
            
            if not predictions:
                break
            
            # Apply temperature
            tokens, probs = zip(*predictions)
            probs = np.array(probs)
            
            if temperature != 1.0:
                probs = np.power(probs, 1.0 / temperature)
                probs = probs / np.sum(probs)
            
            # Sample next token
            next_token = np.random.choice(tokens, p=probs)
            generated.append(next_token)
        
        return generated
    
    def evaluate(self, test_tokens: List[int]) -> float:
        """Calculate perplexity on test set."""
        
        log_likelihood = 0.0
        count = 0
        
        for i in range(self.n - 1, len(test_tokens)):
            context = tuple(test_tokens[i - self.n + 1:i])
            next_token = test_tokens[i]
            
            predictions = self.predict_next(context, top_k=1000)
            pred_dict = dict(predictions)
            
            prob = pred_dict.get(next_token, 1e-10)
            log_likelihood += np.log(prob)
            count += 1
        
        perplexity = np.exp(-log_likelihood / count)
        return perplexity
    
    def save(self, filepath: str):
        """Save model to file."""
        model_data = {
            'n': self.n,
            'ngrams': dict(self.ngrams),
            'vocab': list(self.vocab),
            'total_tokens': self.total_tokens
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from file."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.n = model_data['n']
        self.ngrams = defaultdict(Counter, model_data['ngrams'])
        self.vocab = set(model_data['vocab'])
        self.total_tokens = model_data['total_tokens']
        
        print(f"[OK] Model loaded from {filepath}")

class SimpleTransformerTrainer:
    """
    Simplified training statistics and metrics tracker.
    Simulates transformer training process with n-gram model.
    """
    
    def __init__(self, bin_file: str):
        self.bin_file = bin_file
        self.tokens = self.load_tokens()
        
    def load_tokens(self) -> List[int]:
        """Load tokens from binary file."""
        print(f"Loading dataset from {self.bin_file}...")
        
        with open(self.bin_file, 'rb') as f:
            num_tokens = struct.unpack('Q', f.read(8))[0]
            tokens = []
            for _ in range(num_tokens):
                token_id = struct.unpack('I', f.read(4))[0]
                tokens.append(token_id)
        
        print(f"✅ Loaded {len(tokens):,} tokens\n")
        return tokens
    
    def split_data(self, train_ratio: float = 0.9) -> Tuple[List[int], List[int]]:
        """Split data into train and validation sets."""
        split_idx = int(len(self.tokens) * train_ratio)
        train_tokens = self.tokens[:split_idx]
        val_tokens = self.tokens[split_idx:]
        
        print(f"Data split:")
        print(f"  Training tokens: {len(train_tokens):,}")
        print(f"  Validation tokens: {len(val_tokens):,}")
        
        return train_tokens, val_tokens
    
    def train(self, epochs: int = 10, ngram_size: int = 4):
        """Train the model."""
        
        print("\n" + "="*60)
        print("🚀 SELENIUM SLM TRAINING")
        print("="*60)
        
        # Split data
        train_tokens, val_tokens = self.split_data(train_ratio=0.9)
        
        # Create model
        model = NGramLanguageModel(n=ngram_size)
        
        # Train
        model.train(train_tokens, epochs=epochs)
        
        # Evaluate
        print("\n📊 EVALUATION")
        print("="*60)
        
        print("Calculating perplexity on validation set...")
        val_perplexity = model.evaluate(val_tokens)
        print(f"Validation Perplexity: {val_perplexity:.2f}")
        
        # Statistics
        print("\n📈 MODEL STATISTICS")
        print("="*60)
        print(f"N-gram size: {model.n}")
        print(f"Vocabulary size: {len(model.vocab):,}")
        print(f"Unique contexts: {len(model.ngrams):,}")
        print(f"Total training tokens: {len(train_tokens):,}")
        
        # Save model
        model_path = 'selenium_ngram_model.pkl'
        model.save(model_path)
        
        # Demo generation
        print("\n🎯 GENERATION DEMO")
        print("="*60)
        
        # Generate from different starting contexts
        demo_contexts = [
            train_tokens[:3],
            train_tokens[100:103],
            train_tokens[500:503]
        ]
        
        for i, context in enumerate(demo_contexts, 1):
            print(f"\nDemo {i}:")
            print(f"  Starting context: {context}")
            generated = model.generate(context, max_length=20, temperature=0.8)
            print(f"  Generated sequence: {generated}")
        
        print("\n" + "="*60)
        print("✨ TRAINING COMPLETED!")
        print("="*60)
        
        return model

def generate_training_report(tokens: List[int]):
    """Generate detailed training report."""
    
    print("\n" + "="*60)
    print("📊 DATASET ANALYSIS REPORT")
    print("="*60)
    
    # Basic statistics
    print(f"\nBasic Statistics:")
    print(f"  Total tokens: {len(tokens):,}")
    print(f"  Unique tokens: {len(set(tokens)):,}")
    print(f"  Average token value: {np.mean(tokens):.2f}")
    print(f"  Token value std dev: {np.std(tokens):.2f}")
    
    # Token frequency
    token_freq = Counter(tokens)
    print(f"\nToken Frequency:")
    print(f"  Most common token: {token_freq.most_common(1)[0]}")
    print(f"  Least common tokens: {sum(1 for count in token_freq.values() if count == 1)}")
    
    # Top 10 tokens
    print(f"\nTop 10 Most Frequent Tokens:")
    for token, count in token_freq.most_common(10):
        pct = (count / len(tokens)) * 100
        print(f"    Token {token:6d}: {count:5d} times ({pct:5.2f}%)")
    
    # Sequence analysis
    print(f"\nSequence Analysis:")
    bigrams = [(tokens[i], tokens[i+1]) for i in range(len(tokens)-1)]
    unique_bigrams = len(set(bigrams))
    print(f"  Unique bigrams: {unique_bigrams:,}")
    
    trigrams = [(tokens[i], tokens[i+1], tokens[i+2]) for i in range(len(tokens)-2)]
    unique_trigrams = len(set(trigrams))
    print(f"  Unique trigrams: {unique_trigrams:,}")
    
    print("="*60)

def main():
    """Main training execution."""
    
    print("\n" + "="*60)
    print("🚀 SELENIUM DATASET SLM TRAINER")
    print("="*60)
    print("Using lightweight n-gram language model")
    print("Optimized for CPU training without GPU requirements")
    print("="*60)
    
    # Initialize trainer
    trainer = SimpleTransformerTrainer('src/resources/selenium_dataset.bin')
    
    # Generate report
    generate_training_report(trainer.tokens)
    
    # Train model
    model = trainer.train(epochs=5, ngram_size=4)
    
    print("\n✅ All training tasks completed successfully!")
    print(f"Model saved as: selenium_ngram_model.pkl")
    print("\nYou can now use this model for inference with inference_simple.py")

if __name__ == "__main__":
    main()
