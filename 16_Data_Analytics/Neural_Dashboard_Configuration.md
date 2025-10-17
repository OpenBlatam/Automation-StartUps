# ⚙️ Neural Sales Dashboard - Guía de Configuración

## 🔧 Configuración Completa

### **Archivo de Configuración Principal**
```javascript
// neural-dashboard-config.js
const NeuralDashboardConfig = {
    // ========================================
    // CONFIGURACIÓN GENERAL
    // ========================================
    company: {
        name: "Sintra AI Marketing",
        logo: "🧠",
        primaryColor: "#667eea",
        secondaryColor: "#764ba2",
        accentColor: "#f093fb",
        timezone: "America/Mexico_City"
    },

    // ========================================
    // CONFIGURACIÓN DE KPIs
    // ========================================
    kpis: {
        totalRevenue: {
            name: "Ingresos Totales",
            icon: "fas fa-dollar-sign",
            unit: "$",
            format: "currency",
            target: 150000,
            current: 127450,
            change: 12.5,
            changeType: "positive",
            description: "Suma total de ingresos generados en el período",
            alertThreshold: 0.15, // 15% por encima del objetivo
            priority: "high"
        },
        
        conversionRate: {
            name: "Conversión Lead a Cliente",
            icon: "fas fa-bullseye",
            unit: "%",
            format: "percentage",
            target: 25,
            current: 23.4,
            change: 3.2,
            changeType: "positive",
            description: "Porcentaje de leads que se convierten en clientes",
            alertThreshold: 0.20, // 20% de conversión
            priority: "high"
        },
        
        newCustomers: {
            name: "Nuevos Clientes",
            icon: "fas fa-user-plus",
            unit: "",
            format: "number",
            target: 50,
            current: 47,
            change: 8,
            changeType: "positive",
            description: "Número de clientes adquiridos en el período",
            alertThreshold: 0.10, // 10% por encima del objetivo
            priority: "medium"
        },
        
        mrrGrowth: {
            name: "Crecimiento MRR",
            icon: "fas fa-chart-area",
            unit: "%",
            format: "percentage",
            target: 20,
            current: 18.7,
            change: 2.1,
            changeType: "positive",
            description: "Crecimiento mensual de ingresos recurrentes",
            alertThreshold: 0.15, // 15% de crecimiento
            priority: "high"
        },
        
        avgDealSize: {
            name: "Valor Promedio de Venta",
            icon: "fas fa-gem",
            unit: "$",
            format: "currency",
            target: 3000,
            current: 2710,
            change: 340,
            changeType: "positive",
            description: "Ingresos promedio por transacción",
            alertThreshold: 0.20, // 20% por encima del objetivo
            priority: "medium"
        },
        
        avgCloseTime: {
            name: "Tiempo Promedio de Cierre",
            icon: "fas fa-clock",
            unit: "días",
            format: "number",
            target: 10,
            current: 14,
            change: -3,
            changeType: "negative",
            description: "Días promedio desde lead hasta cierre",
            alertThreshold: 0.20, // 20% por encima del objetivo
            priority: "medium"
        }
    },

    // ========================================
    // CONFIGURACIÓN DE GRÁFICOS
    // ========================================
    charts: {
        salesChannels: {
            title: "Tendencia de Ventas por Canal",
            type: "doughnut",
            data: {
                labels: ['LinkedIn', 'Google Ads', 'Email Marketing', 'Webinars', 'Referidos', 'SEO'],
                values: [47, 32, 28, 19, 15, 12],
                colors: [
                    '#667eea', '#764ba2', '#10b981', 
                    '#f59e0b', '#ef4444', '#8b5cf6'
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 25,
                            usePointStyle: true
                        }
                    }
                }
            }
        },
        
        funnelConversion: {
            title: "Conversión por Funnel de Marketing",
            type: "bar",
            data: {
                labels: ['Visitas', 'Leads', 'MQL', 'SQL', 'Oportunidades', 'Clientes'],
                values: [10000, 1247, 312, 89, 47, 23]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        },
        
        productComparison: {
            title: "Comparativa de Productos/Servicios",
            type: "bar",
            data: {
                labels: ['Curso IA Marketing', 'SaaS Copy.ai', 'Consultoría', 'Certificaciones'],
                values: [45, 67, 23, 12]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value + 'k';
                            }
                        }
                    }
                }
            }
        }
    },

    // ========================================
    // CONFIGURACIÓN DE FILTROS
    // ========================================
    filters: {
        period: [
            { value: "7d", label: "Últimos 7 días", default: false },
            { value: "30d", label: "Últimos 30 días", default: true },
            { value: "90d", label: "Últimos 90 días", default: false },
            { value: "1y", label: "Último año", default: false }
        ],
        
        product: [
            { value: "all", label: "Todos", default: true },
            { value: "course", label: "Curso IA Marketing", default: false },
            { value: "saas", label: "SaaS Copy.ai", default: false },
            { value: "consulting", label: "Consultoría", default: false }
        ],
        
        team: [
            { value: "all", label: "Todos los equipos", default: true },
            { value: "sales", label: "Ventas", default: false },
            { value: "marketing", label: "Marketing", default: false },
            { value: "partners", label: "Socios", default: false }
        ]
    },

    // ========================================
    // CONFIGURACIÓN DE ALERTAS
    // ========================================
    alerts: {
        enabled: true,
        types: {
            success: {
                color: "#10b981",
                icon: "fas fa-check-circle",
                sound: "success.mp3"
            },
            warning: {
                color: "#f59e0b",
                icon: "fas fa-exclamation-triangle",
                sound: "warning.mp3"
            },
            error: {
                color: "#ef4444",
                icon: "fas fa-exclamation-circle",
                sound: "error.mp3"
            },
            info: {
                color: "#06b6d4",
                icon: "fas fa-info-circle",
                sound: "info.mp3"
            }
        },
        rules: [
            {
                condition: "conversionRate > 25",
                type: "success",
                message: "¡Excelente conversión! Considera escalar esta estrategia.",
                action: "showNotification"
            },
            {
                condition: "churnRate > 5",
                type: "error",
                message: "Alerta: Tasa de churn elevada. Activar retención inmediatamente.",
                action: "showAlert"
            },
            {
                condition: "totalRevenue > target * 1.15",
                type: "success",
                message: "¡Objetivo superado! Analiza qué está funcionando bien.",
                action: "showNotification"
            }
        ]
    },

    // ========================================
    // CONFIGURACIÓN DE PREDICCIONES
    // ========================================
    predictions: {
        enabled: true,
        horizon: 30, // días
        accuracy: 94.2,
        models: {
            revenue: "LSTM Neural Network",
            conversion: "Random Forest",
            churn: "Gradient Boosting"
        },
        next30Days: {
            projectedRevenue: 145230,
            newCustomers: 52,
            conversionRate: 26.8,
            avgDealSize: 2890,
            churnRisk: 3
        }
    },

    // ========================================
    // CONFIGURACIÓN DE TEMA
    // ========================================
    theme: {
        name: "Neural Pro",
        colors: {
            primary: "#667eea",
            secondary: "#764ba2",
            accent: "#f093fb",
            success: "#10b981",
            warning: "#f59e0b",
            error: "#ef4444",
            info: "#06b6d4",
            neural: "#8b5cf6"
        },
        fonts: {
            primary: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
            sizes: {
                small: "0.875rem",
                medium: "1rem",
                large: "1.25rem",
                xlarge: "1.5rem",
                xxlarge: "2rem"
            }
        },
        animations: {
            enabled: true,
            duration: 300,
            easing: "cubic-bezier(0.4, 0, 0.2, 1)",
            neuralPulse: true,
            shimmer: true,
            particles: true
        },
        effects: {
            glassmorphism: true,
            gradients: true,
            shadows: true,
            blur: true
        }
    },

    // ========================================
    // CONFIGURACIÓN DE PERFORMANCE
    // ========================================
    performance: {
        lazyLoading: true,
        dataCaching: true,
        chartOptimization: true,
        memoryManagement: true,
        maxDataPoints: 1000,
        compressionLevel: 6,
        updateInterval: 30000 // 30 segundos
    },

    // ========================================
    // CONFIGURACIÓN DE EXPORTACIÓN
    // ========================================
    export: {
        formats: ["json", "csv", "pdf", "png", "excel"],
        includeCharts: true,
        includePredictions: true,
        includeNeuralAnalysis: true,
        compression: true,
        watermark: "Neural Sales Dashboard Pro"
    }
};
```

