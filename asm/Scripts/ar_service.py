from datetime import datetime, timedelta
from app import db
from models import Product, InventoryRecord
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import os
import math

@dataclass
class ARMarker:
    """Marcador de realidad aumentada"""
    marker_id: str
    product_id: int
    position: Tuple[float, float, float]  # x, y, z
    rotation: Tuple[float, float, float]  # roll, pitch, yaw
    scale: Tuple[float, float, float]     # width, height, depth
    marker_type: str  # 'qr', 'aruco', 'image', 'object'
    is_active: bool = True
    created_at: datetime = None

@dataclass
class ARContent:
    """Contenido de realidad aumentada"""
    content_id: str
    marker_id: str
    content_type: str  # '3d_model', 'video', 'image', 'text', 'animation'
    content_url: str
    metadata: Dict
    is_interactive: bool = False
    created_at: datetime = None

@dataclass
class WarehouseLayout:
    """Layout del almacén para AR"""
    layout_id: str
    name: str
    dimensions: Tuple[float, float, float]  # width, height, depth
    zones: List[Dict]
    aisles: List[Dict]
    shelves: List[Dict]
    created_at: datetime = None

class AugmentedRealityService:
    """Servicio de realidad aumentada"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.markers = {}
        self.ar_content = {}
        self.warehouse_layouts = {}
        self.ar_sessions = {}
        
        # Configurar layout por defecto
        self._setup_default_layout()
    
    def _setup_default_layout(self):
        """Configura layout por defecto del almacén"""
        try:
            # Layout principal del almacén
            main_layout = WarehouseLayout(
                layout_id="MAIN_WAREHOUSE",
                name="Almacén Principal",
                dimensions=(100.0, 10.0, 50.0),  # 100m x 10m x 50m
                zones=[
                    {
                        'zone_id': 'ZONE_A',
                        'name': 'Zona A - Productos Electrónicos',
                        'position': (0, 0, 0),
                        'dimensions': (25, 10, 25),
                        'color': '#FF6B6B'
                    },
                    {
                        'zone_id': 'ZONE_B',
                        'name': 'Zona B - Productos de Oficina',
                        'position': (25, 0, 0),
                        'dimensions': (25, 10, 25),
                        'color': '#4ECDC4'
                    },
                    {
                        'zone_id': 'ZONE_C',
                        'name': 'Zona C - Productos de Hogar',
                        'position': (50, 0, 0),
                        'dimensions': (25, 10, 25),
                        'color': '#45B7D1'
                    },
                    {
                        'zone_id': 'ZONE_D',
                        'name': 'Zona D - Productos Varios',
                        'position': (75, 0, 0),
                        'dimensions': (25, 10, 25),
                        'color': '#96CEB4'
                    }
                ],
                aisles=[
                    {
                        'aisle_id': 'AISLE_1',
                        'name': 'Pasillo 1',
                        'start_position': (12.5, 0, 0),
                        'end_position': (12.5, 0, 25),
                        'width': 3.0
                    },
                    {
                        'aisle_id': 'AISLE_2',
                        'name': 'Pasillo 2',
                        'start_position': (37.5, 0, 0),
                        'end_position': (37.5, 0, 25),
                        'width': 3.0
                    },
                    {
                        'aisle_id': 'AISLE_3',
                        'name': 'Pasillo 3',
                        'start_position': (62.5, 0, 0),
                        'end_position': (62.5, 0, 25),
                        'width': 3.0
                    },
                    {
                        'aisle_id': 'AISLE_4',
                        'name': 'Pasillo 4',
                        'start_position': (87.5, 0, 0),
                        'end_position': (87.5, 0, 25),
                        'width': 3.0
                    }
                ],
                shelves=[
                    {
                        'shelf_id': 'SHELF_A1_1',
                        'name': 'Estante A1-1',
                        'position': (5, 2, 5),
                        'dimensions': (10, 2, 1),
                        'capacity': 100,
                        'current_load': 75
                    },
                    {
                        'shelf_id': 'SHELF_A1_2',
                        'name': 'Estante A1-2',
                        'position': (5, 4, 5),
                        'dimensions': (10, 2, 1),
                        'capacity': 100,
                        'current_load': 60
                    },
                    {
                        'shelf_id': 'SHELF_B1_1',
                        'name': 'Estante B1-1',
                        'position': (30, 2, 5),
                        'dimensions': (10, 2, 1),
                        'capacity': 100,
                        'current_load': 90
                    }
                ],
                created_at=datetime.utcnow()
            )
            
            self.warehouse_layouts[main_layout.layout_id] = main_layout
            
            # Crear marcadores AR para productos
            self._create_product_markers()
            
            self.logger.info('Layout de almacén configurado')
            
        except Exception as e:
            self.logger.error(f'Error configurando layout por defecto: {str(e)}')
    
    def _create_product_markers(self):
        """Crea marcadores AR para productos"""
        try:
            # Obtener productos de la base de datos
            products = Product.query.limit(20).all()  # Limitar a 20 productos para demo
            
            for i, product in enumerate(products):
                # Calcular posición en el almacén
                zone_index = i % 4
                shelf_index = (i // 4) % 3
                
                x = 5 + (zone_index * 25) + (shelf_index * 3)
                y = 2 + (shelf_index * 2)
                z = 5 + (i % 5) * 2
                
                marker = ARMarker(
                    marker_id=f"MARKER_{product.id}",
                    product_id=product.id,
                    position=(x, y, z),
                    rotation=(0, 0, 0),
                    scale=(1, 1, 1),
                    marker_type='qr',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                self.markers[marker.marker_id] = marker
                
                # Crear contenido AR para el producto
                content = ARContent(
                    content_id=f"CONTENT_{product.id}",
                    marker_id=marker.marker_id,
                    content_type='3d_model',
                    content_url=f'/static/ar/models/product_{product.id}.glb',
                    metadata={
                        'product_name': product.name,
                        'product_sku': product.sku,
                        'category': product.category,
                        'unit_price': float(product.unit_price),
                        'stock_level': self._get_current_stock(product.id),
                        'description': product.description
                    },
                    is_interactive=True,
                    created_at=datetime.utcnow()
                )
                
                self.ar_content[content.content_id] = content
            
            self.logger.info(f'Creados {len(self.markers)} marcadores AR')
            
        except Exception as e:
            self.logger.error(f'Error creando marcadores de productos: {str(e)}')
    
    def _get_current_stock(self, product_id: int) -> int:
        """Obtiene stock actual de un producto"""
        try:
            entries = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'in'
            ).scalar() or 0
            
            exits = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'out'
            ).scalar() or 0
            
            adjustments = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'adjustment'
            ).scalar() or 0
            
            return max(0, entries - exits + adjustments)
            
        except Exception as e:
            self.logger.error(f'Error obteniendo stock actual: {str(e)}')
            return 0
    
    def get_warehouse_layout(self, layout_id: str = None) -> Dict:
        """Obtiene layout del almacén"""
        try:
            if layout_id is None:
                layout_id = "MAIN_WAREHOUSE"
            
            layout = self.warehouse_layouts.get(layout_id)
            if not layout:
                return {'success': False, 'error': 'Layout no encontrado'}
            
            return {
                'success': True,
                'layout': {
                    'layout_id': layout.layout_id,
                    'name': layout.name,
                    'dimensions': layout.dimensions,
                    'zones': layout.zones,
                    'aisles': layout.aisles,
                    'shelves': layout.shelves,
                    'created_at': layout.created_at.isoformat() if layout.created_at else None
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo layout del almacén: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_ar_markers(self, zone_id: str = None) -> Dict:
        """Obtiene marcadores AR"""
        try:
            markers_data = []
            
            for marker_id, marker in self.markers.items():
                if not marker.is_active:
                    continue
                
                # Filtrar por zona si se especifica
                if zone_id:
                    # Determinar zona basada en posición
                    x, y, z = marker.position
                    if zone_id == 'ZONE_A' and x < 25:
                        pass  # Incluir
                    elif zone_id == 'ZONE_B' and 25 <= x < 50:
                        pass  # Incluir
                    elif zone_id == 'ZONE_C' and 50 <= x < 75:
                        pass  # Incluir
                    elif zone_id == 'ZONE_D' and x >= 75:
                        pass  # Incluir
                    else:
                        continue  # Excluir
                
                markers_data.append({
                    'marker_id': marker.marker_id,
                    'product_id': marker.product_id,
                    'position': marker.position,
                    'rotation': marker.rotation,
                    'scale': marker.scale,
                    'marker_type': marker.marker_type,
                    'is_active': marker.is_active,
                    'created_at': marker.created_at.isoformat() if marker.created_at else None
                })
            
            return {
                'success': True,
                'markers': markers_data,
                'total_markers': len(markers_data),
                'zone_filter': zone_id
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo marcadores AR: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_ar_content(self, marker_id: str = None) -> Dict:
        """Obtiene contenido AR"""
        try:
            content_data = []
            
            for content_id, content in self.ar_content.items():
                if marker_id and content.marker_id != marker_id:
                    continue
                
                content_data.append({
                    'content_id': content.content_id,
                    'marker_id': content.marker_id,
                    'content_type': content.content_type,
                    'content_url': content.content_url,
                    'metadata': content.metadata,
                    'is_interactive': content.is_interactive,
                    'created_at': content.created_at.isoformat() if content.created_at else None
                })
            
            return {
                'success': True,
                'content': content_data,
                'total_content': len(content_data),
                'marker_filter': marker_id
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo contenido AR: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def create_ar_session(self, user_id: str, session_type: str = 'inventory_check') -> Dict:
        """Crea sesión AR"""
        try:
            session_id = f"AR_SESSION_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            session = {
                'session_id': session_id,
                'user_id': user_id,
                'session_type': session_type,
                'start_time': datetime.utcnow(),
                'end_time': None,
                'markers_scanned': [],
                'actions_performed': [],
                'status': 'active'
            }
            
            self.ar_sessions[session_id] = session
            
            return {
                'success': True,
                'session_id': session_id,
                'session': session
            }
            
        except Exception as e:
            self.logger.error(f'Error creando sesión AR: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def scan_marker(self, session_id: str, marker_id: str) -> Dict:
        """Escanea marcador AR"""
        try:
            session = self.ar_sessions.get(session_id)
            if not session:
                return {'success': False, 'error': 'Sesión no encontrada'}
            
            marker = self.markers.get(marker_id)
            if not marker:
                return {'success': False, 'error': 'Marcador no encontrado'}
            
            # Registrar escaneo
            scan_data = {
                'marker_id': marker_id,
                'timestamp': datetime.utcnow(),
                'action': 'scan'
            }
            
            session['markers_scanned'].append(scan_data)
            
            # Obtener contenido AR
            content = None
            for content_id, c in self.ar_content.items():
                if c.marker_id == marker_id:
                    content = c
                    break
            
            return {
                'success': True,
                'marker': {
                    'marker_id': marker.marker_id,
                    'product_id': marker.product_id,
                    'position': marker.position,
                    'rotation': marker.rotation,
                    'scale': marker.scale
                },
                'content': {
                    'content_id': content.content_id if content else None,
                    'content_type': content.content_type if content else None,
                    'content_url': content.content_url if content else None,
                    'metadata': content.metadata if content else None,
                    'is_interactive': content.is_interactive if content else False
                } if content else None,
                'scan_timestamp': scan_data['timestamp'].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f'Error escaneando marcador: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def perform_ar_action(self, session_id: str, action: str, data: Dict) -> Dict:
        """Realiza acción en AR"""
        try:
            session = self.ar_sessions.get(session_id)
            if not session:
                return {'success': False, 'error': 'Sesión no encontrada'}
            
            # Registrar acción
            action_data = {
                'action': action,
                'data': data,
                'timestamp': datetime.utcnow()
            }
            
            session['actions_performed'].append(action_data)
            
            # Procesar acción específica
            if action == 'update_stock':
                return self._process_stock_update(data)
            elif action == 'move_product':
                return self._process_product_move(data)
            elif action == 'add_note':
                return self._process_add_note(data)
            else:
                return {'success': True, 'message': 'Acción registrada'}
            
        except Exception as e:
            self.logger.error(f'Error realizando acción AR: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _process_stock_update(self, data: Dict) -> Dict:
        """Procesa actualización de stock"""
        try:
            product_id = data.get('product_id')
            new_quantity = data.get('quantity')
            notes = data.get('notes', '')
            
            if not product_id or new_quantity is None:
                return {'success': False, 'error': 'Datos incompletos'}
            
            # Crear registro de inventario
            inventory_record = InventoryRecord(
                product_id=product_id,
                quantity=new_quantity,
                movement_type='adjustment',
                unit_price=0.0,
                location='AR Update',
                reference='AR_STOCK_UPDATE',
                notes=notes,
                created_at=datetime.utcnow()
            )
            
            db.session.add(inventory_record)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Stock actualizado exitosamente',
                'new_quantity': new_quantity
            }
            
        except Exception as e:
            self.logger.error(f'Error procesando actualización de stock: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _process_product_move(self, data: Dict) -> Dict:
        """Procesa movimiento de producto"""
        try:
            product_id = data.get('product_id')
            from_position = data.get('from_position')
            to_position = data.get('to_position')
            
            if not all([product_id, from_position, to_position]):
                return {'success': False, 'error': 'Datos incompletos'}
            
            # Actualizar posición del marcador
            marker_id = f"MARKER_{product_id}"
            marker = self.markers.get(marker_id)
            
            if marker:
                marker.position = tuple(to_position)
            
            return {
                'success': True,
                'message': 'Producto movido exitosamente',
                'new_position': to_position
            }
            
        except Exception as e:
            self.logger.error(f'Error procesando movimiento de producto: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _process_add_note(self, data: Dict) -> Dict:
        """Procesa añadir nota"""
        try:
            product_id = data.get('product_id')
            note = data.get('note')
            
            if not product_id or not note:
                return {'success': False, 'error': 'Datos incompletos'}
            
            # Actualizar metadatos del contenido AR
            content_id = f"CONTENT_{product_id}"
            content = self.ar_content.get(content_id)
            
            if content:
                if 'notes' not in content.metadata:
                    content.metadata['notes'] = []
                content.metadata['notes'].append({
                    'note': note,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            return {
                'success': True,
                'message': 'Nota añadida exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f'Error procesando nota: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def end_ar_session(self, session_id: str) -> Dict:
        """Termina sesión AR"""
        try:
            session = self.ar_sessions.get(session_id)
            if not session:
                return {'success': False, 'error': 'Sesión no encontrada'}
            
            session['end_time'] = datetime.utcnow()
            session['status'] = 'completed'
            
            # Calcular estadísticas de la sesión
            duration = (session['end_time'] - session['start_time']).total_seconds()
            
            return {
                'success': True,
                'session': {
                    'session_id': session_id,
                    'duration_seconds': duration,
                    'markers_scanned': len(session['markers_scanned']),
                    'actions_performed': len(session['actions_performed']),
                    'status': session['status']
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error terminando sesión AR: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_ar_dashboard_data(self) -> Dict:
        """Obtiene datos para dashboard AR"""
        try:
            # Estadísticas de marcadores
            total_markers = len(self.markers)
            active_markers = len([m for m in self.markers.values() if m.is_active])
            
            # Estadísticas de contenido
            total_content = len(self.ar_content)
            interactive_content = len([c for c in self.ar_content.values() if c.is_interactive])
            
            # Estadísticas de sesiones
            total_sessions = len(self.ar_sessions)
            active_sessions = len([s for s in self.ar_sessions.values() if s['status'] == 'active'])
            
            # Sesiones recientes
            recent_sessions = [
                s for s in self.ar_sessions.values() 
                if s['start_time'] > datetime.utcnow() - timedelta(hours=24)
            ]
            
            return {
                'success': True,
                'dashboard': {
                    'markers': {
                        'total': total_markers,
                        'active': active_markers,
                        'inactive': total_markers - active_markers
                    },
                    'content': {
                        'total': total_content,
                        'interactive': interactive_content,
                        'static': total_content - interactive_content
                    },
                    'sessions': {
                        'total': total_sessions,
                        'active': active_sessions,
                        'recent_24h': len(recent_sessions)
                    },
                    'warehouse': {
                        'layouts': len(self.warehouse_layouts),
                        'zones': len(self.warehouse_layouts['MAIN_WAREHOUSE'].zones) if 'MAIN_WAREHOUSE' in self.warehouse_layouts else 0,
                        'aisles': len(self.warehouse_layouts['MAIN_WAREHOUSE'].aisles) if 'MAIN_WAREHOUSE' in self.warehouse_layouts else 0,
                        'shelves': len(self.warehouse_layouts['MAIN_WAREHOUSE'].shelves) if 'MAIN_WAREHOUSE' in self.warehouse_layouts else 0
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo datos de dashboard AR: {str(e)}')
            return {'success': False, 'error': str(e)}

# Instancia global del servicio AR
augmented_reality_service = AugmentedRealityService()



