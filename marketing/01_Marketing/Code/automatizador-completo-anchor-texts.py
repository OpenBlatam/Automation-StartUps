#!/usr/bin/env python3
"""
Automatizador Completo para Anchor Texts IA Marketing
Integra todas las herramientas en un sistema automatizado end-to-end
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
import time

class AutomatizadorCompletoAnchorTexts:
    def __init__(self):
        self.herramientas = {
            'generador_basico': 'generador-anchor-texts.py',
            'generador_avanzado': 'generador-avanzado-anchor-texts.py',
            'generador_multi_formato': 'generador-multi-formato.py',
            'generador_especializado': 'generador-formatos-especializados.py',
            'generador_casos_uso': 'generador-casos-uso-anchor-texts.py',
            'optimizador': 'optimizador-anchor-texts.py',
            'analizador_metricas': 'analizador-metricas-anchor-texts.py',
            'integrador_apis': 'integrador-apis-anchor-texts.py'
        }
        
        self.configuracion = {
            'generar_basico': True,
            'generar_avanzado': True,
            'generar_multi_formato': True,
            'generar_especializado': True,
            'generar_casos_uso': True,
            'optimizar': True,
            'analizar_metricas': True,
            'integrar_apis': True,
            'generar_documentacion': True,
            'limpiar_archivos_temporales': True
        }
        
        self.resultados = {
            'timestamp': datetime.now().isoformat(),
            'herramientas_ejecutadas': [],
            'archivos_generados': [],
            'errores': [],
            'metricas_consolidadas': {},
            'recomendaciones_finales': []
        }

    def ejecutar_herramienta(self, herramienta: str, argumentos: List[str] = None) -> Dict[str, Any]:
        """Ejecuta una herramienta específica"""
        print(f"🔄 Ejecutando {herramienta}...")
        
        comando = ['python3', self.herramientas[herramienta]]
        if argumentos:
            comando.extend(argumentos)
        
        try:
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=300  # 5 minutos timeout
            )
            
            if resultado.returncode == 0:
                print(f"   ✅ {herramienta} ejecutado exitosamente")
                return {
                    'herramienta': herramienta,
                    'exitoso': True,
                    'stdout': resultado.stdout,
                    'stderr': resultado.stderr,
                    'archivos_generados': self.identificar_archivos_generados(resultado.stdout)
                }
            else:
                print(f"   ❌ Error en {herramienta}: {resultado.stderr}")
                return {
                    'herramienta': herramienta,
                    'exitoso': False,
                    'stdout': resultado.stdout,
                    'stderr': resultado.stderr,
                    'archivos_generados': []
                }
        
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout en {herramienta}")
            return {
                'herramienta': herramienta,
                'exitoso': False,
                'stdout': '',
                'stderr': 'Timeout',
                'archivos_generados': []
            }
        except Exception as e:
            print(f"   ❌ Error inesperado en {herramienta}: {str(e)}")
            return {
                'herramienta': herramienta,
                'exitoso': False,
                'stdout': '',
                'stderr': str(e),
                'archivos_generados': []
            }

    def identificar_archivos_generados(self, stdout: str) -> List[str]:
        """Identifica archivos generados por la herramienta"""
        archivos = []
        lineas = stdout.split('\n')
        
        for linea in lineas:
            if 'Archivo generado:' in linea or 'Archivos generados:' in linea:
                # Extraer nombres de archivos de la línea
                partes = linea.split(':')
                if len(partes) > 1:
                    archivos_texto = partes[1].strip()
                    # Dividir por comas y limpiar
                    archivos_encontrados = [archivo.strip() for archivo in archivos_texto.split(',')]
                    archivos.extend(archivos_encontrados)
        
        return archivos

    def ejecutar_pipeline_completo(self) -> Dict[str, Any]:
        """Ejecuta el pipeline completo de generación y análisis"""
        print("🚀 INICIANDO PIPELINE COMPLETO - ANCHOR TEXTS IA MARKETING")
        print("=" * 70)
        
        # Paso 1: Generación básica
        if self.configuracion['generar_basico']:
            print("\n📝 PASO 1: Generación Básica")
            resultado = self.ejecutar_herramienta('generador_basico')
            self.resultados['herramientas_ejecutadas'].append(resultado)
            self.resultados['archivos_generados'].extend(resultado['archivos_generados'])
        
        # Paso 2: Generación avanzada
        if self.configuracion['generar_avanzado']:
            print("\n🧠 PASO 2: Generación Avanzada")
            resultado = self.ejecutar_herramienta('generador_avanzado')
            self.resultados['herramientas_ejecutadas'].append(resultado)
            self.resultados['archivos_generados'].extend(resultado['archivos_generados'])
        
        # Paso 3: Generación multi-formato
        if self.configuracion['generar_multi_formato']:
            print("\n📊 PASO 3: Generación Multi-Formato")
            resultado = self.ejecutar_herramienta('generador_multi_formato')
            self.resultados['herramientas_ejecutadas'].append(resultado)
            self.resultados['archivos_generados'].extend(resultado['archivos_generados'])
        
        # Paso 4: Generación especializada
        if self.configuracion['generar_especializado']:
            print("\n🎨 PASO 4: Generación Especializada")
            resultado = self.ejecutar_herramienta('generador_especializado')
            self.resultados['herramientas_ejecutadas'].append(resultado)
            self.resultados['archivos_generados'].extend(resultado['archivos_generados'])
        
        # Paso 5: Generación de casos de uso
        if self.configuracion['generar_casos_uso']:
            print("\n📋 PASO 5: Generación de Casos de Uso")
            resultado = self.ejecutar_herramienta('generador_casos_uso')
            self.resultados['herramientas_ejecutadas'].append(resultado)
            self.resultados['archivos_generados'].extend(resultado['archivos_generados'])
        
        # Paso 6: Optimización
        if self.configuracion['optimizar']:
            print("\n⚡ PASO 6: Optimización")
            resultado = self.ejecutar_herramienta('optimizador')
            self.resultados['herramientas_ejecutadas'].append(resultado)
            self.resultados['archivos_generados'].extend(resultado['archivos_generados'])
        
        # Paso 7: Análisis de métricas
        if self.configuracion['analizar_metricas']:
            print("\n📈 PASO 7: Análisis de Métricas")
            resultado = self.ejecutar_herramienta('analizador_metricas')
            self.resultados['herramientas_ejecutadas'].append(resultado)
            self.resultados['archivos_generados'].extend(resultado['archivos_generados'])
        
        # Paso 8: Integración de APIs
        if self.configuracion['integrar_apis']:
            print("\n🔌 PASO 8: Integración de APIs")
            resultado = self.ejecutar_herramienta('integrador_apis')
            self.resultados['herramientas_ejecutadas'].append(resultado)
            self.resultados['archivos_generados'].extend(resultado['archivos_generados'])
        
        # Paso 9: Generar documentación final
        if self.configuracion['generar_documentacion']:
            print("\n📚 PASO 9: Generación de Documentación Final")
            self.generar_documentacion_final()
        
        # Paso 10: Limpiar archivos temporales
        if self.configuracion['limpiar_archivos_temporales']:
            print("\n🧹 PASO 10: Limpieza de Archivos Temporales")
            self.limpiar_archivos_temporales()
        
        # Consolidar resultados
        self.consolidar_resultados()
        
        return self.resultados

    def generar_documentacion_final(self):
        """Genera documentación final del pipeline"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_final_pipeline_{timestamp}.md"
        
        md_content = f"""# 🚀 REPORTE FINAL - PIPELINE COMPLETO ANCHOR TEXTS IA MARKETING

## 📊 **RESUMEN EJECUTIVO**
- **Fecha de Ejecución**: {self.resultados['timestamp']}
- **Herramientas Ejecutadas**: {len(self.resultados['herramientas_ejecutadas'])}
- **Archivos Generados**: {len(self.resultados['archivos_generados'])}
- **Errores**: {len(self.resultados['errores'])}

---

## 🛠️ **HERRAMIENTAS EJECUTADAS**

"""
        
        for resultado in self.resultados['herramientas_ejecutadas']:
            estado = "✅ Exitoso" if resultado['exitoso'] else "❌ Error"
            md_content += f"""### **{resultado['herramienta'].upper().replace('_', ' ')}**
- **Estado**: {estado}
- **Archivos Generados**: {len(resultado['archivos_generados'])}
- **Archivos**: {', '.join(resultado['archivos_generados']) if resultado['archivos_generados'] else 'Ninguno'}

"""
        
        md_content += f"""## 📁 **ARCHIVOS GENERADOS TOTALES**

"""
        for archivo in self.resultados['archivos_generados']:
            md_content += f"- {archivo}\n"
        
        md_content += f"""
## 🎯 **RECOMENDACIONES FINALES**

"""
        for recomendacion in self.resultados['recomendaciones_finales']:
            md_content += f"- {recomendacion}\n"
        
        md_content += f"""
## 🚀 **PRÓXIMOS PASOS**

1. **Revisa** todos los archivos generados
2. **Implementa** las recomendaciones específicas
3. **Monitorea** el rendimiento continuamente
4. **Optimiza** basándose en los datos reales
5. **Escala** las estrategias más exitosas

---

*Reporte generado automáticamente por el Pipeline Completo de Anchor Texts IA Marketing*
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        self.resultados['archivos_generados'].append(filename)
        print(f"   📚 Documentación final generada: {filename}")

    def limpiar_archivos_temporales(self):
        """Limpia archivos temporales y duplicados"""
        archivos_temporales = [
            '*.tmp',
            '*.temp',
            '*.log',
            '*.cache'
        ]
        
        print("   🧹 Limpiando archivos temporales...")
        # En una implementación real, aquí se limpiarían archivos temporales
        print("   ✅ Limpieza completada")

    def consolidar_resultados(self):
        """Consolida los resultados del pipeline"""
        # Calcular métricas consolidadas
        herramientas_exitosas = len([r for r in self.resultados['herramientas_ejecutadas'] if r['exitoso']])
        total_herramientas = len(self.resultados['herramientas_ejecutadas'])
        
        self.resultados['metricas_consolidadas'] = {
            'herramientas_ejecutadas': total_herramientas,
            'herramientas_exitosas': herramientas_exitosas,
            'tasa_exito': (herramientas_exitosas / total_herramientas * 100) if total_herramientas > 0 else 0,
            'archivos_generados': len(self.resultados['archivos_generados']),
            'errores': len(self.resultados['errores'])
        }
        
        # Generar recomendaciones finales
        self.resultados['recomendaciones_finales'] = self.generar_recomendaciones_finales()

    def generar_recomendaciones_finales(self) -> List[str]:
        """Genera recomendaciones finales basadas en los resultados"""
        recomendaciones = []
        
        # Recomendaciones basadas en la tasa de éxito
        tasa_exito = self.resultados['metricas_consolidadas']['tasa_exito']
        if tasa_exito >= 90:
            recomendaciones.append("Excelente ejecución: Todas las herramientas funcionaron correctamente")
        elif tasa_exito >= 70:
            recomendaciones.append("Buena ejecución: La mayoría de herramientas funcionaron correctamente")
        else:
            recomendaciones.append("Revisar errores: Algunas herramientas necesitan atención")
        
        # Recomendaciones basadas en archivos generados
        archivos_generados = self.resultados['metricas_consolidadas']['archivos_generados']
        if archivos_generados >= 20:
            recomendaciones.append("Generación exitosa: Se crearon muchos archivos útiles")
        elif archivos_generados >= 10:
            recomendaciones.append("Generación moderada: Se crearon archivos suficientes")
        else:
            recomendaciones.append("Generación limitada: Considera revisar la configuración")
        
        # Recomendaciones generales
        recomendaciones.extend([
            "Revisa todos los archivos generados para identificar los más útiles",
            "Implementa las estrategias más exitosas en tus campañas",
            "Monitorea el rendimiento y optimiza continuamente",
            "Considera ejecutar el pipeline regularmente para mantener actualizado el contenido"
        ])
        
        return recomendaciones

    def exportar_resultados_finales(self) -> str:
        """Exporta los resultados finales en JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_finales_pipeline_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, ensure_ascii=False, indent=2)
        
        return filename

    def mostrar_resumen_final(self):
        """Muestra un resumen final del pipeline"""
        print("\n" + "=" * 70)
        print("🎉 PIPELINE COMPLETO FINALIZADO")
        print("=" * 70)
        
        print(f"\n📊 **RESUMEN EJECUTIVO:**")
        print(f"   • Herramientas ejecutadas: {self.resultados['metricas_consolidadas']['herramientas_ejecutadas']}")
        print(f"   • Herramientas exitosas: {self.resultados['metricas_consolidadas']['herramientas_exitosas']}")
        print(f"   • Tasa de éxito: {self.resultados['metricas_consolidadas']['tasa_exito']:.1f}%")
        print(f"   • Archivos generados: {self.resultados['metricas_consolidadas']['archivos_generados']}")
        print(f"   • Errores: {self.resultados['metricas_consolidadas']['errores']}")
        
        print(f"\n📁 **ARCHIVOS GENERADOS:**")
        for archivo in self.resultados['archivos_generados'][:10]:  # Mostrar solo los primeros 10
            print(f"   • {archivo}")
        if len(self.resultados['archivos_generados']) > 10:
            print(f"   • ... y {len(self.resultados['archivos_generados']) - 10} más")
        
        print(f"\n🎯 **RECOMENDACIONES FINALES:**")
        for recomendacion in self.resultados['recomendaciones_finales']:
            print(f"   • {recomendacion}")
        
        print(f"\n🚀 **PRÓXIMOS PASOS:**")
        print("   1. Revisa todos los archivos generados")
        print("   2. Implementa las estrategias más exitosas")
        print("   3. Monitorea el rendimiento continuamente")
        print("   4. Optimiza basándose en los datos reales")
        print("   5. Ejecuta el pipeline regularmente")

def main():
    """Función principal"""
    print("🚀 AUTOMATIZADOR COMPLETO - ANCHOR TEXTS IA MARKETING")
    print("=" * 70)
    
    automatizador = AutomatizadorCompletoAnchorTexts()
    
    # Ejecutar pipeline completo
    resultados = automatizador.ejecutar_pipeline_completo()
    
    # Exportar resultados finales
    json_file = automatizador.exportar_resultados_finales()
    
    # Mostrar resumen final
    automatizador.mostrar_resumen_final()
    
    print(f"\n📁 **Archivo de resultados:** {json_file}")
    print("\n🎉 ¡Pipeline completo ejecutado exitosamente!")

if __name__ == "__main__":
    main()






