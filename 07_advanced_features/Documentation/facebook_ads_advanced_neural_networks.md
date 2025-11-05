---
title: "Facebook Ads Advanced Neural Networks"
category: "07_advanced_features"
tags: []
created: "2025-10-29"
path: "07_advanced_features/facebook_ads_advanced_neural_networks.md"
---

# Redes Neuronales Avanzadas para Predicción en Facebook Ads
## Arquitecturas de Deep Learning y Modelos de Vanguardia

---

## 1. Introducción a las Redes Neuronales Avanzadas

Esta guía presenta arquitecturas avanzadas de redes neuronales para predicción en Facebook Ads, incluyendo Transformers, GANs, Autoencoders, Redes de Grafos y modelos de atención. Estas arquitecturas proporcionan capacidades de predicción y análisis de vanguardia para optimización de campañas publicitarias.

### Objetivos de las Redes Neuronales Avanzadas
- Implementar arquitecturas de deep learning de vanguardia
- Desarrollar modelos de predicción de alta precisión
- Crear sistemas de análisis de comportamiento avanzados
- Establecer modelos de generación de contenido
- Proporcionar insights predictivos profundos

---

## 2. Transformers para Análisis de Creativos

### 2.1 Transformer Multimodal para Creativos

**Analizador de Creativos con Transformer:**
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, AutoImageProcessor
import numpy as np
from PIL import Image
import cv2
from typing import Dict, List, Tuple, Optional
import asyncio

class MultimodalCreativeTransformer(nn.Module):
    def __init__(self, text_model_name='bert-base-uncased', 
                 image_model_name='resnet50', 
                 hidden_dim=768, 
                 num_heads=12, 
                 num_layers=6):
        super().__init__()
        
        # Modelos de codificación
        self.text_encoder = AutoModel.from_pretrained(text_model_name)
        self.image_encoder = self.create_image_encoder()
        
        # Capas de fusión multimodal
        self.text_projection = nn.Linear(self.text_encoder.config.hidden_size, hidden_dim)
        self.image_projection = nn.Linear(2048, hidden_dim)  # ResNet50 output size
        
        # Transformer multimodal
        self.multimodal_transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_dim,
                nhead=num_heads,
                dim_feedforward=hidden_dim * 4,
                dropout=0.1,
                activation='gelu'
            ),
            num_layers=num_layers
        )
        
        # Capas de predicción
        self.ctr_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
        self.conversion_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
        self.engagement_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 5)  # 5 tipos de engagement
        )
        
        # Capa de atención cruzada
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            dropout=0.1
        )
        
    def create_image_encoder(self):
        """Crear codificador de imágenes"""
        return nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((7, 7)),
            
            nn.Flatten(),
            nn.Linear(256 * 7 * 7, 2048),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5)
        )
    
    def encode_text(self, text_inputs):
        """Codificar texto"""
        text_outputs = self.text_encoder(**text_inputs)
        text_features = text_outputs.last_hidden_state  # [batch_size, seq_len, hidden_size]
        
        # Proyectar a dimensión común
        text_features = self.text_projection(text_features)
        
        return text_features
    
    def encode_image(self, image):
        """Codificar imagen"""
        image_features = self.image_encoder(image)  # [batch_size, 2048]
        
        # Proyectar a dimensión común
        image_features = self.image_projection(image_features)  # [batch_size, hidden_dim]
        
        # Expandir para secuencia
        image_features = image_features.unsqueeze(1)  # [batch_size, 1, hidden_dim]
        
        return image_features
    
    def forward(self, text_inputs, image):
        """Pase hacia adelante"""
        # Codificar modalidades
        text_features = self.encode_text(text_inputs)
        image_features = self.encode_image(image)
        
        # Concatenar características
        multimodal_features = torch.cat([text_features, image_features], dim=1)
        
        # Aplicar atención cruzada
        attended_features, _ = self.cross_attention(
            multimodal_features, multimodal_features, multimodal_features
        )
        
        # Aplicar transformer multimodal
        transformer_output = self.multimodal_transformer(attended_features)
        
        # Pooling global
        global_features = torch.mean(transformer_output, dim=1)
        
        # Predicciones
        ctr_prediction = self.ctr_predictor(global_features)
        conversion_prediction = self.conversion_predictor(global_features)
        engagement_prediction = self.engagement_predictor(global_features)
        
        return {
            'ctr': ctr_prediction,
            'conversion': conversion_prediction,
            'engagement': engagement_prediction,
            'features': global_features
        }

