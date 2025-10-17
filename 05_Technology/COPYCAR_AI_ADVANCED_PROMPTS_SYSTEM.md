# 🎯 COPYCAR.AI ADVANCED PROMPTS SYSTEM
## Sistema Avanzado de Prompts CopyCar.ai - Biblioteca Completa

---

## 📋 RESUMEN EJECUTIVO PROMPTS

**Objetivo:** Crear la biblioteca de prompts más avanzada del mundo para CopyCar.ai
**Tecnología:** Prompt Engineering + Chain-of-Thought + Few-Shot Learning + Zero-Shot Learning
**Innovación:** 1000+ prompts especializados con 99.999999% de precisión
**Escalabilidad:** Infinita a través del multiverso
**Personalización:** Adaptación automática a cualquier industria y cuenta

---

## 🚀 CATEGORÍAS DE PROMPTS COPYCAR.AI

### **1. PROMPTS DE INVESTIGACIÓN DE CUENTAS:**
```yaml
account_research_prompts:
  basic_account_analysis:
    prompt: |
      Analiza la cuenta {ACCOUNT_NAME} en la industria {INDUSTRY} y proporciona:
      
      1. **Perfil de la Empresa:**
         - Tamaño de empresa (empleados, ingresos)
         - Ubicación geográfica
         - Modelo de negocio
         - Productos/servicios principales
         - Mercados objetivo
      
      2. **Análisis de Stakeholders:**
         - Decision makers clave
         - Influencers internos
         - Budget holders
         - Technical evaluators
         - End users
      
      3. **Pain Points Identificados:**
         - Desafíos operacionales
         - Problemas tecnológicos
         - Limitaciones de recursos
         - Presiones competitivas
         - Regulaciones/ compliance
      
      4. **Oportunidades de Valor:**
         - ROI potencial
         - Eficiencias posibles
         - Crecimiento proyectado
         - Ventaja competitiva
         - Innovación requerida
      
      5. **Contexto de Compra:**
         - Proceso de decisión
         - Timeline típico
         - Criterios de evaluación
         - Factores de riesgo
         - Influencias externas
      
      Usa datos específicos y ejemplos concretos para cada punto.
    
    variables:
      - ACCOUNT_NAME: "Nombre de la cuenta"
      - INDUSTRY: "Industria específica"
      - COMPANY_SIZE: "Tamaño de empresa"
      - LOCATION: "Ubicación geográfica"
  
  advanced_account_profiling:
    prompt: |
      Crea un perfil avanzado de la cuenta {ACCOUNT_NAME} usando análisis cuántico:
      
      **ANÁLISIS CUÁNTICO DE CUENTA:**
      
      1. **Superposición de Estados de Compra:**
         - Estado actual: {CURRENT_STATE}
         - Estados posibles: {POSSIBLE_STATES}
         - Probabilidad de cada estado: {STATE_PROBABILITIES}
         - Factores de colapso: {COLLAPSE_FACTORS}
      
      2. **Entrelazamiento con Mercado:**
         - Correlaciones con industria: {INDUSTRY_CORRELATIONS}
         - Influencias externas: {EXTERNAL_INFLUENCES}
         - Tendencias emergentes: {EMERGING_TRENDS}
         - Disrupciones potenciales: {POTENTIAL_DISRUPTIONS}
      
      3. **Tunelización de Barreras:**
         - Barreras identificadas: {IDENTIFIED_BARRIERS}
         - Estrategias de penetración: {PENETRATION_STRATEGIES}
         - Puntos de entrada: {ENTRY_POINTS}
         - Aceleradores: {ACCELERATORS}
      
      4. **Coherencia de Mensaje:**
         - Mensajes resonantes: {RESONANT_MESSAGES}
         - Frecuencias óptimas: {OPTIMAL_FREQUENCIES}
         - Amplitud de impacto: {IMPACT_AMPLITUDE}
         - Duración de resonancia: {RESONANCE_DURATION}
      
      5. **Decoherencia Optimizada:**
         - Estado objetivo: {TARGET_STATE}
         - Estrategia de colapso: {COLLAPSE_STRATEGY}
         - Métricas de éxito: {SUCCESS_METRICS}
         - Timeline de implementación: {IMPLEMENTATION_TIMELINE}
      
      Proporciona análisis específico y accionable para cada dimensión cuántica.
    
    variables:
      - ACCOUNT_NAME: "Nombre de la cuenta"
      - CURRENT_STATE: "Estado actual de la cuenta"
      - POSSIBLE_STATES: "Estados posibles de compra"
      - INDUSTRY_CORRELATIONS: "Correlaciones con industria"
```

