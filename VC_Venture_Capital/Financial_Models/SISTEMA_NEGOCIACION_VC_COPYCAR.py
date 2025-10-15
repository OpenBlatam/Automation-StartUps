#!/usr/bin/env python3
"""
Sistema de Negociación VC para CopyCar.ai
Neural Marketing AI - SaaS IA LATAM
Sistema avanzado de negociación con VCs
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class SistemaNegociacionVCCopyCar:
    def __init__(self):
        self.vcs_target = {}
        self.estrategias_negociacion = {}
        self.metricas_negociacion = {}
        self.escenarios_negociacion = {}
        
    def definir_vcs_target(self):
        """Define VCs objetivo para CopyCar.ai"""
        self.vcs_target = {
            'vcs_latam': {
                'kaszek': {
                    'nombre': 'Kaszek Ventures',
                    'fondo': '$1.2B',
                    'check_tipico': '$2M-$15M',
                    'stage': 'Seed-Series B',
                    'portfolio_ai': ['Nubank', 'Rappi', 'MercadoLibre'],
                    'thesis': 'AI y fintech en LATAM',
                    'decision_time': '2-4 semanas',
                    'board_seats': 1,
                    'follow_on_rate': 0.85,
                    'valor_agregado': 'Red LATAM, expertise fintech',
                    'fit_score': 0.95
                },
                'monashees': {
                    'nombre': 'Monashees',
                    'fondo': '$400M',
                    'check_tipico': '$1M-$8M',
                    'stage': 'Pre-Seed-Series A',
                    'portfolio_ai': ['99', 'Loggi', 'CargoX'],
                    'thesis': 'Marketplaces y AI en LATAM',
                    'decision_time': '3-6 semanas',
                    'board_seats': 1,
                    'follow_on_rate': 0.80,
                    'valor_agregado': 'Expertise marketplaces, red Brasil',
                    'fit_score': 0.90
                },
                'canary': {
                    'nombre': 'Canary',
                    'fondo': '$200M',
                    'check_tipico': '$500K-$5M',
                    'stage': 'Pre-Seed-Series A',
                    'portfolio_ai': ['Caju', 'Zippi', 'Caju'],
                    'thesis': 'B2B SaaS y AI en LATAM',
                    'decision_time': '2-3 semanas',
                    'board_seats': 1,
                    'follow_on_rate': 0.75,
                    'valor_agregado': 'Expertise B2B, red México',
                    'fit_score': 0.88
                }
            },
            'vcs_globales': {
                'sequoia': {
                    'nombre': 'Sequoia Capital',
                    'fondo': '$8B',
                    'check_tipico': '$5M-$50M',
                    'stage': 'Series A+',
                    'portfolio_ai': ['OpenAI', 'Stripe', 'WhatsApp'],
                    'thesis': 'AI y software global',
                    'decision_time': '4-8 semanas',
                    'board_seats': 1-2,
                    'follow_on_rate': 0.90,
                    'valor_agregado': 'Red global, expertise AI',
                    'fit_score': 0.85
                },
                'a16z': {
                    'nombre': 'Andreessen Horowitz',
                    'fondo': '$7B',
                    'check_tipico': '$3M-$30M',
                    'stage': 'Seed-Series B',
                    'portfolio_ai': ['OpenAI', 'Stripe', 'Coinbase'],
                    'thesis': 'AI y crypto global',
                    'decision_time': '3-6 semanas',
                    'board_seats': 1-2,
                    'follow_on_rate': 0.88,
                    'valor_agregado': 'Red global, expertise AI',
                    'fit_score': 0.82
                },
                'accel': {
                    'nombre': 'Accel',
                    'fondo': '$3B',
                    'check_tipico': '$2M-$25M',
                    'stage': 'Seed-Series B',
                    'portfolio_ai': ['Slack', 'Dropbox', 'Atlassian'],
                    'thesis': 'SaaS y AI global',
                    'decision_time': '3-5 semanas',
                    'board_seats': 1,
                    'follow_on_rate': 0.85,
                    'valor_agregado': 'Red global, expertise SaaS',
                    'fit_score': 0.80
                }
            }
        }
        
        print("✅ VCs objetivo definidos")
        return self.vcs_target
    
    def definir_estrategias_negociacion(self):
        """Define estrategias de negociación específicas"""
        self.estrategias_negociacion = {
            'posicionamiento': {
                'categoria_creacion': {
                    'mensaje': 'No competimos con Copy.ai - creamos la categoría de AI Marketing para LATAM',
                    'evidencia': [
                        'Mercado LATAM 50% menos saturado que US',
                        'Precios 50% menores que competencia global',
                        'Localización específica para cultura LATAM',
                        'Partnerships con concesionarios automotrices'
                    ]
                },
                'timing_perfecto': {
                    'mensaje': 'Timing perfecto: Adopción de IA en LATAM acelerando',
                    'evidencia': [
                        '35% adopción IA en LATAM vs 60% en US',
                        'Crecimiento 30% anual en sector automotriz',
                        'Regulaciones favorables para IA',
                        'Talento disponible y costos menores'
                    ]
                },
                'ventaja_competitiva': {
                    'mensaje': 'Ventaja competitiva sostenible en LATAM',
                    'evidencia': [
                        'Primer movers en vertical automotriz',
                        'Partnerships exclusivos con concesionarios',
                        'Modelo de precios adaptado a LATAM',
                        'Equipo local con expertise regional'
                    ]
                }
            },
            'tacticas_psicologicas': {
                'escasez': {
                    'mensaje': 'Solo tomamos 2-3 inversionistas para esta ronda',
                    'aplicacion': 'Crear urgencia y competencia'
                },
                'prueba_social': {
                    'mensaje': 'Concesionarios líderes ya confirmaron interés',
                    'aplicacion': 'Validar demanda del mercado'
                },
                'autoridad': {
                    'mensaje': 'Equipo con experiencia en AI y automotriz',
                    'aplicacion': 'Establecer credibilidad y expertise'
                },
                'reciprocidad': {
                    'mensaje': 'Compartimos insights de mercado LATAM',
                    'aplicacion': 'Crear valor antes de pedir inversión'
                }
            },
            'fases_negociacion': {
                'fase_1_apertura': {
                    'objetivo': 'Crear primera impresión y rapport',
                    'duracion': '30-45 minutos',
                    'tacticas': [
                        'Enfoque en valor primero',
                        'Descubrimiento de interés mutuo',
                        'Posicionamiento como experto'
                    ]
                },
                'fase_2_profundizacion': {
                    'objetivo': 'Due diligence y discusiones técnicas',
                    'duracion': '60-90 minutos',
                    'tacticas': [
                        'Posicionamiento como experto',
                        'Resolución de preocupaciones',
                        'Demostración de valor'
                    ]
                },
                'fase_3_term_sheet': {
                    'objetivo': 'Negociación de términos y estructura',
                    'duracion': '45-60 minutos',
                    'tacticas': [
                        'Enfoque ganar-ganar',
                        'Tensión competitiva',
                        'Foco en partnership'
                    ]
                },
                'fase_4_cierre': {
                    'objetivo': 'Términos finales y cierre',
                    'duracion': '30-45 minutos',
                    'tacticas': [
                        'Foco en partnership',
                        'Creación de valor',
                        'Éxito mutuo'
                    ]
                }
            }
        }
        
        print("✅ Estrategias de negociación definidas")
        return self.estrategias_negociacion
    
    def calcular_metricas_negociacion(self):
        """Calcula métricas de negociación"""
        self.metricas_negociacion = {
            'valuacion_objetivo': {
                'pre_money': 15000000,  # $15M
                'post_money': 20000000,  # $20M
                'dilucion': 0.25,  # 25%
                'justificacion': 'Comparable con startups similares en LATAM'
            },
            'terminos_objetivo': {
                'liquidation_preference': 1.0,
                'participation': False,
                'anti_dilution': 'Weighted Average',
                'board_seats': 1,
                'veto_rights': ['Presupuesto', 'Hiring C-level', 'Valuación'],
                'information_rights': True,
                'pro_rata': True
            },
            'usos_fondos': {
                'desarrollo_producto': 0.40,  # 40%
                'marketing_ventas': 0.30,  # 30%
                'equipo': 0.20,  # 20%
                'operaciones': 0.10  # 10%
            },
            'milestones': {
                '6_meses': {
                    'usuarios': 10000,
                    'mrr': 100000,
                    'partnerships': 5
                },
                '12_meses': {
                    'usuarios': 50000,
                    'mrr': 500000,
                    'partnerships': 15
                },
                '18_meses': {
                    'usuarios': 100000,
                    'mrr': 1000000,
                    'partnerships': 25
                }
            }
        }
        
        print("✅ Métricas de negociación calculadas")
        return self.metricas_negociacion
    
    def generar_escenarios_negociacion(self):
        """Genera escenarios de negociación"""
        self.escenarios_negociacion = {
            'escenario_optimista': {
                'probabilidad': 0.30,
                'valuacion_pre': 20000000,  # $20M
                'dilucion': 0.20,  # 20%
                'terminos': 'Favorables',
                'tiempo_cierre': '4-6 semanas',
                'condiciones': [
                    'Múltiples VCs interesados',
                    'Tensión competitiva alta',
                    'Términos favorables para fundador'
                ]
            },
            'escenario_base': {
                'probabilidad': 0.50,
                'valuacion_pre': 15000000,  # $15M
                'dilucion': 0.25,  # 25%
                'terminos': 'Balanceados',
                'tiempo_cierre': '6-8 semanas',
                'condiciones': [
                    'Interés moderado de VCs',
                    'Negociación estándar',
                    'Términos balanceados'
                ]
            },
            'escenario_conservador': {
                'probabilidad': 0.20,
                'valuacion_pre': 10000000,  # $10M
                'dilucion': 0.30,  # 30%
                'terminos': 'Desfavorables',
                'tiempo_cierre': '8-12 semanas',
                'condiciones': [
                    'Interés limitado de VCs',
                    'Negociación difícil',
                    'Términos desfavorables para fundador'
                ]
            }
        }
        
        print("✅ Escenarios de negociación generados")
        return self.escenarios_negociacion
    
    def generar_plan_negociacion(self):
        """Genera plan de negociación detallado"""
        plan = {
            'preparacion': {
                'investigacion_vcs': [
                    'Analizar portfolio y thesis de cada VC',
                    'Identificar conexiones y referencias',
                    'Preparar pitch personalizado por VC',
                    'Desarrollar argumentos específicos'
                ],
                'preparacion_documentos': [
                    'Pitch deck optimizado',
                    'Financial model detallado',
                    'Term sheet template',
                    'Due diligence materials'
                ],
                'preparacion_equipo': [
                    'Entrenar equipo en negociación',
                    'Preparar respuestas a preguntas difíciles',
                    'Desarrollar storytelling efectivo',
                    'Practicar presentaciones'
                ]
            },
            'ejecucion': {
                'semana_1_2': [
                    'Enviar pitch decks a VCs objetivo',
                    'Seguir up con VCs interesados',
                    'Programar meetings iniciales',
                    'Preparar materials específicos'
                ],
                'semana_3_4': [
                    'Realizar meetings iniciales',
                    'Seguir up con VCs interesados',
                    'Proporcionar due diligence materials',
                    'Mantener momentum y urgencia'
                ],
                'semana_5_6': [
                    'Negociar term sheets',
                    'Crear tensión competitiva',
                    'Comparar ofertas',
                    'Preparar para decisión final'
                ],
                'semana_7_8': [
                    'Cerrar deal con VC seleccionado',
                    'Finalizar documentación legal',
                    'Comunicar decisión a otros VCs',
                    'Preparar para cierre'
                ]
            },
            'seguimiento': {
                'post_cierre': [
                    'Integrar VC en board',
                    'Establecer governance',
                    'Desarrollar relación estratégica',
                    'Preparar para siguiente ronda'
                ]
            }
        }
        
        print("✅ Plan de negociación generado")
        return plan
    
    def generar_reporte_negociacion(self):
        """Genera reporte completo de negociación"""
        if not self.vcs_target:
            self.definir_vcs_target()
        
        if not self.estrategias_negociacion:
            self.definir_estrategias_negociacion()
        
        if not self.metricas_negociacion:
            self.calcular_metricas_negociacion()
        
        if not self.escenarios_negociacion:
            self.generar_escenarios_negociacion()
        
        plan = self.generar_plan_negociacion()
        
        reporte = f"""
