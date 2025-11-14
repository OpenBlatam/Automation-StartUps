"""
Módulo models de compatibilidad.
Este módulo permite que los imports 'from models import ...' funcionen correctamente
re-exportando desde el módulo real en 05_Technology/models.py
"""
import sys
import os

# Agregar 05_Technology al path si no está
tech_dir = os.path.join(os.path.dirname(__file__), '05_Technology')
if tech_dir not in sys.path:
    sys.path.insert(0, tech_dir)

# Importar y re-exportar todos los modelos
try:
    from models import (
        Product, InventoryRecord, Alert, SalesRecord, 
        ReorderRecommendation, Supplier, Customer
    )
    __all__ = [
        'Product', 'InventoryRecord', 'Alert', 'SalesRecord',
        'ReorderRecommendation', 'Supplier', 'Customer'
    ]
except ImportError:
    # Si falla, intentar con path alternativo
    import importlib.util
    models_path = os.path.join(tech_dir, 'models.py')
    if os.path.exists(models_path):
        spec = importlib.util.spec_from_file_location("models", models_path)
        models_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_module)
        # Re-exportar las clases principales
        Product = models_module.Product
        InventoryRecord = models_module.InventoryRecord
        Alert = models_module.Alert
        SalesRecord = models_module.SalesRecord
        ReorderRecommendation = models_module.ReorderRecommendation
        Supplier = getattr(models_module, 'Supplier', None)
        Customer = getattr(models_module, 'Customer', None)
        __all__ = [
            'Product', 'InventoryRecord', 'Alert', 'SalesRecord',
            'ReorderRecommendation', 'Supplier', 'Customer'
        ]

