"""
Software y APIs Recomendadas para Optimización Logística
=======================================================

Este archivo contiene una lista completa de software, APIs y herramientas
recomendadas para automatizar la optimización de rutas logísticas.
"""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class HerramientaLogistica:
    """Estructura para herramientas de logística"""
    nombre: str
    tipo: str  # 'software', 'api', 'plataforma', 'algoritmo'
    categoria: str  # 'routing', 'tracking', 'analytics', 'integration'
    descripcion: str
    ventajas: List[str]
    desventajas: List[str]
    costo: str  # 'gratuito', 'freemium', 'pago', 'enterprise'
    url: str
    casos_uso: List[str]

class RecomendacionesSoftware:
    """Clase con recomendaciones de software y APIs para logística"""
    
    def __init__(self):
        self.herramientas = self._inicializar_herramientas()
    
    def _inicializar_herramientas(self) -> List[HerramientaLogistica]:
        """Inicializa lista de herramientas recomendadas"""
        
        return [
            # APIs de Mapas y Navegación
            HerramientaLogistica(
                nombre="Google Maps Platform",
                tipo="api",
                categoria="routing",
                descripcion="API completa para mapas, rutas, tráfico y lugares",
                ventajas=[
                    "Datos de tráfico en tiempo real",
                    "Algoritmos de optimización avanzados",
                    "Cobertura global",
                    "Documentación excelente",
                    "Integración fácil"
                ],
                desventajas=[
                    "Costos por uso pueden ser altos",
                    "Requiere API key",
                    "Rate limits estrictos"
                ],
                costo="pago",
                url="https://developers.google.com/maps",
                casos_uso=[
                    "Optimización de rutas",
                    "Análisis de tráfico",
                    "Geocodificación",
                    "Búsqueda de lugares"
                ]
            ),
            
            HerramientaLogistica(
                nombre="HERE API",
                tipo="api",
                categoria="routing",
                descripcion="Plataforma de ubicación y navegación empresarial",
                ventajas=[
                    "Datos de tráfico precisos",
                    "APIs especializadas en logística",
                    "Cobertura offline",
                    "Precios competitivos",
                    "Soporte empresarial"
                ],
                desventajas=[
                    "Curva de aprendizaje",
                    "Menor comunidad que Google",
                    "Documentación menos extensa"
                ],
                costo="freemium",
                url="https://developer.here.com/",
                casos_uso=[
                    "Navegación comercial",
                    "Análisis de tráfico",
                    "Geocodificación batch",
                    "Mapas offline"
                ]
            ),
            
            HerramientaLogistica(
                nombre="MapBox",
                tipo="api",
                categoria="routing",
                descripcion="Plataforma de mapas personalizables",
                ventajas=[
                    "Mapas altamente personalizables",
                    "APIs de optimización",
                    "Precios flexibles",
                    "Buena documentación",
                    "SDKs para múltiples plataformas"
                ],
                desventajas=[
                    "Menor cobertura de datos de tráfico",
                    "Curva de aprendizaje",
                    "Menos casos de uso empresariales"
                ],
                costo="freemium",
                url="https://www.mapbox.com/",
                casos_uso=[
                    "Aplicaciones móviles",
                    "Visualización de datos",
                    "Mapas personalizados",
                    "Rutas básicas"
                ]
            ),
            
            # Software de Optimización
            HerramientaLogistica(
                nombre="OR-Tools (Google)",
                tipo="software",
                categoria="algoritmo",
                descripcion="Suite de herramientas de optimización de Google",
                ventajas=[
                    "Gratuito y open source",
                    "Algoritmos VRP avanzados",
                    "Soporte para múltiples lenguajes",
                    "Documentación completa",
                    "Comunidad activa"
                ],
                desventajas=[
                    "Curva de aprendizaje técnica",
                    "Requiere conocimiento de programación",
                    "No tiene interfaz gráfica"
                ],
                costo="gratuito",
                url="https://developers.google.com/optimization",
                casos_uso=[
                    "VRP complejo",
                    "Optimización de inventario",
                    "Programación de tareas",
                    "Investigación académica"
                ]
            ),
            
            HerramientaLogistica(
                nombre="Gurobi Optimizer",
                tipo="software",
                categoria="algoritmo",
                descripcion="Solver de optimización matemática comercial",
                ventajas=[
                    "Algoritmos más rápidos",
                    "Soporte técnico profesional",
                    "Interfaces para múltiples lenguajes",
                    "Documentación empresarial",
                    "Garantías de rendimiento"
                ],
                desventajas=[
                    "Costoso para uso comercial",
                    "Requiere licencia",
                    "Curva de aprendizaje"
                ],
                costo="enterprise",
                url="https://www.gurobi.com/",
                casos_uso=[
                    "Optimización empresarial",
                    "VRP a gran escala",
                    "Problemas complejos de scheduling",
                    "Investigación industrial"
                ]
            ),
            
            HerramientaLogistica(
                nombre="CPLEX (IBM)",
                tipo="software",
                categoria="algoritmo",
                descripcion="Solver de optimización matemática de IBM",
                ventajas=[
                    "Rendimiento excelente",
                    "Soporte empresarial",
                    "Integración con IBM Cloud",
                    "Algoritmos avanzados",
                    "Escalabilidad"
                ],
                desventajas=[
                    "Muy costoso",
                    "Complejo de configurar",
                    "Requiere expertise técnico"
                ],
                costo="enterprise",
                url="https://www.ibm.com/products/ilog-cplex-optimization-studio",
                casos_uso=[
                    "Optimización empresarial",
                    "Problemas de gran escala",
                    "Integración con sistemas IBM",
                    "Aplicaciones críticas"
                ]
            ),
            
            # Plataformas de Gestión Logística
            HerramientaLogistica(
                nombre="Route4Me",
                tipo="plataforma",
                categoria="routing",
                descripcion="Plataforma SaaS para optimización de rutas",
                ventajas=[
                    "Interfaz web intuitiva",
                    "Optimización automática",
                    "Tracking en tiempo real",
                    "Integración con APIs",
                    "Soporte móvil"
                ],
                desventajas=[
                    "Costos mensuales",
                    "Limitaciones en personalización",
                    "Dependencia del proveedor"
                ],
                costo="pago",
                url="https://www.route4me.com/",
                casos_uso=[
                    "Gestión de flotas pequeñas",
                    "Entregas de última milla",
                    "Servicios de campo",
                    "Distribución local"
                ]
            ),
            
            HerramientaLogistica(
                nombre="OptiTruck",
                tipo="plataforma",
                categoria="routing",
                descripcion="Solución de optimización para transporte de carga",
                ventajas=[
                    "Especializado en carga pesada",
                    "Considera restricciones de peso",
                    "Optimización de combustible",
                    "Análisis de costos",
                    "Integración con sistemas ERP"
                ],
                desventajas=[
                    "Enfoque específico en carga",
                    "Costos altos",
                    "Menos flexible para otros casos"
                ],
                costo="enterprise",
                url="https://www.optitruck.com/",
                casos_uso=[
                    "Transporte de carga pesada",
                    "Logística industrial",
                    "Distribución regional",
                    "Optimización de combustible"
                ]
            ),
            
            HerramientaLogistica(
                nombre="Transporeon",
                tipo="plataforma",
                categoria="integration",
                descripcion="Plataforma de gestión de transporte y logística",
                ventajas=[
                    "Integración completa",
                    "Marketplace de transportistas",
                    "Análisis avanzado",
                    "Compliance automático",
                    "Escalabilidad"
                ],
                desventajas=[
                    "Complejo de implementar",
                    "Costos altos",
                    "Curva de aprendizaje"
                ],
                costo="enterprise",
                url="https://www.transporeon.com/",
                casos_uso=[
                    "Gestión de transporte empresarial",
                    "Optimización de red logística",
                    "Compliance y documentación",
                    "Análisis de rendimiento"
                ]
            ),
            
            # Herramientas de Tracking
            HerramientaLogistica(
                nombre="Samsara",
                tipo="plataforma",
                categoria="tracking",
                descripcion="Plataforma IoT para gestión de flotas",
                ventajas=[
                    "Hardware IoT integrado",
                    "Analytics avanzados",
                    "Mantenimiento predictivo",
                    "Compliance automático",
                    "Interfaz moderna"
                ],
                desventajas=[
                    "Requiere hardware específico",
                    "Costos altos",
                    "Dependencia del ecosistema"
                ],
                costo="pago",
                url="https://www.samsara.com/",
                casos_uso=[
                    "Gestión de flotas IoT",
                    "Mantenimiento predictivo",
                    "Compliance de seguridad",
                    "Analytics de conducción"
                ]
            ),
            
            HerramientaLogistica(
                nombre="Geotab",
                tipo="plataforma",
                categoria="tracking",
                descripcion="Plataforma de telemetría para vehículos",
                ventajas=[
                    "Hardware confiable",
                    "Analytics detallados",
                    "Integración con APIs",
                    "Escalabilidad",
                    "Soporte global"
                ],
                desventajas=[
                    "Costos por dispositivo",
                    "Curva de aprendizaje",
                    "Limitaciones de personalización"
                ],
                costo="pago",
                url="https://www.geotab.com/",
                casos_uso=[
                    "Telemetría de vehículos",
                    "Gestión de flotas",
                    "Análisis de rendimiento",
                    "Compliance regulatorio"
                ]
            ),
            
            # APIs de Datos Externos
            HerramientaLogistica(
                nombre="OpenWeather API",
                tipo="api",
                categoria="analytics",
                descripcion="API de datos meteorológicos",
                ventajas=[
                    "Datos precisos",
                    "Pronósticos extendidos",
                    "Precios accesibles",
                    "Documentación clara",
                    "Cobertura global"
                ],
                desventajas=[
                    "Rate limits",
                    "Dependencia de conectividad",
                    "Costos por requests"
                ],
                costo="freemium",
                url="https://openweathermap.org/api",
                casos_uso=[
                    "Planificación de rutas",
                    "Análisis de impacto climático",
                    "Optimización por condiciones",
                    "Alertas meteorológicas"
                ]
            ),
            
            HerramientaLogistica(
                nombre="Fuel Price APIs",
                tipo="api",
                categoria="analytics",
                descripcion="APIs de precios de combustible",
                ventajas=[
                    "Datos en tiempo real",
                    "Cobertura nacional",
                    "Integración fácil",
                    "Actualizaciones frecuentes"
                ],
                desventajas=[
                    "Disponibilidad limitada",
                    "Costos variables",
                    "Calidad de datos variable"
                ],
                costo="pago",
                url="https://fuelpriceapi.com/",
                casos_uso=[
                    "Optimización de costos",
                    "Planificación de rutas",
                    "Análisis de rentabilidad",
                    "Comparación de precios"
                ]
            ),
            
            # Herramientas de Análisis
            HerramientaLogistica(
                nombre="Tableau",
                tipo="software",
                categoria="analytics",
                descripcion="Plataforma de visualización y análisis de datos",
                ventajas=[
                    "Visualizaciones potentes",
                    "Integración con múltiples fuentes",
                    "Dashboards interactivos",
                    "Análisis predictivo",
                    "Comunidad activa"
                ],
                desventajas=[
                    "Costos altos",
                    "Curva de aprendizaje",
                    "Requiere datos estructurados"
                ],
                costo="pago",
                url="https://www.tableau.com/",
                casos_uso=[
                    "Dashboards logísticos",
                    "Análisis de rendimiento",
                    "Reportes ejecutivos",
                    "Visualización de rutas"
                ]
            ),
            
            HerramientaLogistica(
                nombre="Power BI",
                tipo="software",
                categoria="analytics",
                descripcion="Herramienta de análisis de datos de Microsoft",
                ventajas=[
                    "Integración con Microsoft ecosystem",
                    "Precios accesibles",
                    "Fácil de usar",
                    "Conectores nativos",
                    "Soporte empresarial"
                ],
                desventajas=[
                    "Limitaciones en personalización",
                    "Dependencia de Microsoft",
                    "Menos flexibilidad que Tableau"
                ],
                costo="freemium",
                url="https://powerbi.microsoft.com/",
                casos_uso=[
                    "Reportes empresariales",
                    "Análisis de KPIs",
                    "Dashboards operativos",
                    "Integración con Office 365"
                ]
            )
        ]
    
    def obtener_por_categoria(self, categoria: str) -> List[HerramientaLogistica]:
        """Obtiene herramientas filtradas por categoría"""
        return [h for h in self.herramientas if h.categoria == categoria]
    
    def obtener_por_costo(self, costo: str) -> List[HerramientaLogistica]:
        """Obtiene herramientas filtradas por costo"""
        return [h for h in self.herramientas if h.costo == costo]
    
    def obtener_por_tipo(self, tipo: str) -> List[HerramientaLogistica]:
        """Obtiene herramientas filtradas por tipo"""
        return [h for h in self.herramientas if h.tipo == tipo]
    
    def buscar_por_caso_uso(self, caso_uso: str) -> List[HerramientaLogistica]:
        """Busca herramientas por caso de uso específico"""
        return [h for h in self.herramientas if caso_uso.lower() in [cu.lower() for cu in h.casos_uso]]
    
    def generar_recomendacion(self, presupuesto: str, tamaño_empresa: str, 
                            caso_uso_principal: str) -> Dict[str, List[HerramientaLogistica]]:
        """Genera recomendaciones personalizadas"""
        
        recomendaciones = {
            'apis_esenciales': [],
            'software_optimizacion': [],
            'plataformas_gestion': [],
            'herramientas_analisis': []
        }
        
        # Filtrar por presupuesto
        if presupuesto == 'bajo':
            herramientas_filtradas = self.obtener_por_costo('gratuito') + self.obtener_por_costo('freemium')
        elif presupuesto == 'medio':
            herramientas_filtradas = self.herramientas
        else:  # alto
            herramientas_filtradas = self.herramientas
        
        # APIs esenciales
        recomendaciones['apis_esenciales'] = [
            h for h in herramientas_filtradas 
            if h.tipo == 'api' and h.categoria in ['routing', 'analytics']
        ]
        
        # Software de optimización
        recomendaciones['software_optimizacion'] = [
            h for h in herramientas_filtradas 
            if h.tipo == 'software' and h.categoria == 'algoritmo'
        ]
        
        # Plataformas de gestión
        recomendaciones['plataformas_gestion'] = [
            h for h in herramientas_filtradas 
            if h.tipo == 'plataforma'
        ]
        
        # Herramientas de análisis
        recomendaciones['herramientas_analisis'] = [
            h for h in herramientas_filtradas 
            if h.categoria == 'analytics'
        ]
        
        return recomendaciones

