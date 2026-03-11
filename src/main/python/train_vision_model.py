"""
AI Vision Model Trainer for Element Detection
Trains a custom vision model on your annotated screenshots
Uses PyTorch for deep learning vision model
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
import cv2
import json
import os
import numpy as np
from typing import List, Dict, Tuple
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScreenshotDataset(Dataset):
    """Dataset for annotated screenshots."""
    
    def __init__(self, annotation_files: List[str], transform=None):
        """
        Args:
            annotation_files: List of JSON annotation file paths
            transform: Optional transforms
        """
        self.samples = []
        self.transform = transform
        
        # Load all annotations
        for ann_file in annotation_files:
            with open(ann_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            image_path = data['image_path']
            if not os.path.exists(image_path):
                logger.warning(f"Image not found: {image_path}, skipping")
                continue
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.warning(f"Could not load image: {image_path}, skipping")
                continue
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process each annotation
            for ann in data['annotations']:
                self.samples.append({
                    'image': image,
                    'bbox': ann['bbox'],
                    'type': ann['type'],
                    'label': ann['label']
                })
        
        logger.info(f"Loaded {len(self.samples)} training samples from {len(annotation_files)} files")
        
        # Element type to index mapping
        self.type_to_idx = {
            'input': 0,
            'button': 1,
            'checkbox': 2,
            'link': 3,
            'select': 4,
            'textarea': 5
        }
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Extract element region
        image = sample['image']
        x, y, w, h = sample['bbox']
        
        # Crop element with some context
        padding = 20
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        
        element_img = image[y1:y2, x1:x2]
        
        # Resize to fixed size
        element_img = cv2.resize(element_img, (224, 224))
        
        # Convert to tensor
        if self.transform:
            element_img = self.transform(element_img)
        else:
            element_img = torch.from_numpy(element_img).permute(2, 0, 1).float() / 255.0
        
        # Get element type index
        elem_type_idx = self.type_to_idx.get(sample['type'], 0)
        
        return element_img, elem_type_idx, sample['label']


class ElementDetectorModel(nn.Module):
    """Vision model for element detection and classification."""
    
    def __init__(self, num_classes=6, pretrained=True):
        super(ElementDetectorModel, self).__init__()
        
        # Use pretrained ResNet18 as backbone
        if pretrained:
            self.backbone = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        else:
            self.backbone = resnet18(weights=None)
        
        # Replace final layer
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


class VisionModelTrainer:
    """Trains custom vision model for element detection."""
    
    def __init__(self, annotation_dir: str, output_dir: str = 'trained_models'):
        """
        Args:
            annotation_dir: Directory containing annotation JSON files
            output_dir: Directory to save trained models
        """
        self.annotation_dir = annotation_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Check for GPU
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Load annotation files
        self.annotation_files = [
            os.path.join(annotation_dir, f) 
            for f in os.listdir(annotation_dir) 
            if f.endswith('_annotations.json')
        ]
        
        if not self.annotation_files:
            raise ValueError(f"No annotation files found in {annotation_dir}")
        
        logger.info(f"Found {len(self.annotation_files)} annotation files")
    
    def train(self, epochs: int = 50, batch_size: int = 16, learning_rate: float = 0.001):
        """
        Train the vision model.
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
        """
        logger.info("=" * 60)
        logger.info("TRAINING AI VISION MODEL")
        logger.info("=" * 60)
        
        # Data transforms
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Create dataset
        dataset = ScreenshotDataset(self.annotation_files, transform=transform)
        
        # Split into train/val (80/20)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        
        logger.info(f"Train samples: {len(train_dataset)}")
        logger.info(f"Validation samples: {len(val_dataset)}")
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
        
        # Create model
        model = ElementDetectorModel(num_classes=6, pretrained=True)
        model = model.to(self.device)
        
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
        
        # Training loop
        best_val_loss = float('inf')
        best_model_path = None
        
        for epoch in range(epochs):
            # Train
            model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for images, labels, _ in train_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
            
            train_loss /= len(train_loader)
            train_acc = 100.0 * train_correct / train_total
            
            # Validate
            model.eval()
            val_loss = 0.0
            val_correct = 0
            val_total = 0
            
            with torch.no_grad():
                for images, labels, _ in val_loader:
                    images = images.to(self.device)
                    labels = labels.to(self.device)
                    
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    
                    val_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels).sum().item()
            
            val_loss /= len(val_loader)
            val_acc = 100.0 * val_correct / val_total
            
            # Adjust learning rate
            scheduler.step(val_loss)
            
            # Log progress
            logger.info(f"Epoch [{epoch+1}/{epochs}] "
                       f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
                       f"Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}%")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                best_model_path = os.path.join(self.output_dir, f'vision_model_best_{timestamp}.pth')
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_loss': val_loss,
                    'val_acc': val_acc,
                    'type_to_idx': dataset.type_to_idx
                }, best_model_path)
                logger.info(f"✓ Saved best model: {best_model_path}")
        
        logger.info("=" * 60)
        logger.info("TRAINING COMPLETE!")
        logger.info(f"Best model: {best_model_path}")
        logger.info(f"Best validation loss: {best_val_loss:.4f}")
        logger.info("=" * 60)
        
        return best_model_path


def main():
    """Main training entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train AI Vision Model')
    parser.add_argument('--annotations', type=str, required=True,
                       help='Directory containing annotation JSON files')
    parser.add_argument('--output', type=str, default='trained_models',
                       help='Output directory for trained models')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    
    args = parser.parse_args()
    
    trainer = VisionModelTrainer(args.annotations, args.output)
    trainer.train(epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.learning_rate)


if __name__ == '__main__':
    main()
