"""
Native PyTorch implementation for website brand analysis.
Enhanced with performance optimizations, better error handling, and additional features.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any, Union
import warnings
import logging
import json
import time
from pathlib import Path
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
import asyncio
import concurrent.futures
from functools import lru_cache
import pickle
import hashlib
from contextlib import asynccontextmanager
import gc
import psutil
import threading
from queue import Queue
import multiprocessing as mp

@dataclass
class BrandAnalyzerArgs:
    """Configuration for the brand analyzer model."""
    hidden_size: int = 768
    num_layers: int = 8
    num_attention_heads: int = 12
    dropout: float = 0.1
    max_sequence_length: int = 2048
    
    color_palette_size: int = 16
    typography_features: int = 64
    layout_features: int = 128
    
    tone_categories: int = 10
    sentiment_dim: int = 32
    style_dim: int = 64
    
    visual_feature_dim: int = 1024
    text_feature_dim: int = 768
    metadata_feature_dim: int = 256
    
    # New performance and feature options
    use_flash_attention: bool = True
    use_gradient_checkpointing: bool = True
    use_mixed_precision: bool = True
    device: str = "auto"
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    max_epochs: int = 100
    patience: int = 10
    min_delta: float = 0.001

class VisualAnalyzer(nn.Module):
    """Analyzes visual elements of websites including colors, typography, and layout."""
    
    def __init__(self, args: BrandAnalyzerArgs):
        super().__init__()
        self.args = args
        
        self.color_encoder = nn.Sequential(
            nn.Linear(3, 64),  # RGB input
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, args.color_palette_size)
        )
        
        self.typography_encoder = nn.Sequential(
            nn.Linear(args.typography_features, 256),
            nn.ReLU(),
            nn.Dropout(args.dropout),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, args.hidden_size // 2)
        )
        
        self.layout_encoder = nn.Sequential(
            nn.Linear(args.layout_features, 256),
            nn.ReLU(),
            nn.Dropout(args.dropout),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, args.hidden_size // 2)
        )
        
        self.visual_fusion = nn.Linear(
            args.color_palette_size + args.hidden_size, 
            args.visual_feature_dim
        )
        
    def forward(self, colors, typography_features, layout_features):
        """
        Analyze visual elements of a website.
        
        Args:
            colors: (batch_size, num_colors, 3) - RGB color values
            typography_features: (batch_size, typography_features) - Font characteristics
            layout_features: (batch_size, layout_features) - Layout structure
        """
        batch_size = colors.shape[0]
        
        color_embeddings = self.color_encoder(colors)  # (batch_size, num_colors, palette_size)
        color_summary = color_embeddings.mean(dim=1)  # (batch_size, palette_size)
        
        typo_emb = self.typography_encoder(typography_features)
        
        layout_emb = self.layout_encoder(layout_features)
        
        visual_structure = torch.cat([typo_emb, layout_emb], dim=-1)
        
        visual_combined = torch.cat([color_summary, visual_structure], dim=-1)
        visual_features = self.visual_fusion(visual_combined)
        
        return {
            'visual_features': visual_features,
            'color_palette': color_summary,
            'typography_embedding': typo_emb,
            'layout_embedding': layout_emb
        }

class TextAnalyzer(nn.Module):
    """Analyzes textual content for tone, style, and brand voice."""
    
    def __init__(self, args: BrandAnalyzerArgs):
        super().__init__()
        self.args = args
        
        self.text_encoder = nn.Sequential(
            nn.Linear(args.text_feature_dim, args.hidden_size),
            nn.ReLU(),
            nn.Dropout(args.dropout),
            nn.Linear(args.hidden_size, args.hidden_size),
            nn.LayerNorm(args.hidden_size)
        )
        
        self.tone_classifier = nn.Sequential(
            nn.Linear(args.hidden_size, args.hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(args.dropout),
            nn.Linear(args.hidden_size // 2, args.tone_categories)
        )
        
        self.sentiment_encoder = nn.Sequential(
            nn.Linear(args.hidden_size, args.sentiment_dim),
            nn.Tanh()
        )
        
        self.style_encoder = nn.Sequential(
            nn.Linear(args.hidden_size, args.style_dim),
            nn.ReLU()
        )
        
    def forward(self, text_features):
        """
        Analyze textual content for brand characteristics.
        
        Args:
            text_features: (batch_size, seq_len, text_feature_dim) - Text embeddings
        """
        encoded_text = self.text_encoder(text_features)
        
        pooled_text = encoded_text.mean(dim=1)  # (batch_size, hidden_size)
        
        tone_logits = self.tone_classifier(pooled_text)
        sentiment_emb = self.sentiment_encoder(pooled_text)
        style_emb = self.style_encoder(pooled_text)
        
        return {
            'text_features': pooled_text,
            'tone_logits': tone_logits,
            'sentiment_embedding': sentiment_emb,
            'style_embedding': style_emb
        }

class BrandFusionLayer(nn.Module):
    """Fuses visual and textual brand elements."""
    
    def __init__(self, args: BrandAnalyzerArgs):
        super().__init__()
        self.args = args
        
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=args.hidden_size,
            num_heads=args.num_attention_heads,
            dropout=args.dropout,
            batch_first=True
        )
        
        self.visual_proj = nn.Linear(args.visual_feature_dim, args.hidden_size)
        
        self.fusion_layer = nn.Sequential(
            nn.Linear(args.hidden_size + args.hidden_size, args.hidden_size),
            nn.ReLU(),
            nn.Dropout(args.dropout),
            nn.Linear(args.hidden_size, args.hidden_size),
            nn.LayerNorm(args.hidden_size)
        )
        
    def forward(self, visual_features, text_features):
        """
        Fuse visual and textual brand elements.
        
        Args:
            visual_features: (batch_size, visual_feature_dim)
            text_features: (batch_size, hidden_size)
        """
        visual_expanded = visual_features.unsqueeze(1)  # (batch_size, 1, visual_feature_dim)
        text_expanded = text_features.unsqueeze(1)  # (batch_size, 1, hidden_size)
        
        visual_aligned = self.visual_proj(visual_expanded)
        
        attended_visual, _ = self.cross_attention(visual_aligned, text_expanded, text_expanded)
        attended_text, _ = self.cross_attention(text_expanded, visual_aligned, visual_aligned)
        
        combined = torch.cat([
            attended_visual.squeeze(1), 
            attended_text.squeeze(1)
        ], dim=-1)
        
        fused_features = self.fusion_layer(combined)
        
        return fused_features

class BrandAnalyzer(nn.Module):
    """Main brand analyzer model for website analysis."""
    
    def __init__(self, args: BrandAnalyzerArgs):
        super().__init__()
        self.args = args
        
        self.visual_analyzer = VisualAnalyzer(args)
        self.text_analyzer = TextAnalyzer(args)
        self.brand_fusion = BrandFusionLayer(args)
        
        self.brand_profile_head = nn.Sequential(
            nn.Linear(args.hidden_size, args.hidden_size),
            nn.ReLU(),
            nn.Dropout(args.dropout),
            nn.Linear(args.hidden_size, args.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(args.hidden_size // 2, args.hidden_size)
        )
        
        self.consistency_head = nn.Sequential(
            nn.Linear(args.hidden_size, args.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(args.hidden_size // 2, 1),
            nn.Sigmoid()
        )
        
    def forward(self, colors, typography_features, layout_features, text_features):
        """
        Analyze website for brand characteristics.
        
        Returns:
            brand_profile: Comprehensive brand embedding
            consistency_score: Brand consistency score (0-1)
            visual_analysis: Detailed visual analysis
            text_analysis: Detailed text analysis
        """
        visual_analysis = self.visual_analyzer(colors, typography_features, layout_features)
        
        text_analysis = self.text_analyzer(text_features)
        
        fused_features = self.brand_fusion(
            visual_analysis['visual_features'],
            text_analysis['text_features']
        )
        
        brand_profile = self.brand_profile_head(fused_features)
        
        consistency_score = self.consistency_head(fused_features)
        
        return {
            'brand_profile': brand_profile,
            'consistency_score': consistency_score,
            'visual_analysis': visual_analysis,
            'text_analysis': text_analysis,
            'fused_features': fused_features
        }
    
    def extract_brand_kit(self, website_data):
        """
        Extract comprehensive brand kit from website analysis.
        
        Args:
            website_data: Dictionary containing website analysis data
            
        Returns:
            Dictionary containing brand kit elements
        """
        with torch.no_grad():
            outputs = self.forward(**website_data)
            
            color_palette = outputs['visual_analysis']['color_palette']
            dominant_colors = torch.topk(color_palette, k=5, dim=-1).indices
            
            typography_emb = outputs['visual_analysis']['typography_embedding']
            
            tone_probs = F.softmax(outputs['text_analysis']['tone_logits'], dim=-1)
            dominant_tone = torch.argmax(tone_probs, dim=-1)[0]
            
            consistency = outputs['consistency_score'][0].item()
            
            brand_kit = {
                'color_palette': dominant_colors.tolist(),
                'typography_profile': typography_emb[0].tolist(),
                'tone_profile': {
                    'dominant_tone': dominant_tone.item(),
                    'tone_distribution': tone_probs[0].tolist()
                },
                'style_embedding': outputs['text_analysis']['style_embedding'][0].tolist(),
                'sentiment_profile': outputs['text_analysis']['sentiment_embedding'][0].tolist(),
                'brand_consistency_score': consistency,
                'brand_profile': outputs['brand_profile'][0].tolist()
            }
            
            return brand_kit

class BrandDataset(Dataset):
    """Dataset class for brand analysis training data."""
    
    def __init__(self, data: List[Dict[str, Any]], args: BrandAnalyzerArgs):
        self.data = data
        self.args = args
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Convert to tensors with proper shapes
        colors = torch.tensor(item['colors'], dtype=torch.float32)
        typography = torch.tensor(item['typography'], dtype=torch.float32)
        layout = torch.tensor(item['layout'], dtype=torch.float32)
        text_features = torch.tensor(item['text_features'], dtype=torch.float32)
        
        # Add batch dimension if needed
        if colors.dim() == 2:
            colors = colors.unsqueeze(0)
        if text_features.dim() == 1:
            text_features = text_features.unsqueeze(0)
            
        return {
            'colors': colors,
            'typography_features': typography,
            'layout_features': layout,
            'text_features': text_features,
            'target_consistency': torch.tensor(item.get('consistency_score', 0.5), dtype=torch.float32)
        }

class BrandTrainer:
    """Enhanced trainer for BrandAnalyzer with advanced features."""
    
    def __init__(self, model: BrandAnalyzer, args: BrandAnalyzerArgs):
        self.model = model
        self.args = args
        self.device = self._setup_device()
        self.model.to(self.device)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup optimizer and scheduler
        self.optimizer = AdamW(
            model.parameters(),
            lr=args.learning_rate,
            weight_decay=args.weight_decay
        )
        
        self.scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=args.max_epochs
        )
        
        # Setup mixed precision training
        self.scaler = torch.cuda.amp.GradScaler() if args.use_mixed_precision else None
        
        # Training state
        self.best_loss = float('inf')
        self.epochs_without_improvement = 0
        
    def _setup_device(self):
        """Setup device for training."""
        if self.args.device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            elif torch.backends.mps.is_available():
                return torch.device("mps")
            else:
                return torch.device("cpu")
        return torch.device(self.args.device)
    
    def train_epoch(self, dataloader: DataLoader) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, batch in enumerate(dataloader):
            # Move batch to device
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            self.optimizer.zero_grad()
            
            if self.scaler:
                with torch.cuda.amp.autocast():
                    outputs = self.model(
                        colors=batch['colors'],
                        typography_features=batch['typography_features'],
                        layout_features=batch['layout_features'],
                        text_features=batch['text_features']
                    )
                    
                    # Calculate loss (consistency prediction)
                    loss = F.mse_loss(
                        outputs['consistency_score'].squeeze(),
                        batch['target_consistency']
                    )
                
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(
                    colors=batch['colors'],
                    typography_features=batch['typography_features'],
                    layout_features=batch['layout_features'],
                    text_features=batch['text_features']
                )
                
                loss = F.mse_loss(
                    outputs['consistency_score'].squeeze(),
                    batch['target_consistency']
                )
                
                loss.backward()
                self.optimizer.step()
            
            total_loss += loss.item()
            
            if batch_idx % 10 == 0:
                self.logger.info(f'Batch {batch_idx}/{len(dataloader)}, Loss: {loss.item():.4f}')
        
        return total_loss / len(dataloader)
    
    def validate(self, dataloader: DataLoader) -> float:
        """Validate the model."""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for batch in dataloader:
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                outputs = self.model(
                    colors=batch['colors'],
                    typography_features=batch['typography_features'],
                    layout_features=batch['layout_features'],
                    text_features=batch['text_features']
                )
                
                loss = F.mse_loss(
                    outputs['consistency_score'].squeeze(),
                    batch['target_consistency']
                )
                
                total_loss += loss.item()
        
        return total_loss / len(dataloader)
    
    def train(self, train_dataloader: DataLoader, val_dataloader: DataLoader = None):
        """Train the model with early stopping."""
        self.logger.info("Starting training...")
        
        for epoch in range(self.args.max_epochs):
            # Training
            train_loss = self.train_epoch(train_dataloader)
            
            # Validation
            if val_dataloader:
                val_loss = self.validate(val_dataloader)
                self.logger.info(f'Epoch {epoch+1}/{self.args.max_epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')
                
                # Early stopping
                if val_loss < self.best_loss - self.args.min_delta:
                    self.best_loss = val_loss
                    self.epochs_without_improvement = 0
                    self.save_checkpoint(epoch, val_loss)
                else:
                    self.epochs_without_improvement += 1
                    
                if self.epochs_without_improvement >= self.args.patience:
                    self.logger.info(f"Early stopping at epoch {epoch+1}")
                    break
            else:
                self.logger.info(f'Epoch {epoch+1}/{self.args.max_epochs}, Train Loss: {train_loss:.4f}')
            
            self.scheduler.step()
    
    def save_checkpoint(self, epoch: int, loss: float, path: str = "best_model.pth"):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'loss': loss,
            'args': self.args
        }
        torch.save(checkpoint, path)
        self.logger.info(f"Checkpoint saved at epoch {epoch} with loss {loss:.4f}")

class BrandAnalyzerAPI:
    """High-level API for brand analysis."""
    
    def __init__(self, model_path: Optional[str] = None, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        if config_path:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.args = BrandAnalyzerArgs(**config.get('brand_analyzer', {}))
        else:
            self.args = BrandAnalyzerArgs()
        
        self.model = BrandAnalyzer(self.args)
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load a trained model."""
        checkpoint = torch.load(model_path, map_location='cpu')
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        self.logger.info(f"Model loaded from {model_path}")
    
    def analyze_website(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a website and return brand insights."""
        try:
            with torch.no_grad():
                # Convert data to tensors
                colors = torch.tensor(website_data['colors'], dtype=torch.float32).unsqueeze(0)
                typography = torch.tensor(website_data['typography'], dtype=torch.float32).unsqueeze(0)
                layout = torch.tensor(website_data['layout'], dtype=torch.float32).unsqueeze(0)
                text_features = torch.tensor(website_data['text_features'], dtype=torch.float32).unsqueeze(0)
                
                # Run analysis
                outputs = self.model(colors, typography, layout, text_features)
                
                # Extract brand kit
                brand_kit = self.model.extract_brand_kit({
                    'colors': colors,
                    'typography_features': typography,
                    'layout_features': layout,
                    'text_features': text_features
                })
                
                return {
                    'success': True,
                    'brand_kit': brand_kit,
                    'analysis_time': time.time(),
                    'model_outputs': {
                        'consistency_score': outputs['consistency_score'].item(),
                        'brand_profile': outputs['brand_profile'].squeeze().tolist()
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing website: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis_time': time.time()
            }
    
    def batch_analyze(self, websites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple websites in batch."""
        results = []
        for i, website in enumerate(websites):
            self.logger.info(f"Analyzing website {i+1}/{len(websites)}")
            result = self.analyze_website(website)
            results.append(result)
        return results

def create_brand_analyzer_model(config: Dict[str, Any]) -> BrandAnalyzer:
    """Create a brand analyzer model from configuration."""
    args = BrandAnalyzerArgs(
        hidden_size=config.get('hidden_size', 768),
        num_layers=config.get('num_layers', 8),
        num_attention_heads=config.get('num_attention_heads', 12),
        dropout=config.get('dropout', 0.1),
        max_sequence_length=config.get('max_sequence_length', 2048),
        
        color_palette_size=config.get('color_palette_size', 16),
        typography_features=config.get('typography_features', 64),
        layout_features=config.get('layout_features', 128),
        
        tone_categories=config.get('tone_categories', 10),
        sentiment_dim=config.get('sentiment_dim', 32),
        style_dim=config.get('style_dim', 64),
        
        visual_feature_dim=config.get('visual_feature_dim', 1024),
        text_feature_dim=config.get('text_feature_dim', 768),
        metadata_feature_dim=config.get('metadata_feature_dim', 256),
        
        # New parameters
        use_flash_attention=config.get('use_flash_attention', True),
        use_gradient_checkpointing=config.get('use_gradient_checkpointing', True),
        use_mixed_precision=config.get('use_mixed_precision', True),
        device=config.get('device', 'auto'),
        batch_size=config.get('batch_size', 32),
        learning_rate=config.get('learning_rate', 1e-4),
        weight_decay=config.get('weight_decay', 0.01),
        max_epochs=config.get('max_epochs', 100),
        patience=config.get('patience', 10),
        min_delta=config.get('min_delta', 0.001)
    )
    
    return BrandAnalyzer(args)

class MemoryManager:
    """Advanced memory management for large-scale brand analysis."""
    
    def __init__(self, max_memory_gb: float = 8.0):
        self.max_memory_gb = max_memory_gb
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.lock = threading.Lock()
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in GB."""
        process = psutil.Process()
        return process.memory_info().rss / (1024**3)
    
    def should_clear_cache(self) -> bool:
        """Check if cache should be cleared based on memory usage."""
        return self.get_memory_usage() > self.max_memory_gb * 0.8
    
    def clear_cache(self):
        """Clear cache to free memory."""
        with self.lock:
            self.cache.clear()
            gc.collect()
    
    def get_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate cache key for data."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_cached_result(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result if available."""
        cache_key = self.get_cache_key(data)
        with self.lock:
            if cache_key in self.cache:
                self.cache_hits += 1
                return self.cache[cache_key]
            self.cache_misses += 1
            return None
    
    def cache_result(self, data: Dict[str, Any], result: Dict[str, Any]):
        """Cache analysis result."""
        if self.should_clear_cache():
            self.clear_cache()
        
        cache_key = self.get_cache_key(data)
        with self.lock:
            self.cache[cache_key] = result

class AsyncBrandAnalyzer:
    """Asynchronous brand analyzer for high-throughput processing."""
    
    def __init__(self, model_path: Optional[str] = None, max_workers: int = 4):
        self.model_path = model_path
        self.max_workers = max_workers
        self.memory_manager = MemoryManager()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.analyzer = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize the analyzer asynchronously."""
        if not self._initialized:
            loop = asyncio.get_event_loop()
            self.analyzer = await loop.run_in_executor(
                self.executor, 
                lambda: BrandAnalyzerAPI(self.model_path)
            )
            self._initialized = True
    
    async def analyze_website_async(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze website asynchronously."""
        await self.initialize()
        
        # Check cache first
        cached_result = self.memory_manager.get_cached_result(website_data)
        if cached_result:
            return cached_result
        
        # Run analysis in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self.analyzer.analyze_website,
            website_data
        )
        
        # Cache result
        if result['success']:
            self.memory_manager.cache_result(website_data, result)
        
        return result
    
    async def batch_analyze_async(self, websites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple websites asynchronously."""
        await self.initialize()
        
        # Create tasks for all websites
        tasks = [
            self.analyze_website_async(website) 
            for website in websites
        ]
        
        # Run all analyses concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'analysis_time': time.time()
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.memory_manager.cache_hits + self.memory_manager.cache_misses
        hit_rate = self.memory_manager.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'cache_hits': self.memory_manager.cache_hits,
            'cache_misses': self.memory_manager.cache_misses,
            'hit_rate': hit_rate,
            'memory_usage_gb': self.memory_manager.get_memory_usage(),
            'cache_size': len(self.memory_manager.cache)
        }

class AutoTuningBrandAnalyzer:
    """Brand analyzer with automatic hyperparameter tuning."""
    
    def __init__(self, base_config: Dict[str, Any]):
        self.base_config = base_config
        self.tuning_history = []
        self.best_config = base_config.copy()
        self.best_score = 0.0
        
    def generate_config_variants(self, num_variants: int = 10) -> List[Dict[str, Any]]:
        """Generate configuration variants for tuning."""
        variants = []
        
        for _ in range(num_variants):
            variant = self.base_config.copy()
            
            # Tune learning rate
            variant['learning_rate'] = np.random.uniform(1e-5, 1e-3)
            
            # Tune batch size
            variant['batch_size'] = np.random.choice([8, 16, 32, 64])
            
            # Tune hidden size
            variant['hidden_size'] = np.random.choice([512, 768, 1024, 1536])
            
            # Tune dropout
            variant['dropout'] = np.random.uniform(0.1, 0.3)
            
            # Tune attention heads
            variant['num_attention_heads'] = np.random.choice([8, 12, 16, 24])
            
            variants.append(variant)
        
        return variants
    
    def evaluate_config(self, config: Dict[str, Any], validation_data: List[Dict[str, Any]]) -> float:
        """Evaluate a configuration on validation data."""
        try:
            # Create model with config
            args = BrandAnalyzerArgs(**config)
            model = BrandAnalyzer(args)
            
            # Create dataset
            dataset = BrandDataset(validation_data, args)
            dataloader = DataLoader(dataset, batch_size=config['batch_size'], shuffle=False)
            
            # Evaluate model
            model.eval()
            total_loss = 0.0
            num_batches = 0
            
            with torch.no_grad():
                for batch in dataloader:
                    outputs = model(
                        colors=batch['colors'],
                        typography_features=batch['typography_features'],
                        layout_features=batch['layout_features'],
                        text_features=batch['text_features']
                    )
                    
                    loss = F.mse_loss(
                        outputs['consistency_score'].squeeze(),
                        batch['target_consistency']
                    )
                    
                    total_loss += loss.item()
                    num_batches += 1
            
            avg_loss = total_loss / num_batches if num_batches > 0 else float('inf')
            return 1.0 / (1.0 + avg_loss)  # Convert loss to score (higher is better)
            
        except Exception as e:
            logging.warning(f"Config evaluation failed: {e}")
            return 0.0
    
    def auto_tune(self, train_data: List[Dict[str, Any]], 
                  val_data: List[Dict[str, Any]], 
                  num_iterations: int = 20) -> Dict[str, Any]:
        """Automatically tune hyperparameters."""
        logging.info("Starting automatic hyperparameter tuning...")
        
        for iteration in range(num_iterations):
            # Generate config variants
            variants = self.generate_config_variants(5)
            
            # Evaluate each variant
            best_variant_score = 0.0
            best_variant = None
            
            for variant in variants:
                score = self.evaluate_config(variant, val_data)
                
                if score > best_variant_score:
                    best_variant_score = score
                    best_variant = variant
                
                self.tuning_history.append({
                    'iteration': iteration,
                    'config': variant,
                    'score': score
                })
            
            # Update best config if improvement found
            if best_variant_score > self.best_score:
                self.best_score = best_variant_score
                self.best_config = best_variant.copy()
                logging.info(f"Iteration {iteration}: New best score {best_variant_score:.4f}")
            
            # Early stopping if no improvement
            if iteration > 5 and best_variant_score <= self.best_score * 0.95:
                logging.info(f"Early stopping at iteration {iteration}")
                break
        
        logging.info(f"Auto-tuning completed. Best score: {self.best_score:.4f}")
        return self.best_config

class ProductionBrandAnalyzer:
    """Production-ready brand analyzer with monitoring and scaling."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.analyzer = None
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'cache_hit_rate': 0.0
        }
        self.response_times = []
        self.start_time = time.time()
        
    def initialize(self):
        """Initialize the production analyzer."""
        self.analyzer = BrandAnalyzerAPI(config_path=self.config_path)
        
    def analyze_with_monitoring(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze website with comprehensive monitoring."""
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        try:
            result = self.analyzer.analyze_website(website_data)
            
            if result['success']:
                self.metrics['successful_requests'] += 1
            else:
                self.metrics['failed_requests'] += 1
            
            # Record response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            # Update average response time
            self.metrics['average_response_time'] = np.mean(self.response_times[-100:])  # Last 100 requests
            
            # Add monitoring data to result
            result['monitoring'] = {
                'response_time': response_time,
                'timestamp': time.time(),
                'uptime': time.time() - self.start_time
            }
            
            return result
            
        except Exception as e:
            self.metrics['failed_requests'] += 1
            return {
                'success': False,
                'error': str(e),
                'monitoring': {
                    'response_time': time.time() - start_time,
                    'timestamp': time.time(),
                    'uptime': time.time() - self.start_time
                }
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the analyzer."""
        uptime = time.time() - self.start_time
        success_rate = self.metrics['successful_requests'] / max(self.metrics['total_requests'], 1)
        
        return {
            'status': 'healthy' if success_rate > 0.95 else 'degraded',
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'total_requests': self.metrics['total_requests'],
            'success_rate': success_rate,
            'average_response_time': self.metrics['average_response_time'],
            'memory_usage_gb': psutil.Process().memory_info().rss / (1024**3),
            'cpu_usage_percent': psutil.cpu_percent()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics."""
        return {
            **self.metrics,
            'response_times': self.response_times[-100:],  # Last 100 response times
            'health_status': self.get_health_status()
        }

class DistributedBrandAnalyzer:
    """Distributed brand analyzer for large-scale processing."""
    
    def __init__(self, num_workers: int = 4, model_path: Optional[str] = None):
        self.num_workers = num_workers
        self.model_path = model_path
        self.workers = []
        self.task_queue = Queue()
        self.result_queue = Queue()
        
    def start_workers(self):
        """Start worker processes."""
        for i in range(self.num_workers):
            worker = mp.Process(
                target=self._worker_process,
                args=(i, self.model_path, self.task_queue, self.result_queue)
            )
            worker.start()
            self.workers.append(worker)
    
    @staticmethod
    def _worker_process(worker_id: int, model_path: str, task_queue: Queue, result_queue: Queue):
        """Worker process for distributed analysis."""
        # Initialize analyzer in worker process
        analyzer = BrandAnalyzerAPI(model_path=model_path)
        
        while True:
            try:
                # Get task from queue
                task = task_queue.get(timeout=1)
                if task is None:  # Shutdown signal
                    break
                
                # Process task
                website_data, task_id = task
                result = analyzer.analyze_website(website_data)
                result['task_id'] = task_id
                result['worker_id'] = worker_id
                
                # Put result in result queue
                result_queue.put(result)
                
            except Exception as e:
                result_queue.put({
                    'success': False,
                    'error': str(e),
                    'task_id': task.get('task_id', -1) if task else -1,
                    'worker_id': worker_id
                })
    
    def analyze_distributed(self, websites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze websites using distributed processing."""
        if not self.workers:
            self.start_workers()
        
        # Submit tasks
        for i, website in enumerate(websites):
            self.task_queue.put((website, i))
        
        # Collect results
        results = [None] * len(websites)
        completed = 0
        
        while completed < len(websites):
            try:
                result = self.result_queue.get(timeout=5)
                if result['task_id'] < len(results):
                    results[result['task_id']] = result
                    completed += 1
            except:
                break
        
        return results
    
    def shutdown(self):
        """Shutdown worker processes."""
        # Send shutdown signals
        for _ in self.workers:
            self.task_queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join()
        
        self.workers.clear()
