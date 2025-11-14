#!/usr/bin/env python3
"""
SVG Processor: Reemplaza variables [VAR] en templates SVG
Uso: python svg_processor.py template.svg variables.json output.svg
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, Any

def replace_svg_variables(svg_content: str, variables: Dict[str, Any]) -> str:
    """
    Reemplaza variables [VAR] en SVG con valores de diccionario.
    
    Args:
        svg_content: Contenido del SVG como string
        variables: Diccionario {variable: valor}
    
    Returns:
        SVG con variables reemplazadas
    """
    result = svg_content
    
    for var, value in variables.items():
        # Buscar [VAR] o [VAR_NAME] y reemplazar
        pattern = rf'\[{var}\]'
        result = re.sub(pattern, str(value), result, flags=re.IGNORECASE)
    
    return result


def process_svg_file(svg_path: Path, variables: Dict[str, Any], output_path: Path = None) -> Path:
    """
    Procesa un archivo SVG y reemplaza variables.
    
    Args:
        svg_path: Ruta al template SVG
        variables: Diccionario de variables a reemplazar
        output_path: Ruta de salida (opcional, default: nombre_personalized.svg)
    
    Returns:
        Path al archivo procesado
    """
    if not svg_path.exists():
        raise FileNotFoundError(f"Template SVG no encontrado: {svg_path}")
    
    # Leer SVG
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Reemplazar variables
    processed_content = replace_svg_variables(svg_content, variables)
    
    # Determinar output path
    if output_path is None:
        output_path = svg_path.parent / f"{svg_path.stem}_personalized.svg"
    
    # Guardar
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"✓ SVG procesado: {output_path}")
    return output_path


def load_variables_from_json(json_path: Path) -> Dict[str, Any]:
    """Carga variables desde archivo JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Uso: python svg_processor.py <template.svg> <variables.json> [output.svg]")
        print("\nEjemplo:")
        print('  python svg_processor.py webinar-preroll-benefits-focused.svg variables.json')
        print('\nvariables.json:')
        print('  {')
        print('    "FECHA": "2025-11-15",')
        print('    "HORA": "14:00 (GMT-5)",')
        print('    "EVENTO": "Curso IA Avanzado"')
        print('  }')
        sys.exit(1)
    
    svg_path = Path(sys.argv[1])
    vars_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    
    # Validar inputs
    if not svg_path.exists():
        print(f"❌ Error: Template no encontrado: {svg_path}")
        sys.exit(1)
    
    if not vars_path.exists():
        print(f"❌ Error: Variables JSON no encontrado: {vars_path}")
        sys.exit(1)
    
    try:
        # Cargar variables
        variables = load_variables_from_json(vars_path)
        print(f"✓ Variables cargadas: {len(variables)} variables")
        
        # Procesar SVG
        result = process_svg_file(svg_path, variables, output_path)
        
        print(f"\n✅ Procesamiento completado: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()