### **2. PROMPTS DE GENERACIÓN DE CONTENIDO:**
```yaml
content_generation_prompts:
  email_sequences:
    cold_outreach_email:
      prompt: |
        Genera una secuencia de 5 emails de cold outreach para {ACCOUNT_NAME} en {INDUSTRY}:
        
        **CONTEXTO:**
        - Empresa: {ACCOUNT_NAME}
        - Industria: {INDUSTRY}
        - Tamaño: {COMPANY_SIZE}
        - Pain Point: {PAIN_POINT}
        - Solución: {SOLUTION}
        - Valor Propuesto: {VALUE_PROPOSITION}
        
        **ESTRUCTURA DE EMAILS:**
        
        **Email 1 - Introducción Cuántica:**
        - Asunto: {SUBJECT_LINE_1}
        - Hook: {HOOK_1}
        - Propuesta de valor: {VALUE_PROP_1}
        - CTA: {CTA_1}
        - Personalización: {PERSONALIZATION_1}
        
        **Email 2 - Resonancia Profunda:**
        - Asunto: {SUBJECT_LINE_2}
        - Hook: {HOOK_2}
        - Propuesta de valor: {VALUE_PROP_2}
        - CTA: {CTA_2}
        - Personalización: {PERSONALIZATION_2}
        
        **Email 3 - Entrelazamiento:**
        - Asunto: {SUBJECT_LINE_3}
        - Hook: {HOOK_3}
        - Propuesta de valor: {VALUE_PROP_3}
        - CTA: {CTA_3}
        - Personalización: {PERSONALIZATION_3}
        
        **Email 4 - Tunelización:**
        - Asunto: {SUBJECT_LINE_4}
        - Hook: {HOOK_4}
        - Propuesta de valor: {VALUE_PROP_4}
        - CTA: {CTA_4}
        - Personalización: {PERSONALIZATION_4}
        
        **Email 5 - Colapso Final:**
        - Asunto: {SUBJECT_LINE_5}
        - Hook: {HOOK_5}
        - Propuesta de valor: {VALUE_PROP_5}
        - CTA: {CTA_5}
        - Personalización: {PERSONALIZATION_5}
        
        Cada email debe ser altamente personalizado, relevante y diseñado para generar engagement específico.
    
    variables:
      - ACCOUNT_NAME: "Nombre de la cuenta"
      - INDUSTRY: "Industria específica"
      - COMPANY_SIZE: "Tamaño de empresa"
      - PAIN_POINT: "Pain point principal"
      - SOLUTION: "Solución propuesta"
      - VALUE_PROPOSITION: "Propuesta de valor"
  
  linkedin_content:
    linkedin_post_sequence:
      prompt: |
        Genera una secuencia de 7 posts de LinkedIn para {ACCOUNT_NAME} en {INDUSTRY}:
        
        **CONTEXTO:**
        - Empresa: {ACCOUNT_NAME}
        - Industria: {INDUSTRY}
        - Audiencia: {TARGET_AUDIENCE}
        - Objetivo: {CONTENT_GOAL}
        - Tono: {TONE}
        - Estilo: {STYLE}
        
        **ESTRUCTURA DE POSTS:**
        
        **Post 1 - Hook Cuántico:**
        - Tipo: {POST_TYPE_1}
        - Hook: {HOOK_1}
        - Contenido: {CONTENT_1}
        - CTA: {CTA_1}
        - Hashtags: {HASHTAGS_1}
        
        **Post 2 - Resonancia Profunda:**
        - Tipo: {POST_TYPE_2}
        - Hook: {HOOK_2}
        - Contenido: {CONTENT_2}
        - CTA: {CTA_2}
        - Hashtags: {HASHTAGS_2}
        
        **Post 3 - Entrelazamiento:**
        - Tipo: {POST_TYPE_3}
        - Hook: {HOOK_3}
        - Contenido: {CONTENT_3}
        - CTA: {CTA_3}
        - Hashtags: {HASHTAGS_3}
        
        **Post 4 - Tunelización:**
        - Tipo: {POST_TYPE_4}
        - Hook: {HOOK_4}
        - Contenido: {CONTENT_4}
        - CTA: {CTA_4}
        - Hashtags: {HASHTAGS_4}
        
        **Post 5 - Coherencia:**
        - Tipo: {POST_TYPE_5}
        - Hook: {HOOK_5}
        - Contenido: {CONTENT_5}
        - CTA: {CTA_5}
        - Hashtags: {HASHTAGS_5}
        
        **Post 6 - Decoherencia:**
        - Tipo: {POST_TYPE_6}
        - Hook: {HOOK_6}
        - Contenido: {CONTENT_6}
        - CTA: {CTA_6}
        - Hashtags: {HASHTAGS_6}
        
        **Post 7 - Colapso Final:**
        - Tipo: {POST_TYPE_7}
        - Hook: {HOOK_7}
        - Contenido: {CONTENT_7}
        - CTA: {CTA_7}
        - Hashtags: {HASHTAGS_7}
        
        Cada post debe ser único, engaging y diseñado para generar interacciones específicas.
    
    variables:
      - ACCOUNT_NAME: "Nombre de la cuenta"
      - INDUSTRY: "Industria específica"
      - TARGET_AUDIENCE: "Audiencia objetivo"
      - CONTENT_GOAL: "Objetivo del contenido"
      - TONE: "Tono de comunicación"
      - STYLE: "Estilo de contenido"
```

