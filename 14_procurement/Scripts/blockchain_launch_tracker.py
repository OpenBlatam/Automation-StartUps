"""
Blockchain Launch Tracker
Sistema de blockchain para trazabilidad y transparencia de lanzamientos
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

from enhanced_launch_planner import EnhancedLaunchPlanner
from ai_powered_insights import AIPoweredInsightsEngine
from quantum_launch_optimizer import QuantumLaunchOptimizer

@dataclass
class Block:
    """Bloque de la blockchain"""
    index: int
    timestamp: float
    data: Dict[str, Any]
    previous_hash: str
    hash: str
    nonce: int
    merkle_root: str
    difficulty: int

@dataclass
class Transaction:
    """Transacción en la blockchain"""
    id: str
    timestamp: float
    sender: str
    receiver: str
    transaction_type: str
    data: Dict[str, Any]
    signature: str
    amount: float = 0.0

@dataclass
class SmartContract:
    """Contrato inteligente"""
    address: str
    name: str
    version: str
    functions: List[str]
    state: Dict[str, Any]
    deployed_at: float
    gas_limit: int

@dataclass
class LaunchToken:
    """Token de lanzamiento"""
    symbol: str
    name: str
    total_supply: int
    decimals: int
    owner: str
    contract_address: str
    launch_date: float
    price: float

class BlockchainLaunchTracker:
    """Tracker de lanzamientos basado en blockchain"""
    
    def __init__(self):
        self.enhanced_planner = EnhancedLaunchPlanner()
        self.insights_engine = AIPoweredInsightsEngine()
        self.quantum_optimizer = QuantumLaunchOptimizer()
        
        # Blockchain parameters
        self.chain = []
        self.difficulty = 4
        self.mining_reward = 50
        self.pending_transactions = []
        self.smart_contracts = {}
        self.tokens = {}
        
        # Initialize blockchain
        self._create_genesis_block()
        
    def _create_genesis_block(self):
        """Crear bloque génesis"""
        genesis_data = {
            "message": "Genesis block for Launch Planning Blockchain",
            "timestamp": time.time(),
            "launch_system_version": "2.0.0",
            "initial_supply": 1000000
        }
        
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data=genesis_data,
            previous_hash="0",
            hash="",
            nonce=0,
            merkle_root=self._calculate_merkle_root([genesis_data]),
            difficulty=self.difficulty
        )
        
        genesis_block.hash = self._calculate_hash(genesis_block)
        self.chain.append(genesis_block)
        
    def _calculate_hash(self, block: Block) -> str:
        """Calcular hash del bloque"""
        block_string = f"{block.index}{block.timestamp}{json.dumps(block.data, sort_keys=True)}{block.previous_hash}{block.nonce}{block.merkle_root}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _calculate_merkle_root(self, transactions: List[Dict[str, Any]]) -> str:
        """Calcular raíz de Merkle"""
        if not transactions:
            return "0"
        
        if len(transactions) == 1:
            return hashlib.sha256(json.dumps(transactions[0], sort_keys=True).encode()).hexdigest()
        
        # Simular árbol de Merkle
        hashes = [hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest() for tx in transactions]
        
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i + 1] if i + 1 < len(hashes) else hashes[i]
                combined = left + right
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = next_level
        
        return hashes[0]
    
    def _proof_of_work(self, block: Block) -> int:
        """Algoritmo de Proof of Work"""
        target = "0" * self.difficulty
        nonce = 0
        
        while True:
            block.nonce = nonce
            hash_result = self._calculate_hash(block)
            
            if hash_result.startswith(target):
                return nonce
            
            nonce += 1
    
    def create_transaction(self, sender: str, receiver: str, transaction_type: str, 
                          data: Dict[str, Any], amount: float = 0.0) -> Transaction:
        """Crear transacción"""
        transaction = Transaction(
            id=hashlib.sha256(f"{sender}{receiver}{time.time()}".encode()).hexdigest()[:16],
            timestamp=time.time(),
            sender=sender,
            receiver=receiver,
            transaction_type=transaction_type,
            data=data,
            signature=self._sign_transaction(sender, data),
            amount=amount
        )
        
        self.pending_transactions.append(transaction)
        return transaction
    
    def _sign_transaction(self, sender: str, data: Dict[str, Any]) -> str:
        """Firmar transacción (simulado)"""
        message = f"{sender}{json.dumps(data, sort_keys=True)}{time.time()}"
        return hashlib.sha256(message.encode()).hexdigest()
    
    def mine_block(self, miner_address: str) -> Block:
        """Minar nuevo bloque"""
        if not self.pending_transactions:
            return None
        
        # Crear transacción de recompensa
        reward_transaction = Transaction(
            id=f"reward_{int(time.time())}",
            timestamp=time.time(),
            sender="system",
            receiver=miner_address,
            transaction_type="mining_reward",
            data={"reward": self.mining_reward},
            signature="system_signature",
            amount=self.mining_reward
        )
        
        # Agregar transacciones al bloque
        block_transactions = self.pending_transactions.copy()
        block_transactions.append(reward_transaction)
        
        # Crear nuevo bloque
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data={
                "transactions": [asdict(tx) for tx in block_transactions],
                "miner": miner_address,
                "block_reward": self.mining_reward
            },
            previous_hash=previous_block.hash,
            hash="",
            nonce=0,
            merkle_root=self._calculate_merkle_root([asdict(tx) for tx in block_transactions]),
            difficulty=self.difficulty
        )
        
        # Proof of Work
        new_block.nonce = self._proof_of_work(new_block)
        new_block.hash = self._calculate_hash(new_block)
        
        # Agregar a la cadena
        self.chain.append(new_block)
        
        # Limpiar transacciones pendientes
        self.pending_transactions = []
        
        return new_block
    
    def deploy_smart_contract(self, name: str, functions: List[str], 
                             initial_state: Dict[str, Any]) -> SmartContract:
        """Desplegar contrato inteligente"""
        contract_address = hashlib.sha256(f"{name}{time.time()}".encode()).hexdigest()[:20]
        
        contract = SmartContract(
            address=contract_address,
            name=name,
            version="1.0.0",
            functions=functions,
            state=initial_state,
            deployed_at=time.time(),
            gas_limit=1000000
        )
        
        self.smart_contracts[contract_address] = contract
        
        # Crear transacción de despliegue
        deploy_transaction = self.create_transaction(
            sender="deployer",
            receiver=contract_address,
            transaction_type="contract_deploy",
            data={
                "contract_name": name,
                "functions": functions,
                "initial_state": initial_state
            }
        )
        
        return contract
    
    def create_launch_token(self, symbol: str, name: str, total_supply: int, 
                           owner: str, price: float) -> LaunchToken:
        """Crear token de lanzamiento"""
        contract_address = hashlib.sha256(f"{symbol}{time.time()}".encode()).hexdigest()[:20]
        
        token = LaunchToken(
            symbol=symbol,
            name=name,
            total_supply=total_supply,
            decimals=18,
            owner=owner,
            contract_address=contract_address,
            launch_date=time.time(),
            price=price
        )
        
        self.tokens[symbol] = token
        
        # Crear transacción de creación de token
        token_transaction = self.create_transaction(
            sender=owner,
            receiver=contract_address,
            transaction_type="token_create",
            data={
                "symbol": symbol,
                "name": name,
                "total_supply": total_supply,
                "price": price
            }
        )
        
        return token
    
    def record_launch_plan(self, plan_data: Dict[str, Any], owner: str) -> str:
        """Registrar plan de lanzamiento en blockchain"""
        # Crear transacción de registro
        transaction = self.create_transaction(
            sender=owner,
            receiver="launch_registry",
            transaction_type="launch_plan_record",
            data={
                "plan_id": plan_data.get("id", f"plan_{int(time.time())}"),
                "plan_data": plan_data,
                "timestamp": time.time(),
                "hash": hashlib.sha256(json.dumps(plan_data, sort_keys=True).encode()).hexdigest()
            }
        )
        
        return transaction.id
    
    def record_launch_milestone(self, plan_id: str, milestone: str, 
                               status: str, owner: str) -> str:
        """Registrar hito de lanzamiento"""
        transaction = self.create_transaction(
            sender=owner,
            receiver="milestone_tracker",
            transaction_type="milestone_update",
            data={
                "plan_id": plan_id,
                "milestone": milestone,
                "status": status,
                "timestamp": time.time(),
                "block_height": len(self.chain)
            }
        )
        
        return transaction.id
    
    def record_launch_metrics(self, plan_id: str, metrics: Dict[str, Any], 
                             owner: str) -> str:
        """Registrar métricas de lanzamiento"""
        transaction = self.create_transaction(
            sender=owner,
            receiver="metrics_tracker",
            transaction_type="metrics_update",
            data={
                "plan_id": plan_id,
                "metrics": metrics,
                "timestamp": time.time(),
                "block_height": len(self.chain)
            }
        )
        
        return transaction.id
    
    def verify_launch_plan(self, plan_id: str) -> Dict[str, Any]:
        """Verificar plan de lanzamiento en blockchain"""
        verification_result = {
            "plan_id": plan_id,
            "verified": False,
            "block_height": None,
            "timestamp": None,
            "hash": None,
            "transactions": []
        }
        
        # Buscar en la blockchain
        for block in self.chain:
            if "transactions" in block.data:
                for tx_data in block.data["transactions"]:
                    if (tx_data.get("transaction_type") == "launch_plan_record" and
                        tx_data.get("data", {}).get("plan_id") == plan_id):
                        verification_result.update({
                            "verified": True,
                            "block_height": block.index,
                            "timestamp": block.timestamp,
                            "hash": block.hash,
                            "transactions": [tx_data]
                        })
                        break
        
        return verification_result
    
    def get_launch_history(self, plan_id: str) -> List[Dict[str, Any]]:
        """Obtener historial de lanzamiento"""
        history = []
        
        for block in self.chain:
            if "transactions" in block.data:
                for tx_data in block.data["transactions"]:
                    tx_data_dict = tx_data.get("data", {})
                    if tx_data_dict.get("plan_id") == plan_id:
                        history.append({
                            "block_height": block.index,
                            "timestamp": block.timestamp,
                            "transaction_type": tx_data.get("transaction_type"),
                            "data": tx_data_dict,
                            "hash": block.hash
                        })
        
        return sorted(history, key=lambda x: x["timestamp"])
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la blockchain"""
        total_transactions = sum(
            len(block.data.get("transactions", [])) 
            for block in self.chain
        )
        
        total_contracts = len(self.smart_contracts)
        total_tokens = len(self.tokens)
        
        return {
            "chain_length": len(self.chain),
            "total_transactions": total_transactions,
            "pending_transactions": len(self.pending_transactions),
            "smart_contracts": total_contracts,
            "tokens": total_tokens,
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward,
            "last_block_hash": self.chain[-1].hash if self.chain else None,
            "genesis_timestamp": self.chain[0].timestamp if self.chain else None
        }
    
    def execute_smart_contract(self, contract_address: str, function_name: str, 
                              parameters: Dict[str, Any], caller: str) -> Dict[str, Any]:
        """Ejecutar función de contrato inteligente"""
        if contract_address not in self.smart_contracts:
            return {"error": "Contract not found"}
        
        contract = self.smart_contracts[contract_address]
        
        if function_name not in contract.functions:
            return {"error": "Function not found"}
        
        # Simular ejecución de contrato
        result = {
            "contract_address": contract_address,
            "function": function_name,
            "parameters": parameters,
            "caller": caller,
            "gas_used": 21000,  # Gas básico
            "execution_time": time.time(),
            "result": "success"
        }
        
        # Actualizar estado del contrato
        if function_name == "update_launch_status":
            contract.state["launch_status"] = parameters.get("status")
        elif function_name == "transfer_tokens":
            contract.state["balance"] = contract.state.get("balance", 0) - parameters.get("amount", 0)
        
        # Crear transacción de ejecución
        execution_transaction = self.create_transaction(
            sender=caller,
            receiver=contract_address,
            transaction_type="contract_execution",
            data={
                "function": function_name,
                "parameters": parameters,
                "result": result
            }
        )
        
        return result
    
    def create_launch_nft(self, plan_id: str, metadata: Dict[str, Any], 
                         owner: str) -> Dict[str, Any]:
        """Crear NFT de lanzamiento"""
        nft_id = hashlib.sha256(f"{plan_id}{time.time()}".encode()).hexdigest()
        
        nft_data = {
            "nft_id": nft_id,
            "plan_id": plan_id,
            "metadata": metadata,
            "owner": owner,
            "created_at": time.time(),
            "token_uri": f"https://launch-nft.com/{nft_id}",
            "contract_address": "0xLaunchNFT"
        }
        
        # Crear transacción de NFT
        nft_transaction = self.create_transaction(
            sender=owner,
            receiver="nft_contract",
            transaction_type="nft_mint",
            data=nft_data
        )
        
        return nft_data
    
    def launch_plan_to_blockchain(self, requirements: str, scenario_type: str, 
                                 owner: str) -> Dict[str, Any]:
        """Convertir plan de lanzamiento a blockchain"""
        try:
            print(f"🔗 Registrando plan de lanzamiento en blockchain...")
            
            # Crear plan de lanzamiento
            launch_plan = self.enhanced_planner.create_enhanced_launch_plan(requirements, scenario_type)
            
            # Generar insights con IA
            insights = self.insights_engine.generate_comprehensive_insights(requirements, scenario_type)
            
            # Optimización cuántica
            quantum_result = self.quantum_optimizer.quantum_launch_optimization(requirements, scenario_type)
            
            # Preparar datos para blockchain
            plan_data = {
                "id": f"plan_{int(time.time())}",
                "requirements": requirements,
                "scenario_type": scenario_type,
                "launch_plan": launch_plan,
                "ai_insights": insights,
                "quantum_optimization": quantum_result,
                "owner": owner,
                "created_at": time.time(),
                "version": "2.0.0"
            }
            
            # Registrar en blockchain
            transaction_id = self.record_launch_plan(plan_data, owner)
            
            # Crear token de lanzamiento
            token = self.create_launch_token(
                symbol="LAUNCH",
                name="Launch Planning Token",
                total_supply=1000000,
                owner=owner,
                price=1.0
            )
            
            # Crear NFT de lanzamiento
            nft = self.create_launch_nft(
                plan_id=plan_data["id"],
                metadata={
                    "name": f"Launch Plan #{plan_data['id']}",
                    "description": f"Blockchain-verified launch plan for {scenario_type}",
                    "image": "https://launch-nft.com/launch-plan.png",
                    "attributes": [
                        {"trait_type": "Scenario", "value": scenario_type},
                        {"trait_type": "Complexity", "value": launch_plan["analysis"]["complexity_score"]},
                        {"trait_type": "Success Probability", "value": insights["insights_summary"]["overall_success_probability"]}
                    ]
                },
                owner=owner
            )
            
            # Minar bloque
            mined_block = self.mine_block(owner)
            
            result = {
                "plan_id": plan_data["id"],
                "transaction_id": transaction_id,
                "block_height": mined_block.index if mined_block else None,
                "token": asdict(token),
                "nft": nft,
                "blockchain_stats": self.get_blockchain_stats(),
                "verification": self.verify_launch_plan(plan_data["id"]),
                "created_at": time.time()
            }
            
            print(f"   ✅ Plan registrado en blockchain")
            print(f"   📊 Block Height: {result['block_height']}")
            print(f"   🪙 Token: {token.symbol} ({token.total_supply:,} supply)")
            print(f"   🎨 NFT: {nft['nft_id']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error registrando en blockchain: {str(e)}")
            return {}

