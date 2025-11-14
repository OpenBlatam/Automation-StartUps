/**
 * 🧠 Neural Sales Dashboard - Configuración Personalizable
 * 
 * Este archivo contiene toda la configuración para personalizar
 * el dashboard según las necesidades específicas de tu negocio.
 */

const DashboardConfig = {
    // ========================================
    // CONFIGURACIÓN GENERAL
    // ========================================
    company: {
        name: "Sintra AI Marketing",
        logo: "🧠",
        primaryColor: "#667eea",
        secondaryColor: "#764ba2",
        accentColor: "#f093fb"
    },

    // ========================================
    // KPIs PRINCIPALES - PERSONALIZABLES
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
            description: "Suma total de ingresos generados en el período"
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
            description: "Porcentaje de leads que se convierten en clientes"
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
            description: "Número de clientes adquiridos en el período"
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
            description: "Crecimiento mensual de ingresos recurrentes"
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
            description: "Ingresos promedio por transacción"
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
            description: "Días promedio desde lead hasta cierre"
        }
    },

    // ========================================
    // MÉTRICAS SECUNDARIAS
    // ========================================
    secondaryMetrics: {
        leadsGenerated: {
            name: "Leads Generados",
            value: 1247,
            format: "number"
        },
        qualifiedLeads: {
            name: "Leads Calificados",
            value: 312,
            format: "number"
        },
        demoRequests: {
            name: "Solicitudes de Demo",
            value: 89,
            format: "number"
        },
        trialConversions: {
            name: "Conversiones de Prueba",
            value: 34,
            format: "number"
        },
        churnRate: {
            name: "Tasa de Churn",
            value: 4.2,
            format: "percentage"
        },
        lifetimeValue: {
            name: "LTV Promedio",
            value: 8450,
            format: "currency"
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
                values: [47, 32, 28, 19, 15, 12]
            }
        },
        
        funnelConversion: {
            title: "Conversión por Funnel de Marketing",
            type: "bar",
            data: {
                labels: ['Visitas', 'Leads', 'MQL', 'SQL', 'Oportunidades', 'Clientes'],
                values: [10000, 1247, 312, 89, 47, 23]
            }
        },
        
        productComparison: {
            title: "Comparativa de Productos/Servicios",
            type: "bar",
            data: {
                labels: ['Curso IA Marketing', 'SaaS Copy.ai', 'Consultoría', 'Certificaciones'],
                values: [45, 67, 23, 12]
            }
        }
    },

    // ========================================
    // FILTROS DISPONIBLES
    // ========================================
    filters: {
        period: [
            { value: "7d", label: "Últimos 7 días" },
            { value: "30d", label: "Últimos 30 días" },
            { value: "90d", label: "Últimos 90 días" },
            { value: "1y", label: "Último año" }
        ],
        
        product: [
            { value: "all", label: "Todos" },
            { value: "course", label: "Curso IA Marketing" },
            { value: "saas", label: "SaaS Copy.ai" },
            { value: "consulting", label: "Consultoría" }
        ],
        
        team: [
            { value: "all", label: "Todos los equipos" },
            { value: "sales", label: "Ventas" },
            { value: "marketing", label: "Marketing" },
            { value: "partners", label: "Socios" }
        ]
    },

    // ========================================
    // INSIGHTS DE IA PERSONALIZABLES
    // ========================================
    aiInsights: [
        {
            type: "opportunity",
            title: "🎯 Oportunidad de Crecimiento",
            description: "El canal de LinkedIn muestra un 40% más de conversión que el promedio. Considera aumentar el presupuesto en un 25%.",
            priority: "high",
            action: "Aumentar presupuesto LinkedIn"
        },
        {
            type: "alert",
            title: "⚠️ Alerta de Churn",
            description: "3 clientes del SaaS muestran señales de abandono. Activar secuencia de retención inmediatamente.",
            priority: "urgent",
            action: "Activar secuencia de retención"
        },
        {
            type: "prediction",
            title: "📈 Predicción Positiva",
            description: "Basado en patrones históricos, se espera un crecimiento del 18% en ingresos para el próximo trimestre.",
            priority: "medium",
            action: "Preparar recursos para crecimiento"
        }
    ],

    // ========================================
    // PREDICCIONES NEURALES
    // ========================================
    predictions: {
        next30Days: {
            projectedRevenue: 145230,
            newCustomers: 52,
            conversionRate: 26.8,
            avgDealSize: 2890
        }
    },

    // ========================================
    // CONFIGURACIÓN DE ALERTAS
    // ========================================
    alerts: {
        revenue: {
            threshold: 0.15, // 15% por encima del objetivo
            message: "¡Excelente rendimiento! Has superado el objetivo de ingresos del mes en un 15%."
        },
        conversion: {
            threshold: 0.20, // 20% de conversión
            message: "Tasa de conversión excelente. LinkedIn está generando el 40% de las conversiones."
        },
        churn: {
            threshold: 0.05, // 5% de churn
            message: "Alerta: Tasa de churn por encima del 5%. Revisar estrategia de retención."
        }
    },

    // ========================================
    // CONFIGURACIÓN DE API
    // ========================================
    api: {
        baseUrl: "https://api.sintra-ai.com",
        endpoints: {
            salesData: "/api/sales-data",
            realTimeUpdates: "/ws/sales-realtime",
            exportData: "/api/export/dashboard"
        },
        refreshInterval: 30000, // 30 segundos
        timeout: 10000 // 10 segundos
    },

    // ========================================
    // CONFIGURACIÓN DE EXPORTACIÓN
    // ========================================
    export: {
        formats: ["json", "csv", "pdf"],
        defaultFormat: "json",
        includeCharts: true,
        includePredictions: true
    },

    // ========================================
    // CONFIGURACIÓN DE TEMA
    // ========================================
    theme: {
        colors: {
            primary: "#667eea",
            secondary: "#764ba2",
            accent: "#f093fb",
            success: "#10b981",
            warning: "#f59e0b",
            error: "#ef4444",
            info: "#06b6d4"
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
            easing: "cubic-bezier(0.4, 0, 0.2, 1)"
        }
    }
};

