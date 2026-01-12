"""
Train a Small Language Model (SLM) on the tokenized Selenium dataset.
This script implements a transformer-based language model for code generation.
"""

import torch
import torch.nn as nn
from torch.nn import functional as F
import struct
import os
import math
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class ModelConfig:
    vocab_size: int = 100277  # cl100k_base vocabulary size
    context_length: int = 256  # Maximum sequence length
    d_model: int = 384  # Embedding dimension
    n_heads: int = 6  # Number of attention heads
    n_layers: int = 6  # Number of transformer layers
    dropout: float = 0.1
    bias: bool = False  # Use bias in Linear and LayerNorm layers
    
class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        assert config.d_model % config.n_heads == 0
        
        self.n_heads = config.n_heads
        self.d_model = config.d_model
        self.head_dim = config.d_model // config.n_heads
        
        # Query, Key, Value projections
        self.qkv_proj = nn.Linear(config.d_model, 3 * config.d_model, bias=config.bias)
        self.out_proj = nn.Linear(config.d_model, config.d_model, bias=config.bias)
        
        # Regularization
        self.attn_dropout = nn.Dropout(config.dropout)
        self.resid_dropout = nn.Dropout(config.dropout)
        
        # Causal mask
        self.register_buffer(
            "causal_mask",
            torch.tril(torch.ones(config.context_length, config.context_length))
            .view(1, 1, config.context_length, config.context_length)
        )
    
    def forward(self, x):
        B, T, C = x.size()  # Batch, Time (sequence), Channels (d_model)
        
        # Calculate query, key, value
        qkv = self.qkv_proj(x)
        q, k, v = qkv.split(self.d_model, dim=2)
        
        # Reshape for multi-head attention
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)  # (B, nh, T, hs)
        q = q.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)  # (B, nh, T, hs)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)  # (B, nh, T, hs)
        
        # Attention weights
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        att = att.masked_fill(self.causal_mask[:, :, :T, :T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.attn_dropout(att)
        
        # Apply attention to values
        y = att @ v  # (B, nh, T, hs)
        y = y.transpose(1, 2).contiguous().view(B, T, C)  # (B, T, C)
        
        # Output projection
        y = self.resid_dropout(self.out_proj(y))
        return y

class FeedForward(nn.Module):
    """Position-wise feed-forward network."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.fc1 = nn.Linear(config.d_model, 4 * config.d_model, bias=config.bias)
        self.fc2 = nn.Linear(4 * config.d_model, config.d_model, bias=config.bias)
        self.dropout = nn.Dropout(config.dropout)
        self.gelu = nn.GELU()
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.gelu(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x

class TransformerBlock(nn.Module):
    """Single transformer block with attention and feed-forward."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.d_model, bias=config.bias)
        self.attn = MultiHeadAttention(config)
        self.ln2 = nn.LayerNorm(config.d_model, bias=config.bias)
        self.ffn = FeedForward(config)
    
    def forward(self, x):
        # Pre-norm architecture
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x

class SeleniumSLM(nn.Module):
    """Small Language Model for Selenium code generation."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # Token and position embeddings
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.position_embedding = nn.Embedding(config.context_length, config.d_model)
        self.dropout = nn.Dropout(config.dropout)
        
        # Transformer blocks
        self.blocks = nn.ModuleList([TransformerBlock(config) for _ in range(config.n_layers)])
        
        # Final layer norm
        self.ln_f = nn.LayerNorm(config.d_model, bias=config.bias)
        
        # Language modeling head
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        
        # Weight tying
        self.token_embedding.weight = self.lm_head.weight
        
        # Initialize weights
        self.apply(self._init_weights)
        
        print(f"Model initialized with {self.get_num_params()/1e6:.2f}M parameters")
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def get_num_params(self):
        """Return the number of parameters in the model."""
        return sum(p.numel() for p in self.parameters())
    
    def forward(self, idx, targets=None):
        B, T = idx.size()
        assert T <= self.config.context_length, f"Sequence length {T} exceeds context length {self.config.context_length}"
        
        # Token embeddings
        tok_emb = self.token_embedding(idx)  # (B, T, d_model)
        
        # Position embeddings
        pos = torch.arange(0, T, dtype=torch.long, device=idx.device)  # (T)
        pos_emb = self.position_embedding(pos)  # (T, d_model)
        
        # Combine embeddings
        x = self.dropout(tok_emb + pos_emb)
        
        # Transformer blocks
        for block in self.blocks:
            x = block(x)
        
        # Final layer norm
        x = self.ln_f(x)
        
        # Language modeling head
        logits = self.lm_head(x)  # (B, T, vocab_size)
        
        # Calculate loss if targets provided
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-1)
        
        return logits, loss
    
    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        """Generate new tokens."""
        for _ in range(max_new_tokens):
            # Crop context if needed
            idx_cond = idx if idx.size(1) <= self.config.context_length else idx[:, -self.config.context_length:]
            
            # Forward pass
            logits, _ = self(idx_cond)
            
            # Get logits for last position
            logits = logits[:, -1, :] / temperature
            
            # Top-k sampling
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')
            
            # Sample from distribution
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            
            # Append to sequence
            idx = torch.cat((idx, idx_next), dim=1)
        
        return idx

class SeleniumDataset(torch.utils.data.Dataset):
    """Dataset loader for tokenized Selenium data."""
    
    def __init__(self, bin_file: str, context_length: int):
        self.context_length = context_length
        
        # Load tokens from binary file
        print(f"Loading dataset from {bin_file}...")
        with open(bin_file, 'rb') as f:
            num_tokens = struct.unpack('Q', f.read(8))[0]
            self.tokens = []
            for _ in range(num_tokens):
                token_id = struct.unpack('I', f.read(4))[0]
                self.tokens.append(token_id)
        
        self.tokens = torch.tensor(self.tokens, dtype=torch.long)
        print(f"Loaded {len(self.tokens):,} tokens")
    
    def __len__(self):
        return len(self.tokens) - self.context_length
    
    def __getitem__(self, idx):
        # Get sequence of context_length + 1 tokens
        chunk = self.tokens[idx:idx + self.context_length + 1]
        x = chunk[:-1]  # Input
        y = chunk[1:]   # Target (shifted by 1)
        return x, y

class Trainer:
    """Training loop for the SLM."""
    
    def __init__(self, model, train_dataset, config, device='cuda'):
        self.model = model
        self.train_dataset = train_dataset
        self.config = config
        self.device = device
        
        # Move model to device
        self.model.to(device)
        
        # Optimizer
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=3e-4,
            betas=(0.9, 0.95),
            weight_decay=0.1
        )
        
        # Learning rate scheduler
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=1000,
            eta_min=3e-5
        )
    
    def train(self, num_epochs: int, batch_size: int, eval_interval: int = 100):
        """Main training loop."""
        
        # DataLoader
        train_loader = torch.utils.data.DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=True
        )
        
        print("\n" + "="*60)
        print("🚀 TRAINING STARTED")
        print("="*60)
        print(f"Device: {self.device}")
        print(f"Epochs: {num_epochs}")
        print(f"Batch size: {batch_size}")
        print(f"Steps per epoch: {len(train_loader)}")
        print(f"Total steps: {num_epochs * len(train_loader)}")
        print("="*60 + "\n")
        
        global_step = 0
        best_loss = float('inf')
        
        for epoch in range(num_epochs):
            self.model.train()
            epoch_loss = 0.0
            epoch_start = time.time()
            
            for batch_idx, (x, y) in enumerate(train_loader):
                # Move to device
                x = x.to(self.device)
                y = y.to(self.device)
                
                # Forward pass
                logits, loss = self.model(x, y)
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                
                # Update weights
                self.optimizer.step()
                
                epoch_loss += loss.item()
                global_step += 1
                
                # Logging
                if (batch_idx + 1) % eval_interval == 0 or (batch_idx + 1) == len(train_loader):
                    avg_loss = epoch_loss / (batch_idx + 1)
                    lr = self.optimizer.param_groups[0]['lr']
                    print(f"Epoch {epoch+1}/{num_epochs} | "
                          f"Step {batch_idx+1}/{len(train_loader)} | "
                          f"Loss: {loss.item():.4f} | "
                          f"Avg Loss: {avg_loss:.4f} | "
                          f"LR: {lr:.2e}")
            
            # Epoch summary
            avg_epoch_loss = epoch_loss / len(train_loader)
            epoch_time = time.time() - epoch_start
            
            print(f"\n{'='*60}")
            print(f"Epoch {epoch+1} completed in {epoch_time:.2f}s")
            print(f"Average Loss: {avg_epoch_loss:.4f}")
            print(f"{'='*60}\n")
            
            # Update learning rate
            self.scheduler.step()
            
            # Save best model
            if avg_epoch_loss < best_loss:
                best_loss = avg_epoch_loss
                self.save_checkpoint(f"best_model.pt")
                print(f"✅ Saved best model (loss: {best_loss:.4f})\n")
            
            # Save periodic checkpoint
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(f"checkpoint_epoch_{epoch+1}.pt")
        
        print("="*60)
        print("✨ TRAINING COMPLETED!")
        print(f"Best Loss: {best_loss:.4f}")
        print("="*60)
    
    def save_checkpoint(self, filename: str):
        """Save model checkpoint."""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
        }
        torch.save(checkpoint, filename)
    
    def load_checkpoint(self, filename: str):
        """Load model checkpoint."""
        checkpoint = torch.load(filename)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        return checkpoint

def main():
    """Main training script."""
    
    # Configuration
    config = ModelConfig(
        vocab_size=100277,
        context_length=256,
        d_model=384,
        n_heads=6,
        n_layers=6,
        dropout=0.1
    )
    
    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Load dataset
    dataset = SeleniumDataset(
        bin_file='src/resources/selenium_dataset.bin',
        context_length=config.context_length
    )
    
    # Create model
    model = SeleniumSLM(config)
    
    # Create trainer
    trainer = Trainer(model, dataset, config, device=device)
    
    # Train
    trainer.train(
        num_epochs=50,
        batch_size=32,
        eval_interval=50
    )
    
    # Save final model
    trainer.save_checkpoint('final_model.pt')
    print("\n✅ Final model saved as 'final_model.pt'")

if __name__ == "__main__":
    main()