def main():
    """Demostración del Blockchain Launch Tracker"""
    print("⛓️ Blockchain Launch Tracker Demo")
    print("=" * 50)
    
    # Inicializar tracker blockchain
    blockchain_tracker = BlockchainLaunchTracker()
    
    # Mostrar estadísticas iniciales
    stats = blockchain_tracker.get_blockchain_stats()
    print(f"📊 Estadísticas de Blockchain:")
    print(f"   Longitud de cadena: {stats['chain_length']}")
    print(f"   Transacciones totales: {stats['total_transactions']}")
    print(f"   Contratos inteligentes: {stats['smart_contracts']}")
    print(f"   Tokens: {stats['tokens']}")
    
    # Desplegar contrato inteligente
    print(f"\n📜 Desplegando contrato inteligente...")
    contract = blockchain_tracker.deploy_smart_contract(
        name="LaunchTracker",
        functions=["update_launch_status", "transfer_tokens", "get_launch_data"],
        initial_state={"launch_count": 0, "total_value": 0}
    )
    print(f"   ✅ Contrato desplegado: {contract.address}")
    
    # Crear plan de lanzamiento y registrarlo en blockchain
    requirements = """
    Lanzar una plataforma blockchain de gestión de lanzamientos.
    Objetivo: 5,000 usuarios en el primer año.
    Presupuesto: $500,000 para desarrollo y marketing.
    Necesitamos 8 desarrolladores blockchain, 2 especialistas en smart contracts.
    Debe integrar con Ethereum, Polygon, y Binance Smart Chain.
    Lanzamiento objetivo: Q3 2024.
    Prioridad máxima para seguridad y descentralización.
    """
    
    print(f"\n🚀 Creando y registrando plan de lanzamiento...")
    result = blockchain_tracker.launch_plan_to_blockchain(
        requirements, "saas_platform", "blockchain_developer"
    )
    
    if result:
        print(f"✅ Plan registrado exitosamente!")
        
        # Registrar hitos
        print(f"\n📋 Registrando hitos de lanzamiento...")
        milestones = [
            ("development_start", "completed"),
            ("smart_contract_deploy", "in_progress"),
            ("testnet_launch", "pending"),
            ("mainnet_launch", "pending")
        ]
        
        for milestone, status in milestones:
            tx_id = blockchain_tracker.record_launch_milestone(
                result["plan_id"], milestone, status, "blockchain_developer"
            )
            print(f"   ✅ {milestone}: {status} (TX: {tx_id})")
        
        # Registrar métricas
        print(f"\n📊 Registrando métricas...")
        metrics = {
            "users": 1250,
            "transactions": 5000,
            "tvl": 100000,
            "success_rate": 0.95
        }
        
        metrics_tx_id = blockchain_tracker.record_launch_metrics(
            result["plan_id"], metrics, "blockchain_developer"
        )
        print(f"   ✅ Métricas registradas (TX: {metrics_tx_id})")
        
        # Minar bloque final
        print(f"\n⛏️ Minando bloque final...")
        final_block = blockchain_tracker.mine_block("blockchain_developer")
        print(f"   ✅ Bloque minado: {final_block.index}")
        
        # Verificar plan
        print(f"\n🔍 Verificando plan en blockchain...")
        verification = blockchain_tracker.verify_launch_plan(result["plan_id"])
        print(f"   ✅ Verificado: {verification['verified']}")
        print(f"   📊 Block Height: {verification['block_height']}")
        print(f"   🔗 Hash: {verification['hash'][:16]}...")
        
        # Obtener historial
        print(f"\n📚 Historial de lanzamiento:")
        history = blockchain_tracker.get_launch_history(result["plan_id"])
        for entry in history:
            print(f"   • {entry['transaction_type']} en bloque {entry['block_height']}")
        
        # Ejecutar contrato inteligente
        print(f"\n🤖 Ejecutando contrato inteligente...")
        contract_result = blockchain_tracker.execute_smart_contract(
            contract.address, "update_launch_status", 
            {"status": "active"}, "blockchain_developer"
        )
        print(f"   ✅ Contrato ejecutado: {contract_result['result']}")
        
        # Estadísticas finales
        final_stats = blockchain_tracker.get_blockchain_stats()
        print(f"\n📊 Estadísticas Finales:")
        print(f"   Longitud de cadena: {final_stats['chain_length']}")
        print(f"   Transacciones totales: {final_stats['total_transactions']}")
        print(f"   Contratos inteligentes: {final_stats['smart_contracts']}")
        print(f"   Tokens: {final_stats['tokens']}")
        
        # Guardar resultados
        with open("blockchain_launch_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "result": result,
                "verification": verification,
                "history": history,
                "final_stats": final_stats
            }, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📁 Resultados guardados en: blockchain_launch_results.json")
    
    print(f"\n🎉 Demo del Blockchain Launch Tracker completado!")
    print(f"   ⛓️ Blockchain: {stats['chain_length']} bloques")
    print(f"   🔗 Transacciones: {stats['total_transactions']}")
    print(f"   📜 Contratos: {stats['smart_contracts']}")
    print(f"   🪙 Tokens: {stats['tokens']}")

if __name__ == "__main__":
    main()









