"""
Blockchain-based Brand Verification and Traceability
Implements decentralized verification and immutable audit trails.
"""

import hashlib
import json
import time
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
import pickle
from pathlib import Path
import sqlite3
import threading
from queue import Queue
import requests
import asyncio
import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets

logger = logging.getLogger(__name__)

@dataclass
class BlockchainConfig:
    """Configuration for blockchain verification."""
    network: str = "testnet"  # mainnet, testnet, local
    block_time: int = 10  # seconds
    difficulty: int = 4  # number of leading zeros
    max_transactions_per_block: int = 100
    consensus_algorithm: str = "proof_of_work"  # proof_of_work, proof_of_stake
    encryption_key_size: int = 2048
    use_merkle_trees: bool = True
    enable_smart_contracts: bool = True

@dataclass
class BrandTransaction:
    """Brand analysis transaction for blockchain."""
    transaction_id: str
    timestamp: float
    brand_data_hash: str
    analysis_result_hash: str
    analyzer_id: str
    consistency_score: float
    verification_status: str  # pending, verified, rejected
    previous_hash: str
    nonce: int = 0
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return asdict(self)
    
    def calculate_hash(self) -> str:
        """Calculate hash of the transaction."""
        transaction_string = f"{self.transaction_id}{self.timestamp}{self.brand_data_hash}{self.analysis_result_hash}{self.analyzer_id}{self.consistency_score}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()

@dataclass
class BrandBlock:
    """Block containing brand analysis transactions."""
    block_id: str
    timestamp: float
    previous_hash: str
    merkle_root: str
    transactions: List[BrandTransaction]
    nonce: int = 0
    hash: str = ""
    
    def calculate_hash(self) -> str:
        """Calculate hash of the block."""
        block_string = f"{self.block_id}{self.timestamp}{self.previous_hash}{self.merkle_root}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> str:
        """Mine the block with given difficulty."""
        target = "0" * difficulty
        
        while True:
            self.nonce += 1
            self.hash = self.calculate_hash()
            
            if self.hash.startswith(target):
                break
        
        return self.hash

class MerkleTree:
    """Merkle tree implementation for transaction verification."""
    
    def __init__(self, transactions: List[BrandTransaction]):
        self.transactions = transactions
        self.tree = self._build_tree()
    
    def _build_tree(self) -> List[List[str]]:
        """Build Merkle tree from transactions."""
        if not self.transactions:
            return []
        
        # Start with transaction hashes
        current_level = [tx.calculate_hash() for tx in self.transactions]
        tree = [current_level]
        
        # Build tree levels
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else current_level[i]
                
                # Combine and hash
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            current_level = next_level
            tree.append(current_level)
        
        return tree
    
    def get_root(self) -> str:
        """Get Merkle root."""
        if not self.tree:
            return ""
        return self.tree[-1][0]
    
    def get_proof(self, transaction_hash: str) -> List[Tuple[str, str]]:
        """Get Merkle proof for a transaction."""
        if not self.tree:
            return []
        
        proof = []
        current_hash = transaction_hash
        
        # Find transaction in first level
        level_index = 0
        tx_index = -1
        for i, tx_hash in enumerate(self.tree[0]):
            if tx_hash == transaction_hash:
                tx_index = i
                break
        
        if tx_index == -1:
            return []
        
        # Build proof path
        current_index = tx_index
        for level in range(len(self.tree) - 1):
            sibling_index = current_index + 1 if current_index % 2 == 0 else current_index - 1
            
            if sibling_index < len(self.tree[level]):
                sibling_hash = self.tree[level][sibling_index]
                position = "right" if current_index % 2 == 0 else "left"
                proof.append((sibling_hash, position))
            
            current_index = current_index // 2
        
        return proof

