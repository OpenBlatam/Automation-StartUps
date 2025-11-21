"""
Extractor de Tablas de Documentos
====================================

Extrae tablas de documentos PDF e imágenes usando OCR avanzado.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class TableCell:
    """Celda de tabla"""
    row: int
    col: int
    text: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float


@dataclass
class Table:
    """Tabla extraída"""
    table_id: str
    rows: int
    cols: int
    cells: List[TableCell]
    data: List[List[str]]  # Matriz de datos
    bbox: Tuple[int, int, int, int]  # Bounding box de la tabla
    confidence: float


class TableExtractor:
    """Extractor de tablas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_tables_from_image(
        self,
        image_path: str,
        min_rows: int = 2,
        min_cols: int = 2
    ) -> List[Table]:
        """Extrae tablas de una imagen"""
        try:
            # Cargar imagen
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"No se pudo cargar imagen: {image_path}")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detectar líneas de tabla
            tables = self._detect_tables(gray, min_rows, min_cols)
            
            # Extraer contenido de cada tabla
            for table in tables:
                table.cells = self._extract_table_cells(img, table)
                table.data = self._cells_to_matrix(table.cells, table.rows, table.cols)
            
            return tables
            
        except Exception as e:
            self.logger.error(f"Error extrayendo tablas: {e}")
            return []
    
    def _detect_tables(
        self,
        gray: np.ndarray,
        min_rows: int,
        min_cols: int
    ) -> List[Table]:
        """Detecta tablas en la imagen"""
        tables = []
        
        # Usar detección de líneas horizontales y verticales
        # Horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
        
        # Combinar
        table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(
            table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        for idx, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 1000:  # Filtrar tablas muy pequeñas
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Estimar filas y columnas
            rows = max(min_rows, h // 30)  # Estimación simple
            cols = max(min_cols, w // 100)
            
            table = Table(
                table_id=f"table_{idx}",
                rows=rows,
                cols=cols,
                cells=[],
                data=[],
                bbox=(x, y, w, h),
                confidence=0.7  # Estimación
            )
            
            tables.append(table)
        
        return tables
    
    def _extract_table_cells(
        self,
        image: np.ndarray,
        table: Table
    ) -> List[TableCell]:
        """Extrae celdas de una tabla"""
        cells = []
        x, y, w, h = table.bbox
        
        # ROI de la tabla
        roi = image[y:y+h, x:x+w]
        
        # Dividir en celdas (simplificado)
        cell_width = w // table.cols
        cell_height = h // table.rows
        
        for row in range(table.rows):
            for col in range(table.cols):
                cell_x = col * cell_width
                cell_y = row * cell_height
                cell_roi = roi[cell_y:cell_y+cell_height, cell_x:cell_x+cell_width]
                
                # OCR en celda (simplificado - usar OCR real)
                cell_text = self._extract_text_from_cell(cell_roi)
                
                cells.append(TableCell(
                    row=row,
                    col=col,
                    text=cell_text,
                    bbox=(x + cell_x, y + cell_y, cell_width, cell_height),
                    confidence=0.8
                ))
        
        return cells
    
    def _extract_text_from_cell(self, cell_image: np.ndarray) -> str:
        """Extrae texto de una celda"""
        # Simplificado - en producción usar OCR real
        try:
            import pytesseract
            text = pytesseract.image_to_string(cell_image, config='--psm 7')
            return text.strip()
        except:
            return ""
    
    def _cells_to_matrix(
        self,
        cells: List[TableCell],
        rows: int,
        cols: int
    ) -> List[List[str]]:
        """Convierte celdas a matriz"""
        matrix = [["" for _ in range(cols)] for _ in range(rows)]
        
        for cell in cells:
            if 0 <= cell.row < rows and 0 <= cell.col < cols:
                matrix[cell.row][cell.col] = cell.text
        
        return matrix
    
    def export_table_to_csv(self, table: Table, output_path: str) -> str:
        """Exporta tabla a CSV"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in table.data:
                writer.writerow(row)
        
        self.logger.info(f"Tabla exportada a CSV: {output_path}")
        return output_path
    
    def export_table_to_excel(self, table: Table, output_path: str) -> str:
        """Exporta tabla a Excel"""
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            
            for row_idx, row_data in enumerate(table.data, 1):
                for col_idx, cell_value in enumerate(row_data, 1):
                    ws.cell(row=row_idx, column=col_idx, value=cell_value)
            
            wb.save(output_path)
            self.logger.info(f"Tabla exportada a Excel: {output_path}")
            return output_path
        except ImportError:
            raise ImportError("openpyxl es requerido para exportar a Excel")

