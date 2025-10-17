#!/usr/bin/env python3
"""
Simulador Avanzado de Escenarios de Dilución
Neural Marketing AI - SaaS IA LATAM
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json

class SimuladorDilucion:
    def __init__(self):
        self.escenarios = {}
        self.resultados = {}
        self.configuracion_base = {
            'acciones_totales': 10000000,
            'acciones_fundador': 6000000,
            'valuacion_actual': 2000000,
            'crecimiento_anual': 0.25,
            'dilucion_por_ronda': 0.20
        }
    
    def simular_escenario(self, nombre, configuracion):
        """Simula un escenario específico de dilución"""
        resultados = {
            'rondas': [],
            'equity_fundador': [],
            'valor_fundador': [],
            'dilucion_acumulada': [],
            'valuacion_empresa': []
        }
        
        acciones_fundador = configuracion['acciones_fundador']
        acciones_totales = configuracion['acciones_totales']
        valuacion = configuracion['valuacion_actual']
        crecimiento = configuracion['crecimiento_anual']
        dilucion_ronda = configuracion['dilucion_por_ronda']
        
        # Ronda inicial
        equity_inicial = (acciones_fundador / acciones_totales) * 100
        valor_inicial = valuacion * (equity_inicial / 100)
        
        resultados['rondas'].append('Inicial')
        resultados['equity_fundador'].append(equity_inicial)
        resultados['valor_fundador'].append(valor_inicial)
        resultados['dilucion_acumulada'].append(0)
        resultados['valuacion_empresa'].append(valuacion)
        
        # Simular rondas futuras
        rondas = ['Pre-Seed', 'Seed', 'Series A', 'Series B', 'Series C']
        dilucion_acumulada = 0
        
        for i, ronda in enumerate(rondas):
            # Calcular nueva valuación
            valuacion = valuacion * (1 + crecimiento)
            
            # Calcular dilución
            if i == 0:  # Pre-Seed ya ocurrió
                dilucion = 0.20
            else:
                dilucion = dilucion_ronda
            
            # Calcular nuevas acciones
            acciones_nuevas = (acciones_totales * dilucion) / (1 - dilucion)
            acciones_totales += acciones_nuevas
            
            # Calcular equity del fundador
            equity_fundador = (acciones_fundador / acciones_totales) * 100
            valor_fundador = valuacion * (equity_fundador / 100)
            
            dilucion_acumulada += dilucion
            
            resultados['rondas'].append(ronda)
            resultados['equity_fundador'].append(equity_fundador)
            resultados['valor_fundador'].append(valor_fundador)
            resultados['dilucion_acumulada'].append(dilucion_acumulada * 100)
            resultados['valuacion_empresa'].append(valuacion)
        
        self.resultados[nombre] = resultados
        return resultados
    
    def simular_estrategias_anti_dilucion(self):
        """Simula diferentes estrategias anti-dilución"""
        estrategias = {
            'Sin_Proteccion': {
                'acciones_totales': 10000000,
                'acciones_fundador': 6000000,
                'valuacion_actual': 2000000,
                'crecimiento_anual': 0.25,
                'dilucion_por_ronda': 0.20
            },
            'Weighted_Average': {
                'acciones_totales': 10000000,
                'acciones_fundador': 6000000,
                'valuacion_actual': 2000000,
                'crecimiento_anual': 0.25,
                'dilucion_por_ronda': 0.15
            },
            'Clases_Diferenciadas': {
                'acciones_totales': 10000000,
                'acciones_fundador': 6000000,
                'valuacion_actual': 2000000,
                'crecimiento_anual': 0.25,
                'dilucion_por_ronda': 0.10
            },
            'SAFE_Convertible': {
                'acciones_totales': 10000000,
                'acciones_fundador': 6000000,
                'valuacion_actual': 2000000,
                'crecimiento_anual': 0.25,
                'dilucion_por_ronda': 0.12
            },
            'Strategic_Partnerships': {
                'acciones_totales': 10000000,
                'acciones_fundador': 6000000,
                'valuacion_actual': 2000000,
                'crecimiento_anual': 0.30,  # Mayor crecimiento
                'dilucion_por_ronda': 0.08
            }
        }
        
        for nombre, config in estrategias.items():
            self.simular_escenario(nombre, config)
    
    def calcular_roi_estrategias(self):
        """Calcula el ROI de cada estrategia"""
        roi_data = []
        
        for estrategia, resultados in self.resultados.items():
            valor_inicial = resultados['valor_fundador'][0]
            valor_final = resultados['valor_fundador'][-1]
            equity_final = resultados['equity_fundador'][-1]
            dilucion_acumulada = resultados['dilucion_acumulada'][-1]
            
            roi = ((valor_final - valor_inicial) / valor_inicial) * 100
            
            roi_data.append({
                'Estrategia': estrategia,
                'Equity_Final': equity_final,
                'Valor_Fundador': valor_final,
                'Dilucion_Acumulada': dilucion_acumulada,
                'ROI': roi
            })
        
        return pd.DataFrame(roi_data)
    
    def generar_graficos(self):
        """Genera gráficos de análisis"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Análisis de Dilución - Neural Marketing AI', fontsize=16, fontweight='bold')
        
        # Gráfico 1: Equity del Fundador por Ronda
        ax1 = axes[0, 0]
        for estrategia, resultados in self.resultados.items():
            ax1.plot(resultados['rondas'], resultados['equity_fundador'], 
                    marker='o', linewidth=2, label=estrategia)
        ax1.set_title('Equity del Fundador por Ronda')
        ax1.set_ylabel('Equity (%)')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Valor del Fundador por Ronda
        ax2 = axes[0, 1]
        for estrategia, resultados in self.resultados.items():
            ax2.plot(resultados['rondas'], [v/1000000 for v in resultados['valor_fundador']], 
                    marker='s', linewidth=2, label=estrategia)
        ax2.set_title('Valor del Fundador por Ronda')
        ax2.set_ylabel('Valor (Millones USD)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Dilución Acumulada
        ax3 = axes[1, 0]
        for estrategia, resultados in self.resultados.items():
            ax3.plot(resultados['rondas'], resultados['dilucion_acumulada'], 
                    marker='^', linewidth=2, label=estrategia)
        ax3.set_title('Dilución Acumulada')
        ax3.set_ylabel('Dilución (%)')
        ax3.tick_params(axis='x', rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Valuación de la Empresa
        ax4 = axes[1, 1]
        for estrategia, resultados in self.resultados.items():
            ax4.plot(resultados['rondas'], [v/1000000 for v in resultados['valuacion_empresa']], 
                    marker='d', linewidth=2, label=estrategia)
        ax4.set_title('Valuación de la Empresa')
        ax4.set_ylabel('Valuación (Millones USD)')
        ax4.tick_params(axis='x', rotation=45)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('analisis_dilucion_neural_marketing.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generar_reporte_ejecutivo(self):
        """Genera un reporte ejecutivo completo"""
        roi_df = self.calcular_roi_estrategias()
        
        reporte = f"""
# 📊 REPORTE EJECUTIVO - ANÁLISIS DE DILUCIÓN
## Neural Marketing AI (Copy.ai LATAM)
### Fecha: {datetime.now().strftime('%d de %B de %Y')}

## 🎯 RESUMEN EJECUTIVO

### Estrategias Analizadas:
"""
        
        for _, row in roi_df.iterrows():
            reporte += f"""
**{row['Estrategia']}**
- Equity Final: {row['Equity_Final']:.1f}%
- Valor Fundador: ${row['Valor_Fundador']/1000000:.1f}M
- Dilución Acumulada: {row['Dilucion_Acumulada']:.1f}%
- ROI: {row['ROI']:.1f}%
"""
        
        # Encontrar la mejor estrategia
        mejor_estrategia = roi_df.loc[roi_df['ROI'].idxmax()]
        
        reporte += f"""

## 🏆 RECOMENDACIÓN

**Mejor Estrategia: {mejor_estrategia['Estrategia']}**
- ROI: {mejor_estrategia['ROI']:.1f}%
- Equity Final: {mejor_estrategia['Equity_Final']:.1f}%
- Valor Adicional: ${(mejor_estrategia['Valor_Fundador'] - self.resultados['Sin_Proteccion']['valor_fundador'][-1])/1000000:.1f}M

## 📈 ANÁLISIS DETALLADO

### Comparación de Estrategias:
"""
        
        # Crear tabla comparativa
        tabla = roi_df.to_string(index=False, float_format='%.1f')
        reporte += f"\n```\n{tabla}\n```\n"
        
        reporte += """

## 🎯 PRÓXIMOS PASOS

1. **Implementar estrategia recomendada**
2. **Consultar asesoría legal especializada**
3. **Preparar propuestas para inversionistas**
4. **Monitorear métricas de dilución**
5. **Ajustar estrategia según resultados**

---
*Generado por Simulador de Dilución Neural Marketing AI*
"""
        
        return reporte
    
    def exportar_datos(self, formato='excel'):
        """Exporta los datos a diferentes formatos"""
        if formato == 'excel':
            with pd.ExcelWriter('analisis_dilucion_neural_marketing.xlsx') as writer:
                # ROI por estrategia
                roi_df = self.calcular_roi_estrategias()
                roi_df.to_excel(writer, sheet_name='ROI_Estrategias', index=False)
                
                # Datos detallados por estrategia
                for estrategia, resultados in self.resultados.items():
                    df = pd.DataFrame(resultados)
                    df.to_excel(writer, sheet_name=estrategia, index=False)
        
        elif formato == 'json':
            datos_exportar = {
                'configuracion_base': self.configuracion_base,
                'resultados': self.resultados,
                'roi_estrategias': self.calcular_roi_estrategias().to_dict('records')
            }
            
            with open('analisis_dilucion_neural_marketing.json', 'w') as f:
                json.dump(datos_exportar, f, indent=2, default=str)
    
    def ejecutar_analisis_completo(self):
        """Ejecuta el análisis completo"""
        print("🚀 Iniciando análisis de dilución...")
        
        # Simular estrategias
        self.simular_estrategias_anti_dilucion()
        print("✅ Estrategias simuladas")
        
        # Calcular ROI
        roi_df = self.calcular_roi_estrategias()
        print("✅ ROI calculado")
        
        # Generar gráficos
        self.generar_graficos()
        print("✅ Gráficos generados")
        
        # Generar reporte
        reporte = self.generar_reporte_ejecutivo()
        print("✅ Reporte generado")
        
        # Exportar datos
        self.exportar_datos('excel')
        self.exportar_datos('json')
        print("✅ Datos exportados")
        
        # Guardar reporte
        with open('reporte_dilucion_neural_marketing.md', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print("🎉 Análisis completo finalizado!")
        print(f"📊 Mejor estrategia: {roi_df.loc[roi_df['ROI'].idxmax(), 'Estrategia']}")
        print(f"💰 ROI: {roi_df['ROI'].max():.1f}%")
        
        return reporte

def main():
    """Función principal"""
    simulador = SimuladorDilucion()
    
    print("=" * 60)
    print("🧮 SIMULADOR DE DILUCIÓN - NEURAL MARKETING AI")
    print("=" * 60)
    
    # Ejecutar análisis completo
    reporte = simulador.ejecutar_analisis_completo()
    
    print("\n" + "=" * 60)
    print("📋 REPORTE EJECUTIVO GENERADO")
    print("=" * 60)
    print(reporte)

if __name__ == "__main__":
    main()