class CryptographicSigner:
    """Cryptographic signing and verification."""
    
    def __init__(self, key_size: int = 2048):
        self.key_size = key_size
        self.private_key = None
        self.public_key = None
        self._generate_keys()
    
    def _generate_keys(self):
        """Generate RSA key pair."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def sign_data(self, data: str) -> str:
        """Sign data with private key."""
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, data: str, signature: str, public_key_pem: str) -> bool:
        """Verify signature with public key."""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )
            
            public_key.verify(
                base64.b64decode(signature.encode()),
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def get_public_key_pem(self) -> str:
        """Get public key in PEM format."""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()

class BrandBlockchain:
    """Blockchain implementation for brand verification."""
    
    def __init__(self, config: BlockchainConfig):
        self.config = config
        self.chain: List[BrandBlock] = []
        self.pending_transactions: List[BrandTransaction] = []
        self.analyzers: Dict[str, str] = {}  # analyzer_id -> public_key
        self.signer = CryptographicSigner(config.encryption_key_size)
        self.db_path = "brand_blockchain.db"
        self._init_database()
        self._create_genesis_block()
        self.mining_thread = None
        self.mining_active = False
        
    def _init_database(self):
        """Initialize SQLite database for blockchain storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                block_id TEXT PRIMARY KEY,
                timestamp REAL,
                previous_hash TEXT,
                merkle_root TEXT,
                nonce INTEGER,
                hash TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                block_id TEXT,
                timestamp REAL,
                brand_data_hash TEXT,
                analysis_result_hash TEXT,
                analyzer_id TEXT,
                consistency_score REAL,
                verification_status TEXT,
                previous_hash TEXT,
                nonce INTEGER,
                signature TEXT,
                FOREIGN KEY (block_id) REFERENCES blocks (block_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyzers (
                analyzer_id TEXT PRIMARY KEY,
                public_key TEXT,
                registration_timestamp REAL,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _create_genesis_block(self):
        """Create the genesis block."""
        if not self.chain:
            genesis_transaction = BrandTransaction(
                transaction_id="genesis",
                timestamp=time.time(),
                brand_data_hash="0",
                analysis_result_hash="0",
                analyzer_id="genesis",
                consistency_score=0.0,
                verification_status="verified",
                previous_hash="0"
            )
            
            genesis_block = BrandBlock(
                block_id="genesis",
                timestamp=time.time(),
                previous_hash="0",
                merkle_root=genesis_transaction.calculate_hash(),
                transactions=[genesis_transaction]
            )
            
            genesis_block.hash = genesis_block.calculate_hash()
            self.chain.append(genesis_block)
            self._save_block_to_db(genesis_block)
    
    def register_analyzer(self, analyzer_id: str, public_key: str) -> bool:
        """Register a new analyzer."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO analyzers 
                (analyzer_id, public_key, registration_timestamp, status)
                VALUES (?, ?, ?, ?)
            ''', (analyzer_id, public_key, time.time(), "active"))
            
            conn.commit()
            conn.close()
            
            self.analyzers[analyzer_id] = public_key
            return True
            
        except Exception as e:
            logger.error(f"Analyzer registration failed: {e}")
            return False
    
    def add_transaction(self, brand_data: Dict[str, Any], 
                       analysis_result: Dict[str, Any],
                       analyzer_id: str) -> str:
        """Add a new brand analysis transaction."""
        try:
            # Calculate hashes
            brand_data_hash = self._calculate_data_hash(brand_data)
            analysis_result_hash = self._calculate_data_hash(analysis_result)
            
            # Get previous transaction hash
            previous_hash = "0"
            if self.pending_transactions:
                previous_hash = self.pending_transactions[-1].calculate_hash()
            elif self.chain:
                previous_hash = self.chain[-1].transactions[-1].calculate_hash()
            
            # Create transaction
            transaction_id = self._generate_transaction_id()
            transaction = BrandTransaction(
                transaction_id=transaction_id,
                timestamp=time.time(),
                brand_data_hash=brand_data_hash,
                analysis_result_hash=analysis_result_hash,
                analyzer_id=analyzer_id,
                consistency_score=analysis_result.get('consistency_score', 0.0),
                verification_status="pending",
                previous_hash=previous_hash
            )
            
            # Sign transaction
            transaction_data = f"{transaction.transaction_id}{transaction.timestamp}{transaction.brand_data_hash}{transaction.analysis_result_hash}{transaction.analyzer_id}{transaction.consistency_score}"
            transaction.signature = self.signer.sign_data(transaction_data)
            
            # Add to pending transactions
            self.pending_transactions.append(transaction)
            
            # Start mining if not already active
            if not self.mining_active:
                self._start_mining()
            
            return transaction_id
            
        except Exception as e:
            logger.error(f"Transaction addition failed: {e}")
            return ""
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of data dictionary."""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        timestamp = str(int(time.time() * 1000))
        random_part = secrets.token_hex(8)
        return f"tx_{timestamp}_{random_part}"
    
    def _start_mining(self):
        """Start mining process."""
        if self.mining_active:
            return
        
        self.mining_active = True
        self.mining_thread = threading.Thread(target=self._mining_loop)
        self.mining_thread.daemon = True
        self.mining_thread.start()
    
    def _mining_loop(self):
        """Mining loop for creating new blocks."""
        while self.mining_active:
            if len(self.pending_transactions) >= self.config.max_transactions_per_block:
                self._mine_block()
            elif self.pending_transactions and time.time() - self.pending_transactions[0].timestamp > self.config.block_time:
                self._mine_block()
            else:
                time.sleep(1)
    
    def _mine_block(self):
        """Mine a new block with pending transactions."""
        if not self.pending_transactions:
            return
        
        try:
            # Take transactions for new block
            block_transactions = self.pending_transactions[:self.config.max_transactions_per_block]
            self.pending_transactions = self.pending_transactions[self.config.max_transactions_per_block:]
            
            # Create Merkle tree
            merkle_tree = MerkleTree(block_transactions)
            merkle_root = merkle_tree.get_root()
            
            # Get previous hash
            previous_hash = self.chain[-1].hash if self.chain else "0"
            
            # Create new block
            block_id = self._generate_block_id()
            new_block = BrandBlock(
                block_id=block_id,
                timestamp=time.time(),
                previous_hash=previous_hash,
                merkle_root=merkle_root,
                transactions=block_transactions
            )
            
            # Mine block
            new_block.mine_block(self.config.difficulty)
            
            # Add to chain
            self.chain.append(new_block)
            self._save_block_to_db(new_block)
            
            logger.info(f"Mined block {block_id} with {len(block_transactions)} transactions")
            
        except Exception as e:
            logger.error(f"Block mining failed: {e}")
    
    def _generate_block_id(self) -> str:
        """Generate unique block ID."""
        timestamp = str(int(time.time() * 1000))
        random_part = secrets.token_hex(8)
        return f"block_{timestamp}_{random_part}"
    
    def _save_block_to_db(self, block: BrandBlock):
        """Save block to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save block
            cursor.execute('''
                INSERT OR REPLACE INTO blocks 
                (block_id, timestamp, previous_hash, merkle_root, nonce, hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (block.block_id, block.timestamp, block.previous_hash, 
                  block.merkle_root, block.nonce, block.hash))
            
            # Save transactions
            for transaction in block.transactions:
                cursor.execute('''
                    INSERT OR REPLACE INTO transactions 
                    (transaction_id, block_id, timestamp, brand_data_hash, 
                     analysis_result_hash, analyzer_id, consistency_score, 
                     verification_status, previous_hash, nonce, signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (transaction.transaction_id, block.block_id, transaction.timestamp,
                      transaction.brand_data_hash, transaction.analysis_result_hash,
                      transaction.analyzer_id, transaction.consistency_score,
                      transaction.verification_status, transaction.previous_hash,
                      transaction.nonce, transaction.signature))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database save failed: {e}")
    
    def verify_transaction(self, transaction_id: str) -> bool:
        """Verify a transaction's integrity."""
        try:
            # Find transaction in blockchain
            transaction = self._find_transaction(transaction_id)
            if not transaction:
                return False
            
            # Verify signature
            if not self._verify_transaction_signature(transaction):
                return False
            
            # Verify hash
            if transaction.calculate_hash() != transaction.calculate_hash():
                return False
            
            # Verify Merkle proof
            if not self._verify_merkle_proof(transaction):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Transaction verification failed: {e}")
            return False
    
    def _find_transaction(self, transaction_id: str) -> Optional[BrandTransaction]:
        """Find transaction by ID in blockchain."""
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.transaction_id == transaction_id:
                    return transaction
        return None
    
    def _verify_transaction_signature(self, transaction: BrandTransaction) -> bool:
        """Verify transaction signature."""
        if transaction.analyzer_id not in self.analyzers:
            return False
        
        public_key = self.analyzers[transaction.analyzer_id]
        transaction_data = f"{transaction.transaction_id}{transaction.timestamp}{transaction.brand_data_hash}{transaction.analysis_result_hash}{transaction.analyzer_id}{transaction.consistency_score}"
        
        return self.signer.verify_signature(transaction_data, transaction.signature, public_key)
    
    def _verify_merkle_proof(self, transaction: BrandTransaction) -> bool:
        """Verify Merkle proof for transaction."""
        # Find block containing transaction
        for block in self.chain:
            if transaction in block.transactions:
                merkle_tree = MerkleTree(block.transactions)
                proof = merkle_tree.get_proof(transaction.calculate_hash())
                
                # Verify proof
                current_hash = transaction.calculate_hash()
                for sibling_hash, position in proof:
                    if position == "left":
                        combined = sibling_hash + current_hash
                    else:
                        combined = current_hash + sibling_hash
                    current_hash = hashlib.sha256(combined.encode()).hexdigest()
                
                return current_hash == block.merkle_root
        
        return False
    
    def get_chain_info(self) -> Dict[str, Any]:
        """Get blockchain information."""
        return {
            'chain_length': len(self.chain),
            'pending_transactions': len(self.pending_transactions),
            'registered_analyzers': len(self.analyzers),
            'last_block_hash': self.chain[-1].hash if self.chain else "0",
            'total_transactions': sum(len(block.transactions) for block in self.chain),
            'mining_active': self.mining_active
        }
    
    def get_transaction_history(self, analyzer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get transaction history."""
        transactions = []
        
        for block in self.chain:
            for transaction in block.transactions:
                if analyzer_id is None or transaction.analyzer_id == analyzer_id:
                    transactions.append({
                        'transaction_id': transaction.transaction_id,
                        'timestamp': transaction.timestamp,
                        'analyzer_id': transaction.analyzer_id,
                        'consistency_score': transaction.consistency_score,
                        'verification_status': transaction.verification_status,
                        'block_id': block.block_id
                    })
        
        return sorted(transactions, key=lambda x: x['timestamp'], reverse=True)
    
    def stop_mining(self):
        """Stop mining process."""
        self.mining_active = False
        if self.mining_thread:
            self.mining_thread.join()

class BrandVerificationService:
    """Service for brand verification and audit trails."""
    
    def __init__(self, config: BlockchainConfig):
        self.config = config
        self.blockchain = BrandBlockchain(config)
        self.analyzer_id = self._generate_analyzer_id()
        self._register_analyzer()
    
    def _generate_analyzer_id(self) -> str:
        """Generate unique analyzer ID."""
        timestamp = str(int(time.time() * 1000))
        random_part = secrets.token_hex(8)
        return f"analyzer_{timestamp}_{random_part}"
    
    def _register_analyzer(self):
        """Register this analyzer with the blockchain."""
        public_key = self.blockchain.signer.get_public_key_pem()
        self.blockchain.register_analyzer(self.analyzer_id, public_key)
    
    def verify_brand_analysis(self, brand_data: Dict[str, Any], 
                            analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify brand analysis and add to blockchain."""
        try:
            # Add transaction to blockchain
            transaction_id = self.blockchain.add_transaction(
                brand_data, analysis_result, self.analyzer_id
            )
            
            if not transaction_id:
                return {
                    'success': False,
                    'error': 'Failed to add transaction to blockchain'
                }
            
            # Wait for transaction to be mined
            max_wait_time = 60  # seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                if self.blockchain.verify_transaction(transaction_id):
                    break
                time.sleep(1)
            
            # Get verification status
            verification_status = self.blockchain.verify_transaction(transaction_id)
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'verification_status': 'verified' if verification_status else 'pending',
                'blockchain_info': self.blockchain.get_chain_info(),
                'analyzer_id': self.analyzer_id
            }
            
        except Exception as e:
            logger.error(f"Brand verification failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_audit_trail(self, brand_data_hash: str) -> List[Dict[str, Any]]:
        """Get audit trail for specific brand data."""
        audit_trail = []
        
        for block in self.blockchain.chain:
            for transaction in block.transactions:
                if transaction.brand_data_hash == brand_data_hash:
                    audit_trail.append({
                        'transaction_id': transaction.transaction_id,
                        'timestamp': transaction.timestamp,
                        'analyzer_id': transaction.analyzer_id,
                        'consistency_score': transaction.consistency_score,
                        'verification_status': transaction.verification_status,
                        'block_id': block.block_id,
                        'block_timestamp': block.timestamp
                    })
        
        return sorted(audit_trail, key=lambda x: x['timestamp'])
    
    def get_analyzer_performance(self, analyzer_id: str) -> Dict[str, Any]:
        """Get performance metrics for an analyzer."""
        transactions = self.blockchain.get_transaction_history(analyzer_id)
        
        if not transactions:
            return {
                'analyzer_id': analyzer_id,
                'total_analyses': 0,
                'average_consistency': 0.0,
                'verification_rate': 0.0
            }
        
        total_analyses = len(transactions)
        verified_analyses = sum(1 for t in transactions if t['verification_status'] == 'verified')
        average_consistency = sum(t['consistency_score'] for t in transactions) / total_analyses
        verification_rate = verified_analyses / total_analyses
        
        return {
            'analyzer_id': analyzer_id,
            'total_analyses': total_analyses,
            'verified_analyses': verified_analyses,
            'average_consistency': average_consistency,
            'verification_rate': verification_rate,
            'first_analysis': min(t['timestamp'] for t in transactions),
            'last_analysis': max(t['timestamp'] for t in transactions)
        }

def create_brand_verification_service(config: BlockchainConfig) -> BrandVerificationService:
    """Create a brand verification service with given configuration."""
    return BrandVerificationService(config)










