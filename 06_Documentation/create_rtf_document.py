#!/usr/bin/env python3
"""
Script para crear documento RTF del Curso Premium de IA en Marketing
RTF se puede abrir directamente en Microsoft Word
"""

import os
import sys
from pathlib import Path
import re

def read_md_file(file_path):
    """Lee un archivo Markdown y retorna su contenido"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return ""
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return ""

def markdown_to_rtf(md_content):
    """Convierte Markdown básico a RTF"""
    
    # Convertir títulos
    md_content = re.sub(r'^# (.*?)$', r'\\par\\b\\fs28\\cf2 \1\\b0\\fs24\\par', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^## (.*?)$', r'\\par\\b\\fs24\\cf3 \1\\b0\\fs20\\par', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^### (.*?)$', r'\\par\\b\\fs20\\cf4 \1\\b0\\fs18\\par', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^#### (.*?)$', r'\\par\\b\\fs18\\cf5 \1\\b0\\fs16\\par', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^##### (.*?)$', r'\\par\\b\\fs16\\cf6 \1\\b0\\fs14\\par', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^###### (.*?)$', r'\\par\\b\\fs14\\cf7 \1\\b0\\fs12\\par', md_content, flags=re.MULTILINE)
    
    # Convertir negritas
    md_content = re.sub(r'\*\*(.*?)\*\*', r'\\b \1\\b0', md_content)
    md_content = re.sub(r'__(.*?)__', r'\\b \1\\b0', md_content)
    
    # Convertir cursivas
    md_content = re.sub(r'\*(.*?)\*', r'\\i \1\\i0', md_content)
    md_content = re.sub(r'_(.*?)_', r'\\i \1\\i0', md_content)
    
    # Convertir código
    md_content = re.sub(r'`(.*?)`', r'\\f1 \1\\f0', md_content)
    
    # Convertir separadores
    md_content = re.sub(r'^---$', r'\\par\\par\\line\\par\\par', md_content, flags=re.MULTILINE)
    
    # Convertir listas básicas
    lines = md_content.split('\n')
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            content = line.strip()[2:].strip()
            result_lines.append(f'\\par\\bullet {content}')
        elif line.strip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            content = line.strip()[3:].strip()
            result_lines.append(f'\\par\\tab {content}')
        else:
            if line.strip():
                result_lines.append(f'\\par {line}')
            else:
                result_lines.append('\\par')
    
    return '\\par'.join(result_lines)

def create_rtf_document(content1, content2, output_path):
    """Crea el documento RTF completo"""
    
    # Convertir contenido a RTF
    rtf_content1 = markdown_to_rtf(content1)
    rtf_content2 = markdown_to_rtf(content2)
    
    # Crear documento RTF completo
    rtf_document = f"""{{\\rtf1\\ansi\\deff0
{{\\fonttbl{{\\f0\\fswiss\\fcharset0 Calibri;}}{{\\f1\\fmodern\\fcharset0 Courier New;}}}}
{{\\colortbl;\\red0\\green0\\blue0;\\red44\\green62\\blue80;\\red52\\green73\\blue94;\\red41\\green128\\blue185;\\red142\\green68\\blue173;\\red39\\green174\\blue96;\\red231\\green76\\blue60;}}
{{\\stylesheet{{\\s0\\snext0\\sb240\\sa120\\ql\\f0\\fs24 Normal;}}}}

\\pard\\qc\\b\\fs32\\cf2 🚀 CURSO PREMIUM: INTELIGENCIA ARTIFICIAL APLICADA AL MARKETING\\b0\\fs24\\par
\\pard\\qc\\b\\fs20\\cf3 Programa de Certificación Profesional Avanzado\\b0\\fs18\\par
\\pard\\qc\\b\\fs18\\cf4 Transforma tu Carrera con IA: De Principiante a Experto en 8 Semanas\\b0\\fs16\\par

\\pard\\ql\\b\\fs16\\cf2 📋 INFORMACIÓN DEL CURSO\\b0\\fs14\\par
\\pard\\ql\\bullet 8 Módulos Principales + 12 Módulos Especializados Opcionales\\par
\\pard\\ql\\bullet 100+ Herramientas de IA premium incluidas\\par
\\pard\\ql\\bullet 50+ Casos de Estudio reales por industria\\par
\\pard\\ql\\bullet 5 Especializaciones por industria\\par
\\pard\\ql\\bullet Certificaciones verificables en blockchain\\par
\\pard\\ql\\bullet Valor total: $15,000+ en herramientas y recursos\\par
\\pard\\ql\\bullet Precio del curso: $497 (97% de descuento)\\par

\\pard\\ql\\par\\par\\line\\par\\par

{rtf_content1}

\\pard\\ql\\par\\par\\line\\par\\par

{rtf_content2}

\\pard\\ql\\par\\par\\line\\par\\par

\\pard\\qc\\i\\fs12 © 2024 - Blatam AI Marketing. Todos los derechos reservados.\\i0\\par
}}"""
    
    # Guardar archivo RTF
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(rtf_document)
        return True
    except Exception as e:
        print(f"Error guardando documento RTF: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Generando documento RTF del Curso Premium de IA en Marketing...")
    
    # Rutas de archivos
    base_dir = Path(".")
    file1 = base_dir / "AI_Marketing_Course_Complete_Structure.md"
    file2 = base_dir / "AI_Marketing_Course_Resources_Delivery_Marketing_Feedback.md"
    output_file = base_dir / "Curso_Premium_IA_Marketing_Completo.rtf"
    
    # Verificar que los archivos existen
    if not file1.exists():
        print(f"❌ Error: No se encontró {file1}")
        return False
    
    if not file2.exists():
        print(f"❌ Error: No se encontró {file2}")
        return False
    
    print("📖 Leyendo archivos Markdown...")
    
    # Leer contenido de ambos archivos
    content1 = read_md_file(file1)
    content2 = read_md_file(file2)
    
    if not content1 or not content2:
        print("❌ Error: No se pudo leer el contenido de los archivos")
        return False
    
    # Crear documento RTF
    print("📄 Creando documento RTF...")
    if create_rtf_document(content1, content2, output_file):
        print(f"✅ Documento RTF generado exitosamente: {output_file}")
        if output_file.exists():
            file_size = output_file.stat().st_size / 1024 / 1024
            print(f"📊 Tamaño del archivo: {file_size:.2f} MB")
        return True
    else:
        print("❌ Error generando documento RTF")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 ¡Documento RTF generado exitosamente!")
            print("📧 El archivo se puede abrir directamente en Microsoft Word.")
            print("💡 También es compatible con Google Docs, LibreOffice y otros editores.")
        else:
            print("\n💥 Error en la generación del documento RTF")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
