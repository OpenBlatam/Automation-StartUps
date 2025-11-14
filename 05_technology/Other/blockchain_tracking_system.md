---
title: "Blockchain Tracking System"
category: "05_technology"
tags: ["technical", "technology"]
created: "2025-10-29"
path: "05_technology/Other/blockchain_tracking_system.md"
---

# Sistema de Tracking con Blockchain - Outreach Morningscore

## Blockchain para Transparencia y Verificación

### Sistema de Tracking Inmutable

#### Smart Contract para Colaboraciones
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OutreachCollaboration {
    struct Collaboration {
        address creator;
        address company;
        string contentHash;
        uint256 timestamp;
        uint256 value;
        bool completed;
        bool verified;
    }
    
    mapping(uint256 => Collaboration) public collaborations;
    uint256 public collaborationCount;
    
    event CollaborationCreated(uint256 indexed id, address indexed creator, address indexed company);
    event CollaborationCompleted(uint256 indexed id, string contentHash);
    event CollaborationVerified(uint256 indexed id, bool verified);
    
    function createCollaboration(
        address _company,
        string memory _contentHash,
        uint256 _value
    ) public returns (uint256) {
        uint256 id = collaborationCount++;
        
        collaborations[id] = Collaboration({
            creator: msg.sender,
            company: _company,
            contentHash: _contentHash,
            timestamp: block.timestamp,
            value: _value,
            completed: false,
            verified: false
        });
        
        emit CollaborationCreated(id, msg.sender, _company);
        return id;
    }
    
    function completeCollaboration(uint256 _id, string memory _contentHash) public {
        require(collaborations[_id].company == msg.sender, "Only company can complete");
        require(!collaborations[_id].completed, "Already completed");
        
        collaborations[_id].completed = true;
        collaborations[_id].contentHash = _contentHash;
        
        emit CollaborationCompleted(_id, _contentHash);
    }
    
    function verifyCollaboration(uint256 _id, bool _verified) public {
        require(collaborations[_id].creator == msg.sender, "Only creator can verify");
        
        collaborations[_id].verified = _verified;
        
        emit CollaborationVerified(_id, _verified);
    }
    
    function getCollaboration(uint256 _id) public view returns (Collaboration memory) {
        return collaborations[_id];
    }
}
```

#### Sistema de Verificación de Contenido
```python
import hashlib
import json
from web3 import Web3
import ipfshttpclient

class BlockchainContentVerification:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/your-project-id'))
        self.contract_address = "0x..."
        self.contract_abi = [...]  # ABI del contrato
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
        self.ipfs_client = ipfshttpclient.connect()
        
    def create_content_hash(self, content):
        """
        Crea un hash único del contenido
        """
        content_string = json.dumps(content, sort_keys=True)
        content_hash = hashlib.sha256(content_string.encode()).hexdigest()
        return content_hash
    
    def store_content_on_ipfs(self, content):
        """
        Almacena el contenido en IPFS
        """
        content_json = json.dumps(content)
        result = self.ipfs_client.add_str(content_json)
        return result['Hash']
    
    def create_collaboration_record(self, company_address, content, value):
        """
        Crea un registro de colaboración en blockchain
        """
        # Crear hash del contenido
        content_hash = self.create_content_hash(content)
        
        # Almacenar en IPFS
        ipfs_hash = self.store_content_on_ipfs(content)
        
        # Crear transacción
        tx_hash = self.contract.functions.createCollaboration(
            company_address,
            content_hash,
            value
        ).transact()
        
        # Esperar confirmación
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return tx_receipt
    
    def verify_content_integrity(self, collaboration_id, content):
        """
        Verifica la integridad del contenido
        """
        # Obtener colaboración del blockchain
        collaboration = self.contract.functions.getCollaboration(collaboration_id).call()
        
        # Crear hash del contenido actual
        current_hash = self.create_content_hash(content)
        
        # Comparar hashes
        return collaboration[2] == current_hash  # contentHash está en índice 2
