#!/usr/bin/env python3
"""
Script para crear documento Word con las narrativas
"""

def create_word_document():
    """Crea un documento Word con las narrativas"""
    
    # Leer el archivo markdown
    with open('AI_Webinar_Narrativas_Completas.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Crear documento RTF (Rich Text Format) que puede abrirse en Word
    rtf_content = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
{\colortbl;\red0\green0\blue0;\red0\green0\blue255;\red128\green128\blue128;}
\f0\fs24
"""
    
    # Procesar contenido
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            rtf_content += "\\par\n"
            continue
            
        # Título principal
        if line.startswith('# 🚀 NARRATIVAS DE MARKETING'):
            rtf_content += f"\\fs32\\b\\cf2 {line[2:]}\\b0\\fs24\\par\\par\n"
            
        # Subtítulos principales
        elif line.startswith('## '):
            rtf_content += f"\\fs28\\b\\cf2 {line[3:]}\\b0\\fs24\\par\\par\n"
            
        # Subtítulos secundarios
        elif line.startswith('### '):
            rtf_content += f"\\fs24\\b {line[4:]}\\b0\\fs20\\par\\par\n"
            
        # Subtítulos terciarios
        elif line.startswith('#### '):
            rtf_content += f"\\fs22\\b {line[5:]}\\b0\\fs20\\par\\par\n"
            
        # Listas
        elif line.startswith('- ') or line.startswith('* '):
            rtf_content += f"\\bullet {line[2:]}\\par\n"
            
        # Párrafos normales
        elif line and not line.startswith('|') and not line.startswith('---'):
            # Escapar caracteres especiales para RTF
            line = line.replace('\\', '\\\\')
            line = line.replace('{', '\\{')
            line = line.replace('}', '\\}')
            rtf_content += f"{line}\\par\n"
    
    rtf_content += "}"
    
    # Escribir archivo RTF
    with open('AI_Webinar_Narrativas_Completas.rtf', 'w', encoding='utf-8') as f:
        f.write(rtf_content)
    
    print("✅ Documento RTF creado: AI_Webinar_Narrativas_Completas.rtf")
    print("📝 Puedes abrir este archivo en Microsoft Word")
    
    return True

if __name__ == "__main__":
    create_word_document()
