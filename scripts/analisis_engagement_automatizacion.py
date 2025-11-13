#!/usr/bin/env python3
"""
Sistema de Automatización de Engagement - Mejoras Avanzadas
===========================================================
Sistema completo de automatización:
- Monitoreo automático continuo
- Alertas inteligentes configurables
- Acciones automáticas basadas en umbrales
- Programación automática de contenido
- Optimización automática en tiempo real
- Reportes automáticos programados
- Integración con workflows
- Dashboard de monitoreo en tiempo real
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
    from analisis_engagement_mejorado import AnalizadorEngagementMejorado
    from analisis_engagement_optimizador import OptimizadorEngagement
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SistemaAutomatizacionEngagement:
    """Sistema completo de automatización de engagement"""
    
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None,
        optimizador: Optional[OptimizadorEngagement] = None
    ):
        """
        Inicializa el sistema de automatización
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
            optimizador: Instancia opcional del OptimizadorEngagement
        """
        self.analizador = analizador_base
        self.analizador_ai = analizador_ai or AnalizadorEngagementAI(analizador_base)
        self.analizador_mejorado = analizador_mejorado or AnalizadorEngagementMejorado(
            analizador_base, self.analizador_ai
        )
        self.optimizador = optimizador or OptimizadorEngagement(
            analizador_base, self.analizador_ai, self.analizador_mejorado
        )
        
        self.alertas_configuradas = []
        self.acciones_automaticas = []
        self.historial_monitoreo = []
    
    def configurar_alerta(
        self,
        nombre: str,
        condicion: Callable,
        umbral: float,
        nivel: str = "MEDIA",
        accion: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Configura una alerta automática
        
        Args:
            nombre: Nombre de la alerta
            condicion: Función que evalúa la condición
            umbral: Valor umbral para la alerta
            nivel: Nivel de alerta (BAJA, MEDIA, ALTA, CRITICA)
            accion: Función opcional a ejecutar cuando se dispara
        
        Returns:
            Configuración de la alerta
        """
        alerta = {
            "nombre": nombre,
            "condicion": condicion,
            "umbral": umbral,
            "nivel": nivel,
            "accion": accion,
            "activa": True,
            "veces_disparada": 0,
            "ultima_disparada": None
        }
        
        self.alertas_configuradas.append(alerta)
        return alerta
    
    def monitorear_continuo(
        self,
        intervalo_minutos: int = 60,
        duracion_horas: int = 24,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Monitoreo continuo automático
        
        Args:
            intervalo_minutos: Intervalo entre verificaciones (minutos)
            duracion_horas: Duración del monitoreo (horas)
            callback: Función opcional a llamar en cada verificación
        
        Returns:
            Resultado del monitoreo
        """
        inicio = datetime.now()
        fin = inicio + timedelta(hours=duracion_horas)
        verificaciones = []
        alertas_disparadas = []
        
        logger.info(f"Iniciando monitoreo continuo por {duracion_horas} horas")
        
        while datetime.now() < fin:
            # Generar reporte actual
            reporte = self.analizador.generar_reporte()
            resumen = reporte.get('resumen_ejecutivo', {})
            
            verificacion = {
                "timestamp": datetime.now().isoformat(),
                "engagement_rate": resumen.get('engagement_rate_promedio', 0),
                "engagement_score": resumen.get('engagement_score_promedio', 0),
                "alertas": []
            }
            
            # Verificar alertas
            for alerta in self.alertas_configuradas:
                if not alerta.get('activa', True):
                    continue
                
                try:
                    valor_actual = alerta['condicion'](reporte, resumen)
                    
                    if valor_actual <= alerta['umbral']:
                        alerta['veces_disparada'] += 1
                        alerta['ultima_disparada'] = datetime.now().isoformat()
                        
                        alerta_info = {
                            "nombre": alerta['nombre'],
                            "nivel": alerta['nivel'],
                            "valor_actual": valor_actual,
                            "umbral": alerta['umbral']
                        }
                        
                        verificacion['alertas'].append(alerta_info)
                        alertas_disparadas.append(alerta_info)
                        
                        # Ejecutar acción si está configurada
                        if alerta.get('accion'):
                            try:
                                alerta['accion'](alerta_info, reporte)
                            except Exception as e:
                                logger.error(f"Error ejecutando acción de alerta: {e}")
                except Exception as e:
                    logger.error(f"Error verificando alerta {alerta['nombre']}: {e}")
            
            verificaciones.append(verificacion)
            
            # Llamar callback si está configurado
            if callback:
                try:
                    callback(verificacion)
                except Exception as e:
                    logger.error(f"Error en callback: {e}")
            
            # Esperar hasta siguiente verificación
            if datetime.now() < fin:
                time.sleep(intervalo_minutos * 60)
        
        resultado = {
            "inicio": inicio.isoformat(),
            "fin": datetime.now().isoformat(),
            "duracion_horas": duracion_horas,
            "verificaciones": len(verificaciones),
            "alertas_disparadas": len(alertas_disparadas),
            "resumen_alertas": self._resumir_alertas(alertas_disparadas),
            "verificaciones": verificaciones[-10:]  # Últimas 10 verificaciones
        }
        
        self.historial_monitoreo.append(resultado)
        return resultado
    
    def _resumir_alertas(self, alertas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resume las alertas disparadas"""
        resumen = defaultdict(int)
        for alerta in alertas:
            resumen[alerta['nivel']] += 1
        return dict(resumen)
    
    def generar_reporte_automatico(
        self,
        frecuencia: str = "diario",
        formato: str = "html",
        destinatarios: List[str] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte automático según frecuencia
        
        Args:
            frecuencia: Frecuencia (diario, semanal, mensual)
            formato: Formato del reporte (html, pdf, json)
            destinatarios: Lista de destinatarios (opcional)
        
        Returns:
            Información del reporte generado
        """
        reporte = self.analizador.generar_reporte()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        archivos_generados = {}
        
        if formato in ['html', 'todos']:
            html_file = f"reporte_auto_{frecuencia}_{timestamp}.html"
            self.analizador.exportar_html(reporte, html_file)
            archivos_generados['html'] = html_file
        
        if formato in ['json', 'todos']:
            json_file = f"reporte_auto_{frecuencia}_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
            archivos_generados['json'] = json_file
        
        return {
            "frecuencia": frecuencia,
            "formato": formato,
            "archivos": archivos_generados,
            "destinatarios": destinatarios or [],
            "timestamp": datetime.now().isoformat(),
            "instrucciones": "Usar servicio de email para enviar a destinatarios"
        }
    
    def optimizar_automaticamente(
        self,
        contenido: Dict[str, Any],
        aplicar_cambios: bool = False
    ) -> Dict[str, Any]:
        """
        Optimiza contenido automáticamente
        
        Args:
            contenido: Diccionario con información del contenido
            aplicar_cambios: Si aplicar cambios automáticamente
        
        Returns:
            Optimizaciones sugeridas o aplicadas
        """
        optimizaciones = self.optimizador.optimizar_contenido(
            tipo_contenido=contenido.get('tipo', 'Y'),
            plataforma=contenido.get('plataforma', 'Instagram'),
            titulo_original=contenido.get('titulo', ''),
            hashtags_originales=contenido.get('hashtags', []),
            hora_original=contenido.get('hora', 10),
            dia_original=contenido.get('dia', 'Monday')
        )
        
        if aplicar_cambios and optimizaciones.get('optimizaciones'):
            # Aplicar optimizaciones de alta prioridad automáticamente
            contenido_optimizado = contenido.copy()
            
            for opt in optimizaciones['optimizaciones']:
                if opt.get('prioridad') == 'ALTA':
                    if opt['tipo'] == 'titulo' and 'mejor_recomendacion' in opt:
                        contenido_optimizado['titulo'] = opt['mejor_recomendacion'].get('solucion', contenido['titulo'])
                    elif opt['tipo'] == 'hashtags' and 'recomendado' in opt:
                        contenido_optimizado['hashtags'] = opt['recomendado']
                    elif opt['tipo'] == 'timing' and 'recomendaciones' in opt:
                        mejor_rec = max(opt['recomendaciones'], key=lambda x: x.get('impacto', 0))
                        if 'hora' in mejor_rec.get('solucion', ''):
                            contenido_optimizado['hora'] = self._extraer_hora(mejor_rec['solucion'])
            
            return {
                "optimizaciones_aplicadas": True,
                "contenido_original": contenido,
                "contenido_optimizado": contenido_optimizado,
                "mejora_estimada": optimizaciones.get('prediccion_mejorada', {}).get('mejora_porcentual', 0)
            }
        
        return {
            "optimizaciones_aplicadas": False,
            "optimizaciones_sugeridas": optimizaciones
        }
    
    def _extraer_hora(self, texto: str) -> int:
        """Extrae hora de un texto"""
        import re
        match = re.search(r'(\d{1,2}):00', texto)
        if match:
            return int(match.group(1))
        return 10
    
    def programar_contenido_optimizado(
        self,
        tipo_contenido: str,
        plataforma: str,
        fecha_publicacion: datetime,
        contenido_base: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Programa contenido con optimización automática
        
        Args:
            tipo_contenido: Tipo de contenido
            plataforma: Plataforma objetivo
            fecha_publicacion: Fecha y hora de publicación
            contenido_base: Contenido base a optimizar
        
        Returns:
            Contenido optimizado y programado
        """
        # Optimizar contenido
        contenido_optimizado = self.optimizar_automaticamente({
            'tipo': tipo_contenido,
            'plataforma': plataforma,
            'titulo': contenido_base.get('titulo', ''),
            'hashtags': contenido_base.get('hashtags', []),
            'hora': fecha_publicacion.hour,
            'dia': fecha_publicacion.strftime('%A')
        }, aplicar_cambios=True)
        
        # Predecir engagement
        prediccion = self.analizador_mejorado.predecir_contenido_viral(
            tipo_contenido=tipo_contenido,
            plataforma=plataforma,
            titulo=contenido_optimizado.get('contenido_optimizado', {}).get('titulo', contenido_base.get('titulo', '')),
            hashtags=contenido_optimizado.get('contenido_optimizado', {}).get('hashtags', contenido_base.get('hashtags', [])),
            tiene_media=contenido_base.get('tiene_media', True),
            hora_publicacion=fecha_publicacion.hour,
            dia_semana=fecha_publicacion.strftime('%A')
        )
        
        return {
            "contenido_programado": {
                "tipo": tipo_contenido,
                "plataforma": plataforma,
                "fecha_publicacion": fecha_publicacion.isoformat(),
                "contenido": contenido_optimizado.get('contenido_optimizado', contenido_base),
                "prediccion_engagement": prediccion.get('prediccion_engagement', {}),
                "score_viral": prediccion.get('score_viral', 0)
            },
            "optimizaciones_aplicadas": contenido_optimizado.get('optimizaciones_aplicadas', False),
            "mejora_estimada": contenido_optimizado.get('mejora_estimada', 0)
        }


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Automatización de Engagement')
    parser.add_argument('--publicaciones', type=int, default=30, help='Número de publicaciones')
    parser.add_argument('--configurar-alertas', action='store_true', help='Configurar alertas de ejemplo')
    parser.add_argument('--monitorear', action='store_true', help='Iniciar monitoreo continuo')
    parser.add_argument('--reporte-auto', action='store_true', help='Generar reporte automático')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    sistema_auto = SistemaAutomatizacionEngagement(analizador_base)
    
    # Configurar alertas de ejemplo
    if args.configurar_alertas:
        print("\n🔔 Configurando alertas...")
        
        # Alerta: Engagement rate bajo
        sistema_auto.configurar_alerta(
            nombre="Engagement Rate Bajo",
            condicion=lambda r, s: s.get('engagement_rate_promedio', 0),
            umbral=1.0,
            nivel="CRITICA"
        )
        
        # Alerta: Contenido viral bajo
        sistema_auto.configurar_alerta(
            nombre="Bajo Contenido Viral",
            condicion=lambda r, s: s.get('contenido_viral_porcentaje', 0),
            umbral=2.0,
            nivel="ALTA"
        )
        
        print(f"✅ {len(sistema_auto.alertas_configuradas)} alertas configuradas")
    
    # Monitoreo continuo (versión corta para demo)
    if args.monitorear:
        print("\n📊 Iniciando monitoreo continuo (versión demo: 1 minuto)...")
        resultado = sistema_auto.monitorear_continuo(
            intervalo_minutos=0.1,  # 6 segundos para demo
            duracion_horas=0.017  # 1 minuto
        )
        print(f"✅ Monitoreo completado:")
        print(f"   Verificaciones: {resultado['verificaciones']}")
        print(f"   Alertas disparadas: {resultado['alertas_disparadas']}")
    
    # Reporte automático
    if args.reporte_auto:
        print("\n📧 Generando reporte automático...")
        reporte = sistema_auto.generar_reporte_automatico(
            frecuencia="diario",
            formato="todos"
        )
        print(f"✅ Reporte generado:")
        for tipo, archivo in reporte['archivos'].items():
            print(f"   {tipo.upper()}: {archivo}")


if __name__ == "__main__":
    main()


