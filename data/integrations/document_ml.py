"""
Machine Learning para Clasificación Avanzada
============================================

Usa modelos de ML para mejorar la clasificación de documentos.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)


class MLDocumentClassifier:
    """Clasificador usando Machine Learning"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.vectorizer = None
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        """Carga modelo ML (simplificado - en producción usaría un modelo real)"""
        try:
            # Intentar cargar modelo pre-entrenado
            if self.model_path:
                import pickle
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get('model')
                    self.vectorizer = model_data.get('vectorizer')
        except Exception as e:
            self.logger.warning(f"No se pudo cargar modelo ML: {e}")
            self.logger.info("Usando clasificador basado en reglas como fallback")
    
    def classify_with_ml(
        self,
        text: str,
        features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Clasifica usando ML"""
        if self.model and self.vectorizer:
            # Usar modelo ML
            try:
                # Vectorizar texto
                text_vector = self.vectorizer.transform([text])
                
                # Predecir
                prediction = self.model.predict(text_vector)[0]
                probabilities = self.model.predict_proba(text_vector)[0]
                
                # Mapear a tipos de documentos
                classes = self.model.classes_
                class_probs = dict(zip(classes, probabilities))
                
                return {
                    "predicted_type": prediction,
                    "confidence": float(max(probabilities)),
                    "all_probabilities": class_probs,
                    "method": "ml"
                }
            except Exception as e:
                self.logger.error(f"Error en predicción ML: {e}")
        
        # Fallback a clasificación basada en features
        return self._classify_with_features(text, features or {})
    
    def _classify_with_features(
        self,
        text: str,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Clasificación basada en features extraídas"""
        scores = {
            "invoice": 0.0,
            "contract": 0.0,
            "form": 0.0,
            "receipt": 0.0,
            "quote": 0.0,
            "statement": 0.0
        }
        
        text_lower = text.lower()
        
        # Features para factura
        invoice_keywords = ["factura", "invoice", "total", "subtotal", "impuestos"]
        invoice_score = sum(1 for kw in invoice_keywords if kw in text_lower)
        scores["invoice"] = invoice_score / len(invoice_keywords)
        
        # Features para contrato
        contract_keywords = ["contrato", "contract", "partes", "cláusula"]
        contract_score = sum(1 for kw in contract_keywords if kw in text_lower)
        scores["contract"] = contract_score / len(contract_keywords)
        
        # Features para formulario
        form_keywords = ["formulario", "form", "nombre", "email", "firma"]
        form_score = sum(1 for kw in form_keywords if kw in text_lower)
        scores["form"] = form_score / len(form_keywords)
        
        # Determinar mejor clase
        best_class = max(scores.items(), key=lambda x: x[1])
        
        return {
            "predicted_type": best_class[0],
            "confidence": best_class[1],
            "all_probabilities": scores,
            "method": "features"
        }
    
    def train_model(
        self,
        training_data: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ):
        """Entrena modelo con datos de entrenamiento"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
        except ImportError:
            raise ImportError(
                "scikit-learn es requerido. Instala con: pip install scikit-learn"
            )
        
        # Preparar datos
        texts = [item["text"] for item in training_data]
        labels = [item["label"] for item in training_data]
        
        # Vectorizar
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = self.vectorizer.fit_transform(texts)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42
        )
        
        # Entrenar modelo
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluar
        accuracy = self.model.score(X_test, y_test)
        self.logger.info(f"Modelo entrenado con accuracy: {accuracy:.2%}")
        
        # Guardar si se especifica
        if save_path:
            import pickle
            with open(save_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'vectorizer': self.vectorizer,
                    'accuracy': accuracy
                }, f)
            self.logger.info(f"Modelo guardado en: {save_path}")


class DocumentEmbedder:
    """Genera embeddings para búsqueda semántica"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Carga modelo de embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f"Modelo de embeddings cargado: {self.model_name}")
        except ImportError:
            self.logger.warning(
                "sentence-transformers no disponible. "
                "Instala con: pip install sentence-transformers"
            )
        except Exception as e:
            self.logger.error(f"Error cargando modelo: {e}")
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Genera embedding para un texto"""
        if not self.model:
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            self.logger.error(f"Error generando embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Genera embeddings para múltiples textos"""
        if not self.model:
            return []
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
        except Exception as e:
            self.logger.error(f"Error generando embeddings: {e}")
            return []
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        document_embeddings: List[np.ndarray],
        top_k: int = 10
    ) -> List[tuple]:
        """Búsqueda por similitud usando embeddings"""
        if not document_embeddings:
            return []
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            similarities = cosine_similarity(
                [query_embedding],
                document_embeddings
            )[0]
            
            # Obtener top k
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            return [
                (idx, float(similarities[idx]))
                for idx in top_indices
            ]
        except Exception as e:
            self.logger.error(f"Error en búsqueda semántica: {e}")
            return []

