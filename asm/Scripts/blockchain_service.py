from datetime import datetime, timedelta
from app import db
from models import Product, InventoryRecord, SalesRecord
import hashlib
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class TransactionType(Enum):
    """Tipos de transacciones en blockchain"""
    PRODUCT_CREATED = "product_created"
    INVENTORY_IN = "inventory_in"
    INVENTORY_OUT = "inventory_out"
    INVENTORY_ADJUSTMENT = "inventory_adjustment"
    SALE_RECORDED = "sale_recorded"
    SUPPLIER_CHANGE = "supplier_change"
    PRICE_CHANGE = "price_change"
    QUALITY_CHECK = "quality_check"
    TRANSFER = "transfer"

@dataclass
class Block:
    """Bloque de blockchain"""
    index: int
    timestamp: datetime
    transactions: List[Dict]
    previous_hash: str
    hash: str
    nonce: int
    merkle_root: str

@dataclass
class Transaction:
    """Transacción en blockchain"""
    id: str
    transaction_type: TransactionType
    product_id: int
    quantity: int
    unit_price: float
    supplier_id: Optional[int]
    location: str
    metadata: Dict
    timestamp: datetime
    user_id: Optional[int]
    signature: str

class BlockchainService:
    """Servicio de blockchain para trazabilidad"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = 4  # Dificultad de minado
        self.mining_reward = 1.0
        
        # Crear bloque génesis
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Crea el bloque génesis"""
        genesis_transaction = Transaction(
            id=str(uuid.uuid4()),
            transaction_type=TransactionType.PRODUCT_CREATED,
            product_id=0,
            quantity=0,
            unit_price=0.0,
            supplier_id=None,
            location="Genesis",
            metadata={"message": "Genesis block created"},
            timestamp=datetime.utcnow(),
            user_id=None,
            signature="genesis"
        )
        
        genesis_block = Block(
            index=0,
            timestamp=datetime.utcnow(),
            transactions=[asdict(genesis_transaction)],
            previous_hash="0",
            hash="",
            nonce=0,
            merkle_root=""
        )
        
        genesis_block.hash = self._calculate_hash(genesis_block)
        genesis_block.merkle_root = self._calculate_merkle_root(genesis_block.transactions)
        
        self.chain.append(genesis_block)
        self.logger.info("Bloque génesis creado")
    
    def _calculate_hash(self, block: Block) -> str:
        """Calcula el hash de un bloque"""
        block_string = json.dumps({
            'index': block.index,
            'timestamp': block.timestamp.isoformat(),
            'transactions': block.transactions,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'merkle_root': block.merkle_root
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _calculate_merkle_root(self, transactions: List[Dict]) -> str:
        """Calcula la raíz de Merkle de las transacciones"""
        if not transactions:
            return "0"
        
        if len(transactions) == 1:
            # Convertir datetime a string para serialización
            tx_copy = transactions[0].copy()
            if 'timestamp' in tx_copy and hasattr(tx_copy['timestamp'], 'isoformat'):
                tx_copy['timestamp'] = tx_copy['timestamp'].isoformat()
            return hashlib.sha256(json.dumps(tx_copy, sort_keys=True).encode()).hexdigest()
        
        # Crear árbol de Merkle
        current_level = []
        for tx in transactions:
            # Convertir datetime a string para serialización
            tx_copy = tx.copy()
            if 'timestamp' in tx_copy and hasattr(tx_copy['timestamp'], 'isoformat'):
                tx_copy['timestamp'] = tx_copy['timestamp'].isoformat()
            tx_hash = hashlib.sha256(json.dumps(tx_copy, sort_keys=True).encode()).hexdigest()
            current_level.append(tx_hash)
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            
            current_level = next_level
        
        return current_level[0]
    
    def _proof_of_work(self, block: Block) -> int:
        """Algoritmo de prueba de trabajo"""
        target = "0" * self.difficulty
        nonce = 0
        
        while True:
            block.nonce = nonce
            block.hash = self._calculate_hash(block)
            
            if block.hash.startswith(target):
                return nonce
            
            nonce += 1
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Añade una transacción pendiente"""
        try:
            # Validar transacción
            if not self._validate_transaction(transaction):
                return False
            
            # Firmar transacción
            transaction.signature = self._sign_transaction(transaction)
            
            self.pending_transactions.append(transaction)
            self.logger.info(f"Transacción añadida: {transaction.transaction_type.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error añadiendo transacción: {str(e)}')
            return False
    
    def _validate_transaction(self, transaction: Transaction) -> bool:
        """Valida una transacción"""
        try:
            # Validaciones básicas
            if transaction.quantity < 0:
                return False
            
            if transaction.unit_price < 0:
                return False
            
            # Validar que el producto existe
            if transaction.product_id > 0:
                product = Product.query.get(transaction.product_id)
                if not product:
                    return False
            
            # Validar tipo de transacción
            if transaction.transaction_type not in TransactionType:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error validando transacción: {str(e)}')
            return False
    
    def _sign_transaction(self, transaction: Transaction) -> str:
        """Firma una transacción"""
        try:
            transaction_data = json.dumps({
                'id': transaction.id,
                'type': transaction.transaction_type.value,
                'product_id': transaction.product_id,
                'quantity': transaction.quantity,
                'unit_price': transaction.unit_price,
                'timestamp': transaction.timestamp.isoformat()
            }, sort_keys=True)
            
            return hashlib.sha256(transaction_data.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f'Error firmando transacción: {str(e)}')
            return ""
    
    def mine_block(self) -> Optional[Block]:
        """Mina un nuevo bloque"""
        try:
            if not self.pending_transactions:
                return None
            
            # Crear bloque con transacciones pendientes
            new_block = Block(
                index=len(self.chain),
                timestamp=datetime.utcnow(),
                transactions=[asdict(tx) for tx in self.pending_transactions],
                previous_hash=self.chain[-1].hash,
                hash="",
                nonce=0,
                merkle_root=""
            )
            
            # Calcular raíz de Merkle
            new_block.merkle_root = self._calculate_merkle_root(new_block.transactions)
            
            # Minar bloque (prueba de trabajo)
            self._proof_of_work(new_block)
            
            # Añadir bloque a la cadena
            self.chain.append(new_block)
            
            # Limpiar transacciones pendientes
            self.pending_transactions = []
            
            self.logger.info(f"Bloque minado: {new_block.index}")
            
            return new_block
            
        except Exception as e:
            self.logger.error(f'Error minando bloque: {str(e)}')
            return None
    
    def get_product_history(self, product_id: int) -> List[Dict]:
        """Obtiene historial de un producto en blockchain"""
        try:
            history = []
            
            for block in self.chain:
                for tx_data in block.transactions:
                    if tx_data.get('product_id') == product_id:
                        history.append({
                            'block_index': block.index,
                            'block_hash': block.hash,
                            'timestamp': block.timestamp.isoformat(),
                            'transaction': tx_data
                        })
            
            return history
            
        except Exception as e:
            self.logger.error(f'Error obteniendo historial del producto: {str(e)}')
            return []
    
    def get_supplier_history(self, supplier_id: int) -> List[Dict]:
        """Obtiene historial de un proveedor en blockchain"""
        try:
            history = []
            
            for block in self.chain:
                for tx_data in block.transactions:
                    if tx_data.get('supplier_id') == supplier_id:
                        history.append({
                            'block_index': block.index,
                            'block_hash': block.hash,
                            'timestamp': block.timestamp.isoformat(),
                            'transaction': tx_data
                        })
            
            return history
            
        except Exception as e:
            self.logger.error(f'Error obteniendo historial del proveedor: {str(e)}')
            return []
    
    def verify_chain(self) -> bool:
        """Verifica la integridad de la cadena"""
        try:
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]
                
                # Verificar hash del bloque anterior
                if current_block.previous_hash != previous_block.hash:
                    return False
                
                # Verificar hash del bloque actual
                if current_block.hash != self._calculate_hash(current_block):
                    return False
                
                # Verificar raíz de Merkle
                if current_block.merkle_root != self._calculate_merkle_root(current_block.transactions):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error verificando cadena: {str(e)}')
            return False
    
    def get_chain_info(self) -> Dict:
        """Obtiene información de la cadena"""
        try:
            total_transactions = sum(len(block.transactions) for block in self.chain)
            
            return {
                'chain_length': len(self.chain),
                'total_transactions': total_transactions,
                'pending_transactions': len(self.pending_transactions),
                'difficulty': self.difficulty,
                'last_block_hash': self.chain[-1].hash if self.chain else None,
                'chain_valid': self.verify_chain()
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo información de la cadena: {str(e)}')
            return {}
    
    def create_product_transaction(self, product_id: int, user_id: int = None) -> bool:
        """Crea transacción de creación de producto"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return False
            
            transaction = Transaction(
                id=str(uuid.uuid4()),
                transaction_type=TransactionType.PRODUCT_CREATED,
                product_id=product_id,
                quantity=0,
                unit_price=product.unit_price,
                supplier_id=product.supplier_id,
                location="System",
                metadata={
                    'product_name': product.name,
                    'category': product.category,
                    'description': product.description
                },
                timestamp=datetime.utcnow(),
                user_id=user_id,
                signature=""
            )
            
            return self.add_transaction(transaction)
            
        except Exception as e:
            self.logger.error(f'Error creando transacción de producto: {str(e)}')
            return False
    
    def create_inventory_transaction(self, inventory_record: InventoryRecord, user_id: int = None) -> bool:
        """Crea transacción de movimiento de inventario"""
        try:
            transaction_type = TransactionType.INVENTORY_IN if inventory_record.movement_type == 'in' else TransactionType.INVENTORY_OUT
            
            if inventory_record.movement_type == 'adjustment':
                transaction_type = TransactionType.INVENTORY_ADJUSTMENT
            
            transaction = Transaction(
                id=str(uuid.uuid4()),
                transaction_type=transaction_type,
                product_id=inventory_record.product_id,
                quantity=inventory_record.quantity,
                unit_price=inventory_record.unit_price or 0.0,
                supplier_id=None,
                location=inventory_record.location or "Unknown",
                metadata={
                    'movement_type': inventory_record.movement_type,
                    'reference': inventory_record.reference,
                    'notes': inventory_record.notes
                },
                timestamp=inventory_record.created_at,
                user_id=user_id,
                signature=""
            )
            
            return self.add_transaction(transaction)
            
        except Exception as e:
            self.logger.error(f'Error creando transacción de inventario: {str(e)}')
            return False
    
    def create_sale_transaction(self, sale_record: SalesRecord, user_id: int = None) -> bool:
        """Crea transacción de venta"""
        try:
            transaction = Transaction(
                id=str(uuid.uuid4()),
                transaction_type=TransactionType.SALE_RECORDED,
                product_id=sale_record.product_id,
                quantity=sale_record.quantity_sold,
                unit_price=sale_record.unit_price,
                supplier_id=None,
                location="Point of Sale",
                metadata={
                    'customer_id': sale_record.customer_id,
                    'total_amount': sale_record.total_amount,
                    'sale_date': sale_record.sale_date.isoformat()
                },
                timestamp=sale_record.sale_date,
                user_id=user_id,
                signature=""
            )
            
            return self.add_transaction(transaction)
            
        except Exception as e:
            self.logger.error(f'Error creando transacción de venta: {str(e)}')
            return False
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict]:
        """Obtiene transacción por ID"""
        try:
            for block in self.chain:
                for tx_data in block.transactions:
                    if tx_data.get('id') == transaction_id:
                        return {
                            'block_index': block.index,
                            'block_hash': block.hash,
                            'timestamp': block.timestamp.isoformat(),
                            'transaction': tx_data
                        }
            
            return None
            
        except Exception as e:
            self.logger.error(f'Error obteniendo transacción por ID: {str(e)}')
            return None
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict]:
        """Obtiene transacciones recientes"""
        try:
            recent_transactions = []
            
            # Recorrer bloques desde el más reciente
            for block in reversed(self.chain):
                for tx_data in reversed(block.transactions):
                    recent_transactions.append({
                        'block_index': block.index,
                        'block_hash': block.hash,
                        'timestamp': block.timestamp.isoformat(),
                        'transaction': tx_data
                    })
                    
                    if len(recent_transactions) >= limit:
                        break
                
                if len(recent_transactions) >= limit:
                    break
            
            return recent_transactions
            
        except Exception as e:
            self.logger.error(f'Error obteniendo transacciones recientes: {str(e)}')
            return []
    
    def export_chain(self) -> Dict:
        """Exporta la cadena completa"""
        try:
            chain_data = {
                'chain_info': self.get_chain_info(),
                'blocks': []
            }
            
            for block in self.chain:
                block_data = {
                    'index': block.index,
                    'timestamp': block.timestamp.isoformat(),
                    'transactions': block.transactions,
                    'previous_hash': block.previous_hash,
                    'hash': block.hash,
                    'nonce': block.nonce,
                    'merkle_root': block.merkle_root
                }
                chain_data['blocks'].append(block_data)
            
            return chain_data
            
        except Exception as e:
            self.logger.error(f'Error exportando cadena: {str(e)}')
            return {}

# Instancia global del servicio de blockchain
blockchain_service = BlockchainService()
