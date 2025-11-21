#!/usr/bin/env python3
"""
Exportador de Paquetes Completos
Exporta paquetes completos de plantillas organizados por categorías.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import zipfile

class ExportadorPaquetes:
    def __init__(self, directorio_base: str = "."):
        self.directorio_base = Path(directorio_base)
        self.categorias = {
            'medicina': [
                'firma_medicina', 'firma_medicina_interna', 'firma_medicina_familiar',
                'firma_medicina_emergencias', 'firma_medicina_deportiva',
                'firma_cardiologia', 'firma_neurologia', 'firma_pediatria',
                'firma_ginecologia', 'firma_ortopedia', 'firma_anestesiologia',
                'firma_psiquiatria', 'firma_oftalmologia', 'firma_dermatologia',
                'firma_radiologia', 'firma_enfermeria'
            ],
            'odontologia': [
                'firma_odontologia', 'firma_odontopediatria', 'firma_ortodoncia'
            ],
            'terapias': [
                'firma_fisioterapia', 'firma_terapia_ocupacional', 'firma_logopedia',
                'firma_podologia', 'firma_psicologia'
            ],
            'salud_bienestar': [
                'firma_nutricion', 'firma_farmacia', 'firma_estetica', 'firma_veterinaria'
            ],
            'profesionales': [
                'firma_tecnologia', 'firma_desarrollador', 'firma_consultor_ia',
                'firma_ventas', 'firma_marketing', 'firma_recursos_humanos',
                'firma_legal', 'firma_abogacia', 'firma_contabilidad', 'firma_finanzas',
                'firma_educacion', 'firma_profesor', 'firma_ingenieria'
            ],
            'empresas': [
                'firma_empresa_startup', 'firma_empresa_corporativa'
            ]
        }
    
    def crear_paquete(self, categoria: str, incluir_scripts: bool = False, incluir_docs: bool = False) -> str:
        """Crea un paquete ZIP de una categoría específica."""
        if categoria not in self.categorias:
            raise ValueError(f"Categoría no válida: {categoria}")
        
        # Crear directorio temporal
        dir_temp = self.directorio_base / f"temp_{categoria}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dir_temp.mkdir(exist_ok=True)
        
        # Copiar plantillas de la categoría
        plantillas_categoria = self.categorias[categoria]
        plantillas_encontradas = []
        
        for prefijo in plantillas_categoria:
            archivos = list(self.directorio_base.glob(f"{prefijo}*.html"))
            for archivo in archivos:
                shutil.copy2(archivo, dir_temp / archivo.name)
                plantillas_encontradas.append(archivo.name)
        
        # Copiar scripts si se solicita
        if incluir_scripts:
            dir_scripts = dir_temp / "scripts"
            dir_scripts.mkdir(exist_ok=True)
            
            scripts_utiles = [
                'personalizar_firma.py', 'validar_firma.py', 'comparar_plantillas.py',
                'generador_plantilla_personalizada.py', 'optimizador_avanzado.py',
                'validador_avanzado.py', 'convertidor_universal.py'
            ]
            
            for script in scripts_utiles:
                script_path = self.directorio_base / script
                if script_path.exists():
                    shutil.copy2(script_path, dir_scripts / script)
        
        # Copiar documentación si se solicita
        if incluir_docs:
            dir_docs = dir_temp / "documentacion"
            dir_docs.mkdir(exist_ok=True)
            
            docs_utiles = [
                'README.md', 'CHANGELOG.md', 'INDICE.md'
            ]
            
            for doc in docs_utiles:
                doc_path = self.directorio_base / doc
                if doc_path.exists():
                    shutil.copy2(doc_path, dir_docs / doc)
        
        # Crear archivo de información del paquete
        info_paquete = {
            'categoria': categoria,
            'fecha': datetime.now().isoformat(),
            'plantillas': plantillas_encontradas,
            'total_plantillas': len(plantillas_encontradas),
            'incluye_scripts': incluir_scripts,
            'incluye_docs': incluir_docs
        }
        
        with open(dir_temp / "info_paquete.json", 'w', encoding='utf-8') as f:
            json.dump(info_paquete, f, indent=2, ensure_ascii=False)
        
        # Crear README del paquete
        readme = f"""# Paquete de Plantillas - {categoria.replace('_', ' ').title()}

Este paquete contiene {len(plantillas_encontradas)} plantillas de firmas de email para el sector {categoria.replace('_', ' ')}.

## Plantillas Incluidas

"""
        for plantilla in plantillas_encontradas:
            readme += f"- {plantilla}\n"
        
        readme += f"""
## Instrucciones

1. Extrae el contenido del archivo ZIP
2. Abre las plantillas HTML en un editor de texto
3. Reemplaza los placeholders [entre corchetes] con tu información
4. Copia el código HTML completo
5. Pégalo en la configuración de firma de tu cliente de email

## Personalización

- Reemplaza [Tu Nombre] con tu nombre completo
- Reemplaza [email@ejemplo.com] con tu email
- Reemplaza [+1 234 567 890] con tu teléfono
- Reemplaza [URL_CALENDARIO] con el enlace a tu calendario
- Reemplaza otros placeholders según corresponda

## Compatibilidad