def mostrar_recomendaciones_completas():
    """Muestra todas las recomendaciones de software y APIs"""
    
    print("=" * 80)
    print("SOFTWARE Y APIs RECOMENDADAS PARA OPTIMIZACIÓN LOGÍSTICA")
    print("=" * 80)
    
    recomendaciones = RecomendacionesSoftware()
    
    # Mostrar por categorías
    categorias = ['routing', 'tracking', 'analytics', 'integration', 'algoritmo']
    
    for categoria in categorias:
        print(f"\n📋 {categoria.upper()}")
        print("-" * 50)
        
        herramientas = recomendaciones.obtener_por_categoria(categoria)
        
        for herramienta in herramientas:
            print(f"\n🔧 {herramienta.nombre}")
            print(f"   Tipo: {herramienta.tipo}")
            print(f"   Costo: {herramienta.costo}")
            print(f"   Descripción: {herramienta.descripcion}")
            print(f"   URL: {herramienta.url}")
            
            print("   Ventajas:")
            for ventaja in herramienta.ventajas:
                print(f"     ✓ {ventaja}")
            
            print("   Casos de uso:")
            for caso in herramienta.casos_uso:
                print(f"     • {caso}")
    
    # Mostrar recomendaciones por presupuesto
    print(f"\n💰 RECOMENDACIONES POR PRESUPUESTO")
    print("-" * 50)
    
    presupuestos = ['bajo', 'medio', 'alto']
    
    for presupuesto in presupuestos:
        print(f"\n💵 PRESUPUESTO {presupuesto.upper()}:")
        
        if presupuesto == 'bajo':
            herramientas = recomendaciones.obtener_por_costo('gratuito') + recomendaciones.obtener_por_costo('freemium')
        elif presupuesto == 'medio':
            herramientas = [h for h in recomendaciones.herramientas if h.costo in ['freemium', 'pago']]
        else:  # alto
            herramientas = recomendaciones.herramientas
        
        for herramienta in herramientas[:5]:  # Top 5 por presupuesto
            print(f"   • {herramienta.nombre} ({herramienta.costo})")
    
    # Mostrar casos de uso específicos
    print(f"\n🎯 CASOS DE USO ESPECÍFICOS")
    print("-" * 50)
    
    casos_uso = [
        'entregas de última milla',
        'distribución empresarial',
        'gestión de flotas',
        'optimización de combustible',
        'análisis de tráfico'
    ]
    
    for caso in casos_uso:
        print(f"\n📍 {caso.upper()}:")
        herramientas = recomendaciones.buscar_por_caso_uso(caso)
        
        for herramienta in herramientas[:3]:  # Top 3 por caso de uso
            print(f"   • {herramienta.nombre}")