```

### Sistema de Reputación Descentralizado

#### Token de Reputación
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReputationToken {
    mapping(address => uint256) public reputation;
    mapping(address => mapping(address => bool)) public endorsements;
    
    event ReputationUpdated(address indexed user, uint256 newReputation);
    event EndorsementGiven(address indexed endorser, address indexed endorsee);
    
    function giveEndorsement(address _endorsee) public {
        require(!endorsements[msg.sender][_endorsee], "Already endorsed");
        
        endorsements[msg.sender][_endorsee] = true;
        reputation[_endorsee] += 10;
        
        emit EndorsementGiven(msg.sender, _endorsee);
        emit ReputationUpdated(_endorsee, reputation[_endorsee]);
    }
    
    function getReputation(address _user) public view returns (uint256) {
        return reputation[_user];
    }
    
    function hasEndorsed(address _endorser, address _endorsee) public view returns (bool) {
        return endorsements[_endorser][_endorsee];
    }
}
```

#### Sistema de Scoring Descentralizado
```python
class DecentralizedReputationSystem:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/your-project-id'))
        self.reputation_contract = self.w3.eth.contract(
            address="0x...",
            abi=[...]
        )
        
    def calculate_reputation_score(self, address):
        """
        Calcula el score de reputación basado en blockchain
        """
        # Obtener reputación base
        base_reputation = self.reputation_contract.functions.getReputation(address).call()
        
        # Calcular factores adicionales
        endorsement_count = self._count_endorsements(address)
        collaboration_success_rate = self._calculate_success_rate(address)
        time_in_system = self._calculate_time_in_system(address)
        
        # Calcular score final
        reputation_score = (
            base_reputation * 0.4 +
            endorsement_count * 0.3 +
            collaboration_success_rate * 0.2 +
            time_in_system * 0.1
        )
        
        return reputation_score
    
    def _count_endorsements(self, address):
        """
        Cuenta el número de endorsements recibidos
        """
        # Implementar lógica para contar endorsements
        pass
    
    def _calculate_success_rate(self, address):
        """
        Calcula la tasa de éxito de colaboraciones
        """
        # Implementar lógica para calcular tasa de éxito
        pass
    
    def _calculate_time_in_system(self, address):
        """
        Calcula el tiempo en el sistema
        """
        # Implementar lógica para calcular tiempo en sistema
        pass
```

### Sistema de Pagos Descentralizado

#### Token de Pago
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OutreachToken {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    uint256 public totalSupply;
    string public name = "Outreach Token";
    string public symbol = "ORT";
    uint8 public decimals = 18;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance");
        
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        
        emit Transfer(msg.sender, _to, _value);
        return true;
    }
    
    function approve(address _spender, uint256 _value) public returns (bool) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }
    
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        require(balanceOf[_from] >= _value, "Insufficient balance");
        require(allowance[_from][msg.sender] >= _value, "Insufficient allowance");
        
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;
        
        emit Transfer(_from, _to, _value);
        return true;
    }
}
```

#### Sistema de Pagos Automático
```python
class DecentralizedPaymentSystem:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/your-project-id'))
        self.token_contract = self.w3.eth.contract(
            address="0x...",
            abi=[...]
        )
        
    def create_payment_agreement(self, creator_address, company_address, amount):
        """
        Crea un acuerdo de pago en blockchain
        """
        # Crear contrato de pago
        payment_contract = self._deploy_payment_contract(
            creator_address,
            company_address,
            amount
        )
        
        return payment_contract
    
    def execute_payment(self, payment_contract_address, amount):
        """
        Ejecuta un pago automático
        """
        # Obtener contrato de pago
        payment_contract = self.w3.eth.contract(
            address=payment_contract_address,
            abi=[...]
        )
        
        # Ejecutar pago
        tx_hash = payment_contract.functions.executePayment(amount).transact()
        
        # Esperar confirmación
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return tx_receipt
    
    def _deploy_payment_contract(self, creator_address, company_address, amount):
        """
        Despliega un contrato de pago
        """
        # Implementar lógica de despliegue
        pass
