"""
AR/VR Immersive Brand Analysis
Implements augmented and virtual reality interfaces for brand analysis.
"""

import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import json
import time
from dataclasses import dataclass
from pathlib import Path
import threading
from queue import Queue
import asyncio
import aiohttp
from PIL import Image
import io
import base64
import math
from scipy.spatial.transform import Rotation
import open3d as o3d
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

logger = logging.getLogger(__name__)

@dataclass
class ARVRConfig:
    """Configuration for AR/VR brand analysis."""
    device_type: str = "mixed_reality"  # ar, vr, mixed_reality
    tracking_method: str = "visual"  # visual, imu, hybrid
    spatial_resolution: float = 0.01  # meters
    temporal_resolution: float = 30.0  # fps
    max_objects: int = 100
    use_hand_tracking: bool = True
    use_eye_tracking: bool = True
    use_voice_commands: bool = True
    enable_haptic_feedback: bool = True
    spatial_audio: bool = True

class SpatialBrandAnalyzer:
    """Spatial brand analysis for AR/VR environments."""
    
    def __init__(self, config: ARVRConfig):
        self.config = config
        self.spatial_objects = {}
        self.brand_annotations = {}
        self.spatial_memory = {}
        self.tracking_data = []
        self.analysis_queue = Queue()
        self.visualization_objects = {}
        
    def analyze_spatial_brand(self, spatial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze brand elements in 3D space."""
        try:
            # Extract 3D brand elements
            brand_elements = self._extract_3d_brand_elements(spatial_data)
            
            # Analyze spatial relationships
            spatial_analysis = self._analyze_spatial_relationships(brand_elements)
            
            # Generate 3D brand kit
            brand_kit_3d = self._generate_3d_brand_kit(brand_elements, spatial_analysis)
            
            # Create immersive visualizations
            visualizations = self._create_immersive_visualizations(brand_kit_3d)
            
            return {
                'success': True,
                'spatial_analysis': spatial_analysis,
                'brand_kit_3d': brand_kit_3d,
                'visualizations': visualizations,
                'spatial_objects': len(brand_elements),
                'analysis_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"Spatial brand analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_3d_brand_elements(self, spatial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract 3D brand elements from spatial data."""
        elements = []
        
        # Extract from point cloud
        if 'point_cloud' in spatial_data:
            point_cloud = spatial_data['point_cloud']
            elements.extend(self._extract_from_point_cloud(point_cloud))
        
        # Extract from RGB-D data
        if 'rgbd_data' in spatial_data:
            rgbd_data = spatial_data['rgbd_data']
            elements.extend(self._extract_from_rgbd(rgbd_data))
        
        # Extract from mesh data
        if 'mesh_data' in spatial_data:
            mesh_data = spatial_data['mesh_data']
            elements.extend(self._extract_from_mesh(mesh_data))
        
        return elements
    
    def _extract_from_point_cloud(self, point_cloud: np.ndarray) -> List[Dict[str, Any]]:
        """Extract brand elements from point cloud data."""
        elements = []
        
        try:
            # Convert to Open3D point cloud
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(point_cloud[:, :3])
            
            if point_cloud.shape[1] > 3:
                pcd.colors = o3d.utility.Vector3dVector(point_cloud[:, 3:6] / 255.0)
            
            # Cluster points to find objects
            labels = np.array(pcd.cluster_dbscan(eps=0.02, min_points=10))
            
            # Extract elements from each cluster
            for label in np.unique(labels):
                if label == -1:  # Noise
                    continue
                
                cluster_points = point_cloud[labels == label]
                element = self._analyze_point_cluster(cluster_points, label)
                if element:
                    elements.append(element)
            
        except Exception as e:
            logger.error(f"Point cloud extraction failed: {e}")
        
        return elements
    
    def _extract_from_rgbd(self, rgbd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract brand elements from RGB-D data."""
        elements = []
        
        try:
            # Get RGB and depth images
            rgb_image = rgbd_data['rgb']
            depth_image = rgbd_data['depth']
            camera_params = rgbd_data.get('camera_params', {})
            
            # Detect brand elements in RGB image
            brand_regions = self._detect_brand_regions(rgb_image)
            
            # Extract 3D information for each region
            for region in brand_regions:
                element = self._extract_3d_from_region(region, rgb_image, depth_image, camera_params)
                if element:
                    elements.append(element)
            
        except Exception as e:
            logger.error(f"RGB-D extraction failed: {e}")
        
        return elements
    
    def _extract_from_mesh(self, mesh_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract brand elements from mesh data."""
        elements = []
        
        try:
            # Load mesh
            mesh = o3d.geometry.TriangleMesh()
            mesh.vertices = o3d.utility.Vector3dVector(mesh_data['vertices'])
            mesh.triangles = o3d.utility.Vector3iVector(mesh_data['triangles'])
            
            if 'colors' in mesh_data:
                mesh.vertex_colors = o3d.utility.Vector3dVector(mesh_data['colors'])
            
            # Analyze mesh for brand elements
            element = self._analyze_mesh_brand_elements(mesh)
            if element:
                elements.append(element)
            
        except Exception as e:
            logger.error(f"Mesh extraction failed: {e}")
        
        return elements
    
    def _analyze_point_cluster(self, cluster_points: np.ndarray, label: int) -> Optional[Dict[str, Any]]:
        """Analyze a cluster of points for brand elements."""
        try:
            # Calculate cluster properties
            center = np.mean(cluster_points[:, :3], axis=0)
            size = np.std(cluster_points[:, :3], axis=0)
            
            # Extract color information
            colors = cluster_points[:, 3:6] if cluster_points.shape[1] > 3 else None
            dominant_color = np.mean(colors, axis=0) if colors is not None else [128, 128, 128]
            
            # Calculate shape properties
            shape_properties = self._calculate_shape_properties(cluster_points[:, :3])
            
            return {
                'type': 'spatial_object',
                'label': label,
                'center': center.tolist(),
                'size': size.tolist(),
                'color': dominant_color.tolist(),
                'shape_properties': shape_properties,
                'point_count': len(cluster_points)
            }
            
        except Exception as e:
            logger.error(f"Point cluster analysis failed: {e}")
            return None
    
    def _detect_brand_regions(self, rgb_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect brand regions in RGB image."""
        regions = []
        
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB)
            
            # Detect text regions
            text_regions = self._detect_text_regions(rgb_image)
            regions.extend(text_regions)
            
            # Detect logo regions
            logo_regions = self._detect_logo_regions(rgb_image)
            regions.extend(logo_regions)
            
            # Detect color regions
            color_regions = self._detect_color_regions(rgb_image, hsv)
            regions.extend(color_regions)
            
        except Exception as e:
            logger.error(f"Brand region detection failed: {e}")
        
        return regions
    
    def _detect_text_regions(self, rgb_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect text regions in image."""
        regions = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            
            # Use EAST text detector or similar
            # For now, use simple edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                # Filter by area and aspect ratio
                area = cv2.contourArea(contour)
                if area < 100:  # Too small
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                if 0.1 < aspect_ratio < 10:  # Reasonable aspect ratio for text
                    regions.append({
                        'type': 'text',
                        'bbox': [x, y, w, h],
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'confidence': min(1.0, area / 1000)
                    })
            
        except Exception as e:
            logger.error(f"Text region detection failed: {e}")
        
        return regions
    
    def _detect_logo_regions(self, rgb_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect logo regions in image."""
        regions = []
        
        try:
            # Use template matching or feature detection
            # For now, use simple corner detection
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            
            # Detect corners
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
            
            if corners is not None:
                # Group nearby corners
                corner_groups = self._group_corners(corners)
                
                for group in corner_groups:
                    if len(group) >= 4:  # At least 4 corners for a logo
                        x_coords = [corner[0][0] for corner in group]
                        y_coords = [corner[0][1] for corner in group]
                        
                        x_min, x_max = min(x_coords), max(x_coords)
                        y_min, y_max = min(y_coords), max(y_coords)
                        
                        regions.append({
                            'type': 'logo',
                            'bbox': [x_min, y_min, x_max - x_min, y_max - y_min],
                            'corner_count': len(group),
                            'confidence': min(1.0, len(group) / 10)
                        })
            
        except Exception as e:
            logger.error(f"Logo region detection failed: {e}")
        
        return regions
    
    def _detect_color_regions(self, rgb_image: np.ndarray, hsv_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect color regions in image."""
        regions = []
        
        try:
            # Define color ranges for common brand colors
            color_ranges = {
                'red': [(0, 50, 50), (10, 255, 255)],
                'blue': [(100, 50, 50), (130, 255, 255)],
                'green': [(40, 50, 50), (80, 255, 255)],
                'yellow': [(20, 50, 50), (30, 255, 255)],
                'purple': [(130, 50, 50), (160, 255, 255)]
            }
            
            for color_name, (lower, upper) in color_ranges.items():
                # Create mask
                mask = cv2.inRange(hsv_image, np.array(lower), np.array(upper))
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 500:  # Significant color region
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        regions.append({
                            'type': 'color_region',
                            'color': color_name,
                            'bbox': [x, y, w, h],
                            'area': area,
                            'confidence': min(1.0, area / 5000)
                        })
            
        except Exception as e:
            logger.error(f"Color region detection failed: {e}")
        
        return regions
    
    def _group_corners(self, corners: np.ndarray, max_distance: float = 50.0) -> List[List[np.ndarray]]:
        """Group nearby corners together."""
        groups = []
        used = set()
        
        for i, corner in enumerate(corners):
            if i in used:
                continue
            
            group = [corner]
            used.add(i)
            
            for j, other_corner in enumerate(corners):
                if j in used:
                    continue
                
                distance = np.linalg.norm(corner - other_corner)
                if distance < max_distance:
                    group.append(other_corner)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _extract_3d_from_region(self, region: Dict[str, Any], rgb_image: np.ndarray, 
                               depth_image: np.ndarray, camera_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract 3D information from 2D region."""
        try:
            bbox = region['bbox']
            x, y, w, h = bbox
            
            # Extract region from images
            rgb_region = rgb_image[y:y+h, x:x+w]
            depth_region = depth_image[y:y+h, x:x+w]
            
            # Calculate 3D position
            center_x, center_y = x + w//2, y + h//2
            depth_value = np.median(depth_region[depth_region > 0])
            
            if depth_value == 0:
                return None
            
            # Convert to 3D coordinates
            fx = camera_params.get('fx', 525.0)
            fy = camera_params.get('fy', 525.0)
            cx = camera_params.get('cx', 320.0)
            cy = camera_params.get('cy', 240.0)
            
            x_3d = (center_x - cx) * depth_value / fx
            y_3d = (center_y - cy) * depth_value / fy
            z_3d = depth_value
            
            # Calculate 3D size
            width_3d = w * depth_value / fx
            height_3d = h * depth_value / fy
            
            return {
                'type': region['type'],
                'position_3d': [x_3d, y_3d, z_3d],
                'size_3d': [width_3d, height_3d, 0.1],  # Assume 10cm depth
                'bbox_2d': bbox,
                'confidence': region.get('confidence', 0.5),
                'color': self._extract_region_color(rgb_region)
            }
            
        except Exception as e:
            logger.error(f"3D extraction failed: {e}")
            return None
    
    def _extract_region_color(self, rgb_region: np.ndarray) -> List[int]:
        """Extract dominant color from region."""
        try:
            # Reshape to list of pixels
            pixels = rgb_region.reshape(-1, 3)
            
            # Use K-means to find dominant color
            kmeans = KMeans(n_clusters=1, random_state=42)
            kmeans.fit(pixels)
            
            dominant_color = kmeans.cluster_centers_[0].astype(int)
            return dominant_color.tolist()
            
        except Exception as e:
            logger.error(f"Color extraction failed: {e}")
            return [128, 128, 128]  # Default gray
    
    def _analyze_mesh_brand_elements(self, mesh: o3d.geometry.TriangleMesh) -> Optional[Dict[str, Any]]:
        """Analyze mesh for brand elements."""
        try:
            # Calculate mesh properties
            vertices = np.asarray(mesh.vertices)
            colors = np.asarray(mesh.vertex_colors) if mesh.has_vertex_colors() else None
            
            # Calculate bounding box
            bbox = mesh.get_axis_aligned_bounding_box()
            center = bbox.get_center()
            size = bbox.get_extent()
            
            # Calculate dominant color
            dominant_color = np.mean(colors, axis=0) * 255 if colors is not None else [128, 128, 128]
            
            # Calculate shape properties
            shape_properties = self._calculate_mesh_shape_properties(mesh)
            
            return {
                'type': 'mesh_object',
                'position_3d': center.tolist(),
                'size_3d': size.tolist(),
                'color': dominant_color.astype(int).tolist(),
                'shape_properties': shape_properties,
                'vertex_count': len(vertices)
            }
            
        except Exception as e:
            logger.error(f"Mesh analysis failed: {e}")
            return None
    
    def _calculate_shape_properties(self, points: np.ndarray) -> Dict[str, float]:
        """Calculate shape properties from 3D points."""
        try:
            # Calculate PCA to get principal axes
            pca = PCA(n_components=3)
            pca.fit(points)
            
            # Calculate aspect ratios
            explained_variance = pca.explained_variance_ratio_
            aspect_ratios = explained_variance / explained_variance[0]
            
            # Calculate compactness
            volume = np.prod(pca.explained_variance_)
            surface_area = self._estimate_surface_area(points)
            compactness = volume / (surface_area ** (3/2)) if surface_area > 0 else 0
            
            return {
                'aspect_ratios': aspect_ratios.tolist(),
                'compactness': compactness,
                'elongation': aspect_ratios[1] / aspect_ratios[0] if aspect_ratios[0] > 0 else 0,
                'flatness': aspect_ratios[2] / aspect_ratios[0] if aspect_ratios[0] > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Shape property calculation failed: {e}")
            return {'aspect_ratios': [1, 1, 1], 'compactness': 0, 'elongation': 1, 'flatness': 1}
    
    def _calculate_mesh_shape_properties(self, mesh: o3d.geometry.TriangleMesh) -> Dict[str, float]:
        """Calculate shape properties from mesh."""
        try:
            # Calculate surface area and volume
            surface_area = mesh.get_surface_area()
            volume = mesh.get_volume()
            
            # Calculate compactness
            compactness = volume / (surface_area ** (3/2)) if surface_area > 0 else 0
            
            # Calculate sphericity
            sphericity = (36 * np.pi * volume**2) ** (1/3) / surface_area if surface_area > 0 else 0
            
            return {
                'surface_area': surface_area,
                'volume': volume,
                'compactness': compactness,
                'sphericity': sphericity
            }
            
        except Exception as e:
            logger.error(f"Mesh shape property calculation failed: {e}")
            return {'surface_area': 0, 'volume': 0, 'compactness': 0, 'sphericity': 0}
    
    def _estimate_surface_area(self, points: np.ndarray) -> float:
        """Estimate surface area from point cloud."""
        try:
            # Use convex hull to estimate surface area
            hull = o3d.geometry.PointCloud()
            hull.points = o3d.utility.Vector3dVector(points)
            hull = hull.compute_convex_hull()[0]
            
            return hull.get_surface_area()
            
        except Exception as e:
            logger.error(f"Surface area estimation failed: {e}")
            return 0.0
    
    def _analyze_spatial_relationships(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze spatial relationships between brand elements."""
        try:
            if len(elements) < 2:
                return {'relationships': [], 'spatial_coherence': 0.0}
            
            relationships = []
            total_coherence = 0.0
            
            for i, element1 in enumerate(elements):
                for j, element2 in enumerate(elements[i+1:], i+1):
                    relationship = self._calculate_spatial_relationship(element1, element2)
                    relationships.append(relationship)
                    total_coherence += relationship['coherence']
            
            spatial_coherence = total_coherence / len(relationships) if relationships else 0.0
            
            return {
                'relationships': relationships,
                'spatial_coherence': spatial_coherence,
                'element_count': len(elements)
            }
            
        except Exception as e:
            logger.error(f"Spatial relationship analysis failed: {e}")
            return {'relationships': [], 'spatial_coherence': 0.0}
    
    def _calculate_spatial_relationship(self, element1: Dict[str, Any], element2: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate spatial relationship between two elements."""
        try:
            pos1 = np.array(element1.get('position_3d', [0, 0, 0]))
            pos2 = np.array(element2.get('position_3d', [0, 0, 0]))
            
            # Calculate distance
            distance = np.linalg.norm(pos1 - pos2)
            
            # Calculate relative position
            relative_pos = pos2 - pos1
            direction = relative_pos / distance if distance > 0 else [0, 0, 0]
            
            # Calculate alignment
            alignment = self._calculate_alignment(element1, element2)
            
            # Calculate coherence based on type compatibility
            coherence = self._calculate_type_coherence(element1, element2)
            
            return {
                'element1_type': element1.get('type', 'unknown'),
                'element2_type': element2.get('type', 'unknown'),
                'distance': distance,
                'direction': direction.tolist(),
                'alignment': alignment,
                'coherence': coherence
            }
            
        except Exception as e:
            logger.error(f"Spatial relationship calculation failed: {e}")
            return {'element1_type': 'unknown', 'element2_type': 'unknown', 'distance': 0, 'direction': [0, 0, 0], 'alignment': 0, 'coherence': 0}
    
    def _calculate_alignment(self, element1: Dict[str, Any], element2: Dict[str, Any]) -> float:
        """Calculate alignment between two elements."""
        try:
            # Get element orientations (simplified)
            orientation1 = element1.get('shape_properties', {}).get('aspect_ratios', [1, 1, 1])
            orientation2 = element2.get('shape_properties', {}).get('aspect_ratios', [1, 1, 1])
            
            # Calculate alignment based on principal axes
            alignment = np.dot(orientation1, orientation2) / (np.linalg.norm(orientation1) * np.linalg.norm(orientation2))
            
            return float(alignment)
            
        except Exception as e:
            logger.error(f"Alignment calculation failed: {e}")
            return 0.0
    
    def _calculate_type_coherence(self, element1: Dict[str, Any], element2: Dict[str, Any]) -> float:
        """Calculate coherence between element types."""
        type1 = element1.get('type', 'unknown')
        type2 = element2.get('type', 'unknown')
        
        # Define type compatibility matrix
        compatibility = {
            ('text', 'logo'): 0.9,
            ('text', 'color_region'): 0.7,
            ('logo', 'color_region'): 0.8,
            ('spatial_object', 'spatial_object'): 0.6,
            ('mesh_object', 'mesh_object'): 0.7
        }
        
        # Check both directions
        key1 = (type1, type2)
        key2 = (type2, type1)
        
        return compatibility.get(key1, compatibility.get(key2, 0.3))
    
    def _generate_3d_brand_kit(self, elements: List[Dict[str, Any]], 
                              spatial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate 3D brand kit from spatial analysis."""
        try:
            # Extract color palette
            colors = [elem.get('color', [128, 128, 128]) for elem in elements if 'color' in elem]
            color_palette = self._create_color_palette(colors)
            
            # Extract typography (from text elements)
            text_elements = [elem for elem in elements if elem.get('type') == 'text']
            typography = self._extract_typography_3d(text_elements)
            
            # Extract layout (from spatial relationships)
            layout = self._extract_layout_3d(elements, spatial_analysis)
            
            # Calculate 3D consistency
            consistency_3d = self._calculate_3d_consistency(elements, spatial_analysis)
            
            return {
                'color_palette_3d': color_palette,
                'typography_3d': typography,
                'layout_3d': layout,
                'consistency_3d': consistency_3d,
                'spatial_coherence': spatial_analysis.get('spatial_coherence', 0.0),
                'element_count': len(elements)
            }
            
        except Exception as e:
            logger.error(f"3D brand kit generation failed: {e}")
            return {'color_palette_3d': [], 'typography_3d': [], 'layout_3d': [], 'consistency_3d': 0.0, 'spatial_coherence': 0.0, 'element_count': 0}
    
    def _create_color_palette(self, colors: List[List[int]]) -> List[List[int]]:
        """Create color palette from 3D elements."""
        if not colors:
            return [[128, 128, 128]]
        
        try:
            # Use K-means to find dominant colors
            kmeans = KMeans(n_clusters=min(8, len(colors)), random_state=42)
            kmeans.fit(colors)
            
            return kmeans.cluster_centers_.astype(int).tolist()
            
        except Exception as e:
            logger.error(f"Color palette creation failed: {e}")
            return colors[:8]  # Return first 8 colors
    
    def _extract_typography_3d(self, text_elements: List[Dict[str, Any]]) -> List[float]:
        """Extract typography features from 3D text elements."""
        if not text_elements:
            return [0.5] * 8  # Default typography
        
        try:
            # Calculate typography features
            sizes = [elem.get('size_3d', [0, 0, 0]) for elem in text_elements]
            positions = [elem.get('position_3d', [0, 0, 0]) for elem in text_elements]
            
            # Calculate size variation
            size_variation = np.std([s[0] for s in sizes]) if sizes else 0
            
            # Calculate position alignment
            position_alignment = self._calculate_position_alignment(positions)
            
            # Calculate text density
            text_density = len(text_elements) / 10.0  # Normalize by area
            
            return [
                size_variation,
                position_alignment,
                text_density,
                0.5,  # Placeholder for other features
                0.5,
                0.5,
                0.5,
                0.5
            ]
            
        except Exception as e:
            logger.error(f"Typography extraction failed: {e}")
            return [0.5] * 8
    
    def _calculate_position_alignment(self, positions: List[List[float]]) -> float:
        """Calculate alignment of text positions."""
        if len(positions) < 2:
            return 0.5
        
        try:
            # Calculate alignment along each axis
            x_positions = [pos[0] for pos in positions]
            y_positions = [pos[1] for pos in positions]
            
            x_alignment = 1 - (np.std(x_positions) / (np.max(x_positions) - np.min(x_positions) + 1e-6))
            y_alignment = 1 - (np.std(y_positions) / (np.max(y_positions) - np.min(y_positions) + 1e-6))
            
            return (x_alignment + y_alignment) / 2
            
        except Exception as e:
            logger.error(f"Position alignment calculation failed: {e}")
            return 0.5
    
    def _extract_layout_3d(self, elements: List[Dict[str, Any]], 
                          spatial_analysis: Dict[str, Any]) -> List[float]:
        """Extract layout features from 3D elements."""
        try:
            # Calculate layout features
            positions = [elem.get('position_3d', [0, 0, 0]) for elem in elements]
            
            if not positions:
                return [0.5] * 8
            
            # Calculate spatial distribution
            positions_array = np.array(positions)
            center = np.mean(positions_array, axis=0)
            spread = np.std(positions_array, axis=0)
            
            # Calculate layout balance
            balance = self._calculate_3d_balance(positions_array, center)
            
            # Calculate layout rhythm
            rhythm = self._calculate_3d_rhythm(positions_array)
            
            # Calculate layout hierarchy
            hierarchy = self._calculate_3d_hierarchy(elements)
            
            return [
                balance,
                rhythm,
                hierarchy,
                spatial_analysis.get('spatial_coherence', 0.0),
                np.mean(spread),
                np.std(spread),
                0.5,  # Placeholder
                0.5   # Placeholder
            ]
            
        except Exception as e:
            logger.error(f"Layout extraction failed: {e}")
            return [0.5] * 8
    
    def _calculate_3d_balance(self, positions: np.ndarray, center: np.ndarray) -> float:
        """Calculate 3D balance of elements."""
        try:
            # Calculate balance around center
            distances = np.linalg.norm(positions - center, axis=1)
            balance = 1 - (np.std(distances) / (np.mean(distances) + 1e-6))
            
            return max(0, min(1, balance))
            
        except Exception as e:
            logger.error(f"3D balance calculation failed: {e}")
            return 0.5
    
    def _calculate_3d_rhythm(self, positions: np.ndarray) -> float:
        """Calculate 3D rhythm of elements."""
        try:
            # Calculate rhythm along each axis
            x_rhythm = self._calculate_axis_rhythm(positions[:, 0])
            y_rhythm = self._calculate_axis_rhythm(positions[:, 1])
            z_rhythm = self._calculate_axis_rhythm(positions[:, 2])
            
            return (x_rhythm + y_rhythm + z_rhythm) / 3
            
        except Exception as e:
            logger.error(f"3D rhythm calculation failed: {e}")
            return 0.5
    
    def _calculate_axis_rhythm(self, axis_positions: np.ndarray) -> float:
        """Calculate rhythm along a single axis."""
        try:
            if len(axis_positions) < 2:
                return 0.5
            
            # Sort positions
            sorted_positions = np.sort(axis_positions)
            
            # Calculate intervals
            intervals = np.diff(sorted_positions)
            
            if len(intervals) == 0:
                return 0.5
            
            # Calculate rhythm regularity
            rhythm = 1 - (np.std(intervals) / (np.mean(intervals) + 1e-6))
            
            return max(0, min(1, rhythm))
            
        except Exception as e:
            logger.error(f"Axis rhythm calculation failed: {e}")
            return 0.5
    
    def _calculate_3d_hierarchy(self, elements: List[Dict[str, Any]]) -> float:
        """Calculate 3D hierarchy of elements."""
        try:
            # Calculate hierarchy based on size and position
            sizes = [elem.get('size_3d', [0, 0, 0]) for elem in elements]
            positions = [elem.get('position_3d', [0, 0, 0]) for elem in elements]
            
            if not sizes or not positions:
                return 0.5
            
            # Calculate size hierarchy
            size_hierarchy = np.std([s[0] for s in sizes]) / (np.mean([s[0] for s in sizes]) + 1e-6)
            
            # Calculate position hierarchy (elements closer to center are more important)
            center = np.mean(positions, axis=0)
            distances = [np.linalg.norm(np.array(pos) - center) for pos in positions]
            position_hierarchy = np.std(distances) / (np.mean(distances) + 1e-6)
            
            # Combine hierarchies
            hierarchy = (size_hierarchy + position_hierarchy) / 2
            
            return max(0, min(1, hierarchy))
            
        except Exception as e:
            logger.error(f"3D hierarchy calculation failed: {e}")
            return 0.5
    
    def _calculate_3d_consistency(self, elements: List[Dict[str, Any]], 
                                 spatial_analysis: Dict[str, Any]) -> float:
        """Calculate 3D consistency of brand elements."""
        try:
            # Calculate color consistency
            colors = [elem.get('color', [128, 128, 128]) for elem in elements if 'color' in elem]
            color_consistency = self._calculate_color_consistency(colors)
            
            # Calculate size consistency
            sizes = [elem.get('size_3d', [0, 0, 0]) for elem in elements if 'size_3d' in elem]
            size_consistency = self._calculate_size_consistency(sizes)
            
            # Calculate spatial consistency
            spatial_consistency = spatial_analysis.get('spatial_coherence', 0.0)
            
            # Combine consistencies
            consistency = (color_consistency + size_consistency + spatial_consistency) / 3
            
            return max(0, min(1, consistency))
            
        except Exception as e:
            logger.error(f"3D consistency calculation failed: {e}")
            return 0.5
    
    def _calculate_color_consistency(self, colors: List[List[int]]) -> float:
        """Calculate color consistency."""
        if len(colors) < 2:
            return 1.0
        
        try:
            # Calculate color distances
            color_distances = []
            for i, color1 in enumerate(colors):
                for color2 in colors[i+1:]:
                    distance = np.linalg.norm(np.array(color1) - np.array(color2))
                    color_distances.append(distance)
            
            # Consistency is inverse of average distance
            avg_distance = np.mean(color_distances)
            consistency = 1 - (avg_distance / 441)  # 441 is max distance in RGB space
            
            return max(0, min(1, consistency))
            
        except Exception as e:
            logger.error(f"Color consistency calculation failed: {e}")
            return 0.5
    
    def _calculate_size_consistency(self, sizes: List[List[float]]) -> float:
        """Calculate size consistency."""
        if len(sizes) < 2:
            return 1.0
        
        try:
            # Calculate size variation
            size_values = [s[0] for s in sizes if s[0] > 0]  # Use first dimension
            
            if not size_values:
                return 0.5
            
            variation = np.std(size_values) / (np.mean(size_values) + 1e-6)
            consistency = 1 - variation
            
            return max(0, min(1, consistency))
            
        except Exception as e:
            logger.error(f"Size consistency calculation failed: {e}")
            return 0.5
    
    def _create_immersive_visualizations(self, brand_kit_3d: Dict[str, Any]) -> Dict[str, Any]:
        """Create immersive visualizations for AR/VR."""
        try:
            visualizations = {
                '3d_scatter_plot': self._create_3d_scatter_plot(brand_kit_3d),
                'color_spectrum': self._create_color_spectrum(brand_kit_3d),
                'spatial_network': self._create_spatial_network(brand_kit_3d),
                'consistency_heatmap': self._create_consistency_heatmap(brand_kit_3d)
            }
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Immersive visualization creation failed: {e}")
            return {}
    
    def _create_3d_scatter_plot(self, brand_kit_3d: Dict[str, Any]) -> Dict[str, Any]:
        """Create 3D scatter plot visualization."""
        try:
            # This would create a 3D scatter plot
            # For now, return placeholder data
            return {
                'type': '3d_scatter',
                'data': [],
                'colors': brand_kit_3d.get('color_palette_3d', []),
                'title': '3D Brand Elements'
            }
            
        except Exception as e:
            logger.error(f"3D scatter plot creation failed: {e}")
            return {'type': '3d_scatter', 'data': [], 'colors': [], 'title': '3D Brand Elements'}
    
    def _create_color_spectrum(self, brand_kit_3d: Dict[str, Any]) -> Dict[str, Any]:
        """Create color spectrum visualization."""
        try:
            colors = brand_kit_3d.get('color_palette_3d', [])
            
            return {
                'type': 'color_spectrum',
                'colors': colors,
                'title': 'Brand Color Spectrum'
            }
            
        except Exception as e:
            logger.error(f"Color spectrum creation failed: {e}")
            return {'type': 'color_spectrum', 'colors': [], 'title': 'Brand Color Spectrum'}
    
    def _create_spatial_network(self, brand_kit_3d: Dict[str, Any]) -> Dict[str, Any]:
        """Create spatial network visualization."""
        try:
            # This would create a network visualization
            # For now, return placeholder data
            return {
                'type': 'spatial_network',
                'nodes': [],
                'edges': [],
                'title': 'Spatial Brand Network'
            }
            
        except Exception as e:
            logger.error(f"Spatial network creation failed: {e}")
            return {'type': 'spatial_network', 'nodes': [], 'edges': [], 'title': 'Spatial Brand Network'}
    
    def _create_consistency_heatmap(self, brand_kit_3d: Dict[str, Any]) -> Dict[str, Any]:
        """Create consistency heatmap visualization."""
        try:
            # This would create a heatmap
            # For now, return placeholder data
            return {
                'type': 'consistency_heatmap',
                'data': [],
                'title': 'Brand Consistency Heatmap'
            }
            
        except Exception as e:
            logger.error(f"Consistency heatmap creation failed: {e}")
            return {'type': 'consistency_heatmap', 'data': [], 'title': 'Brand Consistency Heatmap'}

def create_immersive_analyzer(config: ARVRConfig) -> SpatialBrandAnalyzer:
    """Create an immersive brand analyzer with given configuration."""
    return SpatialBrandAnalyzer(config)










