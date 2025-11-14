"""
Módulo models - Re-exporta modelos desde 05_Technology/models.py
Nota: db debe ser importado desde app antes de usar este módulo
"""
import sys
import os

# Este módulo será importado después de que app.py defina db
# Por lo tanto, podemos importar db de forma segura
try:
    from app import db
except ImportError:
    # Si db no está disponible aún, crear un placeholder
    db = None

# Agregar 05_Technology al path
tech_dir = os.path.join(os.path.dirname(__file__), '05_Technology')
if tech_dir not in sys.path:
    sys.path.insert(0, tech_dir)

# Importar modelos dinámicamente cuando se necesiten
_models_loaded = False
_model_classes = {}

def _load_models():
    """Carga los modelos desde 05_Technology/models.py"""
    global _models_loaded, _model_classes
    
    if _models_loaded:
        return _model_classes
    
    if db is None:
        raise ImportError("db no está inicializado. Importa desde app.py primero.")
    
    try:
        import importlib.util
        models_path = os.path.join(tech_dir, 'models.py')
        
        if not os.path.exists(models_path):
            raise FileNotFoundError(f"Archivo models.py no encontrado en {models_path}")
        
        # Cargar el módulo de modelos
        spec = importlib.util.spec_from_file_location("inventory_models", models_path)
        models_module = importlib.util.module_from_spec(spec)
        
        # Inyectar db en el namespace del módulo antes de ejecutarlo
        models_module.db = db
        
        # Ejecutar el módulo
        spec.loader.exec_module(models_module)
        
        # Extraer las clases de modelo
        _model_classes = {
            'Product': models_module.Product,
            'InventoryRecord': models_module.InventoryRecord,
            'Alert': models_module.Alert,
            'SalesRecord': models_module.SalesRecord,
            'ReorderRecommendation': models_module.ReorderRecommendation,
            'Supplier': models_module.Supplier,
            'Customer': models_module.Customer,
            'KPIMetric': models_module.KPIMetric,
        }
        
        _models_loaded = True
        
        # Re-exportar al namespace actual
        globals().update(_model_classes)
        
        return _model_classes
        
    except Exception as e:
        raise ImportError(f"Error cargando modelos desde 05_Technology/models.py: {e}")

# Las clases se asignarán dinámicamente por app.py antes de que se importen los blueprints
# Estas son referencias que se poblarán después
Product = None
InventoryRecord = None
Alert = None
SalesRecord = None
ReorderRecommendation = None
Supplier = None
Customer = None
KPIMetric = None

# Cargar modelos automáticamente cuando se importa el módulo (si db está disponible)
if db is not None:
    try:
        _load_models()
    except:
        pass  # Se cargarán cuando db esté completamente inicializado

# Permite importar modelos como: from models import Product
# Las clases se cargarán automáticamente cuando se soliciten
__all__ = [
    'Product', 'InventoryRecord', 'Alert', 'SalesRecord',
    'ReorderRecommendation', 'Supplier', 'Customer', 'KPIMetric'
]