def generar_recomendacion_personalizada():
    """Genera recomendación personalizada basada en criterios"""
    
    print("\n" + "=" * 80)
    print("GENERADOR DE RECOMENDACIONES PERSONALIZADAS")
    print("=" * 80)
    
    recomendaciones = RecomendacionesSoftware()
    
    # Simular criterios del usuario
    presupuesto = 'medio'  # 'bajo', 'medio', 'alto'
    tamaño_empresa = 'mediana'  # 'pequeña', 'mediana', 'grande'
    caso_uso_principal = 'distribución empresarial'
    
    print(f"📊 Criterios de selección:")
    print(f"   Presupuesto: {presupuesto}")
    print(f"   Tamaño empresa: {tamaño_empresa}")
    print(f"   Caso de uso principal: {caso_uso_principal}")
    
    # Generar recomendaciones
    recomendacion = recomendaciones.generar_recomendacion(
        presupuesto, tamaño_empresa, caso_uso_principal
    )
    
    print(f"\n🎯 RECOMENDACIONES PERSONALIZADAS:")
    
    for categoria, herramientas in recomendacion.items():
        if herramientas:
            print(f"\n📋 {categoria.upper()}:")
            for herramienta in herramientas[:3]:  # Top 3 por categoría
                print(f"   • {herramienta.nombre}")
                print(f"     {herramienta.descripcion}")
                print(f"     Costo: {herramienta.costo}")
                print(f"     URL: {herramienta.url}")

if __name__ == "__main__":
    mostrar_recomendaciones_completas()
    generar_recomendacion_personalizada()



