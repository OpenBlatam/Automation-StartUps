"""
Federated Learning for Brand Analysis
Implements privacy-preserving distributed learning for brand analysis.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
import hashlib
import threading
from queue import Queue
import asyncio
import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets
from collections import defaultdict
import sqlite3
import base64

logger = logging.getLogger(__name__)

@dataclass
class FederatedConfig:
    """Configuration for federated learning."""
    num_clients: int = 10
    num_rounds: int = 100
    local_epochs: int = 5
    learning_rate: float = 0.01
    batch_size: int = 32
    privacy_budget: float = 1.0
    use_differential_privacy: bool = True
    noise_multiplier: float = 1.1
    l2_norm_clip: float = 1.0
    secure_aggregation: bool = True
    communication_rounds: int = 3
    min_clients_per_round: int = 5
    max_clients_per_round: int = 10

class DifferentialPrivacy:
    """Differential privacy implementation for federated learning."""
    
    def __init__(self, noise_multiplier: float = 1.1, l2_norm_clip: float = 1.0):
        self.noise_multiplier = noise_multiplier
        self.l2_norm_clip = l2_norm_clip
    
    def add_noise(self, gradients: List[torch.Tensor], privacy_budget: float) -> List[torch.Tensor]:
        """Add calibrated noise to gradients for differential privacy."""
        try:
            # Clip gradients
            clipped_gradients = self._clip_gradients(gradients)
            
            # Calculate noise scale
            noise_scale = self.l2_norm_clip * self.noise_multiplier / privacy_budget
            
            # Add Gaussian noise
            noisy_gradients = []
            for grad in clipped_gradients:
                noise = torch.normal(0, noise_scale, size=grad.shape)
                noisy_grad = grad + noise
                noisy_gradients.append(noisy_grad)
            
            return noisy_gradients
            
        except Exception as e:
            logger.error(f"Differential privacy noise addition failed: {e}")
            return gradients
    
    def _clip_gradients(self, gradients: List[torch.Tensor]) -> List[torch.Tensor]:
        """Clip gradients to L2 norm."""
        clipped_gradients = []
        
        for grad in gradients:
            # Calculate L2 norm
            grad_norm = torch.norm(grad)
            
            # Clip if necessary
            if grad_norm > self.l2_norm_clip:
                clipped_grad = grad * (self.l2_norm_clip / grad_norm)
            else:
                clipped_grad = grad
            
            clipped_gradients.append(clipped_grad)
        
        return clipped_gradients
    
    def calculate_privacy_loss(self, num_rounds: int, num_clients: int) -> float:
        """Calculate privacy loss for given number of rounds and clients."""
        # Simplified privacy loss calculation
        # In practice, you'd use more sophisticated methods like RDP
        privacy_loss = num_rounds * num_clients * self.noise_multiplier / (self.l2_norm_clip ** 2)
        return privacy_loss

class SecureAggregation:
    """Secure aggregation for federated learning."""
    
    def __init__(self, num_clients: int):
        self.num_clients = num_clients
        self.private_keys = {}
        self.public_keys = {}
        self._generate_key_pairs()
    
    def _generate_key_pairs(self):
        """Generate RSA key pairs for each client."""
        for client_id in range(self.num_clients):
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            self.private_keys[client_id] = private_key
            self.public_keys[client_id] = public_key
    
    def encrypt_gradients(self, gradients: List[torch.Tensor], client_id: int) -> List[bytes]:
        """Encrypt gradients for secure aggregation."""
        try:
            private_key = self.private_keys[client_id]
            encrypted_gradients = []
            
            for grad in gradients:
                # Convert tensor to bytes
                grad_bytes = grad.detach().numpy().tobytes()
                
                # Encrypt with private key
                encrypted = private_key.encrypt(
                    grad_bytes,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                encrypted_gradients.append(encrypted)
            
            return encrypted_gradients
            
        except Exception as e:
            logger.error(f"Gradient encryption failed: {e}")
            return []
    
    def decrypt_gradients(self, encrypted_gradients: List[bytes], client_id: int) -> List[torch.Tensor]:
        """Decrypt gradients from secure aggregation."""
        try:
            private_key = self.private_keys[client_id]
            decrypted_gradients = []
            
            for encrypted_grad in encrypted_gradients:
                # Decrypt
                decrypted_bytes = private_key.decrypt(
                    encrypted_grad,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Convert back to tensor
                grad_array = np.frombuffer(decrypted_bytes, dtype=np.float32)
                grad_tensor = torch.from_numpy(grad_array)
                decrypted_gradients.append(grad_tensor)
            
            return decrypted_gradients
            
        except Exception as e:
            logger.error(f"Gradient decryption failed: {e}")
            return []
    
    def aggregate_encrypted_gradients(self, encrypted_gradients_list: List[List[bytes]]) -> List[bytes]:
        """Aggregate encrypted gradients securely."""
        try:
            if not encrypted_gradients_list:
                return []
            
            num_gradients = len(encrypted_gradients_list[0])
            aggregated_gradients = []
            
            for i in range(num_gradients):
                # Collect encrypted gradients for this parameter
                encrypted_params = [grads[i] for grads in encrypted_gradients_list]
                
                # Simple aggregation (in practice, you'd use more sophisticated methods)
                aggregated_param = self._aggregate_encrypted_params(encrypted_params)
                aggregated_gradients.append(aggregated_param)
            
            return aggregated_gradients
            
        except Exception as e:
            logger.error(f"Encrypted gradient aggregation failed: {e}")
            return []
    
    def _aggregate_encrypted_params(self, encrypted_params: List[bytes]) -> bytes:
        """Aggregate encrypted parameters (simplified implementation)."""
        # This is a simplified implementation
        # In practice, you'd use more sophisticated secure aggregation protocols
        return encrypted_params[0]  # Placeholder

class FederatedClient:
    """Federated learning client."""
    
    def __init__(self, client_id: int, config: FederatedConfig):
        self.client_id = client_id
        self.config = config
        self.model = None
        self.optimizer = None
        self.local_data = []
        self.privacy_budget = config.privacy_budget
        self.dp = DifferentialPrivacy(config.noise_multiplier, config.l2_norm_clip)
        self.secure_agg = SecureAggregation(config.num_clients)
        
    def initialize_model(self, model: nn.Module):
        """Initialize local model."""
        self.model = model
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
    
    def add_local_data(self, data: List[Dict[str, Any]]):
        """Add local training data."""
        self.local_data.extend(data)
    
    def train_local_model(self, global_model_state: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """Train local model on local data."""
        try:
            # Load global model state
            self.model.load_state_dict(global_model_state)
            
            # Train for local epochs
            local_losses = []
            for epoch in range(self.config.local_epochs):
                epoch_loss = self._train_epoch()
                local_losses.append(epoch_loss)
            
            # Get model gradients
            gradients = self._get_model_gradients()
            
            # Apply differential privacy
            if self.config.use_differential_privacy:
                gradients = self.dp.add_noise(gradients, self.privacy_budget)
            
            # Encrypt gradients for secure aggregation
            encrypted_gradients = self.secure_agg.encrypt_gradients(gradients, self.client_id)
            
            return {
                'client_id': self.client_id,
                'encrypted_gradients': encrypted_gradients,
                'local_losses': local_losses,
                'data_size': len(self.local_data),
                'privacy_budget_used': self.privacy_budget
            }
            
        except Exception as e:
            logger.error(f"Local training failed for client {self.client_id}: {e}")
            return {
                'client_id': self.client_id,
                'error': str(e),
                'data_size': len(self.local_data)
            }
    
    def _train_epoch(self) -> float:
        """Train for one epoch."""
        total_loss = 0.0
        num_batches = 0
        
        # Create data loader
        data_loader = self._create_data_loader()
        
        for batch in data_loader:
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(batch['features'])
            loss = F.mse_loss(outputs, batch['targets'])
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def _create_data_loader(self) -> List[Dict[str, torch.Tensor]]:
        """Create data loader from local data."""
        batches = []
        
        for i in range(0, len(self.local_data), self.config.batch_size):
            batch_data = self.local_data[i:i + self.config.batch_size]
            
            # Extract features and targets
            features = torch.stack([self._extract_features(sample) for sample in batch_data])
            targets = torch.tensor([sample.get('consistency_score', 0.5) for sample in batch_data])
            
            batches.append({
                'features': features,
                'targets': targets
            })
        
        return batches
    
    def _extract_features(self, sample: Dict[str, Any]) -> torch.Tensor:
        """Extract features from sample."""
        features = []
        
        # Color features
        if 'colors' in sample:
            colors = sample['colors']
            for color in colors[:8]:  # Limit to 8 colors
                features.extend(color)
        
        # Pad or truncate colors
        while len(features) < 24:  # 8 colors * 3 RGB
            features.append(0.0)
        features = features[:24]
        
        # Typography features
        if 'typography' in sample:
            typography = sample['typography']
            features.extend(typography[:8])  # Limit to 8 features
        
        # Pad typography
        while len(features) < 32:  # 24 colors + 8 typography
            features.append(0.0)
        features = features[:32]
        
        # Layout features
        if 'layout' in sample:
            layout = sample['layout']
            features.extend(layout[:8])  # Limit to 8 features
        
        # Pad layout
        while len(features) < 40:  # 32 previous + 8 layout
            features.append(0.0)
        features = features[:40]
        
        # Text features
        if 'text_features' in sample:
            text_features = sample['text_features']
            features.extend(text_features[:8])  # Limit to 8 features
        
        # Pad text features
        while len(features) < 48:  # 40 previous + 8 text
            features.append(0.0)
        features = features[:48]
        
        return torch.tensor(features, dtype=torch.float32)
    
    def _get_model_gradients(self) -> List[torch.Tensor]:
        """Get model gradients."""
        gradients = []
        for param in self.model.parameters():
            if param.grad is not None:
                gradients.append(param.grad.clone())
        return gradients

class FederatedServer:
    """Federated learning server."""
    
    def __init__(self, config: FederatedConfig):
        self.config = config
        self.clients = {}
        self.global_model = None
        self.secure_agg = SecureAggregation(config.num_clients)
        self.dp = DifferentialPrivacy(config.noise_multiplier, config.l2_norm_clip)
        self.training_history = []
        self.privacy_budget_remaining = config.privacy_budget
        
    def initialize_global_model(self, model: nn.Module):
        """Initialize global model."""
        self.global_model = model
    
    def add_client(self, client_id: int, client: FederatedClient):
        """Add a client to the federation."""
        self.clients[client_id] = client
    
    def run_federated_training(self) -> Dict[str, Any]:
        """Run federated training rounds."""
        logger.info(f"Starting federated training with {len(self.clients)} clients")
        
        training_results = {
            'rounds_completed': 0,
            'final_accuracy': 0.0,
            'privacy_budget_used': 0.0,
            'client_participation': [],
            'convergence_history': []
        }
        
        for round_num in range(self.config.num_rounds):
            logger.info(f"Starting round {round_num + 1}/{self.config.num_rounds}")
            
            # Select clients for this round
            selected_clients = self._select_clients_for_round()
            
            if len(selected_clients) < self.config.min_clients_per_round:
                logger.warning(f"Not enough clients for round {round_num + 1}")
                break
            
            # Run federated round
            round_result = self._run_federated_round(round_num, selected_clients)
            
            if not round_result['success']:
                logger.error(f"Round {round_num + 1} failed: {round_result['error']}")
                break
            
            # Update training results
            training_results['rounds_completed'] = round_num + 1
            training_results['client_participation'].append({
                'round': round_num + 1,
                'clients': selected_clients,
                'data_size': round_result['total_data_size']
            })
            training_results['convergence_history'].append(round_result['avg_loss'])
            
            # Check convergence
            if self._check_convergence(training_results['convergence_history']):
                logger.info(f"Convergence reached at round {round_num + 1}")
                break
        
        # Calculate final metrics
        training_results['final_accuracy'] = self._evaluate_global_model()
        training_results['privacy_budget_used'] = self.config.privacy_budget - self.privacy_budget_remaining
        
        self.training_history.append(training_results)
        
        logger.info(f"Federated training completed. Rounds: {training_results['rounds_completed']}")
        return training_results
    
    def _select_clients_for_round(self) -> List[int]:
        """Select clients for current round."""
        available_clients = list(self.clients.keys())
        
        # Randomly select clients
        num_clients = min(
            self.config.max_clients_per_round,
            len(available_clients)
        )
        
        selected_clients = np.random.choice(
            available_clients, 
            size=num_clients, 
            replace=False
        ).tolist()
        
        return selected_clients
    
    def _run_federated_round(self, round_num: int, selected_clients: List[int]) -> Dict[str, Any]:
        """Run a single federated round."""
        try:
            # Get global model state
            global_model_state = self.global_model.state_dict()
            
            # Collect local updates from clients
            client_updates = []
            total_data_size = 0
            
            for client_id in selected_clients:
                client = self.clients[client_id]
                
                # Train local model
                local_result = client.train_local_model(global_model_state)
                
                if 'error' not in local_result:
                    client_updates.append(local_result)
                    total_data_size += local_result['data_size']
                else:
                    logger.warning(f"Client {client_id} failed: {local_result['error']}")
            
            if not client_updates:
                return {'success': False, 'error': 'No successful client updates'}
            
            # Aggregate updates
            aggregated_gradients = self._aggregate_client_updates(client_updates)
            
            # Update global model
            self._update_global_model(aggregated_gradients)
            
            # Calculate average loss
            avg_loss = np.mean([update['local_losses'][-1] for update in client_updates])
            
            return {
                'success': True,
                'round': round_num + 1,
                'clients_participated': len(client_updates),
                'total_data_size': total_data_size,
                'avg_loss': avg_loss
            }
            
        except Exception as e:
            logger.error(f"Federated round failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _aggregate_client_updates(self, client_updates: List[Dict[str, Any]]) -> List[torch.Tensor]:
        """Aggregate client updates."""
        try:
            # Collect encrypted gradients
            encrypted_gradients_list = [update['encrypted_gradients'] for update in client_updates]
            
            # Aggregate encrypted gradients
            aggregated_encrypted = self.secure_agg.aggregate_encrypted_gradients(encrypted_gradients_list)
            
            # Decrypt aggregated gradients (simplified)
            aggregated_gradients = self._decrypt_aggregated_gradients(aggregated_encrypted)
            
            return aggregated_gradients
            
        except Exception as e:
            logger.error(f"Client update aggregation failed: {e}")
            return []
    
    def _decrypt_aggregated_gradients(self, encrypted_gradients: List[bytes]) -> List[torch.Tensor]:
        """Decrypt aggregated gradients (simplified implementation)."""
        # This is a simplified implementation
        # In practice, you'd use more sophisticated secure aggregation protocols
        return []
    
    def _update_global_model(self, gradients: List[torch.Tensor]):
        """Update global model with aggregated gradients."""
        try:
            if not gradients:
                return
            
            # Update model parameters
            param_idx = 0
            for param in self.global_model.parameters():
                if param_idx < len(gradients):
                    param.data += gradients[param_idx] * self.config.learning_rate
                    param_idx += 1
            
        except Exception as e:
            logger.error(f"Global model update failed: {e}")
    
    def _check_convergence(self, loss_history: List[float]) -> bool:
        """Check if training has converged."""
        if len(loss_history) < 10:
            return False
        
        # Check if loss has stabilized
        recent_losses = loss_history[-10:]
        loss_std = np.std(recent_losses)
        loss_mean = np.mean(recent_losses)
        
        # Converged if standard deviation is small relative to mean
        return loss_std / (loss_mean + 1e-6) < 0.01
    
    def _evaluate_global_model(self) -> float:
        """Evaluate global model performance."""
        # This would evaluate the model on a test set
        # For now, return a placeholder
        return 0.85

class FederatedBrandAnalyzer:
    """Federated learning brand analyzer."""
    
    def __init__(self, config: FederatedConfig):
        self.config = config
        self.server = FederatedServer(config)
        self.clients = {}
        self.model = self._create_federated_model()
        self.server.initialize_global_model(self.model)
        
    def _create_federated_model(self) -> nn.Module:
        """Create federated learning model."""
        return nn.Sequential(
            nn.Linear(48, 128),  # 48 input features
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
    
    def add_client_data(self, client_id: int, data: List[Dict[str, Any]]):
        """Add data for a specific client."""
        if client_id not in self.clients:
            self.clients[client_id] = FederatedClient(client_id, self.config)
            self.clients[client_id].initialize_model(self.model)
            self.server.add_client(client_id, self.clients[client_id])
        
        self.clients[client_id].add_local_data(data)
    
    def train_federated_model(self) -> Dict[str, Any]:
        """Train federated model."""
        logger.info("Starting federated training...")
        
        # Run federated training
        training_result = self.server.run_federated_training()
        
        # Update all client models with final global model
        global_model_state = self.server.global_model.state_dict()
        for client in self.clients.values():
            client.model.load_state_dict(global_model_state)
        
        return training_result
    
    def analyze_brand_federated(self, brand_data: Dict[str, Any], client_id: int) -> Dict[str, Any]:
        """Analyze brand using federated model."""
        try:
            if client_id not in self.clients:
                return {'success': False, 'error': f'Client {client_id} not found'}
            
            client = self.clients[client_id]
            
            # Extract features
            features = client._extract_features(brand_data)
            features_tensor = features.unsqueeze(0)
            
            # Make prediction
            with torch.no_grad():
                prediction = client.model(features_tensor)
                consistency_score = prediction.item()
            
            return {
                'success': True,
                'consistency_score': consistency_score,
                'client_id': client_id,
                'model_type': 'federated',
                'privacy_preserved': True
            }
            
        except Exception as e:
            logger.error(f"Federated brand analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_federation_stats(self) -> Dict[str, Any]:
        """Get federation statistics."""
        return {
            'total_clients': len(self.clients),
            'total_rounds': len(self.server.training_history),
            'privacy_budget_remaining': self.server.privacy_budget_remaining,
            'client_data_sizes': {
                client_id: len(client.local_data) 
                for client_id, client in self.clients.items()
            }
        }

def create_federated_analyzer(config: FederatedConfig) -> FederatedBrandAnalyzer:
    """Create a federated brand analyzer with given configuration."""
    return FederatedBrandAnalyzer(config)