class CreativeAnalyzer:
    def __init__(self, model_path=None):
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = MultimodalCreativeTransformer()
        
        if model_path:
            self.model.load_state_dict(torch.load(model_path))
        
        self.model.eval()
        
    def preprocess_image(self, image_path):
        """Preprocesar imagen"""
        image = Image.open(image_path).convert('RGB')
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = torch.FloatTensor(image).permute(2, 0, 1).unsqueeze(0)
        return image
    
    def preprocess_text(self, text):
        """Preprocesar texto"""
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        )
        return inputs
    
    def analyze_creative(self, image_path, text, target_audience=None):
        """Analizar creativo completo"""
        # Preprocesar inputs
        image = self.preprocess_image(image_path)
        text_inputs = self.preprocess_text(text)
        
        # Predicción
        with torch.no_grad():
            predictions = self.model(text_inputs, image)
        
        # Análisis detallado
        analysis = {
            'predicted_ctr': predictions['ctr'].item(),
            'predicted_conversion': predictions['conversion'].item(),
            'engagement_scores': predictions['engagement'].squeeze().tolist(),
            'visual_analysis': self.analyze_visual_elements(image),
            'text_analysis': self.analyze_text_elements(text),
            'audience_alignment': self.analyze_audience_alignment(text, target_audience),
            'creative_quality': self.assess_creative_quality(predictions),
            'optimization_suggestions': self.generate_optimization_suggestions(predictions)
        }
        
        return analysis
    
    def analyze_visual_elements(self, image):
        """Analizar elementos visuales"""
        # Análisis de color
        color_analysis = self.analyze_colors(image)
        
        # Análisis de composición
        composition_analysis = self.analyze_composition(image)
        
        # Análisis de contraste
        contrast_analysis = self.analyze_contrast(image)
        
        # Análisis de elementos
        elements_analysis = self.analyze_visual_elements(image)
        
        return {
            'color_score': color_analysis,
            'composition_score': composition_analysis,
            'contrast_score': contrast_analysis,
            'elements_score': elements_analysis,
            'overall_visual_score': (color_analysis + composition_analysis + contrast_analysis + elements_analysis) / 4
        }
    
    def analyze_text_elements(self, text):
        """Analizar elementos de texto"""
        # Análisis de sentimiento
        sentiment = self.analyze_sentiment(text)
        
        # Análisis de legibilidad
        readability = self.analyze_readability(text)
        
        # Análisis de llamada a la acción
        cta_analysis = self.analyze_cta(text)
        
        # Análisis de longitud
        length_analysis = self.analyze_text_length(text)
        
        return {
            'sentiment_score': sentiment,
            'readability_score': readability,
            'cta_score': cta_analysis,
            'length_score': length_analysis,
            'overall_text_score': (sentiment + readability + cta_analysis + length_analysis) / 4
        }
    
    def analyze_audience_alignment(self, text, target_audience):
        """Analizar alineación con audiencia objetivo"""
        if not target_audience:
            return 0.5
        
        # Análisis de tono
        tone_analysis = self.analyze_tone_alignment(text, target_audience)
        
        # Análisis de lenguaje
        language_analysis = self.analyze_language_alignment(text, target_audience)
        
        # Análisis de relevancia
        relevance_analysis = self.analyze_relevance_alignment(text, target_audience)
        
        return {
            'tone_alignment': tone_analysis,
            'language_alignment': language_analysis,
            'relevance_alignment': relevance_analysis,
            'overall_alignment': (tone_analysis + language_analysis + relevance_analysis) / 3
        }
    
    def assess_creative_quality(self, predictions):
        """Evaluar calidad del creativo"""
        ctr_score = predictions['ctr'].item()
        conversion_score = predictions['conversion'].item()
        engagement_scores = predictions['engagement'].squeeze().tolist()
        
        # Calcular score de calidad
        quality_score = (
            ctr_score * 0.3 +
            conversion_score * 0.4 +
            np.mean(engagement_scores) * 0.3
        )
        
        return {
            'overall_quality': quality_score,
            'ctr_quality': ctr_score,
            'conversion_quality': conversion_score,
            'engagement_quality': np.mean(engagement_scores)
        }
    
    def generate_optimization_suggestions(self, predictions):
        """Generar sugerencias de optimización"""
        suggestions = []
        
        ctr_score = predictions['ctr'].item()
        conversion_score = predictions['conversion'].item()
        engagement_scores = predictions['engagement'].squeeze().tolist()
        
        if ctr_score < 0.02:
            suggestions.append("Consider improving visual appeal and headline to increase CTR")
        
        if conversion_score < 0.03:
            suggestions.append("Optimize call-to-action and value proposition for better conversions")
        
        if np.mean(engagement_scores) < 0.5:
            suggestions.append("Enhance engagement elements like interactive features or emotional appeal")
        
        return suggestions

