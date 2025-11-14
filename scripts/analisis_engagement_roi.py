#!/usr/bin/env python3
"""
Análisis de ROI Avanzado de Engagement - Mejoras Premium
=========================================================
Análisis avanzado de ROI y valor de negocio:
- Análisis de ROI detallado por tipo de contenido
- Análisis de ROI por plataforma
- Cálculo de valor de cliente generado
- Análisis de costo por engagement
- ROI proyectado a futuro
- Análisis de break-even
- Comparación de inversión vs retorno
- Recomendaciones de inversión optimizada
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
    from analisis_engagement_mejorado import AnalizadorEngagementMejorado
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorROIEngagement:
    """Analizador avanzado de ROI de engagement"""
    
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None
    ):
        """
        Inicializa el analizador de ROI
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
        """
        self.analizador = analizador_base
        self.analizador_ai = analizador_ai or AnalizadorEngagementAI(analizador_base)
        self.analizador_mejorado = analizador_mejorado or AnalizadorEngagementMejorado(
            analizador_base, self.analizador_ai
        )
        
        # Costos estimados por tipo de contenido (en horas y USD)
        self.costos_contenido = {
            'X': {'horas': 4, 'costo_hora': 50, 'costo_total': 200},
            'Y': {'horas': 2, 'costo_hora': 50, 'costo_total': 100},
            'Z': {'horas': 1, 'costo_hora': 50, 'costo_total': 50}
        }
        
        # Valor estimado por engagement
        self.valor_engagement = {
            'like': 0.10,
            'comentario': 0.50,
            'share': 2.00,
            'impresion': 0.01,
            'reach': 0.02
        }
    
    def analizar_roi_detallado(self) -> Dict[str, Any]:
        """
        Análisis detallado de ROI completo
        
        Returns:
            Análisis completo de ROI con múltiples métricas
        """
        reporte = self.analizador.generar_reporte()
        resumen = reporte.get('resumen_ejecutivo', {})
        
        # ROI por tipo de contenido
        roi_por_tipo = {}
        for tipo_key in ['X', 'Y', 'Z']:
            publicaciones_tipo = [p for p in self.analizador.publicaciones if p.tipo_contenido == tipo_key]
            if publicaciones_tipo:
                roi_por_tipo[tipo_key] = self._calcular_roi_tipo(tipo_key, publicaciones_tipo)
        
        # ROI por plataforma
        roi_por_plataforma = {}
        plataformas = set(p.plataforma for p in self.analizador.publicaciones)
        for plataforma in plataformas:
            publicaciones_plataforma = [p for p in self.analizador.publicaciones if p.plataforma == plataforma]
            if publicaciones_plataforma:
                roi_por_plataforma[plataforma] = self._calcular_roi_plataforma(plataforma, publicaciones_plataforma)
        
        # ROI total
        roi_total = self._calcular_roi_total()
        
        # Análisis de break-even
        break_even = self._analizar_break_even()
        
        # Proyección futura
        proyeccion = self._proyectar_roi_futuro(roi_total)
        
        return {
            "periodo_analizado": f"{len(self.analizador.publicaciones)} publicaciones",
            "roi_total": roi_total,
            "roi_por_tipo": roi_por_tipo,
            "roi_por_plataforma": roi_por_plataforma,
            "break_even": break_even,
            "proyeccion_futura": proyeccion,
            "recomendaciones_inversion": self._generar_recomendaciones_inversion(roi_por_tipo, roi_por_plataforma)
        }
    
    def _calcular_roi_tipo(self, tipo: str, publicaciones: List[Publicacion]) -> Dict[str, Any]:
        """Calcula ROI para un tipo de contenido"""
        costo_info = self.costos_contenido.get(tipo, {'costo_total': 100})
        costo_total = costo_info['costo_total'] * len(publicaciones)
        
        # Calcular valor generado
        valor_total = 0
        total_engagement = 0
        
        for pub in publicaciones:
            valor_pub = (
                pub.likes * self.valor_engagement['like'] +
                pub.comentarios * self.valor_engagement['comentario'] +
                pub.shares * self.valor_engagement['share'] +
                pub.impresiones * self.valor_engagement['impresion'] +
                pub.reach * self.valor_engagement['reach']
            )
            valor_total += valor_pub
            total_engagement += pub.engagement_total
        
        # Calcular ROI
        roi_absoluto = valor_total - costo_total
        roi_porcentual = ((valor_total - costo_total) / costo_total * 100) if costo_total > 0 else 0
        
        # Costo por engagement
        costo_por_engagement = costo_total / total_engagement if total_engagement > 0 else 0
        
        # Valor por engagement
        valor_por_engagement = valor_total / total_engagement if total_engagement > 0 else 0
        
        return {
            "tipo": tipo,
            "cantidad_publicaciones": len(publicaciones),
            "costo_total": round(costo_total, 2),
            "valor_generado": round(valor_total, 2),
            "roi_absoluto": round(roi_absoluto, 2),
            "roi_porcentual": round(roi_porcentual, 2),
            "costo_por_engagement": round(costo_por_engagement, 4),
            "valor_por_engagement": round(valor_por_engagement, 4),
            "total_engagement": total_engagement,
            "publicaciones_necesarias_roi_positivo": self._calcular_publicaciones_roi_positivo(
                tipo, valor_total / len(publicaciones) if publicaciones else 0
            )
        }
    
    def _calcular_roi_plataforma(self, plataforma: str, publicaciones: List[Publicacion]) -> Dict[str, Any]:
        """Calcula ROI para una plataforma"""
        # Determinar tipo promedio para estimar costo
        tipos = [p.tipo_contenido for p in publicaciones]
        tipo_mas_comun = max(set(tipos), key=tipos.count) if tipos else 'Y'
        costo_info = self.costos_contenido.get(tipo_mas_comun, {'costo_total': 100})
        costo_total = costo_info['costo_total'] * len(publicaciones)
        
        # Calcular valor generado
        valor_total = 0
        total_engagement = 0
        
        for pub in publicaciones:
            valor_pub = (
                pub.likes * self.valor_engagement['like'] +
                pub.comentarios * self.valor_engagement['comentario'] +
                pub.shares * self.valor_engagement['share'] +
                pub.impresiones * self.valor_engagement['impresion'] +
                pub.reach * self.valor_engagement['reach']
            )
            valor_total += valor_pub
            total_engagement += pub.engagement_total
        
        roi_absoluto = valor_total - costo_total
        roi_porcentual = ((valor_total - costo_total) / costo_total * 100) if costo_total > 0 else 0
        
        return {
            "plataforma": plataforma,
            "cantidad_publicaciones": len(publicaciones),
            "costo_total": round(costo_total, 2),
            "valor_generado": round(valor_total, 2),
            "roi_absoluto": round(roi_absoluto, 2),
            "roi_porcentual": round(roi_porcentual, 2),
            "total_engagement": total_engagement
        }
    
    def _calcular_roi_total(self) -> Dict[str, Any]:
        """Calcula ROI total del período"""
        costo_total = 0
        valor_total = 0
        total_engagement = 0
        
        for pub in self.analizador.publicaciones:
            costo_info = self.costos_contenido.get(pub.tipo_contenido, {'costo_total': 100})
            costo_total += costo_info['costo_total']
            
            valor_pub = (
                pub.likes * self.valor_engagement['like'] +
                pub.comentarios * self.valor_engagement['comentario'] +
                pub.shares * self.valor_engagement['share'] +
                pub.impresiones * self.valor_engagement['impresion'] +
                pub.reach * self.valor_engagement['reach']
            )
            valor_total += valor_pub
            total_engagement += pub.engagement_total
        
        roi_absoluto = valor_total - costo_total
        roi_porcentual = ((valor_total - costo_total) / costo_total * 100) if costo_total > 0 else 0
        
        return {
            "costo_total": round(costo_total, 2),
            "valor_generado": round(valor_total, 2),
            "roi_absoluto": round(roi_absoluto, 2),
            "roi_porcentual": round(roi_porcentual, 2),
            "total_publicaciones": len(self.analizador.publicaciones),
            "total_engagement": total_engagement,
            "costo_por_publicacion": round(costo_total / len(self.analizador.publicaciones), 2) if self.analizador.publicaciones else 0,
            "valor_por_publicacion": round(valor_total / len(self.analizador.publicaciones), 2) if self.analizador.publicaciones else 0
        }
    
    def _calcular_publicaciones_roi_positivo(self, tipo: str, valor_promedio: float) -> int:
        """Calcula cuántas publicaciones se necesitan para ROI positivo"""
        costo_info = self.costos_contenido.get(tipo, {'costo_total': 100})
        costo_por_publicacion = costo_info['costo_total']
        
        if valor_promedio <= 0:
            return 999999  # Nunca alcanzará ROI positivo
        
        publicaciones_necesarias = int(costo_por_publicacion / valor_promedio) + 1
        return max(1, publicaciones_necesarias)
    
    def _analizar_break_even(self) -> Dict[str, Any]:
        """Analiza punto de break-even"""
        roi_total = self._calcular_roi_total()
        
        costo_total = roi_total['costo_total']
        valor_total = roi_total['valor_generado']
        
        if valor_total == 0:
            return {
                "break_even_alcanzado": False,
                "publicaciones_para_break_even": len(self.analizador.publicaciones) * 2,
                "mensaje": "No se ha generado valor suficiente"
            }
        
        valor_por_publicacion = valor_total / len(self.analizador.publicaciones) if self.analizador.publicaciones else 0
        costo_promedio_por_publicacion = costo_total / len(self.analizador.publicaciones) if self.analizador.publicaciones else 0
        
        if valor_por_publicacion >= costo_promedio_por_publicacion:
            publicaciones_break_even = int(costo_promedio_por_publicacion / valor_por_publicacion) if valor_por_publicacion > 0 else 0
            return {
                "break_even_alcanzado": True,
                "publicaciones_para_break_even": max(1, publicaciones_break_even),
                "valor_por_publicacion": round(valor_por_publicacion, 2),
                "costo_por_publicacion": round(costo_promedio_por_publicacion, 2)
            }
        else:
            return {
                "break_even_alcanzado": False,
                "publicaciones_para_break_even": int(costo_promedio_por_publicacion / valor_por_publicacion) if valor_por_publicacion > 0 else 999999,
                "mensaje": "Se necesitan más publicaciones para alcanzar break-even"
            }
    
    def _proyectar_roi_futuro(self, roi_actual: Dict[str, Any], meses: int = 3) -> Dict[str, Any]:
        """Proyecta ROI a futuro"""
        publicaciones_por_mes = len(self.analizador.publicaciones) / 1  # Asumiendo 1 mes de datos
        
        proyecciones = []
        for mes in range(1, meses + 1):
            publicaciones_proyectadas = int(publicaciones_por_mes * mes)
            costo_proyectado = roi_actual['costo_por_publicacion'] * publicaciones_proyectadas
            valor_proyectado = roi_actual['valor_por_publicacion'] * publicaciones_proyectadas
            roi_proyectado = valor_proyectado - costo_proyectado
            
            proyecciones.append({
                "mes": mes,
                "publicaciones_proyectadas": publicaciones_proyectadas,
                "costo_proyectado": round(costo_proyectado, 2),
                "valor_proyectado": round(valor_proyectado, 2),
                "roi_proyectado": round(roi_proyectado, 2),
                "roi_porcentual_proyectado": round((roi_proyectado / costo_proyectado * 100) if costo_proyectado > 0 else 0, 2)
            })
        
        return {
            "periodo_proyeccion": f"{meses} meses",
            "tasa_crecimiento_asumida": "basada en datos históricos",
            "proyecciones": proyecciones
        }
    
    def _generar_recomendaciones_inversion(
        self,
        roi_por_tipo: Dict[str, Any],
        roi_por_plataforma: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones de inversión optimizada"""
        recomendaciones = []
        
        # Encontrar mejor ROI por tipo
        mejor_tipo = None
        mejor_roi_tipo = -999999
        for tipo, datos in roi_por_tipo.items():
            if datos.get('roi_porcentual', 0) > mejor_roi_tipo:
                mejor_roi_tipo = datos['roi_porcentual']
                mejor_tipo = tipo
        
        if mejor_tipo:
            recomendaciones.append({
                "tipo": "tipo_contenido",
                "recomendacion": f"Invertir más en contenido tipo {mejor_tipo}",
                "roi_actual": mejor_roi_tipo,
                "impacto_esperado": "Alto",
                "prioridad": "ALTA"
            })
        
        # Encontrar mejor ROI por plataforma
        mejor_plataforma = None
        mejor_roi_plataforma = -999999
        for plataforma, datos in roi_por_plataforma.items():
            if datos.get('roi_porcentual', 0) > mejor_roi_plataforma:
                mejor_roi_plataforma = datos['roi_porcentual']
                mejor_plataforma = plataforma
        
        if mejor_plataforma:
            recomendaciones.append({
                "tipo": "plataforma",
                "recomendacion": f"Invertir más en {mejor_plataforma}",
                "roi_actual": mejor_roi_plataforma,
                "impacto_esperado": "Alto",
                "prioridad": "ALTA"
            })
        
        # Recomendaciones de optimización de costos
        tipos_costosos = [tipo for tipo, datos in roi_por_tipo.items() if datos.get('roi_porcentual', 0) < 0]
        if tipos_costosos:
            recomendaciones.append({
                "tipo": "optimizacion_costo",
                "recomendacion": f"Revisar costos de tipos: {', '.join(tipos_costosos)}",
                "impacto_esperado": "Medio",
                "prioridad": "MEDIA"
            })
        
        return recomendaciones


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis de ROI de Engagement')
    parser.add_argument('--publicaciones', type=int, default=30, help='Número de publicaciones')
    parser.add_argument('--proyeccion', type=int, default=3, help='Meses para proyección')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    analizador_roi = AnalizadorROIEngagement(analizador_base)
    
    print("\n💰 Analizando ROI...")
    analisis_roi = analizador_roi.analizar_roi_detallado()
    
    print("\n" + "="*80)
    print("ANÁLISIS DE ROI DETALLADO")
    print("="*80)
    
    roi_total = analisis_roi['roi_total']
    print(f"\n📊 ROI TOTAL:")
    print(f"   Costo Total: ${roi_total['costo_total']:.2f}")
    print(f"   Valor Generado: ${roi_total['valor_generado']:.2f}")
    print(f"   ROI Absoluto: ${roi_total['roi_absoluto']:.2f}")
    print(f"   ROI Porcentual: {roi_total['roi_porcentual']:.2f}%")
    
    print(f"\n📈 ROI POR TIPO DE CONTENIDO:")
    for tipo, datos in analisis_roi['roi_por_tipo'].items():
        print(f"\n   Tipo {tipo}:")
        print(f"     Publicaciones: {datos['cantidad_publicaciones']}")
        print(f"     Costo: ${datos['costo_total']:.2f}")
        print(f"     Valor: ${datos['valor_generado']:.2f}")
        print(f"     ROI: {datos['roi_porcentual']:.2f}%")
    
    print(f"\n📱 ROI POR PLATAFORMA:")
    for plataforma, datos in analisis_roi['roi_por_plataforma'].items():
        print(f"   {plataforma}: ROI {datos['roi_porcentual']:.2f}% (Valor: ${datos['valor_generado']:.2f})")
    
    if analisis_roi.get('break_even'):
        be = analisis_roi['break_even']
        print(f"\n⚖️  BREAK-EVEN:")
        print(f"   Alcanzado: {'Sí' if be.get('break_even_alcanzado') else 'No'}")
        print(f"   Publicaciones necesarias: {be.get('publicaciones_para_break_even', 'N/A')}")
    
    if analisis_roi.get('recomendaciones_inversion'):
        print(f"\n💡 RECOMENDACIONES DE INVERSIÓN:")
        for rec in analisis_roi['recomendaciones_inversion']:
            print(f"   [{rec['prioridad']}] {rec['recomendacion']}")


if __name__ == "__main__":
    main()



