"""
Mobile and Edge Computing Brand Analysis
Optimized for mobile devices and edge computing environments.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import json
import time
from pathlib import Path
import pickle
import zipfile
import base64
from dataclasses import dataclass
import cv2
from PIL import Image
import io
import requests
from urllib.parse import urlparse
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue
import sqlite3
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class MobileConfig:
    """Configuration for mobile brand analysis."""
    model_size: str = "tiny"  # tiny, small, medium, large
    max_image_size: int = 224
    max_colors: int = 8
    max_text_length: int = 1000
    cache_size: int = 100
    offline_mode: bool = True
    compression_level: int = 6
    use_quantization: bool = True
    use_pruning: bool = True
    batch_size: int = 1
    max_memory_mb: int = 100

class MobileBrandAnalyzer:
    """Lightweight brand analyzer optimized for mobile devices."""
    
    def __init__(self, config: MobileConfig):
        self.config = config
        self.model = self._create_mobile_model()
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.db_path = "mobile_brand_cache.db"
        self._init_database()
        
    def _create_mobile_model(self) -> nn.Module:
        """Create a lightweight mobile-optimized model."""
        if self.config.model_size == "tiny":
            return MobileTinyModel(self.config)
        elif self.config.model_size == "small":
            return MobileSmallModel(self.config)
        elif self.config.model_size == "medium":
            return MobileMediumModel(self.config)
        else:
            return MobileLargeModel(self.config)
    
    def _init_database(self):
        """Initialize SQLite database for caching."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brand_cache (
                id TEXT PRIMARY KEY,
                data BLOB,
                timestamp REAL,
                size INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_from_url(self, url: str) -> Dict[str, Any]:
        """Analyze brand from URL with mobile optimization."""
        try:
            # Check cache first
            cache_key = hashlib.md5(url.encode()).hexdigest()
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
            
            # Download and process image
            image_data = self._download_image(url)
            if not image_data:
                return {'success': False, 'error': 'Failed to download image'}
            
            # Extract brand features
            brand_data = self._extract_brand_features(image_data)
            
            # Analyze with mobile model
            result = self._analyze_with_mobile_model(brand_data)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Mobile analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze brand from image data."""
        try:
            # Check cache
            cache_key = hashlib.md5(image_data).hexdigest()
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
            
            # Extract brand features
            brand_data = self._extract_brand_features(image_data)
            
            # Analyze with mobile model
            result = self._analyze_with_mobile_model(brand_data)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Mobile image analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL with mobile optimization."""
        try:
            # Use requests with timeout and size limit
            response = requests.get(
                url, 
                timeout=10,
                headers={'User-Agent': 'MobileBrandAnalyzer/1.0'},
                stream=True
            )
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return None
            
            # Check size limit (1MB for mobile)
            content_length = int(response.headers.get('content-length', 0))
            if content_length > 1024 * 1024:  # 1MB limit
                return None
            
            return response.content
            
        except Exception as e:
            logger.error(f"Image download failed: {e}")
            return None
    
    def _extract_brand_features(self, image_data: bytes) -> Dict[str, Any]:
        """Extract brand features from image data."""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Resize for mobile processing
            image = image.resize((self.config.max_image_size, self.config.max_image_size))
            
            # Extract colors
            colors = self._extract_colors(image)
            
            # Extract typography (simplified)
            typography = self._extract_typography(image)
            
            # Extract layout
            layout = self._extract_layout(image)
            
            # Extract text features (simplified)
            text_features = self._extract_text_features(image)
            
            return {
                'colors': colors,
                'typography': typography,
                'layout': layout,
                'text_features': text_features
            }
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return self._get_default_features()
    
    def _extract_colors(self, image: Image.Image) -> List[List[int]]:
        """Extract dominant colors from image."""
        try:
            # Convert to RGB
            image = image.convert('RGB')
            
            # Resize for faster processing
            image = image.resize((64, 64))
            
            # Get pixel data
            pixels = list(image.getdata())
            
            # Use K-means clustering for color extraction
            from sklearn.cluster import KMeans
            
            # Limit number of colors for mobile
            n_colors = min(self.config.max_colors, len(pixels))
            if n_colors < 2:
                n_colors = 2
            
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get dominant colors
            colors = kmeans.cluster_centers_.astype(int).tolist()
            
            return colors
            
        except Exception as e:
            logger.error(f"Color extraction failed: {e}")
            return [[255, 255, 255], [0, 0, 0]]  # Default colors
    
    def _extract_typography(self, image: Image.Image) -> List[float]:
        """Extract typography features (simplified for mobile)."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            
            # Get image dimensions
            width, height = gray.size
            
            # Calculate basic typography features
            features = [
                width / height,  # Aspect ratio
                np.mean(gray),  # Average brightness
                np.std(gray),   # Contrast
                self._calculate_text_density(gray),  # Text density
                self._calculate_edge_density(gray),  # Edge density
                self._calculate_horizontal_lines(gray),  # Horizontal lines
                self._calculate_vertical_lines(gray),  # Vertical lines
                self._calculate_diagonal_lines(gray)   # Diagonal lines
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Typography extraction failed: {e}")
            return [1.0, 128.0, 64.0, 0.5, 0.3, 0.2, 0.2, 0.1]  # Default features
    
    def _extract_layout(self, image: Image.Image) -> List[float]:
        """Extract layout features (simplified for mobile)."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            
            # Calculate layout features
            features = [
                self._calculate_symmetry(gray),
                self._calculate_balance(gray),
                self._calculate_rhythm(gray),
                self._calculate_proportion(gray),
                self._calculate_hierarchy(gray),
                self._calculate_alignment(gray),
                self._calculate_whitespace(gray),
                self._calculate_complexity(gray)
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Layout extraction failed: {e}")
            return [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.3, 0.5]  # Default features
    
    def _extract_text_features(self, image: Image.Image) -> List[float]:
        """Extract text features (simplified for mobile)."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            
            # Calculate text features
            features = [
                self._calculate_text_regions(gray),
                self._calculate_font_size_variation(gray),
                self._calculate_text_alignment(gray),
                self._calculate_reading_flow(gray),
                self._calculate_text_density(gray),
                self._calculate_contrast_ratio(gray),
                self._calculate_line_spacing(gray),
                self._calculate_paragraph_spacing(gray)
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Text feature extraction failed: {e}")
            return [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]  # Default features
    
    def _calculate_text_density(self, gray_image: Image.Image) -> float:
        """Calculate text density in image."""
        # Simplified text density calculation
        pixels = np.array(gray_image)
        edges = cv2.Canny(pixels, 50, 150)
        return np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
    
    def _calculate_edge_density(self, gray_image: Image.Image) -> float:
        """Calculate edge density in image."""
        pixels = np.array(gray_image)
        edges = cv2.Canny(pixels, 50, 150)
        return np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
    
    def _calculate_horizontal_lines(self, gray_image: Image.Image) -> float:
        """Calculate horizontal line density."""
        pixels = np.array(gray_image)
        horizontal_kernel = np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]])
        horizontal_lines = cv2.filter2D(pixels, -1, horizontal_kernel)
        return np.sum(horizontal_lines > 100) / (horizontal_lines.shape[0] * horizontal_lines.shape[1])
    
    def _calculate_vertical_lines(self, gray_image: Image.Image) -> float:
        """Calculate vertical line density."""
        pixels = np.array(gray_image)
        vertical_kernel = np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]])
        vertical_lines = cv2.filter2D(pixels, -1, vertical_kernel)
        return np.sum(vertical_lines > 100) / (vertical_lines.shape[0] * vertical_lines.shape[1])
    
    def _calculate_diagonal_lines(self, gray_image: Image.Image) -> float:
        """Calculate diagonal line density."""
        pixels = np.array(gray_image)
        diagonal_kernel = np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]])
        diagonal_lines = cv2.filter2D(pixels, -1, diagonal_kernel)
        return np.sum(diagonal_lines > 100) / (diagonal_lines.shape[0] * diagonal_lines.shape[1])
    
    def _calculate_symmetry(self, gray_image: Image.Image) -> float:
        """Calculate symmetry of the image."""
        pixels = np.array(gray_image)
        height, width = pixels.shape
        
        # Horizontal symmetry
        top_half = pixels[:height//2, :]
        bottom_half = pixels[height//2:, :]
        horizontal_symmetry = 1 - np.mean(np.abs(top_half - np.flipud(bottom_half))) / 255
        
        # Vertical symmetry
        left_half = pixels[:, :width//2]
        right_half = pixels[:, width//2:]
        vertical_symmetry = 1 - np.mean(np.abs(left_half - np.fliplr(right_half))) / 255
        
        return (horizontal_symmetry + vertical_symmetry) / 2
    
    def _calculate_balance(self, gray_image: Image.Image) -> float:
        """Calculate visual balance of the image."""
        pixels = np.array(gray_image)
        height, width = pixels.shape
        
        # Calculate center of mass
        y_indices, x_indices = np.ogrid[:height, :width]
        total_mass = np.sum(pixels)
        
        if total_mass == 0:
            return 0.5
        
        center_x = np.sum(x_indices * pixels) / total_mass
        center_y = np.sum(y_indices * pixels) / total_mass
        
        # Calculate balance (closer to center = more balanced)
        balance_x = 1 - abs(center_x - width/2) / (width/2)
        balance_y = 1 - abs(center_y - height/2) / (height/2)
        
        return (balance_x + balance_y) / 2
    
    def _calculate_rhythm(self, gray_image: Image.Image) -> float:
        """Calculate visual rhythm of the image."""
        pixels = np.array(gray_image)
        
        # Calculate horizontal rhythm
        horizontal_profile = np.mean(pixels, axis=0)
        horizontal_rhythm = self._calculate_rhythm_pattern(horizontal_profile)
        
        # Calculate vertical rhythm
        vertical_profile = np.mean(pixels, axis=1)
        vertical_rhythm = self._calculate_rhythm_pattern(vertical_profile)
        
        return (horizontal_rhythm + vertical_rhythm) / 2
    
    def _calculate_rhythm_pattern(self, profile: np.ndarray) -> float:
        """Calculate rhythm pattern in a 1D profile."""
        # Find peaks and valleys
        from scipy.signal import find_peaks
        
        peaks, _ = find_peaks(profile, height=np.mean(profile))
        valleys, _ = find_peaks(-profile, height=-np.mean(profile))
        
        # Calculate rhythm regularity
        all_points = np.concatenate([peaks, valleys])
        all_points = np.sort(all_points)
        
        if len(all_points) < 2:
            return 0.5
        
        intervals = np.diff(all_points)
        rhythm_regularity = 1 - (np.std(intervals) / np.mean(intervals)) if np.mean(intervals) > 0 else 0
        
        return max(0, min(1, rhythm_regularity))
    
    def _calculate_proportion(self, gray_image: Image.Image) -> float:
        """Calculate proportion of the image."""
        pixels = np.array(gray_image)
        height, width = pixels.shape
        
        # Calculate golden ratio proportion
        golden_ratio = 1.618
        aspect_ratio = width / height
        
        # Calculate how close the aspect ratio is to golden ratio
        proportion_score = 1 - abs(aspect_ratio - golden_ratio) / golden_ratio
        
        return max(0, min(1, proportion_score))
    
    def _calculate_hierarchy(self, gray_image: Image.Image) -> float:
        """Calculate visual hierarchy of the image."""
        pixels = np.array(gray_image)
        
        # Calculate contrast between different regions
        # Divide image into 9 regions (3x3 grid)
        h, w = pixels.shape
        regions = []
        
        for i in range(3):
            for j in range(3):
                start_h, end_h = i * h // 3, (i + 1) * h // 3
                start_w, end_w = j * w // 3, (j + 1) * w // 3
                region = pixels[start_h:end_h, start_w:end_w]
                regions.append(np.mean(region))
        
        # Calculate hierarchy based on contrast between regions
        hierarchy_score = np.std(regions) / 255
        
        return max(0, min(1, hierarchy_score))
    
    def _calculate_alignment(self, gray_image: Image.Image) -> float:
        """Calculate alignment of elements in the image."""
        pixels = np.array(gray_image)
        
        # Find edges
        edges = cv2.Canny(pixels, 50, 150)
        
        # Calculate alignment of edges
        # This is a simplified implementation
        alignment_score = 0.5  # Placeholder
        
        return alignment_score
    
    def _calculate_whitespace(self, gray_image: Image.Image) -> float:
        """Calculate whitespace ratio in the image."""
        pixels = np.array(gray_image)
        
        # Define whitespace as pixels close to white (value > 200)
        whitespace_pixels = np.sum(pixels > 200)
        total_pixels = pixels.size
        
        whitespace_ratio = whitespace_pixels / total_pixels
        
        return whitespace_ratio
    
    def _calculate_complexity(self, gray_image: Image.Image) -> float:
        """Calculate visual complexity of the image."""
        pixels = np.array(gray_image)
        
        # Calculate complexity based on edge density and color variation
        edges = cv2.Canny(pixels, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Calculate color variation
        color_variation = np.std(pixels) / 255
        
        # Combine edge density and color variation
        complexity = (edge_density + color_variation) / 2
        
        return max(0, min(1, complexity))
    
    def _calculate_text_regions(self, gray_image: Image.Image) -> float:
        """Calculate number of text regions in the image."""
        # Simplified text region detection
        pixels = np.array(gray_image)
        
        # Use edge detection to find text-like regions
        edges = cv2.Canny(pixels, 50, 150)
        
        # Count connected components as text regions
        from scipy import ndimage
        labeled_array, num_features = ndimage.label(edges)
        
        # Filter by size (text regions should be reasonably sized)
        text_regions = 0
        for i in range(1, num_features + 1):
            region_size = np.sum(labeled_array == i)
            if 100 < region_size < 10000:  # Reasonable size for text
                text_regions += 1
        
        # Normalize by image size
        normalized_regions = text_regions / (pixels.shape[0] * pixels.shape[1] / 10000)
        
        return min(1.0, normalized_regions)
    
    def _calculate_font_size_variation(self, gray_image: Image.Image) -> float:
        """Calculate font size variation in the image."""
        # Simplified font size variation calculation
        return 0.5  # Placeholder
    
    def _calculate_text_alignment(self, gray_image: Image.Image) -> float:
        """Calculate text alignment in the image."""
        # Simplified text alignment calculation
        return 0.5  # Placeholder
    
    def _calculate_reading_flow(self, gray_image: Image.Image) -> float:
        """Calculate reading flow of the image."""
        # Simplified reading flow calculation
        return 0.5  # Placeholder
    
    def _calculate_contrast_ratio(self, gray_image: Image.Image) -> float:
        """Calculate contrast ratio of the image."""
        pixels = np.array(gray_image)
        
        # Calculate contrast ratio
        max_brightness = np.max(pixels)
        min_brightness = np.min(pixels)
        
        if min_brightness == 0:
            return 1.0
        
        contrast_ratio = max_brightness / min_brightness
        
        # Normalize to 0-1 range
        normalized_contrast = min(1.0, contrast_ratio / 10.0)
        
        return normalized_contrast
    
    def _calculate_line_spacing(self, gray_image: Image.Image) -> float:
        """Calculate line spacing in the image."""
        # Simplified line spacing calculation
        return 0.5  # Placeholder
    
    def _calculate_paragraph_spacing(self, gray_image: Image.Image) -> float:
        """Calculate paragraph spacing in the image."""
        # Simplified paragraph spacing calculation
        return 0.5  # Placeholder
    
    def _get_default_features(self) -> Dict[str, Any]:
        """Get default features when extraction fails."""
        return {
            'colors': [[255, 255, 255], [0, 0, 0]],
            'typography': [1.0, 128.0, 64.0, 0.5, 0.3, 0.2, 0.2, 0.1],
            'layout': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.3, 0.5],
            'text_features': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        }
    
    def _analyze_with_mobile_model(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze brand data with mobile model."""
        try:
            # Prepare input data
            input_data = self._prepare_mobile_input(brand_data)
            
            # Run inference
            with torch.no_grad():
                output = self.model(input_data)
                consistency_score = output.item()
            
            # Generate mobile brand kit
            mobile_brand_kit = self._generate_mobile_brand_kit(brand_data, consistency_score)
            
            return {
                'success': True,
                'consistency_score': consistency_score,
                'mobile_brand_kit': mobile_brand_kit,
                'model_size': self.config.model_size,
                'analysis_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"Mobile model analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_mobile_input(self, brand_data: Dict[str, Any]) -> torch.Tensor:
        """Prepare input data for mobile model."""
        # Combine all features into a single tensor
        features = []
        
        # Add color features
        colors = brand_data.get('colors', [])
        for color in colors[:self.config.max_colors]:
            features.extend(color)
        
        # Pad or truncate colors
        while len(features) < self.config.max_colors * 3:
            features.append(0.0)
        features = features[:self.config.max_colors * 3]
        
        # Add typography features
        typography = brand_data.get('typography', [])
        features.extend(typography)
        
        # Add layout features
        layout = brand_data.get('layout', [])
        features.extend(layout)
        
        # Add text features
        text_features = brand_data.get('text_features', [])
        features.extend(text_features)
        
        # Convert to tensor
        return torch.tensor(features, dtype=torch.float32).unsqueeze(0)
    
    def _generate_mobile_brand_kit(self, brand_data: Dict[str, Any], 
                                 consistency_score: float) -> Dict[str, Any]:
        """Generate mobile-optimized brand kit."""
        return {
            'mobile_color_palette': brand_data.get('colors', []),
            'mobile_typography': brand_data.get('typography', []),
            'mobile_layout': brand_data.get('layout', []),
            'mobile_consistency': consistency_score,
            'mobile_optimized': True,
            'model_size': self.config.model_size
        }
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT data FROM brand_cache WHERE id = ?', (cache_key,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return pickle.loads(result[0])
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """Save result to cache."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            data = pickle.dumps(result)
            timestamp = time.time()
            size = len(data)
            
            cursor.execute('''
                INSERT OR REPLACE INTO brand_cache (id, data, timestamp, size)
                VALUES (?, ?, ?, ?)
            ''', (cache_key, data, timestamp, size))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Cache save failed: {e}")

class MobileTinyModel(nn.Module):
    """Tiny mobile model for brand analysis."""
    
    def __init__(self, config: MobileConfig):
        super().__init__()
        self.config = config
        
        # Calculate input size
        input_size = config.max_colors * 3 + 8 + 8 + 8  # colors + typography + layout + text
        
        self.layers = nn.Sequential(
            nn.Linear(input_size, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
        # Apply quantization if enabled
        if config.use_quantization:
            self.quantize()
    
    def forward(self, x):
        return self.layers(x)
    
    def quantize(self):
        """Apply quantization to the model."""
        # Simplified quantization
        for module in self.modules():
            if isinstance(module, nn.Linear):
                # Quantize weights
                module.weight.data = torch.round(module.weight.data * 127) / 127
                if module.bias is not None:
                    module.bias.data = torch.round(module.bias.data * 127) / 127

class MobileSmallModel(nn.Module):
    """Small mobile model for brand analysis."""
    
    def __init__(self, config: MobileConfig):
        super().__init__()
        self.config = config
        
        input_size = config.max_colors * 3 + 8 + 8 + 8
        
        self.layers = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
        if config.use_quantization:
            self.quantize()
    
    def forward(self, x):
        return self.layers(x)
    
    def quantize(self):
        """Apply quantization to the model."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                module.weight.data = torch.round(module.weight.data * 127) / 127
                if module.bias is not None:
                    module.bias.data = torch.round(module.bias.data * 127) / 127

class MobileMediumModel(nn.Module):
    """Medium mobile model for brand analysis."""
    
    def __init__(self, config: MobileConfig):
        super().__init__()
        self.config = config
        
        input_size = config.max_colors * 3 + 8 + 8 + 8
        
        self.layers = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        if config.use_quantization:
            self.quantize()
    
    def forward(self, x):
        return self.layers(x)
    
    def quantize(self):
        """Apply quantization to the model."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                module.weight.data = torch.round(module.weight.data * 127) / 127
                if module.bias is not None:
                    module.bias.data = torch.round(module.bias.data * 127) / 127

class MobileLargeModel(nn.Module):
    """Large mobile model for brand analysis."""
    
    def __init__(self, config: MobileConfig):
        super().__init__()
        self.config = config
        
        input_size = config.max_colors * 3 + 8 + 8 + 8
        
        self.layers = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        if config.use_quantization:
            self.quantize()
    
    def forward(self, x):
        return self.layers(x)
    
    def quantize(self):
        """Apply quantization to the model."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                module.weight.data = torch.round(module.weight.data * 127) / 127
                if module.bias is not None:
                    module.bias.data = torch.round(module.bias.data * 127) / 127

def create_mobile_analyzer(config: MobileConfig) -> MobileBrandAnalyzer:
    """Create a mobile brand analyzer with given configuration."""
    return MobileBrandAnalyzer(config)










