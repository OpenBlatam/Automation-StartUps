#!/usr/bin/env python3
"""
Validador de DMs - Revisa DMs antes de enviar
Verifica personalización, estructura, timing y mejores prácticas
"""

import re
import sys
from typing import List, Dict, Tuple

class ValidadorDM:
    def __init__(self):
        self.errores = []
        self.avisos = []
        self.exitos = []
    
    def validar(self, dm: str, contexto: Dict = None) -> Tuple[bool, List[str], List[str]]:
        """
        Valida un DM completo
        Retorna: (es_valido, errores, avisos)
        """
        self.errores = []
        self.avisos = []
        self.exitos = []
        
        # Validaciones obligatorias
        self._validar_variables_sin_reemplazar(dm)
        self._validar_longitud(dm)
        self._validar_estructura(dm)
        self._validar_cta(dm)
        
        # Validaciones recomendadas
        self._validar_logro_especifico(dm, contexto)
        self._validar_tono(dm, contexto)
        self._validar_metricas(dm)
        self._validar_utm_en_links(dm)
        
        es_valido = len(self.errores) == 0
        
        return es_valido, self.errores, self.avisos
    
    def _validar_variables_sin_reemplazar(self, dm: str):
        """Verifica que no haya variables sin reemplazar"""
        variables_no_reemplazadas = re.findall(r'\[(\w+)\]', dm)
        if variables_no_reemplazadas:
            self.errores.append(f"❌ Variables sin reemplazar: {', '.join(set(variables_no_reemplazadas))}")
        else:
            self.exitos.append("✅ Todas las variables reemplazadas")
    
    def _validar_longitud(self, dm: str):
        """Verifica que el DM tenga longitud apropiada"""
        lineas = dm.strip().split('\n')
        lineas_no_vacias = [l for l in lineas if l.strip()]
        
        if len(lineas_no_vacias) > 6:
            self.avisos.append(f"⚠️  DM muy largo: {len(lineas_no_vacias)} líneas (recomendado: 4-5)")
        elif len(lineas_no_vacias) < 3:
            self.avisos.append(f"⚠️  DM muy corto: {len(lineas_no_vacias)} líneas (recomendado: 4)")
        else:
            self.exitos.append(f"✅ Longitud apropiada: {len(lineas_no_vacias)} líneas")
        
        caracteres = len(dm)
        if caracteres > 500:
            self.avisos.append(f"⚠️  Muchos caracteres: {caracteres} (ideal: <400)")
        elif caracteres < 150:
            self.avisos.append(f"⚠️  Pocos caracteres: {caracteres} (puede parecer muy breve)")
        else:
            self.exitos.append(f"✅ Longitud de caracteres apropiada: {caracteres}")
    
    def _validar_estructura(self, dm: str):
        """Verifica que tenga estructura básica"""
        lineas = [l.strip() for l in dm.strip().split('\n') if l.strip()]
        
        if not any('?' in l or '¿' in l for l in lineas):
            self.avisos.append("⚠️  No se detectó pregunta final - considera añadir una")
        
        # Verifica saludo
        primera_linea = lineas[0].lower()
        saludos = ['hola', 'hi', 'hey', 'buenas', 'felicidades', 'congrats', '¡', '!']
        if not any(saludo in primera_linea for saludo in saludos):
            self.avisos.append("⚠️  No se detectó saludo apropiado en primera línea")
        else:
            self.exitos.append("✅ Saludo apropiado detectado")
    
    def _validar_cta(self, dm: str):
        """Verifica que haya CTA pero no múltiples"""
        # Detecta CTAs comunes
        cta_patterns = [
            r'¿[^?]*\?',
            r'agenda',
            r'demo',
            r'invitación',
            r'reserva',
            r'te (reservo|mando|envío|comparto)',
            r'link',
            r'interes[ae]',
            r'prefiere',
        ]
        
        matches = []
        for pattern in cta_patterns:
            matches.extend(re.findall(pattern, dm, re.IGNORECASE))
        
        if len(matches) == 0:
            self.errores.append("❌ No se detectó CTA claro - añade pregunta o siguiente paso")
        elif len(matches) > 3:
            self.avisos.append(f"⚠️  Múltiples CTAs detectados ({len(matches)}) - simplifica a 1")
        else:
            self.exitos.append("✅ CTA detectado apropiadamente")
    
    def _validar_logro_especifico(self, dm: str, contexto: Dict):
        """Verifica que el logro sea específico"""
        palabras_genéricas = ['logro', 'éxito', 'resultado', 'avance', 'crecimiento']
        if any(palabra in dm.lower() for palabra in palabras_genéricas):
            if contexto and contexto.get('achievement'):
                logro = contexto['achievement'].lower()
                if any(gen in logro for gen in palabras_genéricas):
                    self.avisos.append("⚠️  Logro mencionado parece genérico - sé más específico si es posible")
            else:
                self.avisos.append("⚠️  No se detectó logro específico en el contexto")
    
    def _validar_tono(self, dm: str, contexto: Dict):
        """Sugerencias sobre tono"""
        # Verifica excesos
        if dm.count('!') > 3:
            self.avisos.append("⚠️  Muchos signos de exclamación - puede parecer demasiado entusiasta")
        
        if dm.count('💰') > 2 or dm.count('🚀') > 2:
            self.avisos.append("⚠️  Muchos emojis - usa con moderación según perfil")
    
    def _validar_metricas(self, dm: str):
        """Verifica si hay métricas mencionadas"""
        # Detecta números que parecen métricas
        numeros = re.findall(r'\d+[x%kmKMB]', dm)
        porcentajes = re.findall(r'\d+%', dm)
        
        if numeros or porcentajes:
            self.exitos.append(f"✅ Métricas mencionadas: {', '.join((numeros + porcentajes)[:3])}")
        else:
            self.avisos.append("⚠️  No se detectaron métricas - considera añadir dato específico")
    
    def _validar_utm_en_links(self, dm: str):
        """Verifica que los links tengan UTM"""
        links = re.findall(r'https?://[^\s\)]+', dm)
        if links:
            links_sin_utm = [l for l in links if 'utm_' not in l]
            if links_sin_utm:
                self.avisos.append(f"⚠️  Links sin UTM: {len(links_sin_utm)} de {len(links)} - añade parámetros UTM")
            else:
                self.exitos.append("✅ Todos los links tienen UTM")
        else:
            self.avisos.append("⚠️  No se detectaron links - verifica si deberías incluir alguno")