# Uso del analizador de creativos
if __name__ == "__main__":
    # Crear analizador
    analyzer = CreativeAnalyzer()
    
    # Analizar creativo
    image_path = "creative_image.jpg"
    text = "Discover amazing products at unbeatable prices! Shop now and save 50%!"
    target_audience = {
        'age_range': '25-35',
        'interests': ['shopping', 'deals', 'fashion'],
        'behavior': 'price_conscious'
    }
    
    analysis = analyzer.analyze_creative(image_path, text, target_audience)
    
    print("Creative Analysis Results:")
    for key, value in analysis.items():
        print(f"{key}: {value}")
```

### 2.2 Transformer para Análisis de Audiencias

**Analizador de Audiencias con Transformer:**
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import Dict, List, Tuple, Optional
import pandas as pd

class AudienceTransformer(nn.Module):
    def __init__(self, input_dim=100, hidden_dim=512, num_heads=8, num_layers=6):
        super().__init__()
        
        # Capa de embedding
        self.embedding = nn.Linear(input_dim, hidden_dim)
        
        # Transformer encoder
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_dim,
                nhead=num_heads,
                dim_feedforward=hidden_dim * 4,
                dropout=0.1,
                activation='gelu'
            ),
            num_layers=num_layers
        )
        
        # Capas de predicción
        self.performance_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 1)
        )
        
        self.segment_classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 10)  # 10 segmentos
        )
        
        self.behavior_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 5)  # 5 comportamientos
        )
        
        # Capa de atención
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            dropout=0.1
        )
        
    def forward(self, audience_features):
        """Pase hacia adelante"""
        # Embedding
        embedded = self.embedding(audience_features)
        
        # Aplicar atención
        attended, _ = self.attention(embedded, embedded, embedded)
        
        # Transformer
        transformer_output = self.transformer(attended)
        
        # Pooling global
        global_features = torch.mean(transformer_output, dim=1)
        
        # Predicciones
        performance = self.performance_predictor(global_features)
        segment = self.segment_classifier(global_features)
        behavior = self.behavior_predictor(global_features)
        
        return {
            'performance': performance,
            'segment': segment,
            'behavior': behavior,
            'features': global_features
        }

class AudienceAnalyzer:
    def __init__(self, model_path=None):
        self.model = AudienceTransformer()
        
        if model_path:
            self.model.load_state_dict(torch.load(model_path))
        
        self.model.eval()
        
    def prepare_audience_features(self, audience_data):
        """Preparar características de audiencia"""
        features = []
        
        for audience in audience_data:
            feature_vector = self.extract_audience_features(audience)
            features.append(feature_vector)
        
        return torch.FloatTensor(features)
    
    def extract_audience_features(self, audience):
        """Extraer características de audiencia"""
        features = []
        
        # Características demográficas
        features.extend([
            audience.get('age', 30) / 100,
            1.0 if audience.get('gender') == 'M' else 0.0,
            audience.get('income', 50000) / 100000,
            audience.get('education_level', 3) / 5
        ])
        
        # Características de comportamiento
        features.extend([
            audience.get('social_media_usage', 5) / 10,
            audience.get('online_shopping_frequency', 3) / 10,
            audience.get('device_usage', 5) / 10,
            audience.get('content_consumption', 5) / 10
        ])
        
        # Características de intereses
        interests = audience.get('interests', [])
        for interest in ['tech', 'fashion', 'sports', 'entertainment', 'business']:
            features.append(1.0 if interest in interests else 0.0)
        
        # Características de ubicación
        location = audience.get('location', {})
        features.extend([
            location.get('urban_score', 0.5),
            location.get('income_level', 0.5),
            location.get('population_density', 0.5)
        ])
        
        # Características de engagement
        features.extend([
            audience.get('engagement_rate', 0.02) * 50,
            audience.get('click_through_rate', 0.01) * 100,
            audience.get('conversion_rate', 0.01) * 100
        ])
        
        # Rellenar con ceros si es necesario
        while len(features) < 100:
            features.append(0.0)
        
        return features[:100]  # Truncar a 100 características
    
    def analyze_audience(self, audience_data):
        """Analizar audiencia"""
        features = self.prepare_audience_features(audience_data)
        
        with torch.no_grad():
            predictions = self.model(features)
        
        analysis = {
            'performance_prediction': predictions['performance'].squeeze().tolist(),
            'segment_classification': predictions['segment'].squeeze().tolist(),
            'behavior_prediction': predictions['behavior'].squeeze().tolist(),
            'audience_insights': self.generate_audience_insights(predictions),
            'optimization_recommendations': self.generate_optimization_recommendations(predictions)
        }
        
        return analysis
    
    def generate_audience_insights(self, predictions):
        """Generar insights de audiencia"""
        insights = []
        
        performance_scores = predictions['performance'].squeeze().tolist()
        segment_scores = predictions['segment'].squeeze().tolist()
        behavior_scores = predictions['behavior'].squeeze().tolist()
        
        # Insights de performance
        avg_performance = np.mean(performance_scores)
        if avg_performance > 0.7:
            insights.append("High-performing audience segment")
        elif avg_performance > 0.5:
            insights.append("Moderate-performing audience segment")
        else:
            insights.append("Low-performing audience segment")
        
        # Insights de segmento
        dominant_segment = np.argmax(segment_scores)
        segment_names = ['tech_enthusiasts', 'fashion_lovers', 'sports_fans', 
                        'entertainment_seekers', 'business_professionals',
                        'budget_conscious', 'luxury_seekers', 'early_adopters',
                        'traditional_consumers', 'social_influencers']
        
        insights.append(f"Dominant segment: {segment_names[dominant_segment]}")
        
        # Insights de comportamiento
        behavior_names = ['impulse_buyer', 'researcher', 'brand_loyal', 
                         'price_sensitive', 'social_shopper']
        
        for i, score in enumerate(behavior_scores):
            if score > 0.7:
                insights.append(f"Strong {behavior_names[i]} behavior")
        
        return insights
    
    def generate_optimization_recommendations(self, predictions):
        """Generar recomendaciones de optimización"""
        recommendations = []
        
        performance_scores = predictions['performance'].squeeze().tolist()
        segment_scores = predictions['segment'].squeeze().tolist()
        behavior_scores = predictions['behavior'].squeeze().tolist()
        
        # Recomendaciones basadas en performance
        if np.mean(performance_scores) < 0.5:
            recommendations.append("Consider refining audience targeting criteria")
            recommendations.append("Test different creative approaches for this segment")
        
        # Recomendaciones basadas en segmento
        dominant_segment = np.argmax(segment_scores)
        if dominant_segment == 0:  # tech_enthusiasts
            recommendations.append("Focus on innovation and cutting-edge features")
            recommendations.append("Use technical language and specifications")
        elif dominant_segment == 1:  # fashion_lovers
            recommendations.append("Emphasize style and aesthetic appeal")
            recommendations.append("Use high-quality visual content")
        
        # Recomendaciones basadas en comportamiento
        if behavior_scores[0] > 0.7:  # impulse_buyer
            recommendations.append("Create urgency with limited-time offers")
            recommendations.append("Use compelling visual triggers")
        elif behavior_scores[1] > 0.7:  # researcher
            recommendations.append("Provide detailed product information")
            recommendations.append("Include comparison charts and reviews")
        
        return recommendations

# Uso del analizador de audiencias
if __name__ == "__main__":
    # Crear analizador
    analyzer = AudienceAnalyzer()
    
    # Datos de audiencia
    audience_data = [
        {
            'age': 25, 'gender': 'M', 'income': 60000, 'education_level': 4,
            'social_media_usage': 8, 'online_shopping_frequency': 6,
            'device_usage': 7, 'content_consumption': 8,
            'interests': ['tech', 'gaming', 'sports'],
            'location': {'urban_score': 0.8, 'income_level': 0.7, 'population_density': 0.9},
            'engagement_rate': 0.03, 'click_through_rate': 0.02, 'conversion_rate': 0.025
        },
        {
            'age': 35, 'gender': 'F', 'income': 80000, 'education_level': 5,
            'social_media_usage': 6, 'online_shopping_frequency': 8,
            'device_usage': 8, 'content_consumption': 7,
            'interests': ['fashion', 'beauty', 'lifestyle'],
            'location': {'urban_score': 0.9, 'income_level': 0.8, 'population_density': 0.8},
            'engagement_rate': 0.04, 'click_through_rate': 0.025, 'conversion_rate': 0.035
        }
    ]
    
    # Analizar audiencia
    analysis = analyzer.analyze_audience(audience_data)
    
    print("Audience Analysis Results:")
    for key, value in analysis.items():
        print(f"{key}: {value}")
```