## 🎨 Personalización de Tema

### **Cambiar Colores**
```javascript
// Personalizar colores del tema
NeuralDashboardConfig.theme.colors = {
    primary: "#tu-color-principal",
    secondary: "#tu-color-secundario",
    accent: "#tu-color-acento",
    success: "#10b981",
    warning: "#f59e0b",
    error: "#ef4444",
    info: "#06b6d4",
    neural: "#8b5cf6"
};
```

### **Personalizar Fuentes**
```javascript
// Cambiar fuentes
NeuralDashboardConfig.theme.fonts = {
    primary: "'Roboto', sans-serif",
    sizes: {
        small: "0.8rem",
        medium: "1rem",
        large: "1.3rem",
        xlarge: "1.6rem",
        xxlarge: "2.2rem"
    }
};
```

## 📊 Configuración de KPIs

### **Agregar Nuevo KPI**
```javascript
// Agregar KPI personalizado
NeuralDashboardConfig.kpis.customKPI = {
    name: "Mi KPI Personalizado",
    icon: "fas fa-chart-line",
    unit: "%",
    format: "percentage",
    target: 80,
    current: 75,
    change: 5,
    changeType: "positive",
    description: "Descripción de mi KPI personalizado",
    alertThreshold: 0.10,
    priority: "medium"
};
```

