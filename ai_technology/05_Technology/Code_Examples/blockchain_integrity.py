#!/usr/bin/env python3
"""
Sistema de blockchain para integridad y trazabilidad de documentos
"""

import os
import json
import hashlib
import sqlite3
from datetime import datetime
import threading
import time

class BlockchainIntegritySystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.blockchain_db = os.path.join(base_path, "blockchain.db")
        self.business_areas = [
            '01_Marketing', '02_Finance', '03_Human_Resources', '04_Operations',
            '05_Technology', '06_Strategy', '07_Risk_Management', '08_AI_Artificial_Intelligence',
            '09_Sales', '10_Customer_Service', '11_Research_Development', '12_Quality_Assurance',
            '13_Legal_Compliance', '14_Procurement', '15_Logistics', '16_Data_Analytics',
            '17_Innovation', '18_Sustainability', '19_International_Business', '20_Project_Management'
        ]
        self.init_blockchain_database()
    
    def init_blockchain_database(self):
        """Inicializar base de datos blockchain"""
        conn = sqlite3.connect(self.blockchain_db)
        cursor = conn.cursor()
        
        # Tabla de bloques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_hash TEXT UNIQUE,
                previous_hash TEXT,
                timestamp TEXT,
                nonce INTEGER,
                merkle_root TEXT,
                block_data TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de transacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_hash TEXT UNIQUE,
                block_id INTEGER,
                file_path TEXT,
                file_hash TEXT,
                action TEXT,
                user_id TEXT,
                timestamp TEXT,
                metadata TEXT,
                FOREIGN KEY (block_id) REFERENCES blocks (id)
            )
        ''')
        
        # Tabla de integridad de archivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_integrity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                current_hash TEXT,
                original_hash TEXT,
                first_created TEXT,
                last_modified TEXT,
                modification_count INTEGER DEFAULT 0,
                integrity_status TEXT DEFAULT 'verified'
            )
        ''')
        
        # Tabla de auditoría
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                action TEXT,
                user_id TEXT,
                timestamp TEXT,
                details TEXT,
                blockchain_hash TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_merkle_root(self, transactions):
        """Calcular raíz de Merkle para las transacciones"""
        if not transactions:
            return ""
        
        # Si solo hay una transacción, devolver su hash
        if len(transactions) == 1:
            return transactions[0]
        
        # Crear árbol de Merkle
        current_level = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                    next_level.append(hashlib.sha256(combined.encode()).hexdigest())
                else:
                    next_level.append(current_level[i])
            current_level = next_level
        
        return current_level[0]
    
    def create_transaction(self, file_path, action, user_id, metadata=None):
        """Crear transacción blockchain"""
        # Calcular hash del archivo
        file_hash = self.calculate_file_hash(file_path)
        
        # Crear datos de transacción
        transaction_data = {
            'file_path': file_path,
            'file_hash': file_hash,
            'action': action,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Crear hash de transacción
        transaction_string = f"{file_path}{file_hash}{action}{user_id}{transaction_data['timestamp']}"
        transaction_hash = hashlib.sha256(transaction_string.encode()).hexdigest()
        
        return transaction_hash, transaction_data
    
    def calculate_file_hash(self, file_path):
        """Calcular hash SHA-256 de un archivo"""
        if not os.path.exists(file_path):
            return None
        
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None
    
    def mine_block(self, transactions):
        """Minar bloque con proof-of-work"""
        if not transactions:
            return None
        
        # Obtener hash del último bloque
        conn = sqlite3.connect(self.blockchain_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT block_hash FROM blocks ORDER BY id DESC LIMIT 1')
        last_block = cursor.fetchone()
        previous_hash = last_block[0] if last_block else "0"
        
        # Calcular raíz de Merkle
        transaction_hashes = [tx['transaction_hash'] for tx in transactions]
        merkle_root = self.calculate_merkle_root(transaction_hashes)
        
        # Minar bloque (proof-of-work simplificado)
        nonce = 0
        target = "0000"  # Dificultad simplificada
        
        while True:
            block_data = f"{previous_hash}{merkle_root}{nonce}{datetime.now().isoformat()}"
            block_hash = hashlib.sha256(block_data.encode()).hexdigest()
            
            if block_hash.startswith(target):
                break
            
            nonce += 1
            
            # Límite de intentos para evitar bloqueo
            if nonce > 100000:
                print("⚠️  Dificultad de minado muy alta, usando hash simple")
                block_hash = hashlib.sha256(block_data.encode()).hexdigest()
                break
        
        # Crear bloque
        block = {
            'block_hash': block_hash,
            'previous_hash': previous_hash,
            'timestamp': datetime.now().isoformat(),
            'nonce': nonce,
            'merkle_root': merkle_root,
            'block_data': block_data
        }
        
        # Guardar bloque
        cursor.execute('''
            INSERT INTO blocks (block_hash, previous_hash, timestamp, nonce, merkle_root, block_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (block_hash, previous_hash, block['timestamp'], nonce, merkle_root, block_data, datetime.now().isoformat()))
        
        block_id = cursor.lastrowid
        
        # Guardar transacciones
        for transaction in transactions:
            cursor.execute('''
                INSERT INTO transactions (transaction_hash, block_id, file_path, file_hash, action, user_id, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (transaction['transaction_hash'], block_id, transaction['file_path'], 
                  transaction['file_hash'], transaction['action'], transaction['user_id'],
                  transaction['timestamp'], json.dumps(transaction['metadata'])))
        
        conn.commit()
        conn.close()
        
        return block
    
    def add_file_to_blockchain(self, file_path, user_id, action='create'):
        """Agregar archivo al blockchain"""
        if not os.path.exists(file_path):
            return None, "Archivo no encontrado"
        
        # Crear transacción
        transaction_hash, transaction_data = self.create_transaction(file_path, action, user_id)
        
        # Minar bloque
        block = self.mine_block([transaction_data])
        
        if block:
            # Actualizar integridad del archivo
            self.update_file_integrity(file_path, transaction_data['file_hash'])
            
            # Registrar en auditoría
            self.log_audit(file_path, action, user_id, f"Blockchain hash: {block['block_hash']}")
            
            return block['block_hash'], "Archivo agregado al blockchain exitosamente"
        else:
            return None, "Error minando bloque"
    
    def update_file_integrity(self, file_path, file_hash):
        """Actualizar integridad del archivo"""
        conn = sqlite3.connect(self.blockchain_db)
        cursor = conn.cursor()
        
        # Verificar si el archivo ya existe
        cursor.execute('SELECT id, original_hash, modification_count FROM file_integrity WHERE file_path = ?', (file_path,))
        existing = cursor.fetchone()
        
        if existing:
            # Actualizar archivo existente
            file_id, original_hash, mod_count = existing
            cursor.execute('''
                UPDATE file_integrity
                SET current_hash = ?, last_modified = ?, modification_count = modification_count + 1
                WHERE file_path = ?
            ''', (file_hash, datetime.now().isoformat(), file_path))
        else:
            # Crear nuevo registro
            cursor.execute('''
                INSERT INTO file_integrity (file_path, current_hash, original_hash, first_created, last_modified)
                VALUES (?, ?, ?, ?, ?)
            ''', (file_path, file_hash, file_hash, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def verify_file_integrity(self, file_path):
        """Verificar integridad del archivo"""
        if not os.path.exists(file_path):
            return False, "Archivo no encontrado"
        
        # Calcular hash actual
        current_hash = self.calculate_file_hash(file_path)
        if not current_hash:
            return False, "Error calculando hash"
        
        # Obtener hash original del blockchain
        conn = sqlite3.connect(self.blockchain_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT original_hash, current_hash FROM file_integrity WHERE file_path = ?', (file_path,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "Archivo no encontrado en blockchain"
        
        original_hash, stored_hash = result
        conn.close()
        
        # Verificar integridad
        if current_hash == stored_hash:
            return True, "Integridad verificada"
        else:
            return False, f"Hash no coincide. Actual: {current_hash[:16]}..., Esperado: {stored_hash[:16]}..."
    
    def get_file_history(self, file_path):
        """Obtener historial de un archivo en el blockchain"""
        conn = sqlite3.connect(self.blockchain_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.action, t.user_id, t.timestamp, t.metadata, b.block_hash
            FROM transactions t
            JOIN blocks b ON t.block_id = b.id
            WHERE t.file_path = ?
            ORDER BY t.timestamp ASC
        ''', (file_path,))
        
        history = []
        for row in cursor.fetchall():
            action, user_id, timestamp, metadata, block_hash = row
            history.append({
                'action': action,
                'user_id': user_id,
                'timestamp': timestamp,
                'metadata': json.loads(metadata) if metadata else {},
                'block_hash': block_hash
            })
        
        conn.close()
        return history
    
    def log_audit(self, file_path, action, user_id, details):
        """Registrar en log de auditoría"""
        conn = sqlite3.connect(self.blockchain_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_log (file_path, action, user_id, timestamp, details, blockchain_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (file_path, action, user_id, datetime.now().isoformat(), details, ""))
        
        conn.commit()
        conn.close()
    
    def get_blockchain_stats(self):
        """Obtener estadísticas del blockchain"""
        conn = sqlite3.connect(self.blockchain_db)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM blocks')
        total_blocks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM transactions')
        total_transactions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM file_integrity')
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM file_integrity WHERE integrity_status = "verified"')
        verified_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM file_integrity WHERE integrity_status = "compromised"')
        compromised_files = cursor.fetchone()[0]
        
        # Archivos más modificados
        cursor.execute('''
            SELECT file_path, modification_count FROM file_integrity
            ORDER BY modification_count DESC
            LIMIT 10
        ''')
        most_modified = cursor.fetchall()
        
        # Actividad por área
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN file_path LIKE '%01_Marketing%' THEN 'Marketing'
                    WHEN file_path LIKE '%02_Finance%' THEN 'Finance'
                    WHEN file_path LIKE '%03_Human_Resources%' THEN 'Human Resources'
                    WHEN file_path LIKE '%05_Technology%' THEN 'Technology'
                    ELSE 'Other'
                END as area,
                COUNT(*) as count
            FROM transactions
            GROUP BY area
            ORDER BY count DESC
        ''')
        area_activity = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_blocks': total_blocks,
            'total_transactions': total_transactions,
            'total_files': total_files,
            'verified_files': verified_files,
            'compromised_files': compromised_files,
            'most_modified': most_modified,
            'area_activity': area_activity
        }
    
    def scan_all_files(self, user_id='system'):
        """Escanear todos los archivos y agregarlos al blockchain"""
        print("🔍 Escaneando archivos para blockchain...")
        
        added_count = 0
        errors = []
        
        for area in self.business_areas:
            area_path = os.path.join(self.base_path, area)
            if not os.path.exists(area_path):
                continue
            
            print(f"📁 Procesando área: {area}")
            
            for root, dirs, files in os.walk(area_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        
                        try:
                            # Verificar si ya está en blockchain
                            conn = sqlite3.connect(self.blockchain_db)
                            cursor = conn.cursor()
                            cursor.execute('SELECT id FROM file_integrity WHERE file_path = ?', (file_path,))
                            exists = cursor.fetchone()
                            conn.close()
                            
                            if not exists:
                                # Agregar al blockchain
                                block_hash, message = self.add_file_to_blockchain(file_path, user_id, 'create')
                                if block_hash:
                                    added_count += 1
                                    print(f"  ✅ {os.path.basename(file_path)}")
                                else:
                                    errors.append(f"Error con {file_path}: {message}")
                            else:
                                print(f"  ⏭️  {os.path.basename(file_path)} (ya existe)")
                        
                        except Exception as e:
                            errors.append(f"Error procesando {file_path}: {e}")
        
        print(f"\n📊 Resumen del escaneo:")
        print(f"  ✅ Archivos agregados: {added_count}")
        print(f"  ❌ Errores: {len(errors)}")
        
        if errors:
            print(f"\n🚨 Errores encontrados:")
            for error in errors[:5]:  # Mostrar solo los primeros 5
                print(f"  • {error}")
            if len(errors) > 5:
                print(f"  ... y {len(errors) - 5} más")
        
        return added_count, errors

def main():
    blockchain = BlockchainIntegritySystem()
    
    print("⛓️ Sistema de Blockchain para Integridad de Documentos")
    print("=" * 60)
    print("1. Agregar archivo al blockchain")
    print("2. Verificar integridad de archivo")
    print("3. Obtener historial de archivo")
    print("4. Escanear todos los archivos")
    print("5. Ver estadísticas del blockchain")
    print("6. Verificar integridad de todos los archivos")
    print("7. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-7): ").strip()
        
        if choice == '1':
            file_path = input("Ruta del archivo: ").strip()
            user_id = input("ID de usuario: ").strip()
            action = input("Acción (create/update): ").strip()
            
            block_hash, message = blockchain.add_file_to_blockchain(file_path, user_id, action)
            if block_hash:
                print(f"✅ {message}")
                print(f"🔗 Hash del bloque: {block_hash}")
            else:
                print(f"❌ {message}")
        
        elif choice == '2':
            file_path = input("Ruta del archivo: ").strip()
            is_valid, message = blockchain.verify_file_integrity(file_path)
            
            if is_valid:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        
        elif choice == '3':
            file_path = input("Ruta del archivo: ").strip()
            history = blockchain.get_file_history(file_path)
            
            if history:
                print(f"\n📋 Historial de {os.path.basename(file_path)}:")
                for entry in history:
                    print(f"  • {entry['action']} por {entry['user_id']} en {entry['timestamp']}")
                    print(f"    Bloque: {entry['block_hash'][:16]}...")
            else:
                print("❌ No se encontró historial para este archivo")
        
        elif choice == '4':
            user_id = input("ID de usuario para el escaneo: ").strip()
            added_count, errors = blockchain.scan_all_files(user_id)
            print(f"\n🎉 Escaneo completado: {added_count} archivos agregados")
        
        elif choice == '5':
            stats = blockchain.get_blockchain_stats()
            print(f"\n📊 Estadísticas del Blockchain:")
            print(f"  ⛓️  Total bloques: {stats['total_blocks']}")
            print(f"  📝 Total transacciones: {stats['total_transactions']}")
            print(f"  📁 Total archivos: {stats['total_files']}")
            print(f"  ✅ Archivos verificados: {stats['verified_files']}")
            print(f"  ❌ Archivos comprometidos: {stats['compromised_files']}")
            
            if stats['area_activity']:
                print(f"\n📈 Actividad por área:")
                for area, count in stats['area_activity'].items():
                    print(f"  • {area}: {count}")
        
        elif choice == '6':
            print("🔍 Verificando integridad de todos los archivos...")
            verified_count = 0
            compromised_count = 0
            
            for area in blockchain.business_areas:
                area_path = os.path.join(blockchain.base_path, area)
                if not os.path.exists(area_path):
                    continue
                
                for root, dirs, files in os.walk(area_path):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            is_valid, message = blockchain.verify_file_integrity(file_path)
                            
                            if is_valid:
                                verified_count += 1
                            else:
                                compromised_count += 1
                                print(f"❌ {os.path.basename(file_path)}: {message}")
            
            print(f"\n📊 Verificación completada:")
            print(f"  ✅ Archivos íntegros: {verified_count}")
            print(f"  ❌ Archivos comprometidos: {compromised_count}")
        
        elif choice == '7':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()