// ========================================
// FUNCIONES DE UTILIDAD
// ========================================

/**
 * Formatea un valor según su tipo
 */
function formatValue(value, format, unit = "") {
    switch (format) {
        case "currency":
            return new Intl.NumberFormat('es-ES', {
                style: 'currency',
                currency: 'USD'
            }).format(value);
        case "percentage":
            return `${value}%`;
        case "number":
            return new Intl.NumberFormat('es-ES').format(value);
        default:
            return `${value}${unit}`;
    }
}

/**
 * Calcula el cambio porcentual
 */
function calculateChange(current, previous) {
    if (previous === 0) return 0;
    return ((current - previous) / previous) * 100;
}

/**
 * Determina el tipo de cambio (positive, negative, neutral)
 */
function getChangeType(change) {
    if (change > 0) return "positive";
    if (change < 0) return "negative";
    return "neutral";
}

/**
 * Genera insights automáticos basados en los datos
 */
function generateInsights(data) {
    const insights = [];
    
    // Insight de conversión
    if (data.conversionRate > 20) {
        insights.push({
            type: "success",
            title: "🎯 Excelente Conversión",
            description: `Tasa de conversión del ${data.conversionRate}% supera el objetivo del 20%.`
        });
    }
    
    // Insight de ingresos
    if (data.totalRevenue > data.target) {
        const growth = calculateChange(data.totalRevenue, data.target);
        insights.push({
            type: "success",
            title: "💰 Objetivo Superado",
            description: `Ingresos ${growth.toFixed(1)}% por encima del objetivo.`
        });
    }
    
    return insights;
}

// Exportar configuración
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardConfig;
} else {
    window.DashboardConfig = DashboardConfig;
}