```

### Sistema de Auditoría Descentralizado

#### Auditoría Automática
```python
class DecentralizedAuditSystem:
    def __init__(self):
        self.audit_contracts = []
        
    def create_audit_record(self, collaboration_id, audit_data):
        """
        Crea un registro de auditoría en blockchain
        """
        # Crear hash de datos de auditoría
        audit_hash = hashlib.sha256(json.dumps(audit_data).encode()).hexdigest()
        
        # Almacenar en blockchain
        tx_hash = self._store_audit_record(collaboration_id, audit_hash)
        
        return tx_hash
    
    def verify_audit_integrity(self, collaboration_id, audit_data):
        """
        Verifica la integridad de la auditoría
        """
        # Obtener hash almacenado
        stored_hash = self._get_audit_hash(collaboration_id)
        
        # Crear hash de datos actuales
        current_hash = hashlib.sha256(json.dumps(audit_data).encode()).hexdigest()
        
        # Comparar hashes
        return stored_hash == current_hash
    
    def _store_audit_record(self, collaboration_id, audit_hash):
        """
        Almacena registro de auditoría
        """
        # Implementar lógica de almacenamiento
        pass
    
    def _get_audit_hash(self, collaboration_id):
        """
        Obtiene hash de auditoría
        """
        # Implementar lógica de obtención
        pass
```

### Dashboard de Blockchain

#### Visualización de Datos Blockchain
```python
import streamlit as st
import plotly.express as px
import pandas as pd

class BlockchainDashboard:
    def __init__(self):
        self.blockchain_data = self._load_blockchain_data()
        
    def create_dashboard(self):
        """
        Crea dashboard de blockchain
        """
        st.title("🔗 Blockchain Outreach Dashboard")
        
        # Métricas principales
        self._display_blockchain_metrics()
        
        # Gráficos de transacciones
        self._display_transaction_charts()
        
        # Análisis de reputación
        self._display_reputation_analysis()
        
        # Auditoría de contenido
        self._display_content_audit()
    
    def _display_blockchain_metrics(self):
        """
        Muestra métricas de blockchain
        """
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Collaborations", "25", "5")
        
        with col2:
            st.metric("Blockchain Transactions", "150", "12")
        
        with col3:
            st.metric("Reputation Score", "8.7", "0.3")
        
        with col4:
            st.metric("Content Verified", "98%", "2%")
    
    def _display_transaction_charts(self):
        """
        Muestra gráficos de transacciones
        """
        st.subheader("📊 Transaction Analysis")
        
        # Gráfico de transacciones por día
        fig = px.line(
            x=pd.date_range('2024-01-01', periods=30, freq='D'),
            y=np.random.randn(30).cumsum() + 5,
            title="Daily Transactions"
        )
        st.plotly_chart(fig)
    
    def _display_reputation_analysis(self):
        """
        Muestra análisis de reputación
        """
        st.subheader("⭐ Reputation Analysis")
        
        # Gráfico de reputación por usuario
        fig = px.bar(
            x=['User 1', 'User 2', 'User 3', 'User 4'],
            y=[8.5, 7.2, 9.1, 6.8],
            title="Reputation Scores"
        )
        st.plotly_chart(fig)
    
    def _display_content_audit(self):
        """
        Muestra auditoría de contenido
        """
        st.subheader("🔍 Content Audit")
        
        # Tabla de auditoría
        audit_data = pd.DataFrame({
            'Content ID': ['C001', 'C002', 'C003', 'C004'],
            'Status': ['Verified', 'Verified', 'Pending', 'Verified'],
            'Hash': ['0x123...', '0x456...', '0x789...', '0xabc...'],
            'Timestamp': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04']
        })
        
        st.dataframe(audit_data)
    
    def _load_blockchain_data(self):
        """
        Carga datos de blockchain
        """
        # Implementar carga de datos
        pass
```

## Checklist de Implementación Blockchain

### Fase 1: Configuración Básica
- [ ] Configurar Web3 y conexión a blockchain
- [ ] Desplegar smart contracts básicos
- [ ] Implementar sistema de hashing
- [ ] Configurar IPFS para almacenamiento
- [ ] Crear dashboard básico

### Fase 2: Implementación Avanzada
- [ ] Implementar sistema de reputación
- [ ] Crear sistema de pagos
- [ ] Configurar auditoría automática
- [ ] Implementar verificación de contenido
- [ ] Crear dashboard completo

### Fase 3: Optimización
- [ ] Optimizar gas fees
- [ ] Implementar layer 2 solutions
- [ ] Mejorar escalabilidad
- [ ] Añadir más funcionalidades
- [ ] Integrar con sistemas existentes