# 🚀 SISTEMA DE NEGOCIACIÓN VC - CopyCar.ai
## Neural Marketing AI - SaaS IA LATAM
### {datetime.now().strftime('%d de %B de %Y - %H:%M:%S')}

## 🎯 RESUMEN EJECUTIVO

### Objetivo de Negociación
- **Valuación Pre-Money Objetivo**: ${self.metricas_negociacion['valuacion_objetivo']['pre_money']/1000000:.0f}M
- **Valuación Post-Money Objetivo**: ${self.metricas_negociacion['valuacion_objetivo']['post_money']/1000000:.0f}M
- **Dilución Objetivo**: {self.metricas_negociacion['valuacion_objetivo']['dilucion']*100:.0f}%
- **Tiempo de Cierre Objetivo**: 6-8 semanas

### VCs Objetivo Identificados
- **VCs LATAM**: 3 (Kaszek, Monashees, Canary)
- **VCs Globales**: 3 (Sequoia, A16Z, Accel)
- **Total VCs**: 6
- **Fit Score Promedio**: 0.87

## 🎯 VCs OBJETIVO DETALLADOS

### VCs LATAM (Prioridad Alta)
"""
        
        # Agregar VCs LATAM
        for nombre, vc in self.vcs_target['vcs_latam'].items():
            reporte += f"""
