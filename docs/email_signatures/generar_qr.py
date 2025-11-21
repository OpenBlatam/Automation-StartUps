#!/usr/bin/env python3
"""
Generador de QR Codes para Firmas de Email
Crea códigos QR personalizados para incluir en firmas
"""

import qrcode
from qrcode.image.pil import PilImage
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def generar_qr(url: str, output_path: str, size: int = 200, color: str = "#1a73e8", bg_color: str = "#ffffff", logo_path: str = None):
    """
    Genera un código QR personalizado
    
    Args:
        url: URL o texto para el QR
        output_path: Ruta donde guardar la imagen
        size: Tamaño de la imagen (píxeles)
        color: Color del QR (hex)
        bg_color: Color de fondo (hex)
        logo_path: Ruta opcional a logo para centrar
    """
    # Crear QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Convertir colores hex a RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    qr_color = hex_to_rgb(color)
    bg_rgb = hex_to_rgb(bg_color)
    
    # Crear imagen
    img = qr.make_image(fill_color=qr_color, back_color=bg_rgb)
    
    # Redimensionar
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Agregar logo si se proporciona
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)
            # Redimensionar logo (20% del tamaño del QR)
            logo_size = int(size * 0.2)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Crear imagen con fondo blanco para el logo
            logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), bg_rgb)
            logo_bg.paste(logo, (10, 10))
            
            # Centrar logo en QR
            qr_width, qr_height = img.size
            logo_width, logo_height = logo_bg.size
            position = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)
            img.paste(logo_bg, position)
        except Exception as e:
            print(f"⚠️  No se pudo agregar logo: {e}")
    
    # Guardar imagen
    img.save(output_path)
    print(f"✅ QR Code generado: {output_path}")
    return output_path


def generar_qr_url_api(url: str, size: int = 120) -> str:
    """
    Genera URL para API de QR code (sin generar archivo)
    
    Args:
        url: URL para el QR
        size: Tamaño en píxeles
    
    Returns:
        URL de la API
    """
    from urllib.parse import quote
    url_encoded = quote(url)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={url_encoded}&bgcolor=ffffff&color=1a73e8"
    return qr_url


def main():
    """Función principal"""
    print("=" * 70)
    print("🔲 Generador de QR Codes para Firmas de Email")
    print("=" * 70)
    print()
    
    # Configuración
    url = input("Ingresa la URL para el QR code (o Enter para usar ejemplo): ").strip()
    if not url:
        url = "https://www.tuwebsite.com"
        print(f"Usando URL por defecto: {url}")
    
    output_dir = Path(__file__).parent / "qr_codes"
    output_dir.mkdir(exist_ok=True)
    
    # Generar diferentes tamaños
    sizes = {
        'small': 120,
        'medium': 200,
        'large': 300
    }
    
    print("\n🔄 Generando QR codes en diferentes tamaños...\n")
    
    for name, size in sizes.items():
        output_path = output_dir / f"qr_code_{name}.png"
        generar_qr(url, str(output_path), size=size)
    
    # Generar URL de API
    print("\n📋 URL de API para usar en HTML:")
    api_url = generar_qr_url_api(url)
    print(f"\n{api_url}\n")
    
    print("=" * 70)
    print("✅ Proceso completado")
    print(f"📁 Archivos guardados en: {output_dir}")
    print("\n💡 Para usar en HTML:")
    print(f'   <img src="{api_url}" alt="QR Code">')
    print("=" * 70)


if __name__ == "__main__":
    try:
        import qrcode
        import PIL
    except ImportError:
        print("❌ Faltan dependencias. Instala con:")
        print("   pip install qrcode[pil] pillow")
        exit(1)
    
    main()






