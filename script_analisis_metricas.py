#!/usr/bin/env python3
"""
Script de Análisis de Métricas de Outreach
Lee CSV con datos de outreach y genera análisis automático
"""

import csv
import sys
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Optional

def cargar_datos(archivo_csv: str) -> List[Dict[str, str]]:
    """Carga datos desde CSV"""
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró {archivo_csv}")
        sys.exit(1)

def calcular_tasa_respuesta(datos: List[Dict[str, str]]) -> Dict[str, float]:
    """Calcula tasa de respuesta por diferentes dimensiones"""
    resultados = {
        'general': {'enviados': 0, 'respuestas': 0},
        'por_canal': Counter(),
        'por_producto': Counter(),
        'por_industria': Counter(),
        'por_version_dm': Counter()
    }
    
    for row in datos:
        enviado = row.get('fecha_envio', '').strip() != ''
        respuesta = row.get('respuesta', '').strip().lower() in ['si', 'sí', 'yes', '1', 'true']
        
        if enviado:
            resultados['general']['enviados'] += 1
            if respuesta:
                resultados['general']['respuestas'] += 1
                
                canal = row.get('canal', 'N/A')
                producto = row.get('producto', 'N/A')
                industria = row.get('lead_industria', 'N/A')
                version = row.get('version_dm', 'N/A')
                
                resultados['por_canal'][canal] += 1
                resultados['por_producto'][producto] += 1
                resultados['por_industria'][industria] += 1
                resultados['por_version_dm'][version] += 1
    
    return resultados

def calcular_conversion(datos: List[Dict[str, str]]) -> Dict[str, float]:
    """Calcula tasa de conversión"""
    respuestas = 0
    conversiones = 0
    
    for row in datos:
        respuesta = row.get('respuesta', '').strip().lower() in ['si', 'sí', 'yes', '1', 'true']
        convertido = row.get('convertido', '').strip().lower() in ['si', 'sí', 'yes', '1', 'true']
        
        if respuesta:
            respuestas += 1
            if convertido:
                conversiones += 1
    
    tasa_conversion = (conversiones / respuestas * 100) if respuestas > 0 else 0
    
    return {
        'respuestas': respuestas,
        'conversiones': conversiones,
        'tasa_conversion': tasa_conversion
    }

def calcular_cac(datos: List[Dict[str, str]], costo_total: Optional[float] = None) -> Dict[str, float]:
    """Calcula CAC promedio"""
    conversiones = sum(1 for row in datos if row.get('convertido', '').strip().lower() in ['si', 'sí', 'yes', '1', 'true'])
    
    if costo_total is None:
        # Si no se proporciona costo, usa revenue/ROI estimado
        revenue_total = sum(float(row.get('revenue', 0) or 0) for row in datos)
        costo_estimado = revenue_total / 3  # Asumiendo ROI 3x
    else:
        costo_estimado = costo_total
    
    cac = (costo_estimado / conversiones) if conversiones > 0 else 0
    
    return {
        'conversiones': conversiones,
        'costo_total': costo_estimado,
        'cac_promedio': cac
    }

def analizar_timing(datos: List[Dict[str, str]]) -> Dict[str, any]:
    """Analiza mejores timing basado en respuestas"""
    timing_respuestas = {
        'por_dia': Counter(),
        'por_hora': Counter()
    }
    
    for row in datos:
        respuesta = row.get('respuesta', '').strip().lower() in ['si', 'sí', 'yes', '1', 'true']
        fecha_envio = row.get('fecha_envio', '')
        
        if respuesta and fecha_envio:
            try:
                fecha = datetime.strptime(fecha_envio.split()[0], '%Y-%m-%d')
                dia_semana = fecha.strftime('%A')
                
                if len(fecha_envio.split()) > 1:
                    hora_str = fecha_envio.split()[1].split(':')[0]
                    hora = int(hora_str)
                else:
                    hora = 12  # Default si no hay hora
                
                timing_respuestas['por_dia'][dia_semana] += 1
                timing_respuestas['por_hora'][f"{hora}h"] += 1
            except:
                pass
    
    return timing_respuestas

def generar_reporte(datos: List[Dict[str, str]], costo_total: Optional[float] = None):
    """Genera reporte completo"""
    print("\n" + "="*80)
    print("📊 REPORTE DE ANÁLISIS DE OUTREACH")
    print("="*80 + "\n")
    
    # Tasa de respuesta
    tasa = calcular_tasa_respuesta(datos)
    total_enviados = tasa['general']['enviados']
    total_respuestas = tasa['general']['respuestas']
    tasa_general = (total_respuestas / total_enviados * 100) if total_enviados > 0 else 0
    
    print(f"📈 TASA DE RESPUESTA GENERAL")
    print(f"   Enviados: {total_enviados}")
    print(f"   Respuestas: {total_respuestas}")
    print(f"   Tasa: {tasa_general:.2f}%\n")
    
    # Por canal
    print("📱 POR CANAL:")
    for canal, respuestas in tasa['por_canal'].most_common():
        tasa_canal = (respuestas / total_respuestas * 100) if total_respuestas > 0 else 0
        print(f"   {canal}: {respuestas} respuestas ({tasa_canal:.1f}% del total)")
    
    # Por producto
    print("\n📦 POR PRODUCTO:")
    for producto, respuestas in tasa['por_producto'].most_common():
        tasa_producto = (respuestas / total_respuestas * 100) if total_respuestas > 0 else 0
        print(f"   {producto}: {respuestas} respuestas ({tasa_producto:.1f}% del total)")
    
    # Conversión
    conversion = calcular_conversion(datos)
    print(f"\n💰 TASA DE CONVERSIÓN")
    print(f"   Respuestas: {conversion['respuestas']}")
    print(f"   Conversiones: {conversion['conversiones']}")
    print(f"   Tasa: {conversion['tasa_conversion']:.2f}%\n")
    
    # CAC
    cac = calcular_cac(datos, costo_total)
    print(f"💵 CAC (Costo de Adquisición)")
    print(f"   Conversiones: {cac['conversiones']}")
    print(f"   CAC Promedio: ${cac['cac_promedio']:.2f}\n")
    
    # Timing
    timing = analizar_timing(datos)
    print("⏰ TIMING ÓPTIMO (Basado en Respuestas)")
    print("   Por día:")
    for dia, count in timing['por_dia'].most_common(3):
        print(f"      {dia}: {count} respuestas")
    print("   Por hora:")
    for hora, count in timing['por_hora'].most_common(3):
        print(f"      {hora}: {count} respuestas")
    
    print("\n" + "="*80)
    print("✅ Análisis completado")
    print("="*80 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python SCRIPT_ANALISIS_METRICAS.py <archivo.csv> [costo_total]")
        print("\nEjemplo: python SCRIPT_ANALISIS_METRICAS.py datos_outreach.csv 5000")
        sys.exit(1)
    
    archivo_csv = sys.argv[1]
    costo_total = float(sys.argv[2]) if len(sys.argv) > 2 else None
    
    datos = cargar_datos(archivo_csv)
    generar_reporte(datos, costo_total)




