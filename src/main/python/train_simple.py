"""
N-gram Language Model - Minimal version for production (model loading only)
Full training code removed - model is pre-trained in selenium_ngram_model.pkl
"""

import pickle
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
    
    def get_probability(self, context: Tuple[str, ...], word: str) -> float:
        """Get probability of word given context."""
        if context not in self.ngrams:
            return 0.0
        
        total_count = sum(self.ngrams[context].values())
        if total_count == 0:
            return 0.0
        
        word_count = self.ngrams[context][word]
        return word_count / total_count
    
    def generate_next_word(self, context: Tuple[str, ...], top_k: int = 5) -> List[Tuple[str, float]]:
        """Generate next word probabilities given context."""
        if context not in self.ngrams:
            return []
        
        counter = self.ngrams[context]
        total = sum(counter.values())
        
        # Get top-k words with their probabilities
        top_words = counter.most_common(top_k)
        return [(word, count/total) for word, count in top_words]
