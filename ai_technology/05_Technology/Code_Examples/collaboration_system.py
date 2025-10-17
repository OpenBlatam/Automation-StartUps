#!/usr/bin/env python3
"""
Sistema de colaboración y compartir archivos
"""

import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
import sqlite3
import shutil
from pathlib import Path

class CollaborationSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.collab_db = os.path.join(base_path, "collaboration.db")
        self.shared_folder = os.path.join(base_path, "shared")
        self.init_database()
        self.ensure_shared_folder()
    
    def init_database(self):
        """Inicializar base de datos de colaboración"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        # Tabla de archivos compartidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_files (
                id TEXT PRIMARY KEY,
                original_path TEXT,
                shared_path TEXT,
                filename TEXT,
                area TEXT,
                shared_by TEXT,
                shared_at TEXT,
                expires_at TEXT,
                access_count INTEGER DEFAULT 0,
                is_public BOOLEAN DEFAULT FALSE,
                description TEXT,
                tags TEXT
            )
        ''')
        
        # Tabla de comentarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                author TEXT,
                comment TEXT,
                created_at TEXT,
                parent_id INTEGER,
                FOREIGN KEY (file_id) REFERENCES shared_files (id),
                FOREIGN KEY (parent_id) REFERENCES comments (id)
            )
        ''')
        
        # Tabla de versiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                version_number INTEGER,
                file_path TEXT,
                created_at TEXT,
                changes TEXT,
                created_by TEXT,
                FOREIGN KEY (file_id) REFERENCES shared_files (id)
            )
        ''')
        
        # Tabla de permisos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                user_email TEXT,
                permission_type TEXT,
                granted_at TEXT,
                granted_by TEXT,
                FOREIGN KEY (file_id) REFERENCES shared_files (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def ensure_shared_folder(self):
        """Asegurar que existe la carpeta compartida"""
        os.makedirs(self.shared_folder, exist_ok=True)
        
        # Crear subcarpetas por área
        areas = [
            'Marketing', 'Finance', 'Human_Resources', 'Operations', 'Technology',
            'Strategy', 'Risk_Management', 'AI_Artificial_Intelligence', 'Sales',
            'Customer_Service', 'Research_Development', 'Quality_Assurance',
            'Legal_Compliance', 'Procurement', 'Logistics', 'Data_Analytics',
            'Innovation', 'Sustainability', 'International_Business', 'Project_Management'
        ]
        
        for area in areas:
            area_folder = os.path.join(self.shared_folder, area)
            os.makedirs(area_folder, exist_ok=True)
    
    def share_file(self, file_path, shared_by, description="", tags="", is_public=False, expires_days=30):
        """Compartir un archivo"""
        if not os.path.exists(file_path):
            return None, "Archivo no encontrado"
        
        # Generar ID único
        file_id = str(uuid.uuid4())
        
        # Determinar área
        area = self.determine_area(file_path)
        
        # Crear ruta compartida
        filename = os.path.basename(file_path)
        shared_filename = f"{file_id}_{filename}"
        shared_path = os.path.join(self.shared_folder, area, shared_filename)
        
        try:
            # Copiar archivo a carpeta compartida
            shutil.copy2(file_path, shared_path)
            
            # Calcular fecha de expiración
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.collab_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO shared_files 
                (id, original_path, shared_path, filename, area, shared_by, shared_at, 
                 expires_at, is_public, description, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, file_path, shared_path, filename, area, shared_by, 
                  datetime.now().isoformat(), expires_at, is_public, description, tags))
            
            conn.commit()
            conn.close()
            
            return file_id, "Archivo compartido exitosamente"
            
        except Exception as e:
            return None, f"Error compartiendo archivo: {e}"
    
    def determine_area(self, file_path):
        """Determinar área basada en la ruta del archivo"""
        path_parts = Path(file_path).parts
        
        for part in path_parts:
            if part.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_',
                              '11_', '12_', '13_', '14_', '15_', '16_', '17_', '18_', '19_', '20_')):
                area_mapping = {
                    '01_Marketing': 'Marketing',
                    '02_Finance': 'Finance',
                    '03_Human_Resources': 'Human_Resources',
                    '04_Operations': 'Operations',
                    '05_Technology': 'Technology',
                    '06_Strategy': 'Strategy',
                    '07_Risk_Management': 'Risk_Management',
                    '08_AI_Artificial_Intelligence': 'AI_Artificial_Intelligence',
                    '09_Sales': 'Sales',
                    '10_Customer_Service': 'Customer_Service',
                    '11_Research_Development': 'Research_Development',
                    '12_Quality_Assurance': 'Quality_Assurance',
                    '13_Legal_Compliance': 'Legal_Compliance',
                    '14_Procurement': 'Procurement',
                    '15_Logistics': 'Logistics',
                    '16_Data_Analytics': 'Data_Analytics',
                    '17_Innovation': 'Innovation',
                    '18_Sustainability': 'Sustainability',
                    '19_International_Business': 'International_Business',
                    '20_Project_Management': 'Project_Management'
                }
                return area_mapping.get(part, 'General')
        
        return 'General'
    
    def get_shared_files(self, area=None, user_email=None, public_only=False):
        """Obtener archivos compartidos"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        where_conditions = []
        params = []
        
        if area:
            where_conditions.append("area = ?")
            params.append(area)
        
        if user_email:
            where_conditions.append("shared_by = ?")
            params.append(user_email)
        
        if public_only:
            where_conditions.append("is_public = TRUE")
        
        # Solo archivos no expirados
        where_conditions.append("expires_at > ?")
        params.append(datetime.now().isoformat())
        
        where_clause = " AND ".join(where_conditions)
        
        cursor.execute(f'''
            SELECT id, filename, area, shared_by, shared_at, expires_at, 
                   access_count, is_public, description, tags
            FROM shared_files
            WHERE {where_clause}
            ORDER BY shared_at DESC
        ''', params)
        
        files = []
        for row in cursor.fetchall():
            files.append({
                'id': row[0],
                'filename': row[1],
                'area': row[2],
                'shared_by': row[3],
                'shared_at': row[4],
                'expires_at': row[5],
                'access_count': row[6],
                'is_public': bool(row[7]),
                'description': row[8],
                'tags': row[9].split(',') if row[9] else []
            })
        
        conn.close()
        return files
    
    def access_file(self, file_id):
        """Acceder a un archivo compartido"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT shared_path, filename, expires_at, access_count
            FROM shared_files
            WHERE id = ?
        ''', (file_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None, "Archivo no encontrado"
        
        shared_path, filename, expires_at, access_count = result
        
        # Verificar si no ha expirado
        if datetime.now().isoformat() > expires_at:
            conn.close()
            return None, "El archivo ha expirado"
        
        # Incrementar contador de acceso
        cursor.execute('''
            UPDATE shared_files
            SET access_count = access_count + 1
            WHERE id = ?
        ''', (file_id,))
        
        conn.commit()
        conn.close()
        
        return shared_path, filename
    
    def add_comment(self, file_id, author, comment, parent_id=None):
        """Agregar comentario a un archivo"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comments (file_id, author, comment, created_at, parent_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_id, author, comment, datetime.now().isoformat(), parent_id))
        
        conn.commit()
        conn.close()
        
        return "Comentario agregado exitosamente"
    
    def get_comments(self, file_id):
        """Obtener comentarios de un archivo"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, author, comment, created_at, parent_id
            FROM comments
            WHERE file_id = ?
            ORDER BY created_at ASC
        ''', (file_id,))
        
        comments = []
        for row in cursor.fetchall():
            comments.append({
                'id': row[0],
                'author': row[1],
                'comment': row[2],
                'created_at': row[3],
                'parent_id': row[4]
            })
        
        conn.close()
        return comments
    
    def create_version(self, file_id, changes, created_by):
        """Crear nueva versión de un archivo"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        # Obtener número de versión actual
        cursor.execute('''
            SELECT MAX(version_number) FROM file_versions WHERE file_id = ?
        ''', (file_id,))
        
        result = cursor.fetchone()
        next_version = (result[0] or 0) + 1
        
        # Obtener archivo original
        cursor.execute('SELECT shared_path FROM shared_files WHERE id = ?', (file_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None, "Archivo no encontrado"
        
        original_path = result[0]
        version_path = f"{original_path}.v{next_version}"
        
        try:
            # Crear copia de la versión
            shutil.copy2(original_path, version_path)
            
            # Guardar en base de datos
            cursor.execute('''
                INSERT INTO file_versions 
                (file_id, version_number, file_path, created_at, changes, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (file_id, next_version, version_path, datetime.now().isoformat(), 
                  changes, created_by))
            
            conn.commit()
            conn.close()
            
            return next_version, "Versión creada exitosamente"
            
        except Exception as e:
            conn.close()
            return None, f"Error creando versión: {e}"
    
    def get_file_versions(self, file_id):
        """Obtener versiones de un archivo"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version_number, file_path, created_at, changes, created_by
            FROM file_versions
            WHERE file_id = ?
            ORDER BY version_number DESC
        ''', (file_id,))
        
        versions = []
        for row in cursor.fetchall():
            versions.append({
                'version_number': row[0],
                'file_path': row[1],
                'created_at': row[2],
                'changes': row[3],
                'created_by': row[4]
            })
        
        conn.close()
        return versions
    
    def cleanup_expired_files(self):
        """Limpiar archivos expirados"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        # Obtener archivos expirados
        cursor.execute('''
            SELECT id, shared_path FROM shared_files
            WHERE expires_at < ?
        ''', (datetime.now().isoformat(),))
        
        expired_files = cursor.fetchall()
        cleaned_count = 0
        
        for file_id, shared_path in expired_files:
            try:
                # Eliminar archivo físico
                if os.path.exists(shared_path):
                    os.remove(shared_path)
                
                # Eliminar registros de base de datos
                cursor.execute('DELETE FROM shared_files WHERE id = ?', (file_id,))
                cursor.execute('DELETE FROM comments WHERE file_id = ?', (file_id,))
                cursor.execute('DELETE FROM file_versions WHERE file_id = ?', (file_id,))
                cursor.execute('DELETE FROM permissions WHERE file_id = ?', (file_id,))
                
                cleaned_count += 1
                
            except Exception as e:
                print(f"Error limpiando archivo {file_id}: {e}")
        
        conn.commit()
        conn.close()
        
        return cleaned_count
    
    def get_collaboration_stats(self):
        """Obtener estadísticas de colaboración"""
        conn = sqlite3.connect(self.collab_db)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM shared_files')
        total_shared = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM shared_files WHERE is_public = TRUE')
        public_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM comments')
        total_comments = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM file_versions')
        total_versions = cursor.fetchone()[0]
        
        # Archivos por área
        cursor.execute('''
            SELECT area, COUNT(*) FROM shared_files
            GROUP BY area
            ORDER BY COUNT(*) DESC
        ''')
        area_stats = dict(cursor.fetchall())
        
        # Archivos más accedidos
        cursor.execute('''
            SELECT filename, access_count FROM shared_files
            ORDER BY access_count DESC
            LIMIT 10
        ''')
        popular_files = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_shared': total_shared,
            'public_files': public_files,
            'total_comments': total_comments,
            'total_versions': total_versions,
            'area_stats': area_stats,
            'popular_files': popular_files
        }

def main():
    collab = CollaborationSystem()
    
    print("🤝 Sistema de Colaboración y Compartir Archivos")
    print("=" * 50)
    print("1. Compartir archivo")
    print("2. Ver archivos compartidos")
    print("3. Acceder a archivo")
    print("4. Agregar comentario")
    print("5. Ver comentarios")
    print("6. Crear versión")
    print("7. Ver versiones")
    print("8. Limpiar archivos expirados")
    print("9. Ver estadísticas")
    print("10. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-10): ").strip()
        
        if choice == '1':
            file_path = input("Ruta del archivo: ").strip()
            shared_by = input("Compartido por (email): ").strip()
            description = input("Descripción (opcional): ").strip()
            tags = input("Tags separados por coma (opcional): ").strip()
            is_public = input("¿Es público? (y/n): ").strip().lower() == 'y'
            
            file_id, message = collab.share_file(file_path, shared_by, description, tags, is_public)
            if file_id:
                print(f"✅ {message}")
                print(f"📋 ID del archivo: {file_id}")
            else:
                print(f"❌ {message}")
        
        elif choice == '2':
            area = input("Área específica (opcional): ").strip()
            user = input("Usuario específico (opcional): ").strip()
            public_only = input("¿Solo públicos? (y/n): ").strip().lower() == 'y'
            
            files = collab.get_shared_files(area or None, user or None, public_only)
            if files:
                print(f"\n📁 Archivos compartidos ({len(files)}):")
                for file in files:
                    print(f"  • {file['filename']} ({file['area']})")
                    print(f"    ID: {file['id']}")
                    print(f"    Compartido por: {file['shared_by']}")
                    print(f"    Accesos: {file['access_count']}")
                    print(f"    Público: {'Sí' if file['is_public'] else 'No'}")
                    print("-" * 40)
            else:
                print("❌ No se encontraron archivos compartidos")
        
        elif choice == '3':
            file_id = input("ID del archivo: ").strip()
            shared_path, filename = collab.access_file(file_id)
            if shared_path:
                print(f"✅ Archivo accesible: {filename}")
                print(f"📁 Ruta: {shared_path}")
            else:
                print(f"❌ {filename}")
        
        elif choice == '4':
            file_id = input("ID del archivo: ").strip()
            author = input("Autor del comentario: ").strip()
            comment = input("Comentario: ").strip()
            
            message = collab.add_comment(file_id, author, comment)
            print(f"✅ {message}")
        
        elif choice == '5':
            file_id = input("ID del archivo: ").strip()
            comments = collab.get_comments(file_id)
            if comments:
                print(f"\n💬 Comentarios ({len(comments)}):")
                for comment in comments:
                    print(f"  • {comment['author']}: {comment['comment']}")
                    print(f"    {comment['created_at']}")
                    print("-" * 30)
            else:
                print("❌ No hay comentarios para este archivo")
        
        elif choice == '6':
            file_id = input("ID del archivo: ").strip()
            changes = input("Descripción de cambios: ").strip()
            created_by = input("Creado por: ").strip()
            
            version, message = collab.create_version(file_id, changes, created_by)
            if version:
                print(f"✅ {message}")
                print(f"📋 Número de versión: {version}")
            else:
                print(f"❌ {message}")
        
        elif choice == '7':
            file_id = input("ID del archivo: ").strip()
            versions = collab.get_file_versions(file_id)
            if versions:
                print(f"\n📋 Versiones ({len(versions)}):")
                for version in versions:
                    print(f"  • v{version['version_number']} - {version['created_at']}")
                    print(f"    Cambios: {version['changes']}")
                    print(f"    Creado por: {version['created_by']}")
                    print("-" * 30)
            else:
                print("❌ No hay versiones para este archivo")
        
        elif choice == '8':
            cleaned = collab.cleanup_expired_files()
            print(f"✅ {cleaned} archivos expirados eliminados")
        
        elif choice == '9':
            stats = collab.get_collaboration_stats()
            print(f"\n📊 Estadísticas de Colaboración:")
            print(f"  📁 Total compartidos: {stats['total_shared']}")
            print(f"  🌐 Archivos públicos: {stats['public_files']}")
            print(f"  💬 Total comentarios: {stats['total_comments']}")
            print(f"  📋 Total versiones: {stats['total_versions']}")
            
            if stats['area_stats']:
                print(f"\n📈 Por área:")
                for area, count in stats['area_stats'].items():
                    print(f"  • {area}: {count}")
        
        elif choice == '10':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()



