#!/usr/bin/env python3
"""
Data Validation and Cleaning System for Competitive Pricing Analysis
==================================================================

Sistema de validación y limpieza de datos que proporciona:
- Validación de esquemas de datos
- Limpieza automática de datos
- Detección de anomalías
- Normalización de datos
- Validación de integridad
- Transformación de datos
- Reportes de calidad
- Corrección automática
"""

import pandas as pd
import numpy as np
import sqlite3
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationRule:
    """Regla de validación"""
    name: str
    field: str
    rule_type: str  # required, type, range, pattern, custom
    parameters: Dict[str, Any]
    error_message: str
    severity: str = "error"  # error, warning, info

@dataclass
class ValidationResult:
    """Resultado de validación"""
    field: str
    value: Any
    is_valid: bool
    error_message: str
    rule_name: str
    severity: str
    suggested_value: Optional[Any] = None

@dataclass
class DataQualityReport:
    """Reporte de calidad de datos"""
    total_records: int
    valid_records: int
    invalid_records: int
    quality_score: float
    validation_results: List[ValidationResult]
    field_statistics: Dict[str, Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    recommendations: List[str]

@dataclass
class CleaningRule:
    """Regla de limpieza"""
    name: str
    field: str
    cleaning_type: str  # remove, replace, transform, normalize
    parameters: Dict[str, Any]
    description: str

class DataValidationSystem:
    """Sistema de validación y limpieza de datos"""
    
    def __init__(self, db_path: str = "data_validation.db"):
        """Inicializar sistema de validación"""
        self.db_path = db_path
        self.validation_rules = []
        self.cleaning_rules = []
        self.custom_validators = {}
        self.custom_cleaners = {}
        
        # Inicializar base de datos
        self._init_database()
        
        # Cargar reglas por defecto
        self._load_default_rules()
        
        logger.info("Data Validation System initialized")
    
    def _init_database(self):
        """Inicializar base de datos de validación"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de reglas de validación
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    field TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    severity TEXT DEFAULT 'error',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de reglas de limpieza
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cleaning_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    field TEXT NOT NULL,
                    cleaning_type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de reportes de calidad
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_name TEXT NOT NULL,
                    total_records INTEGER NOT NULL,
                    valid_records INTEGER NOT NULL,
                    quality_score REAL NOT NULL,
                    report_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Data validation database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing validation database: {e}")
            raise
    
    def _load_default_rules(self):
        """Cargar reglas de validación por defecto"""
        try:
            # Reglas para datos de precios
            default_rules = [
                ValidationRule(
                    name="price_required",
                    field="price",
                    rule_type="required",
                    parameters={},
                    error_message="Price is required",
                    severity="error"
                ),
                ValidationRule(
                    name="price_positive",
                    field="price",
                    rule_type="range",
                    parameters={"min": 0, "max": 1000000},
                    error_message="Price must be positive and reasonable",
                    severity="error"
                ),
                ValidationRule(
                    name="price_numeric",
                    field="price",
                    rule_type="type",
                    parameters={"type": "numeric"},
                    error_message="Price must be numeric",
                    severity="error"
                ),
                ValidationRule(
                    name="product_name_required",
                    field="product_name",
                    rule_type="required",
                    parameters={},
                    error_message="Product name is required",
                    severity="error"
                ),
                ValidationRule(
                    name="product_name_length",
                    field="product_name",
                    rule_type="range",
                    parameters={"min_length": 1, "max_length": 500},
                    error_message="Product name must be between 1 and 500 characters",
                    severity="warning"
                ),
                ValidationRule(
                    name="competitor_required",
                    field="competitor",
                    rule_type="required",
                    parameters={},
                    error_message="Competitor is required",
                    severity="error"
                ),
                ValidationRule(
                    name="date_valid",
                    field="date_collected",
                    rule_type="type",
                    parameters={"type": "datetime"},
                    error_message="Date must be valid datetime",
                    severity="error"
                ),
                ValidationRule(
                    name="currency_valid",
                    field="currency",
                    rule_type="pattern",
                    parameters={"pattern": r"^[A-Z]{3}$"},
                    error_message="Currency must be 3-letter code (e.g., USD, EUR)",
                    severity="error"
                ),
                ValidationRule(
                    name="url_valid",
                    field="source",
                    rule_type="pattern",
                    parameters={"pattern": r"^https?://"},
                    error_message="Source must be valid URL",
                    severity="warning"
                )
            ]
            
            for rule in default_rules:
                self.add_validation_rule(rule)
            
            # Reglas de limpieza por defecto
            default_cleaning_rules = [
                CleaningRule(
                    name="trim_whitespace",
                    field="product_name",
                    cleaning_type="transform",
                    parameters={"function": "strip"},
                    description="Remove leading and trailing whitespace"
                ),
                CleaningRule(
                    name="normalize_currency",
                    field="currency",
                    cleaning_type="transform",
                    parameters={"function": "upper"},
                    description="Convert currency to uppercase"
                ),
                CleaningRule(
                    name="remove_price_symbols",
                    field="price",
                    cleaning_type="transform",
                    parameters={"function": "remove_symbols"},
                    description="Remove currency symbols from price"
                ),
                CleaningRule(
                    name="normalize_competitor_name",
                    field="competitor",
                    cleaning_type="transform",
                    parameters={"function": "title_case"},
                    description="Normalize competitor name to title case"
                )
            ]
            
            for rule in default_cleaning_rules:
                self.add_cleaning_rule(rule)
            
            logger.info("Default validation and cleaning rules loaded")
            
        except Exception as e:
            logger.error(f"Error loading default rules: {e}")
    
    def add_validation_rule(self, rule: ValidationRule):
        """Agregar regla de validación"""
        try:
            # Verificar si ya existe
            existing_rule = next((r for r in self.validation_rules if r.name == rule.name), None)
            if existing_rule:
                logger.warning(f"Validation rule {rule.name} already exists, updating...")
                self.validation_rules.remove(existing_rule)
            
            self.validation_rules.append(rule)
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO validation_rules 
                (name, field, rule_type, parameters, error_message, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                rule.name,
                rule.field,
                rule.rule_type,
                json.dumps(rule.parameters),
                rule.error_message,
                rule.severity
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Validation rule added: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error adding validation rule: {e}")
            raise
    
    def add_cleaning_rule(self, rule: CleaningRule):
        """Agregar regla de limpieza"""
        try:
            # Verificar si ya existe
            existing_rule = next((r for r in self.cleaning_rules if r.name == rule.name), None)
            if existing_rule:
                logger.warning(f"Cleaning rule {rule.name} already exists, updating...")
                self.cleaning_rules.remove(existing_rule)
            
            self.cleaning_rules.append(rule)
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO cleaning_rules 
                (name, field, cleaning_type, parameters, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                rule.name,
                rule.field,
                rule.cleaning_type,
                json.dumps(rule.parameters),
                rule.description
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaning rule added: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error adding cleaning rule: {e}")
            raise
    
    def add_custom_validator(self, name: str, validator_func: Callable[[Any], Tuple[bool, str]]):
        """Agregar validador personalizado"""
        try:
            self.custom_validators[name] = validator_func
            logger.info(f"Custom validator added: {name}")
            
        except Exception as e:
            logger.error(f"Error adding custom validator: {e}")
            raise
    
    def add_custom_cleaner(self, name: str, cleaner_func: Callable[[Any], Any]):
        """Agregar limpiador personalizado"""
        try:
            self.custom_cleaners[name] = cleaner_func
            logger.info(f"Custom cleaner added: {name}")
            
        except Exception as e:
            logger.error(f"Error adding custom cleaner: {e}")
            raise
    
    def validate_data(self, data: pd.DataFrame) -> DataQualityReport:
        """Validar datos"""
        try:
            logger.info(f"Validating {len(data)} records...")
            
            validation_results = []
            field_statistics = {}
            anomalies = []
            
            # Validar cada campo según las reglas
            for rule in self.validation_rules:
                if rule.field in data.columns:
                    field_results = self._validate_field(data, rule)
                    validation_results.extend(field_results)
            
            # Calcular estadísticas por campo
            for column in data.columns:
                field_statistics[column] = self._calculate_field_statistics(data[column])
            
            # Detectar anomalías
            anomalies = self._detect_anomalies(data)
            
            # Calcular puntuación de calidad
            total_validations = len(validation_results)
            valid_validations = len([r for r in validation_results if r.is_valid])
            quality_score = (valid_validations / total_validations * 100) if total_validations > 0 else 100
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(validation_results, field_statistics, anomalies)
            
            report = DataQualityReport(
                total_records=len(data),
                valid_records=len(data) - len([r for r in validation_results if not r.is_valid and r.severity == "error"]),
                invalid_records=len([r for r in validation_results if not r.is_valid and r.severity == "error"]),
                quality_score=quality_score,
                validation_results=validation_results,
                field_statistics=field_statistics,
                anomalies=anomalies,
                recommendations=recommendations
            )
            
            # Guardar reporte
            self._save_quality_report("validation", report)
            
            logger.info(f"Data validation completed. Quality score: {quality_score:.2f}%")
            return report
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            raise
    
    def _validate_field(self, data: pd.DataFrame, rule: ValidationRule) -> List[ValidationResult]:
        """Validar campo específico"""
        results = []
        
        try:
            field_data = data[rule.field]
            
            for idx, value in field_data.items():
                is_valid, error_message, suggested_value = self._apply_validation_rule(value, rule)
                
                result = ValidationResult(
                    field=rule.field,
                    value=value,
                    is_valid=is_valid,
                    error_message=error_message if not is_valid else "",
                    rule_name=rule.name,
                    severity=rule.severity,
                    suggested_value=suggested_value
                )
                
                results.append(result)
                
        except Exception as e:
            logger.error(f"Error validating field {rule.field}: {e}")
        
        return results
    
    def _apply_validation_rule(self, value: Any, rule: ValidationRule) -> Tuple[bool, str, Optional[Any]]:
        """Aplicar regla de validación"""
        try:
            if rule.rule_type == "required":
                return self._validate_required(value, rule)
            elif rule.rule_type == "type":
                return self._validate_type(value, rule)
            elif rule.rule_type == "range":
                return self._validate_range(value, rule)
            elif rule.rule_type == "pattern":
                return self._validate_pattern(value, rule)
            elif rule.rule_type == "custom":
                return self._validate_custom(value, rule)
            else:
                return True, "", None
                
        except Exception as e:
            logger.error(f"Error applying validation rule {rule.name}: {e}")
            return False, f"Validation error: {str(e)}", None
    
    def _validate_required(self, value: Any, rule: ValidationRule) -> Tuple[bool, str, Optional[Any]]:
        """Validar campo requerido"""
        if pd.isna(value) or value is None or value == "":
            return False, rule.error_message, None
        return True, "", None
    
    def _validate_type(self, value: Any, rule: ValidationRule) -> Tuple[bool, str, Optional[Any]]:
        """Validar tipo de dato"""
        expected_type = rule.parameters.get("type")
        
        if pd.isna(value):
            return True, "", None  # Los valores nulos se manejan con regla required
        
        if expected_type == "numeric":
            try:
                float(value)
                return True, "", None
            except (ValueError, TypeError):
                # Intentar sugerir valor numérico
                suggested = self._suggest_numeric_value(str(value))
                return False, rule.error_message, suggested
        
        elif expected_type == "integer":
            try:
                int(value)
                return True, "", None
            except (ValueError, TypeError):
                suggested = self._suggest_integer_value(str(value))
                return False, rule.error_message, suggested
        
        elif expected_type == "datetime":
            try:
                pd.to_datetime(value)
                return True, "", None
            except (ValueError, TypeError):
                suggested = self._suggest_datetime_value(str(value))
                return False, rule.error_message, suggested
        
        elif expected_type == "string":
            if isinstance(value, str):
                return True, "", None
            else:
                return False, rule.error_message, str(value)
        
        return True, "", None
    
    def _validate_range(self, value: Any, rule: ValidationRule) -> Tuple[bool, str, Optional[Any]]:
        """Validar rango de valores"""
        if pd.isna(value):
            return True, "", None
        
        try:
            numeric_value = float(value)
            
            # Validar rango numérico
            if "min" in rule.parameters and numeric_value < rule.parameters["min"]:
                return False, rule.error_message, rule.parameters["min"]
            
            if "max" in rule.parameters and numeric_value > rule.parameters["max"]:
                return False, rule.error_message, rule.parameters["max"]
            
            # Validar longitud de string
            if "min_length" in rule.parameters and len(str(value)) < rule.parameters["min_length"]:
                return False, rule.error_message, None
            
            if "max_length" in rule.parameters and len(str(value)) > rule.parameters["max_length"]:
                return False, rule.error_message, None
            
            return True, "", None
            
        except (ValueError, TypeError):
            return False, rule.error_message, None
    
    def _validate_pattern(self, value: Any, rule: ValidationRule) -> Tuple[bool, str, Optional[Any]]:
        """Validar patrón regex"""
        if pd.isna(value):
            return True, "", None
        
        pattern = rule.parameters.get("pattern")
        if not pattern:
            return True, "", None
        
        try:
            if re.match(pattern, str(value)):
                return True, "", None
            else:
                return False, rule.error_message, None
                
        except re.error:
            return False, f"Invalid regex pattern: {pattern}", None
    
    def _validate_custom(self, value: Any, rule: ValidationRule) -> Tuple[bool, str, Optional[Any]]:
        """Validar con función personalizada"""
        validator_name = rule.parameters.get("validator")
        if validator_name in self.custom_validators:
            try:
                is_valid, error_message = self.custom_validators[validator_name](value)
                return is_valid, error_message, None
            except Exception as e:
                return False, f"Custom validation error: {str(e)}", None
        
        return True, "", None
    
    def _suggest_numeric_value(self, value: str) -> Optional[float]:
        """Sugerir valor numérico"""
        try:
            # Remover símbolos de moneda y espacios
            cleaned = re.sub(r'[^\d.,]', '', value)
            cleaned = cleaned.replace(',', '.')
            
            if cleaned:
                return float(cleaned)
        except:
            pass
        
        return None
    
    def _suggest_integer_value(self, value: str) -> Optional[int]:
        """Sugerir valor entero"""
        try:
            # Remover decimales
            cleaned = re.sub(r'[^\d]', '', value)
            if cleaned:
                return int(cleaned)
        except:
            pass
        
        return None
    
    def _suggest_datetime_value(self, value: str) -> Optional[str]:
        """Sugerir valor de fecha"""
        try:
            # Intentar parsear con diferentes formatos
            formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    datetime.strptime(value, fmt)
                    return value
                except ValueError:
                    continue
        except:
            pass
        
        return None
    
    def _calculate_field_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """Calcular estadísticas de campo"""
        stats = {
            'total_count': len(series),
            'null_count': series.isnull().sum(),
            'null_percentage': (series.isnull().sum() / len(series)) * 100,
            'unique_count': series.nunique(),
            'duplicate_count': len(series) - series.nunique()
        }
        
        # Estadísticas numéricas
        if pd.api.types.is_numeric_dtype(series):
            numeric_series = pd.to_numeric(series, errors='coerce')
            stats.update({
                'min': numeric_series.min(),
                'max': numeric_series.max(),
                'mean': numeric_series.mean(),
                'median': numeric_series.median(),
                'std': numeric_series.std(),
                'zero_count': (numeric_series == 0).sum(),
                'negative_count': (numeric_series < 0).sum()
            })
        
        # Estadísticas de texto
        if pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            string_series = series.astype(str)
            stats.update({
                'min_length': string_series.str.len().min(),
                'max_length': string_series.str.len().max(),
                'avg_length': string_series.str.len().mean(),
                'empty_string_count': (string_series == '').sum(),
                'whitespace_only_count': (string_series.str.strip() == '').sum()
            })
        
        return stats
    
    def _detect_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detectar anomalías en los datos"""
        anomalies = []
        
        try:
            # Anomalías en precios
            if 'price' in data.columns:
                price_series = pd.to_numeric(data['price'], errors='coerce')
                
                # Valores atípicos usando IQR
                Q1 = price_series.quantile(0.25)
                Q3 = price_series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = data[(price_series < lower_bound) | (price_series > upper_bound)]
                if len(outliers) > 0:
                    anomalies.append({
                        'type': 'price_outliers',
                        'field': 'price',
                        'count': len(outliers),
                        'description': f'Found {len(outliers)} price outliers using IQR method',
                        'severity': 'medium'
                    })
                
                # Precios cero o negativos
                zero_negative = data[price_series <= 0]
                if len(zero_negative) > 0:
                    anomalies.append({
                        'type': 'invalid_prices',
                        'field': 'price',
                        'count': len(zero_negative),
                        'description': f'Found {len(zero_negative)} zero or negative prices',
                        'severity': 'high'
                    })
            
            # Duplicados
            duplicates = data.duplicated()
            if duplicates.any():
                anomalies.append({
                    'type': 'duplicates',
                    'field': 'all',
                    'count': duplicates.sum(),
                    'description': f'Found {duplicates.sum()} duplicate records',
                    'severity': 'medium'
                })
            
            # Valores faltantes por columna
            missing_by_column = data.isnull().sum()
            for column, missing_count in missing_by_column.items():
                if missing_count > 0:
                    missing_percentage = (missing_count / len(data)) * 100
                    severity = 'high' if missing_percentage > 50 else 'medium' if missing_percentage > 20 else 'low'
                    
                    anomalies.append({
                        'type': 'missing_values',
                        'field': column,
                        'count': missing_count,
                        'description': f'{missing_percentage:.1f}% missing values in {column}',
                        'severity': severity
                    })
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    def _generate_recommendations(self, validation_results: List[ValidationResult], 
                                field_statistics: Dict[str, Dict[str, Any]], 
                                anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generar recomendaciones de mejora"""
        recommendations = []
        
        try:
            # Recomendaciones basadas en validaciones
            error_count = len([r for r in validation_results if not r.is_valid and r.severity == "error"])
            warning_count = len([r for r in validation_results if not r.is_valid and r.severity == "warning"])
            
            if error_count > 0:
                recommendations.append(f"Fix {error_count} validation errors to improve data quality")
            
            if warning_count > 0:
                recommendations.append(f"Review {warning_count} validation warnings for potential improvements")
            
            # Recomendaciones basadas en estadísticas
            for field, stats in field_statistics.items():
                if stats['null_percentage'] > 20:
                    recommendations.append(f"Consider data collection improvements for {field} ({(stats['null_percentage']):.1f}% missing)")
                
                if stats['duplicate_count'] > 0:
                    recommendations.append(f"Review duplicate values in {field} ({stats['duplicate_count']} duplicates)")
            
            # Recomendaciones basadas en anomalías
            for anomaly in anomalies:
                if anomaly['severity'] == 'high':
                    recommendations.append(f"Address {anomaly['type']} in {anomaly['field']}: {anomaly['description']}")
            
            # Recomendaciones generales
            if not recommendations:
                recommendations.append("Data quality is good. Continue monitoring for consistency.")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Limpiar datos"""
        try:
            logger.info(f"Cleaning {len(data)} records...")
            
            cleaned_data = data.copy()
            
            # Aplicar reglas de limpieza
            for rule in self.cleaning_rules:
                if rule.field in cleaned_data.columns:
                    cleaned_data = self._apply_cleaning_rule(cleaned_data, rule)
            
            logger.info("Data cleaning completed")
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            raise
    
    def _apply_cleaning_rule(self, data: pd.DataFrame, rule: CleaningRule) -> pd.DataFrame:
        """Aplicar regla de limpieza"""
        try:
            if rule.cleaning_type == "remove":
                # Remover registros que cumplan condición
                condition = rule.parameters.get("condition")
                if condition:
                    data = data[~data[rule.field].apply(lambda x: eval(condition))]
            
            elif rule.cleaning_type == "replace":
                # Reemplazar valores
                old_value = rule.parameters.get("old_value")
                new_value = rule.parameters.get("new_value")
                data[rule.field] = data[rule.field].replace(old_value, new_value)
            
            elif rule.cleaning_type == "transform":
                # Transformar valores
                function_name = rule.parameters.get("function")
                data[rule.field] = self._apply_transform_function(data[rule.field], function_name)
            
            elif rule.cleaning_type == "normalize":
                # Normalizar valores
                normalization_type = rule.parameters.get("type")
                data[rule.field] = self._apply_normalization(data[rule.field], normalization_type)
            
            elif rule.cleaning_type == "custom":
                # Función personalizada
                cleaner_name = rule.parameters.get("cleaner")
                if cleaner_name in self.custom_cleaners:
                    data[rule.field] = data[rule.field].apply(self.custom_cleaners[cleaner_name])
            
            return data
            
        except Exception as e:
            logger.error(f"Error applying cleaning rule {rule.name}: {e}")
            return data
    
    def _apply_transform_function(self, series: pd.Series, function_name: str) -> pd.Series:
        """Aplicar función de transformación"""
        try:
            if function_name == "strip":
                return series.astype(str).str.strip()
            elif function_name == "upper":
                return series.astype(str).str.upper()
            elif function_name == "lower":
                return series.astype(str).str.lower()
            elif function_name == "title_case":
                return series.astype(str).str.title()
            elif function_name == "remove_symbols":
                return series.astype(str).str.replace(r'[^\d.,]', '', regex=True)
            elif function_name in self.custom_cleaners:
                return series.apply(self.custom_cleaners[function_name])
            else:
                return series
                
        except Exception as e:
            logger.error(f"Error applying transform function {function_name}: {e}")
            return series
    
    def _apply_normalization(self, series: pd.Series, normalization_type: str) -> pd.Series:
        """Aplicar normalización"""
        try:
            if normalization_type == "currency":
                # Normalizar códigos de moneda
                currency_mapping = {
                    'usd': 'USD', 'dollar': 'USD', '$': 'USD',
                    'eur': 'EUR', 'euro': 'EUR', '€': 'EUR',
                    'gbp': 'GBP', 'pound': 'GBP', '£': 'GBP'
                }
                return series.astype(str).str.lower().replace(currency_mapping)
            
            elif normalization_type == "competitor":
                # Normalizar nombres de competidores
                competitor_mapping = {
                    'amazon': 'Amazon',
                    'ebay': 'eBay',
                    'walmart': 'Walmart',
                    'target': 'Target'
                }
                return series.astype(str).str.lower().replace(competitor_mapping)
            
            else:
                return series
                
        except Exception as e:
            logger.error(f"Error applying normalization {normalization_type}: {e}")
            return series
    
    def _save_quality_report(self, dataset_name: str, report: DataQualityReport):
        """Guardar reporte de calidad"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO quality_reports 
                (dataset_name, total_records, valid_records, quality_score, report_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                dataset_name,
                report.total_records,
                report.valid_records,
                report.quality_score,
                json.dumps(asdict(report), default=str)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving quality report: {e}")
    
    def get_quality_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener reportes de calidad"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT dataset_name, total_records, valid_records, quality_score, created_at
                FROM quality_reports
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            reports = []
            for result in results:
                reports.append({
                    'dataset_name': result[0],
                    'total_records': result[1],
                    'valid_records': result[2],
                    'quality_score': result[3],
                    'created_at': result[4]
                })
            
            return reports
            
        except Exception as e:
            logger.error(f"Error getting quality reports: {e}")
            return []
    
    def validate_and_clean_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, DataQualityReport]:
        """Validar y limpiar datos en una sola operación"""
        try:
            # Primero validar
            report = self.validate_data(data)
            
            # Luego limpiar
            cleaned_data = self.clean_data(data)
            
            # Validar datos limpios
            cleaned_report = self.validate_data(cleaned_data)
            
            logger.info(f"Data validation and cleaning completed. Quality improved from {report.quality_score:.2f}% to {cleaned_report.quality_score:.2f}%")
            
            return cleaned_data, cleaned_report
            
        except Exception as e:
            logger.error(f"Error in validate and clean data: {e}")
            raise

def main():
    """Función principal para demostrar sistema de validación"""
    print("=" * 60)
    print("DATA VALIDATION AND CLEANING SYSTEM - DEMO")
    print("=" * 60)
    
    # Inicializar sistema de validación
    validation_system = DataValidationSystem()
    
    # Crear datos de prueba con problemas
    test_data = pd.DataFrame({
        'product_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'product_name': ['Product 1', '  Product 2  ', '', 'Product 4', 'Product 5'],
        'price': ['$19.99', '25.50', '0', '-5.00', 'invalid'],
        'competitor': ['amazon', 'eBay', 'Walmart', 'target', 'Amazon'],
        'currency': ['usd', 'USD', 'EUR', 'gbp', 'INVALID'],
        'date_collected': ['2024-01-01', '2024-01-02', 'invalid-date', '2024-01-04', '2024-01-05'],
        'source': ['https://amazon.com', 'http://ebay.com', 'invalid-url', 'https://walmart.com', 'https://target.com']
    })
    
    print("Original data:")
    print(test_data)
    print()
    
    # Validar datos
    print("Validating data...")
    report = validation_system.validate_data(test_data)
    
    print(f"Quality Score: {report.quality_score:.2f}%")
    print(f"Valid Records: {report.valid_records}/{report.total_records}")
    print(f"Invalid Records: {report.invalid_records}")
    print()
    
    # Mostrar errores de validación
    print("Validation Errors:")
    errors = [r for r in report.validation_results if not r.is_valid and r.severity == "error"]
    for error in errors[:10]:  # Mostrar primeros 10
        print(f"  • {error.field}: {error.error_message} (Value: {error.value})")
        if error.suggested_value:
            print(f"    Suggested: {error.suggested_value}")
    print()
    
    # Mostrar anomalías
    print("Anomalies Detected:")
    for anomaly in report.anomalies:
        print(f"  • {anomaly['type']}: {anomaly['description']} (Severity: {anomaly['severity']})")
    print()
    
    # Mostrar recomendaciones
    print("Recommendations:")
    for rec in report.recommendations:
        print(f"  • {rec}")
    print()
    
    # Limpiar datos
    print("Cleaning data...")
    cleaned_data = validation_system.clean_data(test_data)
    
    print("Cleaned data:")
    print(cleaned_data)
    print()
    
    # Validar datos limpios
    print("Validating cleaned data...")
    cleaned_report = validation_system.validate_data(cleaned_data)
    
    print(f"Cleaned Quality Score: {cleaned_report.quality_score:.2f}%")
    print(f"Improvement: {cleaned_report.quality_score - report.quality_score:.2f}%")
    print()
    
    # Mostrar reportes de calidad
    print("Quality Reports History:")
    reports = validation_system.get_quality_reports(limit=5)
    for rep in reports:
        print(f"  • {rep['dataset_name']}: {rep['quality_score']:.2f}% ({rep['valid_records']}/{rep['total_records']} valid)")
    
    print("\n" + "=" * 60)
    print("DATA VALIDATION DEMO COMPLETED")
    print("=" * 60)
    print("🔍 Data validation features:")
    print("  • Schema validation")
    print("  • Data type validation")
    print("  • Range and pattern validation")
    print("  • Custom validation rules")
    print("  • Anomaly detection")
    print("  • Data cleaning and normalization")
    print("  • Quality scoring and reporting")
    print("  • Automated data correction suggestions")

if __name__ == "__main__":
    main()