#### {vc['nombre']}
- **Fondo**: {vc['fondo']}
- **Check Típico**: {vc['check_tipico']}
- **Stage**: {vc['stage']}
- **Portfolio AI**: {', '.join(vc['portfolio_ai'])}
- **Thesis**: {vc['thesis']}
- **Tiempo Decisión**: {vc['decision_time']}
- **Valor Agregado**: {vc['valor_agregado']}
- **Fit Score**: {vc['fit_score']*100:.0f}%
"""
        
        # Agregar VCs Globales
        reporte += f"""

### VCs Globales (Prioridad Media)
"""
        
        for nombre, vc in self.vcs_target['vcs_globales'].items():
            reporte += f"""
#### {vc['nombre']}
- **Fondo**: {vc['fondo']}
- **Check Típico**: {vc['check_tipico']}
- **Stage**: {vc['stage']}
- **Portfolio AI**: {', '.join(vc['portfolio_ai'])}
- **Thesis**: {vc['thesis']}
- **Tiempo Decisión**: {vc['decision_time']}
- **Valor Agregado**: {vc['valor_agregado']}
- **Fit Score**: {vc['fit_score']*100:.0f}%
"""
        
        # Agregar estrategias
        reporte += f"""

## 🎯 ESTRATEGIAS DE NEGOCIACIÓN