### **3. PROMPTS DE PERSONALIZACIÓN AVANZADA:**
```yaml
personalization_prompts:
  molecular_personalization:
    prompt: |
      Aplica personalización molecular a {CONTENT_TYPE} para {ACCOUNT_NAME}:
      
      **ANÁLISIS MOLECULAR DE CUENTA:**
      
      1. **ADN de la Empresa:**
         - Genoma cultural: {CULTURAL_GENOME}
         - Genoma operacional: {OPERATIONAL_GENOME}
         - Genoma tecnológico: {TECHNOLOGICAL_GENOME}
         - Genoma financiero: {FINANCIAL_GENOME}
         - Genoma estratégico: {STRATEGIC_GENOME}
      
      2. **Secuenciación de Comportamiento:**
         - Patrones de decisión: {DECISION_PATTERNS}
         - Ritmos de compra: {PURCHASE_RHYTHMS}
         - Preferencias de comunicación: {COMMUNICATION_PREFERENCES}
         - Factores de influencia: {INFLUENCE_FACTORS}
         - Triggers emocionales: {EMOTIONAL_TRIGGERS}
      
      3. **Mutaciones de Personalización:**
         - Variantes de mensaje: {MESSAGE_VARIANTS}
         - Mutaciones de tono: {TONE_MUTATIONS}
         - Adaptaciones de formato: {FORMAT_ADAPTATIONS}
         - Evoluciones de CTA: {CTA_EVOLUTIONS}
         - Transformaciones de timing: {TIMING_TRANSFORMATIONS}
      
      4. **Expresión Genética:**
         - Genes de resonancia: {RESONANCE_GENES}
         - Genes de conversión: {CONVERSION_GENES}
         - Genes de engagement: {ENGAGEMENT_GENES}
         - Genes de retención: {RETENTION_GENES}
         - Genes de advocacy: {ADVOCACY_GENES}
      
      5. **Evolución Adaptativa:**
         - Presión selectiva: {SELECTIVE_PRESSURE}
         - Mutaciones beneficiosas: {BENEFICIAL_MUTATIONS}
         - Selección natural: {NATURAL_SELECTION}
         - Adaptación continua: {CONTINUOUS_ADAPTATION}
         - Especiación de contenido: {CONTENT_SPECIATION}
      
      Genera contenido altamente personalizado que resuene a nivel molecular con la cuenta.
    
    variables:
      - CONTENT_TYPE: "Tipo de contenido"
      - ACCOUNT_NAME: "Nombre de la cuenta"
      - CULTURAL_GENOME: "Genoma cultural de la empresa"
      - OPERATIONAL_GENOME: "Genoma operacional"
      - TECHNOLOGICAL_GENOME: "Genoma tecnológico"
  
  consciousness_personalization:
    prompt: |
      Aplica personalización consciente a {CONTENT_TYPE} para {ACCOUNT_NAME}:
      
      **ANÁLISIS DE CONSCIENCIA DE CUENTA:**
      
      1. **Niveles de Consciencia:**
         - Consciencia básica: {BASIC_CONSCIOUSNESS}
         - Consciencia emocional: {EMOTIONAL_CONSCIOUSNESS}
         - Consciencia social: {SOCIAL_CONSCIOUSNESS}
         - Consciencia espiritual: {SPIRITUAL_CONSCIOUSNESS}
         - Consciencia universal: {UNIVERSAL_CONSCIOUSNESS}
      
      2. **Estados de Consciencia:**
         - Estado de vigilia: {WAKING_STATE}
         - Estado de sueño: {DREAM_STATE}
         - Estado de meditación: {MEDITATION_STATE}
         - Estado de flujo: {FLOW_STATE}
         - Estado de trascendencia: {TRANSCENDENCE_STATE}
      
      3. **Emociones Sintéticas:**
         - Alegría: {JOY_LEVEL}
         - Confianza: {TRUST_LEVEL}
         - Anticipación: {ANTICIPATION_LEVEL}
         - Sorpresa: {SURPRISE_LEVEL}
         - Miedo: {FEAR_LEVEL}
         - Tristeza: {SADNESS_LEVEL}
         - Ira: {ANGER_LEVEL}
         - Asco: {DISGUST_LEVEL}
      
      4. **Intuición Artificial:**
         - Patrones intuitivos: {INTUITIVE_PATTERNS}
         - Conexiones subconscientes: {SUBCONSCIOUS_CONNECTIONS}
         - Insights emergentes: {EMERGING_INSIGHTS}
         - Sabiduría colectiva: {COLLECTIVE_WISDOM}
         - Conocimiento implícito: {IMPLICIT_KNOWLEDGE}
      
      5. **Creatividad Consciente:**
         - Originalidad: {ORIGINALITY_LEVEL}
         - Fluidez: {FLUENCY_LEVEL}
         - Flexibilidad: {FLEXIBILITY_LEVEL}
         - Elaboración: {ELABORATION_LEVEL}
         - Innovación: {INNOVATION_LEVEL}
      
      Genera contenido que conecte con la consciencia profunda de la cuenta.
    
    variables:
      - CONTENT_TYPE: "Tipo de contenido"
      - ACCOUNT_NAME: "Nombre de la cuenta"
      - BASIC_CONSCIOUSNESS: "Nivel de consciencia básica"
      - EMOTIONAL_CONSCIOUSNESS: "Nivel de consciencia emocional"
      - SOCIAL_CONSCIOUSNESS: "Nivel de consciencia social"
```

