"""
Validadores y funciones de validación para el sistema
"""
from datetime import datetime
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Valida formato de teléfono"""
    # Permite varios formatos: +52 55 1234 5678, (555) 123-4567, etc.
    pattern = r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$'
    return bool(re.match(pattern, phone.replace(' ', '')))

def validate_sku(sku: str) -> bool:
    """Valida formato de SKU"""
    # SKU debe tener al menos 3 caracteres, solo letras, números y guiones
    pattern = r'^[A-Z0-9][A-Z0-9\-]{2,49}$'
    return bool(re.match(pattern, sku.upper()))

def validate_price(price: float, min_price: float = 0.0) -> bool:
    """Valida que el precio sea válido"""
    try:
        price_float = float(price)
        return price_float >= min_price
    except (ValueError, TypeError):
        return False

def validate_stock_quantity(quantity: int, allow_negative: bool = False) -> bool:
    """Valida cantidad de stock"""
    try:
        qty = int(quantity)
        return qty >= 0 if not allow_negative else True
    except (ValueError, TypeError):
        return False

def validate_date(date_string: str, date_format: str = '%Y-%m-%d') -> Optional[datetime]:
    """Valida y parsea una fecha"""
    try:
        return datetime.strptime(date_string, date_format)
    except (ValueError, TypeError):
        return None

def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitiza strings eliminando caracteres peligrosos"""
    if not text:
        return ''
    
    # Remover caracteres de control excepto espacios y saltos de línea
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Limitar longitud si se especifica
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_product_data(data: dict) -> tuple[bool, list[str]]:
    """Valida datos de producto y retorna (es_válido, lista_de_errores)"""
    errors = []
    
    if 'name' not in data or not data['name'] or len(data['name']) < 3:
        errors.append("El nombre del producto debe tener al menos 3 caracteres")
    
    if 'sku' not in data or not validate_sku(data['sku']):
        errors.append("SKU inválido. Debe tener al menos 3 caracteres, solo letras, números y guiones")
    
    if 'unit_price' not in data or not validate_price(data['unit_price'], min_price=0.0):
        errors.append("El precio unitario debe ser un número mayor o igual a 0")
    
    if 'cost_price' not in data or not validate_price(data['cost_price'], min_price=0.0):
        errors.append("El precio de costo debe ser un número mayor o igual a 0")
    
    if 'min_stock_level' in data and not validate_stock_quantity(data['min_stock_level']):
        errors.append("El nivel mínimo de stock debe ser un número entero no negativo")
    
    if 'max_stock_level' in data:
        min_stock = data.get('min_stock_level', 0)
        max_stock = data.get('max_stock_level', 0)
        if max_stock < min_stock:
            errors.append("El nivel máximo de stock debe ser mayor o igual al mínimo")
    
    return len(errors) == 0, errors