### Posicionamiento Estratégico
"""
        
        for estrategia, detalles in self.estrategias_negociacion['posicionamiento'].items():
            reporte += f"""
#### {estrategia.replace('_', ' ').title()}
- **Mensaje**: {detalles['mensaje']}
- **Evidencia**:
"""
            for evidencia in detalles['evidencia']:
                reporte += f"  - {evidencia}\n"
        
        # Agregar tácticas psicológicas
        reporte += f"""

### Tácticas Psicológicas
"""
        
        for tactica, detalles in self.estrategias_negociacion['tacticas_psicologicas'].items():
            reporte += f"""
#### {tactica.replace('_', ' ').title()}
- **Mensaje**: {detalles['mensaje']}
- **Aplicación**: {detalles['aplicacion']}
"""
        
        # Agregar fases de negociación
        reporte += f"""

### Fases de Negociación
"""
        
        for fase, detalles in self.estrategias_negociacion['fases_negociacion'].items():
            reporte += f"""
#### {fase.replace('_', ' ').title()}
- **Objetivo**: {detalles['objetivo']}
- **Duración**: {detalles['duracion']}
- **Tácticas**:
"""
            for tactica in detalles['tacticas']:
                reporte += f"  - {tactica}\n"
        
        # Agregar métricas
        reporte += f"""

## 📊 MÉTRICAS DE NEGOCIACIÓN

### Valuación Objetivo
- **Pre-Money**: ${self.metricas_negociacion['valuacion_objetivo']['pre_money']/1000000:.0f}M
- **Post-Money**: ${self.metricas_negociacion['valuacion_objetivo']['post_money']/1000000:.0f}M
- **Dilución**: {self.metricas_negociacion['valuacion_objetivo']['dilucion']*100:.0f}%
- **Justificación**: {self.metricas_negociacion['valuacion_objetivo']['justificacion']}

### Términos Objetivo
- **Liquidation Preference**: {self.metricas_negociacion['terminos_objetivo']['liquidation_preference']}x
- **Participation**: {'Sí' if self.metricas_negociacion['terminos_objetivo']['participation'] else 'No'}
- **Anti-Dilution**: {self.metricas_negociacion['terminos_objetivo']['anti_dilution']}
- **Board Seats**: {self.metricas_negociacion['terminos_objetivo']['board_seats']}
- **Veto Rights**: {', '.join(self.metricas_negociacion['terminos_objetivo']['veto_rights'])}
- **Information Rights**: {'Sí' if self.metricas_negociacion['terminos_objetivo']['information_rights'] else 'No'}
- **Pro Rata**: {'Sí' if self.metricas_negociacion['terminos_objetivo']['pro_rata'] else 'No'}