def validar_dm_desde_texto(texto: str, contexto: Dict = None):
    """Función helper para validar un DM desde texto"""
    validador = ValidadorDM()
    es_valido, errores, avisos = validador.validar(texto, contexto)
    
    print("\n" + "="*60)
    print("VALIDACIÓN DE DM")
    print("="*60)
    
    if es_valido:
        print("\n✅ DM VÁLIDO - Listo para revisar")
    else:
        print("\n❌ DM CON ERRORES - Revisa antes de enviar")
    
    if validador.exitos:
        print("\n✅ Éxitos:")
        for exito in validador.exitos:
            print(f"  {exito}")
    
    if errores:
        print("\n❌ Errores (corregir obligatorio):")
        for error in errores:
            print(f"  {error}")
    
    if avisos:
        print("\n⚠️  Avisos (recomendaciones):")
        for aviso in avisos:
            print(f"  {aviso}")
    
    print("\n" + "="*60)
    
    return es_valido

if __name__ == "__main__":
    print("Validador de DMs")
    print("\nOpciones:")
    print("1. Validar DM desde archivo")
    print("2. Validar DM desde input manual")
    
    opcion = input("\nOpción (1 o 2): ").strip()
    
    if opcion == "1":
        archivo = input("Ruta del archivo: ").strip()
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                dm_texto = f.read()
            validar_dm_desde_texto(dm_texto)
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {archivo}")
            sys.exit(1)
    elif opcion == "2":
        print("\nPega tu DM completo (termina con Ctrl+D o línea vacía):")
        dm_lineas = []
        try:
            while True:
                linea = input()
                if not linea.strip():
                    break
                dm_lineas.append(linea)
        except EOFError:
            pass
        
        dm_texto = '\n'.join(dm_lineas)
        validar_dm_desde_texto(dm_texto)
    else:
        print("❌ Opción inválida")
        sys.exit(1)




