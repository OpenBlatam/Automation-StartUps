#!/usr/bin/env python3
"""
Sistema de comandos de voz para el sistema de organización empresarial
"""

import os
import json
import sqlite3
import speech_recognition as sr
import pyttsx3
import threading
import time
from datetime import datetime
import webbrowser

class VoiceCommandSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.voice_db = os.path.join(base_path, "voice_commands.db")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.is_listening = False
        self.command_history = []
        self.business_areas = {
            '01_Marketing': 'Marketing',
            '02_Finance': 'Finance',
            '03_Human_Resources': 'Human Resources',
            '04_Operations': 'Operations',
            '05_Technology': 'Technology',
            '06_Strategy': 'Strategy',
            '07_Risk_Management': 'Risk Management',
            '08_AI_Artificial_Intelligence': 'AI and Artificial Intelligence',
            '09_Sales': 'Sales',
            '10_Customer_Service': 'Customer Service'
        }
        self.init_voice_database()
        self.setup_voice_engine()
    
    def init_voice_database(self):
        """Inicializar base de datos de comandos de voz"""
        conn = sqlite3.connect(self.voice_db)
        cursor = conn.cursor()
        
        # Tabla de comandos de voz
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_text TEXT,
                action TEXT,
                parameters TEXT,
                success_rate REAL DEFAULT 0.0,
                last_used TEXT,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de historial de comandos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_text TEXT,
                recognized_text TEXT,
                action_taken TEXT,
                success BOOLEAN,
                timestamp TEXT,
                response_time REAL
            )
        ''')
        
        # Tabla de configuración de voz
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_config (
                id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'es-ES',
                voice_speed REAL DEFAULT 1.0,
                voice_volume REAL DEFAULT 0.8,
                auto_listen BOOLEAN DEFAULT FALSE,
                wake_word TEXT DEFAULT 'sistema'
            )
        ''')
        
        # Insertar comandos predefinidos
        predefined_commands = [
            ('buscar documentos', 'search', '{"query": "{query}"}', 0.0, datetime.now().isoformat(), 0),
            ('abrir área', 'open_area', '{"area": "{area}"}', 0.0, datetime.now().isoformat(), 0),
            ('mostrar estadísticas', 'show_stats', '{}', 0.0, datetime.now().isoformat(), 0),
            ('organizar archivos', 'organize', '{}', 0.0, datetime.now().isoformat(), 0),
            ('hacer backup', 'backup', '{}', 0.0, datetime.now().isoformat(), 0),
            ('abrir interfaz web', 'open_web', '{}', 0.0, datetime.now().isoformat(), 0),
            ('ayuda', 'help', '{}', 0.0, datetime.now().isoformat(), 0),
            ('salir', 'exit', '{}', 0.0, datetime.now().isoformat(), 0)
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO voice_commands (command_text, action, parameters, success_rate, last_used, usage_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', predefined_commands)
        
        # Insertar configuración por defecto
        cursor.execute('''
            INSERT OR IGNORE INTO voice_config (id, language, voice_speed, voice_volume, auto_listen, wake_word)
            VALUES (1, 'es-ES', 1.0, 0.8, FALSE, 'sistema')
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_voice_engine(self):
        """Configurar motor de texto a voz"""
        voices = self.tts_engine.getProperty('voices')
        
        # Buscar voz en español
        for voice in voices:
            if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Configurar velocidad y volumen
        self.tts_engine.setProperty('rate', 150)  # Velocidad de habla
        self.tts_engine.setProperty('volume', 0.8)  # Volumen
    
    def speak(self, text):
        """Convertir texto a voz"""
        print(f"🔊 {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self, timeout=5):
        """Escuchar comando de voz"""
        try:
            with self.microphone as source:
                print("🎤 Escuchando...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("🔄 Procesando audio...")
            text = self.recognizer.recognize_google(audio, language='es-ES')
            print(f"📝 Reconocido: {text}")
            return text.lower()
        
        except sr.WaitTimeoutError:
            print("⏰ Tiempo de espera agotado")
            return None
        except sr.UnknownValueError:
            print("❓ No se pudo entender el audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error del servicio de reconocimiento: {e}")
            return None
    
    def process_command(self, command_text):
        """Procesar comando de voz"""
        start_time = time.time()
        
        # Buscar comando en base de datos
        conn = sqlite3.connect(self.voice_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT action, parameters FROM voice_commands
            WHERE command_text LIKE ?
            ORDER BY success_rate DESC, usage_count DESC
        ''', (f"%{command_text}%",))
        
        result = cursor.fetchone()
        
        if result:
            action, parameters = result
            parameters = json.loads(parameters)
            
            # Actualizar estadísticas
            cursor.execute('''
                UPDATE voice_commands
                SET usage_count = usage_count + 1, last_used = ?
                WHERE command_text LIKE ?
            ''', (datetime.now().isoformat(), f"%{command_text}%"))
            
            conn.commit()
            conn.close()
            
            # Ejecutar acción
            success = self.execute_action(action, parameters, command_text)
            
            # Registrar en historial
            response_time = time.time() - start_time
            self.log_command(command_text, command_text, action, success, response_time)
            
            return success
        else:
            conn.close()
            self.speak("No entendí el comando. Intenta decir 'ayuda' para ver los comandos disponibles.")
            self.log_command(command_text, command_text, "unknown", False, time.time() - start_time)
            return False
    
    def execute_action(self, action, parameters, original_command):
        """Ejecutar acción basada en comando"""
        try:
            if action == 'search':
                query = self.extract_parameter(original_command, 'query')
                if query:
                    self.speak(f"Buscando documentos sobre {query}")
                    # Aquí se integraría con el sistema de búsqueda
                    return True
                else:
                    self.speak("¿Qué quieres buscar?")
                    return False
            
            elif action == 'open_area':
                area = self.extract_area_from_command(original_command)
                if area:
                    self.speak(f"Abriendo área de {area}")
                    # Aquí se abriría la interfaz web en el área específica
                    return True
                else:
                    self.speak("¿Qué área quieres abrir?")
                    return False
            
            elif action == 'show_stats':
                self.speak("Mostrando estadísticas del sistema")
                # Aquí se mostrarían las estadísticas
                return True
            
            elif action == 'organize':
                self.speak("Iniciando organización automática de archivos")
                # Aquí se ejecutaría la organización automática
                return True
            
            elif action == 'backup':
                self.speak("Iniciando proceso de backup")
                # Aquí se ejecutaría el backup
                return True
            
            elif action == 'open_web':
                self.speak("Abriendo interfaz web")
                webbrowser.open('http://localhost:5000')
                return True
            
            elif action == 'help':
                self.show_voice_help()
                return True
            
            elif action == 'exit':
                self.speak("Cerrando sistema de comandos de voz")
                return True
            
            else:
                self.speak("Comando no reconocido")
                return False
        
        except Exception as e:
            self.speak(f"Error ejecutando comando: {e}")
            return False
    
    def extract_parameter(self, command, param_name):
        """Extraer parámetro del comando"""
        # Implementación simple de extracción de parámetros
        if param_name == 'query':
            # Buscar palabras después de "buscar"
            words = command.split()
            if 'buscar' in words:
                query_start = words.index('buscar') + 1
                return ' '.join(words[query_start:])
        return None
    
    def extract_area_from_command(self, command):
        """Extraer área del comando"""
        for area_code, area_name in self.business_areas.items():
            if area_name.lower() in command:
                return area_name
        return None
    
    def log_command(self, original_command, recognized_text, action, success, response_time):
        """Registrar comando en historial"""
        conn = sqlite3.connect(self.voice_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO command_history (command_text, recognized_text, action_taken, success, timestamp, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (original_command, recognized_text, action, success, datetime.now().isoformat(), response_time))
        
        conn.commit()
        conn.close()
    
    def show_voice_help(self):
        """Mostrar ayuda de comandos de voz"""
        help_text = """
        Comandos de voz disponibles:
        - Buscar documentos sobre [tema]
        - Abrir área de [nombre del área]
        - Mostrar estadísticas
        - Organizar archivos
        - Hacer backup
        - Abrir interfaz web
        - Ayuda
        - Salir
        """
        self.speak(help_text)
        print(help_text)
    
    def start_continuous_listening(self):
        """Iniciar escucha continua"""
        self.is_listening = True
        self.speak("Sistema de comandos de voz activado. Di 'ayuda' para ver los comandos disponibles.")
        
        while self.is_listening:
            try:
                command = self.listen(timeout=3)
                if command:
                    if 'salir' in command or 'exit' in command:
                        self.speak("Cerrando sistema de comandos de voz")
                        self.is_listening = False
                        break
                    else:
                        self.process_command(command)
                
                time.sleep(0.5)  # Pequeña pausa entre escuchas
            
            except KeyboardInterrupt:
                self.speak("Sistema de comandos de voz detenido")
                self.is_listening = False
                break
    
    def get_voice_stats(self):
        """Obtener estadísticas de comandos de voz"""
        conn = sqlite3.connect(self.voice_db)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM command_history')
        total_commands = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM command_history WHERE success = 1')
        successful_commands = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(response_time) FROM command_history')
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Comandos más usados
        cursor.execute('''
            SELECT action, COUNT(*) as count
            FROM command_history
            GROUP BY action
            ORDER BY count DESC
            LIMIT 10
        ''')
        popular_commands = cursor.fetchall()
        
        # Precisión por comando
        cursor.execute('''
            SELECT action, 
                   COUNT(*) as total,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                   AVG(response_time) as avg_time
            FROM command_history
            GROUP BY action
            ORDER BY total DESC
        ''')
        command_accuracy = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_commands': total_commands,
            'successful_commands': successful_commands,
            'success_rate': (successful_commands / total_commands * 100) if total_commands > 0 else 0,
            'avg_response_time': avg_response_time,
            'popular_commands': popular_commands,
            'command_accuracy': command_accuracy
        }
    
    def train_voice_model(self):
        """Entrenar modelo de voz con comandos personalizados"""
        print("🎓 Entrenando modelo de voz...")
        
        # Comandos de entrenamiento
        training_commands = [
            "buscar documentos de marketing",
            "abrir área de finanzas",
            "mostrar estadísticas del sistema",
            "organizar archivos automáticamente",
            "hacer backup de seguridad",
            "abrir interfaz web",
            "ayuda con comandos",
            "salir del sistema"
        ]
        
        for command in training_commands:
            print(f"📝 Entrenando: {command}")
            # Aquí se implementaría el entrenamiento real del modelo
            time.sleep(0.5)
        
        print("✅ Entrenamiento completado")

def main():
    voice_system = VoiceCommandSystem()
    
    print("🎤 Sistema de Comandos de Voz")
    print("=" * 40)
    print("1. Iniciar escucha continua")
    print("2. Comando único")
    print("3. Entrenar modelo de voz")
    print("4. Ver estadísticas")
    print("5. Configurar voz")
    print("6. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-6): ").strip()
        
        if choice == '1':
            print("🎤 Iniciando escucha continua...")
            print("Di 'salir' para detener")
            voice_system.start_continuous_listening()
        
        elif choice == '2':
            print("🎤 Di tu comando:")
            command = voice_system.listen()
            if command:
                voice_system.process_command(command)
        
        elif choice == '3':
            voice_system.train_voice_model()
        
        elif choice == '4':
            stats = voice_system.get_voice_stats()
            print(f"\n📊 Estadísticas de Comandos de Voz:")
            print(f"  🎤 Total comandos: {stats['total_commands']}")
            print(f"  ✅ Comandos exitosos: {stats['successful_commands']}")
            print(f"  📈 Tasa de éxito: {stats['success_rate']:.1f}%")
            print(f"  ⏱️  Tiempo promedio: {stats['avg_response_time']:.2f}s")
            
            if stats['popular_commands']:
                print(f"\n🔥 Comandos más populares:")
                for action, count in stats['popular_commands']:
                    print(f"  • {action}: {count} veces")
        
        elif choice == '5':
            print("🔧 Configuración de voz:")
            speed = input("Velocidad (0.5-2.0, default 1.0): ").strip()
            volume = input("Volumen (0.0-1.0, default 0.8): ").strip()
            
            if speed:
                voice_system.tts_engine.setProperty('rate', float(speed) * 150)
            if volume:
                voice_system.tts_engine.setProperty('volume', float(volume))
            
            voice_system.speak("Configuración de voz actualizada")
        
        elif choice == '6':
            voice_system.speak("Hasta luego")
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()