### Usos de Fondos
- **Desarrollo Producto**: {self.metricas_negociacion['usos_fondos']['desarrollo_producto']*100:.0f}%
- **Marketing y Ventas**: {self.metricas_negociacion['usos_fondos']['marketing_ventas']*100:.0f}%
- **Equipo**: {self.metricas_negociacion['usos_fondos']['equipo']*100:.0f}%
- **Operaciones**: {self.metricas_negociacion['usos_fondos']['operaciones']*100:.0f}%

### Milestones
"""
        
        for periodo, milestones in self.metricas_negociacion['milestones'].items():
            reporte += f"""
#### {periodo.replace('_', ' ').title()}
- **Usuarios**: {milestones['usuarios']:,}
- **MRR**: ${milestones['mrr']:,}
- **Partnerships**: {milestones['partnerships']}
"""
        
        # Agregar escenarios
        reporte += f"""

## 🎲 ESCENARIOS DE NEGOCIACIÓN

### Escenarios Simulados
"""
        
        for escenario, detalles in self.escenarios_negociacion.items():
            reporte += f"""
#### {escenario.replace('_', ' ').title()}
- **Probabilidad**: {detalles['probabilidad']*100:.0f}%
- **Valuación Pre**: ${detalles['valuacion_pre']/1000000:.0f}M
- **Dilución**: {detalles['dilucion']*100:.0f}%
- **Términos**: {detalles['terminos']}
- **Tiempo Cierre**: {detalles['tiempo_cierre']}
- **Condiciones**:
"""
            for condicion in detalles['condiciones']:
                reporte += f"  - {condicion}\n"
        
        # Agregar plan
        reporte += f"""

## 🚀 PLAN DE NEGOCIACIÓN

### Preparación
"""
        
        for categoria, acciones in plan['preparacion'].items():
            reporte += f"""
#### {categoria.replace('_', ' ').title()}
"""
            for accion in acciones:
                reporte += f"- {accion}\n"
        
        # Agregar ejecución
        reporte += f"""

### Ejecución
"""
        
        for periodo, acciones in plan['ejecucion'].items():
            reporte += f"""
#### {periodo.replace('_', ' ').title()}
"""
            for accion in acciones:
                reporte += f"- {accion}\n"
        
        # Agregar seguimiento
        reporte += f"""

### Seguimiento
"""
        
        for categoria, acciones in plan['seguimiento'].items():
            reporte += f"""
#### {categoria.replace('_', ' ').title()}
"""
            for accion in acciones:
                reporte += f"- {accion}\n"
        
        reporte += f"""

## 🎯 PRÓXIMOS PASOS

### Acciones Inmediatas
1. **Preparar materials** de negociación
2. **Entrenar equipo** en técnicas de negociación
3. **Identificar referencias** para cada VC
4. **Desarrollar storytelling** específico por VC
5. **Preparar respuestas** a preguntas difíciles

### Acciones Estratégicas
1. **Iniciar outreach** a VCs objetivo
2. **Crear tensión competitiva** entre VCs
3. **Mantener momentum** en negociaciones
4. **Comparar ofertas** objetivamente
5. **Preparar para cierre** exitoso

---
*Generado por Sistema de Negociación VC - Neural Marketing AI*
"""
        
        return reporte
    
    def ejecutar_analisis_negociacion(self):
        """Ejecuta análisis completo de negociación"""
        print("🚀 Iniciando análisis de negociación VC...")
        
        # Definir VCs objetivo
        self.definir_vcs_target()
        
        # Definir estrategias
        self.definir_estrategias_negociacion()
        
        # Calcular métricas
        self.calcular_metricas_negociacion()
        
        # Generar escenarios
        self.generar_escenarios_negociacion()
        
        # Generar reporte
        reporte = self.generar_reporte_negociacion()
        
        # Guardar reporte
        with open('reporte_negociacion_vc_copycar.md', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print("✅ Análisis de negociación completado")
        print(f"🎯 VCs objetivo identificados: {len(self.vcs_target['vcs_latam']) + len(self.vcs_target['vcs_globales'])}")
        print(f"📊 Escenarios generados: {len(self.escenarios_negociacion)}")
        
        return reporte

def main():
    """Función principal"""
    sistema = SistemaNegociacionVCCopyCar()
    
    print("=" * 80)
    print("🚀 SISTEMA DE NEGOCIACIÓN VC - COPYCAR.AI")
    print("Neural Marketing AI - SaaS IA LATAM")
    print("=" * 80)
    
    # Ejecutar análisis completo
    reporte = sistema.ejecutar_analisis_negociacion()
    
    print("\n" + "=" * 80)
    print("📋 REPORTE DE NEGOCIACIÓN GENERADO")
    print("=" * 80)
    print(reporte)

if __name__ == "__main__":
    main()
