"""
Comparadores de Datos de Nómina
Funciones para comparar períodos, empleados, departamentos, etc.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PayrollComparator:
    """Comparador de datos de nómina"""
    
    @staticmethod
    def compare_periods(
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compara dos períodos de nómina
        
        Args:
            current: Datos del período actual
            previous: Datos del período anterior
        
        Returns:
            Dict con comparación y cambios
        """
        comparison = {
            "current": current,
            "previous": previous,
            "changes": {},
            "percentages": {},
            "trends": {}
        }
        
        # Campos a comparar
        fields = [
            "employee_count",
            "total_hours",
            "regular_hours",
            "overtime_hours",
            "total_gross_pay",
            "total_deductions",
            "total_expenses",
            "total_net_pay"
        ]
        
        for field in fields:
            current_val = current.get(field, Decimal("0.00"))
            previous_val = previous.get(field, Decimal("0.00"))
            
            # Calcular cambio absoluto
            if isinstance(current_val, (int, Decimal)) and isinstance(previous_val, (int, Decimal)):
                change = Decimal(str(current_val)) - Decimal(str(previous_val))
                comparison["changes"][field] = change
                
                # Calcular cambio porcentual
                if previous_val != Decimal("0.00") and previous_val != 0:
                    if isinstance(current_val, Decimal):
                        pct = (change / Decimal(str(previous_val)) * 100).quantize(Decimal("0.01"))
                    else:
                        pct = Decimal(str((change / previous_val) * 100)).quantize(Decimal("0.01"))
                    comparison["percentages"][field] = pct
                    
                    # Determinar tendencia
                    if change > Decimal("0.01"):
                        comparison["trends"][field] = "increasing"
                    elif change < Decimal("-0.01"):
                        comparison["trends"][field] = "decreasing"
                    else:
                        comparison["trends"][field] = "stable"
                else:
                    comparison["percentages"][field] = Decimal("0.00")
                    comparison["trends"][field] = "stable"
        
        return comparison
    
    @staticmethod
    def compare_employees(
        employee1: Dict[str, Any],
        employee2: Dict[str, Any],
        period_data1: Dict[str, Any],
        period_data2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compara dos empleados en el mismo período
        
        Args:
            employee1: Datos del primer empleado
            employee2: Datos del segundo empleado
            period_data1: Datos del período del primer empleado
            period_data2: Datos del período del segundo empleado
        
        Returns:
            Dict con comparación
        """
        comparison = {
            "employee1": {
                "id": employee1.get("employee_id"),
                "name": employee1.get("name"),
                "data": period_data1
            },
            "employee2": {
                "id": employee2.get("employee_id"),
                "name": employee2.get("name"),
                "data": period_data2
            },
            "differences": {}
        }
        
        # Comparar campos numéricos
        numeric_fields = [
            "total_hours", "regular_hours", "overtime_hours",
            "gross_pay", "total_deductions", "net_pay"
        ]
        
        for field in numeric_fields:
            val1 = period_data1.get(field, Decimal("0.00"))
            val2 = period_data2.get(field, Decimal("0.00"))
            
            if isinstance(val1, (int, Decimal)) and isinstance(val2, (int, Decimal)):
                val1_decimal = Decimal(str(val1))
                val2_decimal = Decimal(str(val2))
                
                diff = val1_decimal - val2_decimal
                comparison["differences"][field] = {
                    "difference": diff.quantize(Decimal("0.01")),
                    "employee1": val1_decimal.quantize(Decimal("0.01")),
                    "employee2": val2_decimal.quantize(Decimal("0.01"))
                }
        
        return comparison
    
    @staticmethod
    def compare_departments(
        dept1_data: Dict[str, Any],
        dept2_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compara dos departamentos
        
        Args:
            dept1_data: Datos del primer departamento
            dept2_data: Datos del segundo departamento
        
        Returns:
            Dict con comparación
        """
        comparison = {
            "department1": dept1_data,
            "department2": dept2_data,
            "comparison": {}
        }
        
        fields = [
            "employee_count",
            "total_hours",
            "total_gross",
            "total_net",
            "average_gross_per_employee",
            "average_hours_per_employee"
        ]
        
        for field in fields:
            val1 = dept1_data.get(field, Decimal("0.00"))
            val2 = dept2_data.get(field, Decimal("0.00"))
            
            if isinstance(val1, (int, Decimal)) and isinstance(val2, (int, Decimal)):
                val1_decimal = Decimal(str(val1))
                val2_decimal = Decimal(str(val2))
                
                diff = val1_decimal - val2_decimal
                
                if val2_decimal != Decimal("0.00"):
                    pct = (diff / val2_decimal * 100).quantize(Decimal("0.01"))
                else:
                    pct = Decimal("0.00")
                
                comparison["comparison"][field] = {
                    "difference": diff.quantize(Decimal("0.01")),
                    "percentage": pct,
                    "dept1": val1_decimal.quantize(Decimal("0.01")),
                    "dept2": val2_decimal.quantize(Decimal("0.01"))
                }
        
        return comparison
    
    @staticmethod
    def find_outliers(
        data: List[Dict[str, Any]],
        field: str,
        method: str = "iqr"
    ) -> List[Dict[str, Any]]:
        """
        Encuentra valores atípicos en una lista de datos
        
        Args:
            data: Lista de diccionarios con datos
            field: Campo numérico a analizar
            method: Método (iqr, zscore, percentile)
        
        Returns:
            Lista de valores atípicos
        """
        if not data:
            return []
        
        # Extraer valores
        values = []
        for item in data:
            val = item.get(field)
            if isinstance(val, (int, float, Decimal)):
                values.append(Decimal(str(val)))
        
        if len(values) < 3:
            return []
        
        outliers = []
        
        if method == "iqr":
            # Método IQR (Interquartile Range)
            sorted_values = sorted(values)
            q1_idx = len(sorted_values) // 4
            q3_idx = 3 * len(sorted_values) // 4
            
            q1 = sorted_values[q1_idx]
            q3 = sorted_values[q3_idx]
            iqr = q3 - q1
            
            lower_bound = q1 - Decimal("1.5") * iqr
            upper_bound = q3 + Decimal("1.5") * iqr
            
            for item in data:
                val = item.get(field)
                if isinstance(val, (int, float, Decimal)):
                    val_decimal = Decimal(str(val))
                    if val_decimal < lower_bound or val_decimal > upper_bound:
                        outliers.append(item)
        
        elif method == "zscore":
            # Método Z-score
            import math
            mean = sum(values) / Decimal(str(len(values)))
            variance = sum((v - mean) ** 2 for v in values) / Decimal(str(len(values)))
            std_dev = Decimal(str(math.sqrt(float(variance)))) if variance > 0 else Decimal("0.00")
            
            if std_dev > 0:
                for item in data:
                    val = item.get(field)
                    if isinstance(val, (int, float, Decimal)):
                        val_decimal = Decimal(str(val))
                        z_score = abs((val_decimal - mean) / std_dev)
                        if z_score > Decimal("2.5"):  # Más de 2.5 desviaciones estándar
                            outliers.append(item)
        
        elif method == "percentile":
            # Método de percentiles (valores fuera del 5-95%)
            sorted_values = sorted(values)
            p5_idx = int(len(sorted_values) * 0.05)
            p95_idx = int(len(sorted_values) * 0.95)
            
            lower_bound = sorted_values[p5_idx]
            upper_bound = sorted_values[p95_idx]
            
            for item in data:
                val = item.get(field)
                if isinstance(val, (int, float, Decimal)):
                    val_decimal = Decimal(str(val))
                    if val_decimal < lower_bound or val_decimal > upper_bound:
                        outliers.append(item)
        
        return outliers
    
    @staticmethod
    def rank_employees(
        employees_data: List[Dict[str, Any]],
        field: str,
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Rankea empleados por un campo
        
        Args:
            employees_data: Lista de datos de empleados
            field: Campo a rankear
            ascending: Si ordenar ascendente o descendente
        
        Returns:
            Lista rankeada con posición
        """
        # Filtrar y ordenar
        valid_data = [
            item for item in employees_data
            if field in item and isinstance(item[field], (int, float, Decimal))
        ]
        
        sorted_data = sorted(
            valid_data,
            key=lambda x: Decimal(str(x[field])),
            reverse=not ascending
        )
        
        # Agregar ranking
        ranked = []
        for i, item in enumerate(sorted_data, 1):
            ranked_item = item.copy()
            ranked_item["rank"] = i
            ranked_item["rank_percentage"] = (
                Decimal(str(i)) / Decimal(str(len(sorted_data))) * 100
            ).quantize(Decimal("0.01"))
            ranked.append(ranked_item)
        
        return ranked
    
    @staticmethod
    def calculate_correlation(
        data: List[Dict[str, Any]],
        field1: str,
        field2: str
    ) -> Dict[str, Any]:
        """
        Calcula correlación entre dos campos
        
        Args:
            data: Lista de datos
            field1: Primer campo
            field2: Segundo campo
        
        Returns:
            Dict con coeficiente de correlación y estadísticas
        """
        import math
        
        # Extraer valores válidos
        pairs = []
        for item in data:
            val1 = item.get(field1)
            val2 = item.get(field2)
            
            if isinstance(val1, (int, float, Decimal)) and isinstance(val2, (int, float, Decimal)):
                pairs.append((
                    Decimal(str(val1)),
                    Decimal(str(val2))
                ))
        
        if len(pairs) < 2:
            return {
                "correlation": Decimal("0.00"),
                "sample_size": len(pairs),
                "valid": False
            }
        
        # Calcular medias
        mean1 = sum(p[0] for p in pairs) / Decimal(str(len(pairs)))
        mean2 = sum(p[1] for p in pairs) / Decimal(str(len(pairs)))
        
        # Calcular covarianza y desviaciones estándar
        covariance = sum((p[0] - mean1) * (p[1] - mean2) for p in pairs) / Decimal(str(len(pairs)))
        
        variance1 = sum((p[0] - mean1) ** 2 for p in pairs) / Decimal(str(len(pairs)))
        variance2 = sum((p[1] - mean2) ** 2 for p in pairs) / Decimal(str(len(pairs)))
        
        import math
        std_dev1 = Decimal(str(math.sqrt(float(variance1)))) if variance1 > 0 else Decimal("0.00")
        std_dev2 = Decimal(str(math.sqrt(float(variance2)))) if variance2 > 0 else Decimal("0.00")
        
        # Calcular correlación de Pearson
        if std_dev1 > 0 and std_dev2 > 0:
            correlation = (covariance / (std_dev1 * std_dev2)).quantize(Decimal("0.01"))
        else:
            correlation = Decimal("0.00")
        
        return {
            "correlation": correlation,
            "sample_size": len(pairs),
            "valid": True,
            "field1_mean": mean1.quantize(Decimal("0.01")),
            "field2_mean": mean2.quantize(Decimal("0.01")),
            "field1_std": std_dev1.quantize(Decimal("0.01")),
            "field2_std": std_dev2.quantize(Decimal("0.01"))
        }
