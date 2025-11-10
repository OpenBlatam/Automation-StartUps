"""
Sistema de Exportación de Datos

Exporta datos de precios a múltiples formatos
"""

import logging
import json
import csv
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class PriceExporter:
    """Exporta datos de precios a diferentes formatos"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.export_dir = Path(config.get('export_dir', '/tmp/price_exports'))
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(
        self,
        data: List[Dict],
        filename: Optional[str] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Exporta datos a CSV
        
        Args:
            data: Lista de diccionarios a exportar
            filename: Nombre del archivo (opcional)
            include_metadata: Incluir metadatos en el archivo
        
        Returns:
            Ruta del archivo exportado
        """
        if not data:
            raise ValueError("No data to export")
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prices_export_{timestamp}.csv"
        
        filepath = self.export_dir / filename
        
        # Convertir a DataFrame
        df = pd.DataFrame(data)
        
        # Agregar metadatos si se solicita
        if include_metadata:
            metadata = {
                'export_date': datetime.now().isoformat(),
                'total_records': len(data),
            }
            # Guardar metadatos en archivo separado
            metadata_file = filepath.with_suffix('.meta.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        # Exportar CSV
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"Datos exportados a CSV: {filepath} ({len(data)} registros)")
        return str(filepath)
    
    def export_to_json(
        self,
        data: List[Dict],
        filename: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """
        Exporta datos a JSON
        
        Args:
            data: Lista de diccionarios a exportar
            filename: Nombre del archivo (opcional)
            pretty: Formato legible
        
        Returns:
            Ruta del archivo exportado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prices_export_{timestamp}.json"
        
        filepath = self.export_dir / filename
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_records': len(data),
            'data': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(export_data, f, ensure_ascii=False)
        
        logger.info(f"Datos exportados a JSON: {filepath} ({len(data)} registros)")
        return str(filepath)
    
    def export_to_excel(
        self,
        data: List[Dict],
        filename: Optional[str] = None,
        sheet_name: str = 'Prices'
    ) -> str:
        """
        Exporta datos a Excel
        
        Args:
            data: Lista de diccionarios a exportar
            filename: Nombre del archivo (opcional)
            sheet_name: Nombre de la hoja
        
        Returns:
            Ruta del archivo exportado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prices_export_{timestamp}.xlsx"
        
        filepath = self.export_dir / filename
        
        # Convertir a DataFrame
        df = pd.DataFrame(data)
        
        # Exportar a Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"Datos exportados a Excel: {filepath} ({len(data)} registros)")
        return str(filepath)
    
    def export_price_history(
        self,
        product_id: str,
        history_data: List[Dict],
        format: str = 'csv'
    ) -> str:
        """
        Exporta historial de precios de un producto
        
        Args:
            product_id: ID del producto
            history_data: Datos históricos
            format: Formato de exportación (csv, json, excel)
        
        Returns:
            Ruta del archivo exportado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            filename = f"price_history_{product_id}_{timestamp}.csv"
            return self.export_to_csv(history_data, filename)
        elif format == 'json':
            filename = f"price_history_{product_id}_{timestamp}.json"
            return self.export_to_json(history_data, filename)
        elif format == 'excel':
            filename = f"price_history_{product_id}_{timestamp}.xlsx"
            return self.export_to_excel(history_data, filename, sheet_name=f'History_{product_id}')
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def export_analysis_report(
        self,
        analysis_data: Dict,
        format: str = 'json'
    ) -> str:
        """
        Exporta reporte de análisis
        
        Args:
            analysis_data: Datos de análisis
            format: Formato de exportación
        
        Returns:
            Ruta del archivo exportado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"analysis_report_{timestamp}.json"
            return self.export_to_json([analysis_data], filename)
        elif format == 'excel':
            # Aplanar estructura para Excel
            flattened = self._flatten_dict(analysis_data)
            filename = f"analysis_report_{timestamp}.xlsx"
            return self.export_to_excel([flattened], filename, sheet_name='Analysis')
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Aplana diccionario anidado"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convertir lista a string o expandir
                if len(v) > 0 and isinstance(v[0], dict):
                    # Expandir lista de dicts
                    for i, item in enumerate(v):
                        items.extend(
                            self._flatten_dict(item, f"{new_key}_{i}", sep=sep).items()
                        )
                else:
                    items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def export_comparison_report(
        self,
        comparison_data: Dict,
        format: str = 'excel'
    ) -> str:
        """
        Exporta reporte de comparación
        
        Args:
            comparison_data: Datos de comparación
            format: Formato de exportación
        
        Returns:
            Ruta del archivo exportado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        comparisons = comparison_data.get('comparisons', [])
        
        if format == 'excel':
            filename = f"comparison_report_{timestamp}.xlsx"
            filepath = self.export_dir / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de comparaciones
                if comparisons:
                    df_comparisons = pd.DataFrame(comparisons)
                    df_comparisons.to_excel(writer, sheet_name='Comparisons', index=False)
                
                # Hoja de resumen
                summary = {
                    'Metric': [
                        'Total Products',
                        'Products with Competition',
                        'Above Market',
                        'Below Market',
                        'In Market'
                    ],
                    'Value': [
                        comparison_data.get('total_products', 0),
                        comparison_data.get('products_with_competition', 0),
                        comparison_data.get('above_market', 0),
                        comparison_data.get('below_market', 0),
                        comparison_data.get('in_market', 0),
                    ]
                }
                df_summary = pd.DataFrame(summary)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            logger.info(f"Reporte de comparación exportado: {filepath}")
            return str(filepath)
        else:
            filename = f"comparison_report_{timestamp}.json"
            return self.export_to_json([comparison_data], filename)