### **Modificar KPI Existente**
```javascript
// Modificar KPI existente
NeuralDashboardConfig.kpis.totalRevenue = {
    ...NeuralDashboardConfig.kpis.totalRevenue,
    target: 200000, // Nuevo objetivo
    alertThreshold: 0.20 // Nuevo umbral de alerta
};
```

## 📈 Configuración de Gráficos

### **Agregar Nuevo Gráfico**
```javascript
// Agregar gráfico personalizado
NeuralDashboardConfig.charts.customChart = {
    title: "Mi Gráfico Personalizado",
    type: "line",
    data: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        values: [100, 120, 110, 140, 130, 150]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
};
```

### **Personalizar Colores de Gráficos**
```javascript
// Personalizar colores
NeuralDashboardConfig.charts.salesChannels.data.colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', 
    '#96CEB4', '#FFEAA7', '#DDA0DD'
];
```

## 🔔 Configuración de Alertas

### **Agregar Nueva Regla de Alerta**
```javascript
// Agregar regla personalizada
NeuralDashboardConfig.alerts.rules.push({
    condition: "newCustomers > 60",
    type: "success",
    message: "¡Excelente! Has superado el objetivo de nuevos clientes.",
    action: "showNotification"
});
```

### **Personalizar Tipos de Alerta**
```javascript
// Agregar tipo de alerta personalizado
NeuralDashboardConfig.alerts.types.custom = {
    color: "#9B59B6",
    icon: "fas fa-star",
    sound: "custom.mp3"
};
```

## 🎯 Configuración de Filtros

### **Agregar Nuevo Filtro**
```javascript
// Agregar filtro personalizado
NeuralDashboardConfig.filters.region = [
    { value: "all", label: "Todas las regiones", default: true },
    { value: "north", label: "Norte", default: false },
    { value: "south", label: "Sur", default: false },
    { value: "east", label: "Este", default: false },
    { value: "west", label: "Oeste", default: false }
];
```

## 🔧 Configuración de Performance

### **Optimizar Rendimiento**
```javascript
// Configuración de performance
NeuralDashboardConfig.performance = {
    lazyLoading: true,
    dataCaching: true,
    chartOptimization: true,
    memoryManagement: true,
    maxDataPoints: 500, // Reducir para mejor rendimiento
    compressionLevel: 8, // Mayor compresión
    updateInterval: 60000 // Actualizar cada minuto
};
```

## 📤 Configuración de Exportación

### **Personalizar Exportación**
```javascript
// Configuración de exportación
NeuralDashboardConfig.export = {
    formats: ["json", "csv", "pdf"],
    includeCharts: true,
    includePredictions: true,
    includeNeuralAnalysis: false, // Deshabilitar análisis neural
    compression: true,
    watermark: "Mi Empresa - Dashboard 2024"
};
```

## 🚀 Configuración de Despliegue

### **Configuración para Producción**
```javascript
// Configuración de producción
const ProductionConfig = {
    ...NeuralDashboardConfig,
    performance: {
        ...NeuralDashboardConfig.performance,
        updateInterval: 60000, // Menos frecuente en producción
        maxDataPoints: 2000
    },
    theme: {
        ...NeuralDashboardConfig.theme,
        animations: {
            ...NeuralDashboardConfig.theme.animations,
            particles: false // Deshabilitar partículas en producción
        }
    }
};
```

### **Configuración para Desarrollo**
```javascript
// Configuración de desarrollo
const DevelopmentConfig = {
    ...NeuralDashboardConfig,
    performance: {
        ...NeuralDashboardConfig.performance,
        updateInterval: 10000, // Más frecuente en desarrollo
        maxDataPoints: 100
    },
    theme: {
        ...NeuralDashboardConfig.theme,
        animations: {
            ...NeuralDashboardConfig.theme.animations,
            particles: true,
            shimmer: true
        }
    }
};
```

## 🔄 Configuración Dinámica

### **Cargar Configuración desde API**
```javascript
async function loadDynamicConfig() {
    try {
        const response = await fetch('/api/dashboard-config');
        const config = await response.json();
        
        // Aplicar configuración dinámica
        Object.assign(NeuralDashboardConfig, config);
        
        // Reinicializar dashboard
        initializeDashboard();
        
    } catch (error) {
        console.error('Error cargando configuración:', error);
        // Usar configuración por defecto
        initializeDashboard();
    }
}
```

### **Guardar Configuración**
```javascript
async function saveConfig(config) {
    try {
        const response = await fetch('/api/dashboard-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            showNotification('✅ Configuración guardada correctamente', 'success');
        }
        
    } catch (error) {
        showNotification('❌ Error guardando configuración', 'error');
    }
}
```

---

## 🎉 ¡Configuración Completa!

Tu Neural Sales Dashboard está completamente configurado y personalizable.

**Próximos pasos:**
1. ⚙️ Personalizar configuración según tus necesidades
2. 🎨 Ajustar tema y colores
3. 📊 Configurar KPIs específicos
4. 🚀 Desplegar en tu entorno

¿Necesitas ayuda con la configuración? ¡Contáctanos!