Todas las plantillas están optimizadas para:
- ✅ Gmail
- ✅ Outlook
- ✅ Apple Mail
- ✅ Yahoo Mail
- ✅ Dispositivos móviles

Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(dir_temp / "README.txt", 'w', encoding='utf-8') as f:
            f.write(readme)
        
        # Crear archivo ZIP
        nombre_zip = f"paquete_{categoria}_{datetime.now().strftime('%Y%m%d')}.zip"
        archivo_zip = self.directorio_base / nombre_zip
        
        with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dir_temp):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(dir_temp)
                    zipf.write(file_path, arcname)
        
        # Limpiar directorio temporal
        shutil.rmtree(dir_temp)
        
        print(f"✅ Paquete creado: {archivo_zip}")
        print(f"   - Plantillas: {len(plantillas_encontradas)}")
        print(f"   - Scripts: {'Sí' if incluir_scripts else 'No'}")
        print(f"   - Documentación: {'Sí' if incluir_docs else 'No'}")
        
        return str(archivo_zip)
    
    def crear_paquete_completo(self, incluir_scripts: bool = True, incluir_docs: bool = True) -> str:
        """Crea un paquete completo con todas las plantillas."""
        # Crear directorio temporal
        dir_temp = self.directorio_base / f"temp_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dir_temp.mkdir(exist_ok=True)
        
        # Copiar todas las plantillas
        plantillas = list(self.directorio_base.glob("firma_*.html"))
        plantillas_encontradas = []
        
        for plantilla in plantillas:
            shutil.copy2(plantilla, dir_temp / plantilla.name)
            plantillas_encontradas.append(plantilla.name)
        
        # Copiar scripts si se solicita
        if incluir_scripts:
            dir_scripts = dir_temp / "scripts"
            dir_scripts.mkdir(exist_ok=True)
            
            scripts = list(self.directorio_base.glob("*.py"))
            for script in scripts:
                shutil.copy2(script, dir_scripts / script.name)
        
        # Copiar documentación si se solicita
        if incluir_docs:
            dir_docs = dir_temp / "documentacion"
            dir_docs.mkdir(exist_ok=True)
            
            docs = list(self.directorio_base.glob("*.md"))
            for doc in docs:
                shutil.copy2(doc, dir_docs / doc.name)
        
        # Crear archivo de información
        info_paquete = {
            'tipo': 'completo',
            'fecha': datetime.now().isoformat(),
            'total_plantillas': len(plantillas_encontradas),
            'categorias': list(self.categorias.keys()),
            'incluye_scripts': incluir_scripts,
            'incluye_docs': incluir_docs
        }
        
        with open(dir_temp / "info_paquete.json", 'w', encoding='utf-8') as f:
            json.dump(info_paquete, f, indent=2, ensure_ascii=False)
        
        # Crear README
        readme = f"""# Paquete Completo de Plantillas de Email

Este paquete contiene {len(plantillas_encontradas)} plantillas de firmas de email para múltiples sectores e industrias.

## Categorías Incluidas

"""
        for categoria in self.categorias.keys():
            readme += f"- {categoria.replace('_', ' ').title()}\n"
        
        readme += f"""
## Instrucciones

1. Extrae el contenido del archivo ZIP
2. Navega a la categoría que te interese
3. Abre las plantillas HTML en un editor de texto
4. Reemplaza los placeholders [entre corchetes] con tu información
5. Copia el código HTML completo
6. Pégalo en la configuración de firma de tu cliente de email

## Personalización

- Reemplaza [Tu Nombre] con tu nombre completo
- Reemplaza [email@ejemplo.com] con tu email
- Reemplaza [+1 234 567 890] con tu teléfono
- Reemplaza [URL_CALENDARIO] con el enlace a tu calendario
- Reemplaza otros placeholders según corresponda

## Compatibilidad

Todas las plantillas están optimizadas para:
- ✅ Gmail
- ✅ Outlook
- ✅ Apple Mail
- ✅ Yahoo Mail
- ✅ Dispositivos móviles

Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(dir_temp / "README.txt", 'w', encoding='utf-8') as f:
            f.write(readme)
        
        # Crear archivo ZIP
        nombre_zip = f"paquete_completo_{datetime.now().strftime('%Y%m%d')}.zip"
        archivo_zip = self.directorio_base / nombre_zip
        
        with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dir_temp):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(dir_temp)
                    zipf.write(file_path, arcname)
        
        # Limpiar directorio temporal
        shutil.rmtree(dir_temp)
        
        print(f"✅ Paquete completo creado: {archivo_zip}")
        print(f"   - Plantillas: {len(plantillas_encontradas)}")
        print(f"   - Scripts: {'Sí' if incluir_scripts else 'No'}")
        print(f"   - Documentación: {'Sí' if incluir_docs else 'No'}")
        
        return str(archivo_zip)
    
    def listar_categorias(self) -> List[str]:
        """Lista todas las categorías disponibles."""
        return list(self.categorias.keys())

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Exporta paquetes de plantillas')
    parser.add_argument('accion', choices=['categoria', 'completo', 'listar'],
                       help='Acción a realizar')
    parser.add_argument('-c', '--categoria', help='Categoría para exportar')
    parser.add_argument('--sin-scripts', action='store_true',
                       help='No incluir scripts en el paquete')
    parser.add_argument('--sin-docs', action='store_true',
                       help='No incluir documentación en el paquete')
    
    args = parser.parse_args()
    
    exportador = ExportadorPaquetes()
    
    if args.accion == 'listar':
        categorias = exportador.listar_categorias()
        print("\n📦 Categorías disponibles:")
        for cat in categorias:
            print(f"   - {cat}")
    
    elif args.accion == 'categoria':
        if not args.categoria:
            print("❌ Especifica una categoría con -c")
            print("   Usa 'listar' para ver categorías disponibles")
            return
        
        exportador.crear_paquete(
            args.categoria,
            incluir_scripts=not args.sin_scripts,
            incluir_docs=not args.sin_docs
        )
    
    elif args.accion == 'completo':
        exportador.crear_paquete_completo(
            incluir_scripts=not args.sin_scripts,
            incluir_docs=not args.sin_docs
        )

if __name__ == "__main__":
    main()