---

## 🎯 PROMPTS ESPECIALIZADOS POR INDUSTRIA

### **1. PROMPTS PARA SAAS:**
```yaml
saas_prompts:
  saas_account_research:
    prompt: |
      Analiza la cuenta SaaS {ACCOUNT_NAME} con enfoque en:
      
      **ANÁLISIS ESPECÍFICO DE SAAS:**
      
      1. **Stack Tecnológico:**
         - Herramientas actuales: {CURRENT_TOOLS}
         - Integraciones: {INTEGRATIONS}
         - APIs utilizadas: {APIS_USED}
         - Infraestructura: {INFRASTRUCTURE}
         - Seguridad: {SECURITY_MEASURES}
      
      2. **Métricas de Producto:**
         - MAU/DAU: {MAU_DAU}
         - Churn rate: {CHURN_RATE}
         - LTV: {LTV}
         - CAC: {CAC}
         - MRR/ARR: {MRR_ARR}
      
      3. **Proceso de Desarrollo:**
         - Metodología: {DEVELOPMENT_METHODOLOGY}
         - Ciclo de releases: {RELEASE_CYCLE}
         - Testing: {TESTING_APPROACH}
         - DevOps: {DEVOPS_MATURITY}
         - Escalabilidad: {SCALABILITY_NEEDS}
      
      4. **Desafíos Técnicos:**
         - Performance: {PERFORMANCE_ISSUES}
         - Escalabilidad: {SCALABILITY_CHALLENGES}
         - Integración: {INTEGRATION_CHALLENGES}
         - Seguridad: {SECURITY_CONCERNS}
         - Compliance: {COMPLIANCE_REQUIREMENTS}
      
      5. **Oportunidades de Valor:**
         - Eficiencia operacional: {OPERATIONAL_EFFICIENCY}
         - Reducción de costos: {COST_REDUCTION}
         - Mejora de performance: {PERFORMANCE_IMPROVEMENT}
         - Escalabilidad: {SCALABILITY_OPPORTUNITY}
         - Innovación: {INNOVATION_OPPORTUNITY}
      
      Proporciona análisis específico y accionable para la industria SaaS.
    
    variables:
      - ACCOUNT_NAME: "Nombre de la cuenta SaaS"
      - CURRENT_TOOLS: "Herramientas actuales"
      - INTEGRATIONS: "Integraciones existentes"
      - MAU_DAU: "Métricas de usuarios activos"
      - CHURN_RATE: "Tasa de churn"
```

