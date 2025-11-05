#!/usr/bin/env python3
import os
import subprocess
import sys

def convert_html_to_image():
    print("Convirtiendo HTML a imagen JPEG...")
    
    html_file = "Infografia_Unidad-8_AdanPablo_semana4.html"
    output_file = "Infografia_Unidad-8_AdanPablo_semana4.jpeg"
    
    if not os.path.exists(html_file):
        print(f"Error: No se encontró el archivo {html_file}")
        return False
    
    try:
        # Try using wkhtmltoimage if available
        subprocess.run(['wkhtmltoimage', '--format', 'jpeg', '--quality', '100', 
                       '--width', '1200', '--height', '800', 
                       html_file, output_file], check=True)
        print(f"✅ Imagen creada exitosamente: {output_file}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ wkhtmltoimage no está disponible")
    
    try:
        # Try using weasyprint
        import weasyprint
        from weasyprint import HTML, CSS
        
        html_doc = HTML(filename=html_file)
        html_doc.write_png(output_file.replace('.jpeg', '.png'))
        
        # Convert PNG to JPEG using PIL if available
        try:
            from PIL import Image
            img = Image.open(output_file.replace('.jpeg', '.png'))
            rgb_img = img.convert('RGB')
            rgb_img.save(output_file, 'JPEG', quality=95)
            os.remove(output_file.replace('.jpeg', '.png'))
            print(f"✅ Imagen JPEG creada exitosamente: {output_file}")
            return True
        except ImportError:
            print("✅ Imagen PNG creada. Instala PIL para convertir a JPEG.")
            return True
            
    except ImportError:
        print("❌ weasyprint no está disponible")
    
    print("\n" + "="*60)
    print("MÉTODOS MANUALES PARA CREAR LA IMAGEN:")
    print("="*60)
    print("1. CAPTURA DE PANTALLA (Más fácil):")
    print("   - La infografía está abierta en tu navegador")
    print("   - Ajusta el zoom para ver la infografía completa")
    print("   - Mac: Cmd+Shift+4, selecciona el área")
    print("   - Guarda como: Infografia_Unidad-8_AdanPablo_semana4.jpeg")
    print()
    print("2. HERRAMIENTAS DE NAVEGADOR:")
    print("   - Presiona F12 en el navegador")
    print("   - Presiona Cmd+Option+P (Mac) o Ctrl+Shift+P (Windows)")
    print("   - Busca 'screenshot' y selecciona 'Capture full size screenshot'")
    print("   - Guarda como: Infografia_Unidad-8_AdanPablo_semana4.jpeg")
    print()
    print("3. HERRAMIENTAS ONLINE:")
    print("   - Ve a: html-css-js.com/html/html-to-image")
    print("   - Copia el contenido del archivo HTML")
    print("   - Pega en la herramienta y genera la imagen")
    print("   - Descarga como JPEG")
    print("="*60)
    
    return False

if __name__ == "__main__":
    convert_html_to_image()
