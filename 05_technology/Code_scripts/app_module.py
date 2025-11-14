"""
Módulo app de compatibilidad.
Este módulo permite que los imports 'from app import db' funcionen correctamente
re-exportando desde el módulo real en 05_Technology/app.py
"""
import sys
import os

# Agregar 05_Technology al path si no está
tech_dir = os.path.join(os.path.dirname(__file__), '05_Technology')
if tech_dir not in sys.path:
    sys.path.insert(0, tech_dir)

# Importar y re-exportar desde el módulo real
try:
    from app import db, migrate, mail, create_app
    __all__ = ['db', 'migrate', 'mail', 'create_app']
except ImportError as e:
    # Si falla, intentar con path alternativo
    import importlib.util
    app_path = os.path.join(tech_dir, 'app.py')
    if os.path.exists(app_path):
        spec = importlib.util.spec_from_file_location("app", app_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        db = app_module.db
        migrate = app_module.migrate
        mail = app_module.mail
        create_app = app_module.create_app
        __all__ = ['db', 'migrate', 'mail', 'create_app']
    else:
        raise ImportError(f"No se pudo importar el módulo app: {e}")