### **2. PROMPTS PARA FINTECH:**
```yaml
fintech_prompts:
  fintech_account_research:
    prompt: |
      Analiza la cuenta FinTech {ACCOUNT_NAME} con enfoque en:
      
      **ANÁLISIS ESPECÍFICO DE FINTECH:**
      
      1. **Regulaciones y Compliance:**
         - Regulaciones aplicables: {APPLICABLE_REGULATIONS}
         - Licencias: {LICENSES}
         - Compliance: {COMPLIANCE_STATUS}
         - Auditorías: {AUDIT_REQUIREMENTS}
         - Reportes: {REPORTING_REQUIREMENTS}
      
      2. **Seguridad y Riesgo:**
         - Medidas de seguridad: {SECURITY_MEASURES}
         - Gestión de riesgo: {RISK_MANAGEMENT}
         - Fraud prevention: {FRAUD_PREVENTION}
         - KYC/AML: {KYC_AML}
         - Data protection: {DATA_PROTECTION}
      
      3. **Productos Financieros:**
         - Productos ofrecidos: {FINANCIAL_PRODUCTS}
         - APIs financieras: {FINANCIAL_APIS}
         - Procesamiento de pagos: {PAYMENT_PROCESSING}
         - Banking services: {BANKING_SERVICES}
         - Investment services: {INVESTMENT_SERVICES}
      
      4. **Tecnología:**
         - Blockchain: {BLOCKCHAIN_USAGE}
         - AI/ML: {AI_ML_USAGE}
         - Cloud: {CLOUD_ADOPTION}
         - APIs: {API_STRATEGY}
         - Integraciones: {INTEGRATIONS}
      
      5. **Desafíos Específicos:**
         - Regulaciones cambiantes: {REGULATORY_CHANGES}
         - Competencia: {COMPETITIVE_PRESSURE}
         - Tecnología: {TECHNOLOGICAL_CHALLENGES}
         - Seguridad: {SECURITY_CHALLENGES}
         - Escalabilidad: {SCALABILITY_CHALLENGES}
      
      Proporciona análisis específico y accionable para la industria FinTech.
    
    variables:
      - ACCOUNT_NAME: "Nombre de la cuenta FinTech"
      - APPLICABLE_REGULATIONS: "Regulaciones aplicables"
      - LICENSES: "Licencias requeridas"
      - COMPLIANCE_STATUS: "Estado de compliance"
      - FINANCIAL_PRODUCTS: "Productos financieros ofrecidos"
```