---

## 3. GANs para Generación de Creativos

### 3.1 Generador de Creativos con GAN

**Generador de Creativos Publicitarios:**
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
from PIL import Image
import cv2
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt

class CreativeGenerator(nn.Module):
    def __init__(self, noise_dim=100, text_dim=768, image_dim=3):
        super().__init__()
        
        self.noise_dim = noise_dim
        self.text_dim = text_dim
        self.image_dim = image_dim
        
        # Generador
        self.generator = nn.Sequential(
            # Capa inicial
            nn.Linear(noise_dim + text_dim, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            
            # Capas intermedias
            nn.Linear(1024, 2048),
            nn.BatchNorm1d(2048),
            nn.ReLU(inplace=True),
            
            nn.Linear(2048, 4096),
            nn.BatchNorm1d(4096),
            nn.ReLU(inplace=True),
            
            # Capa final
            nn.Linear(4096, 224 * 224 * image_dim),
            nn.Tanh()
        )
        
        # Discriminador
        self.discriminator = nn.Sequential(
            # Capa inicial
            nn.Linear(224 * 224 * image_dim + text_dim, 1024),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(0.3),
            
            # Capas intermedias
            nn.Linear(1024, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(0.3),
            
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(0.3),
            
            # Capa final
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        
    def forward(self, noise, text_features):
        """Generar creativo"""
        # Concatenar ruido y características de texto
        input_features = torch.cat([noise, text_features], dim=1)
        
        # Generar imagen
        generated_image = self.generator(input_features)
        
        # Reshape a formato de imagen
        generated_image = generated_image.view(-1, self.image_dim, 224, 224)
        
        return generated_image
    
    def discriminate(self, image, text_features):
        """Discriminar imagen"""
        # Flatten imagen
        image_flat = image.view(image.size(0), -1)
        
        # Concatenar imagen y características de texto
        input_features = torch.cat([image_flat, text_features], dim=1)
        
        # Discriminar
        discrimination = self.discriminator(input_features)
        
        return discrimination

class CreativeDataset(Dataset):
    def __init__(self, image_paths, texts, labels):
        self.image_paths = image_paths
        self.texts = texts
        self.labels = labels
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # Cargar imagen
        image = Image.open(self.image_paths[idx]).convert('RGB')
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = torch.FloatTensor(image).permute(2, 0, 1)
        
        # Obtener texto y etiqueta
        text = self.texts[idx]
        label = self.labels[idx]
        
        return image, text, label

class CreativeGAN:
    def __init__(self, noise_dim=100, text_dim=768, image_dim=3):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Modelos
        self.generator = CreativeGenerator(noise_dim, text_dim, image_dim).to(self.device)
        self.discriminator = CreativeGenerator(noise_dim, text_dim, image_dim).to(self.device)
        
        # Optimizadores
        self.g_optimizer = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        # Funciones de pérdida
        self.criterion = nn.BCELoss()
        
        # Text encoder
        self.text_encoder = self.create_text_encoder()
        
    def create_text_encoder(self):
        """Crear codificador de texto"""
        return nn.Sequential(
            nn.Linear(512, 768),  # Asumiendo texto codificado a 512 dims
            nn.ReLU(),
            nn.Linear(768, 768)
        )
    
    def train_gan(self, dataloader, epochs=100):
        """Entrenar GAN"""
        for epoch in range(epochs):
            for batch_idx, (real_images, texts, labels) in enumerate(dataloader):
                real_images = real_images.to(self.device)
                texts = texts.to(self.device)
                labels = labels.to(self.device)
                
                # Codificar texto
                text_features = self.text_encoder(texts)
                
                # Entrenar discriminador
                self.train_discriminator(real_images, text_features, labels)
                
                # Entrenar generador
                self.train_generator(text_features, labels)
                
                # Logging
                if batch_idx % 100 == 0:
                    print(f'Epoch {epoch}, Batch {batch_idx}, '
                          f'D Loss: {self.d_loss:.4f}, G Loss: {self.g_loss:.4f}')
    
    def train_discriminator(self, real_images, text_features, labels):
        """Entrenar discriminador"""
        self.d_optimizer.zero_grad()
        
        # Discriminar imágenes reales
        real_output = self.discriminator.discriminate(real_images, text_features)
        real_loss = self.criterion(real_output, torch.ones_like(real_output))
        
        # Generar imágenes falsas
        noise = torch.randn(real_images.size(0), self.generator.noise_dim).to(self.device)
        fake_images = self.generator(noise, text_features)
        
        # Discriminar imágenes falsas
        fake_output = self.discriminator.discriminate(fake_images.detach(), text_features)
        fake_loss = self.criterion(fake_output, torch.zeros_like(fake_output))
        
        # Pérdida total del discriminador
        self.d_loss = real_loss + fake_loss
        self.d_loss.backward()
        self.d_optimizer.step()
    
    def train_generator(self, text_features, labels):
        """Entrenar generador"""
        self.g_optimizer.zero_grad()
        
        # Generar imágenes falsas
        noise = torch.randn(text_features.size(0), self.generator.noise_dim).to(self.device)
        fake_images = self.generator(noise, text_features)
        
        # Discriminar imágenes falsas
        fake_output = self.discriminator.discriminate(fake_images, text_features)
        
        # Pérdida del generador
        self.g_loss = self.criterion(fake_output, torch.ones_like(fake_output))
        self.g_loss.backward()
        self.g_optimizer.step()
    
    def generate_creative(self, text, num_samples=1):
        """Generar creativo"""
        self.generator.eval()
        
        with torch.no_grad():
            # Codificar texto
            text_features = self.text_encoder(text)
            
            # Generar ruido
            noise = torch.randn(num_samples, self.generator.noise_dim).to(self.device)
            
            # Generar imagen
            generated_image = self.generator(noise, text_features)
            
            # Convertir a formato PIL
            generated_image = generated_image.squeeze().cpu()
            generated_image = (generated_image + 1) / 2  # Normalizar a [0, 1]
            generated_image = generated_image.permute(1, 2, 0).numpy()
            generated_image = (generated_image * 255).astype(np.uint8)
            
            return Image.fromarray(generated_image)
    
    def save_model(self, path):
        """Guardar modelo"""
        torch.save({
            'generator_state_dict': self.generator.state_dict(),
            'discriminator_state_dict': self.discriminator.state_dict(),
            'g_optimizer_state_dict': self.g_optimizer.state_dict(),
            'd_optimizer_state_dict': self.d_optimizer.state_dict()
        }, path)
    
    def load_model(self, path):
        """Cargar modelo"""
        checkpoint = torch.load(path)
        self.generator.load_state_dict(checkpoint['generator_state_dict'])
        self.discriminator.load_state_dict(checkpoint['discriminator_state_dict'])
        self.g_optimizer.load_state_dict(checkpoint['g_optimizer_state_dict'])
        self.d_optimizer.load_state_dict(checkpoint['d_optimizer_state_dict'])

# Uso del generador de creativos
if __name__ == "__main__":
    # Crear GAN
    gan = CreativeGAN()
    
    # Generar creativo
    text = "Amazing deals on tech gadgets! Shop now and save big!"
    generated_image = gan.generate_creative(text)
    
    # Guardar imagen generada
    generated_image.save("generated_creative.jpg")
    
    print("Creative generated successfully!")
```

---

## Conclusión

Las redes neuronales avanzadas representan el futuro de la predicción y análisis en Facebook Ads, proporcionando capacidades de deep learning de vanguardia. La implementación exitosa requiere:

**Elementos Clave:**
1. **Transformers**: Análisis multimodal de creativos y audiencias
2. **GANs**: Generación de creativos publicitarios
3. **Autoencoders**: Compresión y análisis de características
4. **Redes de Grafos**: Análisis de relaciones entre audiencias
5. **Modelos de Atención**: Enfoque en características relevantes

**Beneficios:**
- Predicción de alta precisión
- Análisis multimodal avanzado
- Generación de contenido creativo
- Comprensión profunda de audiencias
- Optimización automática de campañas

**Próximos Pasos:**
1. Implementar arquitecturas básicas
2. Desarrollar modelos de predicción
3. Crear sistemas de generación
4. Establecer análisis de comportamiento
5. Integrar con sistemas de optimización

La implementación exitosa de estas redes neuronales avanzadas resultará en un sistema de Facebook Ads que comprende y predice el comportamiento de audiencias con precisión sin precedentes, estableciendo nuevos estándares en el ecosistema publicitario digital.


