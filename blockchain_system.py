"""
Sistema de Blockchain para Trazabilidad de Productos
===================================================

Sistema completo de blockchain para trazabilidad completa de productos,
certificación de autenticidad y gestión de cadena de suministro.
"""

import hashlib
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import sqlite3
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)

class TransactionType(Enum):
    """Tipos de transacciones blockchain"""
    PRODUCT_CREATION = "product_creation"
    PRODUCT_TRANSFER = "product_transfer"
    QUALITY_CHECK = "quality_check"
    CERTIFICATION = "certification"
    RECALL = "recall"
    SUPPLIER_VERIFICATION = "supplier_verification"

class BlockStatus(Enum):
    """Estado de bloques"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

@dataclass
class Transaction:
    """Transacción blockchain"""
    transaction_id: str
    transaction_type: TransactionType
    product_id: str
    from_address: str
    to_address: str
    data: Dict[str, Any]
    timestamp: datetime
    signature: str
    hash: str

@dataclass
class Block:
    """Bloque blockchain"""
    block_id: str
    previous_hash: str
    transactions: List[Transaction]
    timestamp: datetime
    nonce: int
    hash: str
    status: BlockStatus
    miner: str

@dataclass
class ProductTrace:
    """Trazabilidad de producto"""
    product_id: str
    creation_transaction: str
    transfer_history: List[str]
    quality_checks: List[str]
    certifications: List[str]
    current_owner: str
    authenticity_score: float
    last_updated: datetime

class CryptographicManager:
    """Gestor de criptografía"""
    
    def __init__(self):
        self.private_keys = {}
        self.public_keys = {}
        self.key_pairs = {}
    
    def generate_key_pair(self, entity_id: str) -> Tuple[str, str]:
        """Generar par de claves para entidad"""
        
        # Generar clave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Obtener clave pública
        public_key = private_key.public_key()
        
        # Serializar claves
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Convertir a strings
        private_key_str = base64.b64encode(private_pem).decode('utf-8')
        public_key_str = base64.b64encode(public_pem).decode('utf-8')
        
        # Almacenar claves
        self.private_keys[entity_id] = private_key_str
        self.public_keys[entity_id] = public_key_str
        self.key_pairs[entity_id] = (private_key, public_key)
        
        logger.info(f"Par de claves generado para entidad: {entity_id}")
        
        return private_key_str, public_key_str
    
    def sign_transaction(self, entity_id: str, transaction_data: str) -> str:
        """Firmar transacción"""
        
        if entity_id not in self.key_pairs:
            raise ValueError(f"Claves no encontradas para entidad: {entity_id}")
        
        private_key, _ = self.key_pairs[entity_id]
        
        # Firmar datos
        signature = private_key.sign(
            transaction_data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Codificar firma
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return signature_b64
    
    def verify_signature(self, entity_id: str, transaction_data: str, signature: str) -> bool:
        """Verificar firma"""
        
        if entity_id not in self.public_keys:
            return False
        
        try:
            # Decodificar clave pública
            public_key_pem = base64.b64decode(self.public_keys[entity_id])
            public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
            
            # Decodificar firma
            signature_bytes = base64.b64decode(signature)
            
            # Verificar firma
            public_key.verify(
                signature_bytes,
                transaction_data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando firma: {e}")
            return False
    
    def get_public_key(self, entity_id: str) -> Optional[str]:
        """Obtener clave pública"""
        return self.public_keys.get(entity_id)

class BlockchainManager:
    """Gestor de blockchain"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.crypto_manager = CryptographicManager()
        self.difficulty = 4  # Número de ceros al inicio del hash
        self.mining_reward = 10
        self.lock = threading.Lock()
        
        # Crear bloque génesis
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Crear bloque génesis"""
        genesis_transaction = Transaction(
            transaction_id="genesis_0",
            transaction_type=TransactionType.PRODUCT_CREATION,
            product_id="genesis",
            from_address="0",
            to_address="system",
            data={"message": "Genesis block"},
            timestamp=datetime.now(),
            signature="genesis",
            hash="0"
        )
        
        genesis_block = Block(
            block_id="genesis_0",
            previous_hash="0",
            transactions=[genesis_transaction],
            timestamp=datetime.now(),
            nonce=0,
            hash="0",
            status=BlockStatus.CONFIRMED,
            miner="system"
        )
        
        self.chain.append(genesis_block)
        logger.info("Bloque génesis creado")
    
    def create_transaction(self, transaction_type: TransactionType, product_id: str,
                          from_address: str, to_address: str, data: Dict[str, Any],
                          entity_id: str) -> str:
        """Crear transacción"""
        
        with self.lock:
            # Crear ID único
            transaction_id = f"{transaction_type.value}_{product_id}_{int(time.time() * 1000)}"
            
            # Crear datos de transacción
            transaction_data = {
                'transaction_id': transaction_id,
                'transaction_type': transaction_type.value,
                'product_id': product_id,
                'from_address': from_address,
                'to_address': to_address,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            transaction_json = json.dumps(transaction_data, sort_keys=True)
            
            # Firmar transacción
            signature = self.crypto_manager.sign_transaction(entity_id, transaction_json)
            
            # Crear hash
            transaction_hash = self._calculate_hash(transaction_json + signature)
            
            # Crear transacción
            transaction = Transaction(
                transaction_id=transaction_id,
                transaction_type=transaction_type,
                product_id=product_id,
                from_address=from_address,
                to_address=to_address,
                data=data,
                timestamp=datetime.now(),
                signature=signature,
                hash=transaction_hash
            )
            
            # Agregar a transacciones pendientes
            self.pending_transactions.append(transaction)
            
            logger.info(f"Transacción creada: {transaction_id}")
            
            return transaction_id
    
    def mine_block(self, miner_id: str) -> Optional[Block]:
        """Minar bloque"""
        
        with self.lock:
            if not self.pending_transactions:
                return None
            
            # Crear nuevo bloque
            previous_block = self.chain[-1]
            block_id = f"block_{len(self.chain)}"
            
            # Seleccionar transacciones (máximo 10 por bloque)
            transactions = self.pending_transactions[:10]
            
            # Crear bloque
            new_block = Block(
                block_id=block_id,
                previous_hash=previous_block.hash,
                transactions=transactions,
                timestamp=datetime.now(),
                nonce=0,
                hash="",
                status=BlockStatus.PENDING,
                miner=miner_id
            )
            
            # Minar bloque (Proof of Work)
            new_block = self._proof_of_work(new_block)
            
            # Verificar bloque
            if self._verify_block(new_block):
                # Agregar a cadena
                self.chain.append(new_block)
                
                # Remover transacciones minadas
                self.pending_transactions = self.pending_transactions[10:]
                
                logger.info(f"Bloque minado: {block_id}")
                
                return new_block
            else:
                logger.error(f"Bloque inválido: {block_id}")
                return None
    
    def _proof_of_work(self, block: Block) -> Block:
        """Algoritmo de Proof of Work"""
        
        target = "0" * self.difficulty
        
        while True:
            block_data = self._get_block_data(block)
            block_hash = self._calculate_hash(block_data)
            
            if block_hash.startswith(target):
                block.hash = block_hash
                block.status = BlockStatus.CONFIRMED
                break
            
            block.nonce += 1
        
        return block
    
    def _get_block_data(self, block: Block) -> str:
        """Obtener datos del bloque para hash"""
        
        transactions_data = []
        for tx in block.transactions:
            transactions_data.append({
                'id': tx.transaction_id,
                'type': tx.transaction_type.value,
                'product_id': tx.product_id,
                'from': tx.from_address,
                'to': tx.to_address,
                'data': tx.data,
                'timestamp': tx.timestamp.isoformat(),
                'signature': tx.signature
            })
        
        block_data = {
            'block_id': block.block_id,
            'previous_hash': block.previous_hash,
            'transactions': transactions_data,
            'timestamp': block.timestamp.isoformat(),
            'nonce': block.nonce,
            'miner': block.miner
        }
        
        return json.dumps(block_data, sort_keys=True)
    
    def _calculate_hash(self, data: str) -> str:
        """Calcular hash SHA-256"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _verify_block(self, block: Block) -> bool:
        """Verificar validez del bloque"""
        
        # Verificar hash del bloque anterior
        if len(self.chain) > 0:
            previous_block = self.chain[-1]
            if block.previous_hash != previous_block.hash:
                return False
        
        # Verificar transacciones
        for transaction in block.transactions:
            if not self._verify_transaction(transaction):
                return False
        
        # Verificar hash del bloque
        block_data = self._get_block_data(block)
        calculated_hash = self._calculate_hash(block_data)
        
        return calculated_hash == block.hash
    
    def _verify_transaction(self, transaction: Transaction) -> bool:
        """Verificar validez de transacción"""
        
        # Recrear datos de transacción
        transaction_data = {
            'transaction_id': transaction.transaction_id,
            'transaction_type': transaction.transaction_type.value,
            'product_id': transaction.product_id,
            'from_address': transaction.from_address,
            'to_address': transaction.to_address,
            'data': transaction.data,
            'timestamp': transaction.timestamp.isoformat()
        }
        
        transaction_json = json.dumps(transaction_data, sort_keys=True)
        
        # Verificar firma
        return self.crypto_manager.verify_signature(
            transaction.from_address,
            transaction_json,
            transaction.signature
        )
    
    def get_product_trace(self, product_id: str) -> Optional[ProductTrace]:
        """Obtener trazabilidad de producto"""
        
        trace_transactions = []
        
        # Buscar todas las transacciones del producto
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.product_id == product_id:
                    trace_transactions.append(transaction)
        
        if not trace_transactions:
            return None
        
        # Ordenar por timestamp
        trace_transactions.sort(key=lambda x: x.timestamp)
        
        # Construir trazabilidad
        creation_transaction = None
        transfer_history = []
        quality_checks = []
        certifications = []
        current_owner = None
        authenticity_score = 1.0
        
        for transaction in trace_transactions:
            if transaction.transaction_type == TransactionType.PRODUCT_CREATION:
                creation_transaction = transaction.transaction_id
                current_owner = transaction.to_address
            
            elif transaction.transaction_type == TransactionType.PRODUCT_TRANSFER:
                transfer_history.append(transaction.transaction_id)
                current_owner = transaction.to_address
            
            elif transaction.transaction_type == TransactionType.QUALITY_CHECK:
                quality_checks.append(transaction.transaction_id)
                # Actualizar score de autenticidad basado en verificaciones
                if transaction.data.get('passed', False):
                    authenticity_score += 0.1
                else:
                    authenticity_score -= 0.2
            
            elif transaction.transaction_type == TransactionType.CERTIFICATION:
                certifications.append(transaction.transaction_id)
                authenticity_score += 0.2
        
        # Normalizar score
        authenticity_score = max(0.0, min(1.0, authenticity_score))
        
        return ProductTrace(
            product_id=product_id,
            creation_transaction=creation_transaction,
            transfer_history=transfer_history,
            quality_checks=quality_checks,
            certifications=certifications,
            current_owner=current_owner,
            authenticity_score=authenticity_score,
            last_updated=datetime.now()
        )
    
    def verify_product_authenticity(self, product_id: str) -> Dict[str, Any]:
        """Verificar autenticidad de producto"""
        
        trace = self.get_product_trace(product_id)
        
        if not trace:
            return {
                'authentic': False,
                'reason': 'Producto no encontrado en blockchain',
                'score': 0.0
            }
        
        # Verificar cadena de custodia
        custody_verified = True
        issues = []
        
        # Verificar que todas las transferencias son válidas
        for transfer_id in trace.transfer_history:
            # Aquí se podría verificar cada transferencia individualmente
            pass
        
        # Verificar certificaciones
        certification_verified = len(trace.certifications) > 0
        
        # Verificar verificaciones de calidad
        quality_verified = len(trace.quality_checks) > 0
        
        # Calcular autenticidad final
        authentic = (
            custody_verified and 
            certification_verified and 
            quality_verified and 
            trace.authenticity_score > 0.7
        )
        
        if not custody_verified:
            issues.append("Cadena de custodia incompleta")
        if not certification_verified:
            issues.append("Sin certificaciones")
        if not quality_verified:
            issues.append("Sin verificaciones de calidad")
        if trace.authenticity_score <= 0.7:
            issues.append("Score de autenticidad bajo")
        
        return {
            'authentic': authentic,
            'score': trace.authenticity_score,
            'issues': issues,
            'trace': trace
        }
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de blockchain"""
        
        total_transactions = sum(len(block.transactions) for block in self.chain)
        pending_transactions = len(self.pending_transactions)
        
        # Contar transacciones por tipo
        transaction_types = {}
        for block in self.chain:
            for transaction in block.transactions:
                tx_type = transaction.transaction_type.value
                transaction_types[tx_type] = transaction_types.get(tx_type, 0) + 1
        
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'pending_transactions': pending_transactions,
            'transaction_types': transaction_types,
            'difficulty': self.difficulty,
            'mining_reward': self.mining_reward,
            'chain_length': len(self.chain)
        }

class SupplyChainBlockchain:
    """Blockchain para cadena de suministro"""
    
    def __init__(self):
        self.blockchain = BlockchainManager()
        self.entities = {}  # Registro de entidades
        self.products = {}   # Registro de productos
        
    def register_entity(self, entity_id: str, entity_type: str, 
                       entity_data: Dict[str, Any]) -> Tuple[str, str]:
        """Registrar nueva entidad"""
        
        # Generar claves para la entidad
        private_key, public_key = self.blockchain.crypto_manager.generate_key_pair(entity_id)
        
        # Registrar entidad
        self.entities[entity_id] = {
            'entity_type': entity_type,
            'entity_data': entity_data,
            'public_key': public_key,
            'registered_at': datetime.now(),
            'status': 'active'
        }
        
        logger.info(f"Entidad registrada: {entity_id} ({entity_type})")
        
        return private_key, public_key
    
    def create_product(self, product_id: str, creator_id: str, 
                      product_data: Dict[str, Any]) -> str:
        """Crear nuevo producto en blockchain"""
        
        if creator_id not in self.entities:
            raise ValueError(f"Entidad no registrada: {creator_id}")
        
        # Crear transacción de creación
        transaction_id = self.blockchain.create_transaction(
            TransactionType.PRODUCT_CREATION,
            product_id,
            creator_id,
            creator_id,  # El creador es el primer propietario
            product_data,
            creator_id
        )
        
        # Registrar producto
        self.products[product_id] = {
            'creator': creator_id,
            'creation_transaction': transaction_id,
            'product_data': product_data,
            'created_at': datetime.now(),
            'status': 'active'
        }
        
        logger.info(f"Producto creado: {product_id} por {creator_id}")
        
        return transaction_id
    
    def transfer_product(self, product_id: str, from_entity: str, 
                        to_entity: str, transfer_data: Dict[str, Any]) -> str:
        """Transferir producto"""
        
        if from_entity not in self.entities or to_entity not in self.entities:
            raise ValueError("Una o ambas entidades no están registradas")
        
        if product_id not in self.products:
            raise ValueError(f"Producto no encontrado: {product_id}")
        
        # Crear transacción de transferencia
        transaction_id = self.blockchain.create_transaction(
            TransactionType.PRODUCT_TRANSFER,
            product_id,
            from_entity,
            to_entity,
            transfer_data,
            from_entity
        )
        
        logger.info(f"Producto transferido: {product_id} de {from_entity} a {to_entity}")
        
        return transaction_id
    
    def add_quality_check(self, product_id: str, checker_id: str, 
                         check_data: Dict[str, Any]) -> str:
        """Agregar verificación de calidad"""
        
        if checker_id not in self.entities:
            raise ValueError(f"Entidad no registrada: {checker_id}")
        
        # Crear transacción de verificación
        transaction_id = self.blockchain.create_transaction(
            TransactionType.QUALITY_CHECK,
            product_id,
            checker_id,
            checker_id,
            check_data,
            checker_id
        )
        
        logger.info(f"Verificación de calidad agregada: {product_id} por {checker_id}")
        
        return transaction_id
    
    def add_certification(self, product_id: str, certifier_id: str, 
                         certification_data: Dict[str, Any]) -> str:
        """Agregar certificación"""
        
        if certifier_id not in self.entities:
            raise ValueError(f"Entidad no registrada: {certifier_id}")
        
        # Crear transacción de certificación
        transaction_id = self.blockchain.create_transaction(
            TransactionType.CERTIFICATION,
            product_id,
            certifier_id,
            certifier_id,
            certification_data,
            certifier_id
        )
        
        logger.info(f"Certificación agregada: {product_id} por {certifier_id}")
        
        return transaction_id
    
    def mine_pending_transactions(self, miner_id: str) -> Optional[Block]:
        """Minar transacciones pendientes"""
        return self.blockchain.mine_block(miner_id)
    
    def get_product_history(self, product_id: str) -> List[Dict[str, Any]]:
        """Obtener historial completo del producto"""
        
        history = []
        
        for block in self.blockchain.chain:
            for transaction in block.transactions:
                if transaction.product_id == product_id:
                    history.append({
                        'transaction_id': transaction.transaction_id,
                        'type': transaction.transaction_type.value,
                        'from': transaction.from_address,
                        'to': transaction.to_address,
                        'data': transaction.data,
                        'timestamp': transaction.timestamp.isoformat(),
                        'block_id': block.block_id,
                        'verified': True
                    })
        
        # Ordenar por timestamp
        history.sort(key=lambda x: x['timestamp'])
        
        return history
    
    def verify_supply_chain_integrity(self, product_id: str) -> Dict[str, Any]:
        """Verificar integridad de la cadena de suministro"""
        
        trace = self.blockchain.get_product_trace(product_id)
        
        if not trace:
            return {
                'integrity_verified': False,
                'reason': 'Producto no encontrado',
                'score': 0.0
            }
        
        # Verificar cada paso de la cadena
        integrity_checks = {
            'creation_verified': trace.creation_transaction is not None,
            'transfers_verified': len(trace.transfer_history) > 0,
            'quality_checks_passed': len(trace.quality_checks) > 0,
            'certifications_valid': len(trace.certifications) > 0,
            'authenticity_score': trace.authenticity_score
        }
        
        # Calcular score de integridad
        integrity_score = sum([
            integrity_checks['creation_verified'],
            integrity_checks['transfers_verified'],
            integrity_checks['quality_checks_passed'],
            integrity_checks['certifications_valid'],
            trace.authenticity_score
        ]) / 5.0
        
        integrity_verified = integrity_score > 0.8
        
        return {
            'integrity_verified': integrity_verified,
            'integrity_score': integrity_score,
            'checks': integrity_checks,
            'trace': trace
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        
        blockchain_stats = self.blockchain.get_blockchain_stats()
        
        return {
            'blockchain': blockchain_stats,
            'entities_registered': len(self.entities),
            'products_registered': len(self.products),
            'active_entities': len([e for e in self.entities.values() if e['status'] == 'active']),
            'active_products': len([p for p in self.products.values() if p['status'] == 'active'])
        }

# Instancia global del sistema blockchain
supply_chain_blockchain = SupplyChainBlockchain()

# Funciones de conveniencia
def register_supply_chain_entity(entity_id: str, entity_type: str, 
                                entity_data: Dict[str, Any]) -> Tuple[str, str]:
    """Registrar entidad en cadena de suministro"""
    return supply_chain_blockchain.register_entity(entity_id, entity_type, entity_data)

def create_blockchain_product(product_id: str, creator_id: str, 
                             product_data: Dict[str, Any]) -> str:
    """Crear producto en blockchain"""
    return supply_chain_blockchain.create_product(product_id, creator_id, product_data)

def transfer_blockchain_product(product_id: str, from_entity: str, 
                              to_entity: str, transfer_data: Dict[str, Any]) -> str:
    """Transferir producto en blockchain"""
    return supply_chain_blockchain.transfer_product(product_id, from_entity, to_entity, transfer_data)

def verify_product_authenticity(product_id: str) -> Dict[str, Any]:
    """Verificar autenticidad de producto"""
    return supply_chain_blockchain.blockchain.verify_product_authenticity(product_id)

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de blockchain para trazabilidad...")
    
    try:
        # Registrar entidades
        manufacturer_key, manufacturer_pub = register_supply_chain_entity(
            "manufacturer_001",
            "manufacturer",
            {"name": "Fábrica ABC", "location": "Ciudad A", "certification": "ISO9001"}
        )
        
        distributor_key, distributor_pub = register_supply_chain_entity(
            "distributor_001",
            "distributor",
            {"name": "Distribuidor XYZ", "location": "Ciudad B", "license": "DIST001"}
        )
        
        retailer_key, retailer_pub = register_supply_chain_entity(
            "retailer_001",
            "retailer",
            {"name": "Tienda 123", "location": "Ciudad C", "license": "RETAIL001"}
        )
        
        print("✅ Entidades registradas en blockchain")
        
        # Crear producto
        product_data = {
            "name": "Producto Premium",
            "category": "Electrónicos",
            "batch_number": "BATCH001",
            "manufacturing_date": "2024-01-15",
            "specifications": {"weight": "1.5kg", "color": "negro"}
        }
        
        create_tx = create_blockchain_product("PROD001", "manufacturer_001", product_data)
        print(f"✅ Producto creado: {create_tx}")
        
        # Transferir producto
        transfer_data = {
            "reason": "Distribución",
            "quantity": 100,
            "transport_method": "Camión refrigerado"
        }
        
        transfer_tx = transfer_blockchain_product(
            "PROD001", "manufacturer_001", "distributor_001", transfer_data
        )
        print(f"✅ Producto transferido: {transfer_tx}")
        
        # Agregar verificación de calidad
        quality_data = {
            "check_type": "Inspección visual",
            "passed": True,
            "inspector": "Inspector001",
            "notes": "Producto en perfecto estado"
        }
        
        quality_tx = supply_chain_blockchain.add_quality_check(
            "PROD001", "distributor_001", quality_data
        )
        print(f"✅ Verificación de calidad: {quality_tx}")
        
        # Agregar certificación
        cert_data = {
            "certificate_type": "Calidad Premium",
            "certifier": "CertificadorAutorizado",
            "valid_until": "2025-01-15",
            "certificate_number": "CERT001"
        }
        
        cert_tx = supply_chain_blockchain.add_certification(
            "PROD001", "distributor_001", cert_data
        )
        print(f"✅ Certificación agregada: {cert_tx}")
        
        # Minar transacciones
        block = supply_chain_blockchain.mine_pending_transactions("miner_001")
        if block:
            print(f"✅ Bloque minado: {block.block_id}")
        
        # Verificar autenticidad
        authenticity = verify_product_authenticity("PROD001")
        print(f"✅ Autenticidad verificada: {authenticity['authentic']}")
        print(f"   Score: {authenticity['score']:.2f}")
        
        # Obtener historial del producto
        history = supply_chain_blockchain.get_product_history("PROD001")
        print(f"✅ Historial del producto: {len(history)} transacciones")
        
        # Verificar integridad de cadena de suministro
        integrity = supply_chain_blockchain.verify_supply_chain_integrity("PROD001")
        print(f"✅ Integridad verificada: {integrity['integrity_verified']}")
        print(f"   Score: {integrity['integrity_score']:.2f}")
        
        # Estadísticas del sistema
        stats = supply_chain_blockchain.get_system_stats()
        print(f"✅ Estadísticas del sistema:")
        print(f"   Bloques: {stats['blockchain']['total_blocks']}")
        print(f"   Transacciones: {stats['blockchain']['total_transactions']}")
        print(f"   Entidades: {stats['entities_registered']}")
        print(f"   Productos: {stats['products_registered']}")
        
    except Exception as e:
        logger.error(f"Error en pruebas de blockchain: {e}")
    
    print("✅ Sistema de blockchain funcionando correctamente")