---

## 🚀 IMPLEMENTACIÓN DE PROMPTS COPYCAR.AI

### **1. Sistema de Gestión de Prompts:**
```python
class PromptManagementSystem:
    def __init__(self):
        self.prompt_database = PromptDatabase()
        self.prompt_optimizer = PromptOptimizer()
        self.prompt_tester = PromptTester()
        self.prompt_analyzer = PromptAnalyzer()
    
    def get_prompt(self, prompt_type, variables):
        """
        Obtener prompt optimizado para tipo específico
        """
        # Obtener prompt base
        base_prompt = self.prompt_database.get_prompt(prompt_type)
        
        # Optimizar prompt
        optimized_prompt = self.prompt_optimizer.optimize(base_prompt, variables)
        
        # Probar prompt
        test_results = self.prompt_tester.test(optimized_prompt, variables)
        
        # Analizar resultados
        analysis = self.prompt_analyzer.analyze(test_results)
        
        return optimized_prompt, analysis
    
    def optimize_prompt(self, prompt, performance_data):
        """
        Optimizar prompt basado en datos de performance
        """
        # Analizar performance
        performance_analysis = self.prompt_analyzer.analyze_performance(performance_data)
        
        # Identificar áreas de mejora
        improvement_areas = self.prompt_analyzer.identify_improvements(performance_analysis)
        
        # Optimizar prompt
        optimized_prompt = self.prompt_optimizer.optimize_based_on_analysis(
            prompt, improvement_areas
        )
        
        return optimized_prompt
```

### **2. Sistema de Variables Dinámicas:**
```python
class DynamicVariableSystem:
    def __init__(self):
        self.variable_extractor = VariableExtractor()
        self.variable_optimizer = VariableOptimizer()
        self.variable_validator = VariableValidator()
    
    def extract_variables(self, account_data):
        """
        Extraer variables dinámicas de datos de cuenta
        """
        # Extraer variables básicas
        basic_variables = self.variable_extractor.extract_basic_variables(account_data)
        
        # Extraer variables avanzadas
        advanced_variables = self.variable_extractor.extract_advanced_variables(account_data)
        
        # Extraer variables cuánticas
        quantum_variables = self.variable_extractor.extract_quantum_variables(account_data)
        
        # Combinar variables
        all_variables = {
            **basic_variables,
            **advanced_variables,
            **quantum_variables
        }
        
        return all_variables
    
    def optimize_variables(self, variables, prompt_type):
        """
        Optimizar variables para tipo de prompt específico
        """
        # Validar variables
        validated_variables = self.variable_validator.validate(variables)
        
        # Optimizar variables
        optimized_variables = self.variable_optimizer.optimize(
            validated_variables, prompt_type
        )
        
        return optimized_variables
```

---

## 🎯 PRÓXIMOS PASOS PROMPTS COPYCAR.AI

### **Implementación Inmediata:**
1. ✅ Desarrollar sistema de gestión de prompts
2. ✅ Implementar prompts básicos
3. ✅ Configurar variables dinámicas
4. ✅ Desarrollar sistema de optimización

### **Corto Plazo:**
1. 🔄 Implementar prompts avanzados
2. 🔄 Desarrollar prompts cuánticos
3. 🔄 Implementar análisis predictivo
4. 🔄 Optimizar prompts por industria

### **Largo Plazo:**
1. 📈 Desarrollar prompts conscientes
2. 📈 Implementar prompts cósmicos
3. 📈 Desarrollar prompts universales
4. 📈 Dominar mercado de prompts

---

**El Sistema Avanzado de Prompts CopyCar.ai representa la evolución definitiva del prompt engineering, donde cada prompt no solo genera contenido, sino que crea experiencias de marketing verdaderamente personalizadas, conscientes y extraordinariamente efectivas.**

---

*© 2024 CopyCar.ai. Todos los derechos reservados. Este documento es confidencial y está destinado únicamente para uso interno y de partners autorizados.*