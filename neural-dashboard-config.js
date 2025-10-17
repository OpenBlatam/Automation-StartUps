/**
 * 🧠 Neural Sales Dashboard AI Pro - Configuración Avanzada
 * 
 * Este archivo contiene todas las configuraciones personalizables del dashboard
 * Permite modificar métricas, colores, gráficos y funcionalidades sin tocar el código principal
 */

// ============================================================================
// 🎨 CONFIGURACIÓN DE TEMA Y COLORES
// ============================================================================

const THEME_CONFIG = {
    // Paleta de colores neural
    colors: {
        primary: '#667eea',
        secondary: '#764ba2',
        accent: '#00ff88',
        neuralBlue: '#00d4ff',
        neuralRed: '#ff6b6b',
        neuralYellow: '#ffd93d',
        neuralPurple: '#9b59b6',
        text: '#ffffff',
        background: 'rgba(255, 255, 255, 0.1)',
        border: 'rgba(255, 255, 255, 0.2)'
    },
    
    // Gradientes personalizados
    gradients: {
        primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        neural: 'linear-gradient(45deg, #00ff88, #00d4ff)',
        success: 'linear-gradient(45deg, #00ff88, #00d4ff)',
        warning: 'linear-gradient(45deg, #ffd93d, #ff6b6b)',
        danger: 'linear-gradient(45deg, #ff6b6b, #9b59b6)'
    },
    
    // Efectos visuales
    effects: {
        blur: 'blur(20px)',
        shadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
        glow: '0 0 20px rgba(255, 255, 255, 0.5)',
        pulse: '0 0 30px rgba(0, 255, 136, 0.8)'
    }
};

// ============================================================================
// 📊 CONFIGURACIÓN DE MÉTRICAS
// ============================================================================

const METRICS_CONFIG = {
    // Métricas principales del dashboard
    metrics: [
        {
            id: 'totalRevenue',
            title: 'Ingresos Totales',
            icon: 'fas fa-dollar-sign',
            color: '#00ff88',
            value: 347850,
            change: 28.5,
            changeType: 'positive',
            format: 'currency',
            currency: 'USD',
            decimals: 0
        },
        {
            id: 'newCustomers',
            title: 'Nuevos Clientes',
            icon: 'fas fa-users',
            color: '#00d4ff',
            value: 1847,
            change: 33.2,
            changeType: 'positive',
            format: 'number',
            decimals: 0
        },
        {
            id: 'conversionRate',
            title: 'Tasa de Conversión',
            icon: 'fas fa-percentage',
            color: '#ff6b6b',
            value: 38.7,
            change: 15.3,
            changeType: 'positive',
            format: 'percentage',
            decimals: 1
        },
        {
            id: 'avgTime',
            title: 'Tiempo Promedio',
            icon: 'fas fa-clock',
            color: '#ffd93d',
            value: 1.8,
            change: -22.1,
            changeType: 'negative',
            format: 'time',
            unit: 'días',
            decimals: 1
        }
    ],
    
    // Configuración de actualización
    update: {
        interval: 30000, // 30 segundos
        enabled: true,
        animation: true,
        sound: false
    }
};

// ============================================================================
// 📈 CONFIGURACIÓN DE GRÁFICOS
// ============================================================================

const CHARTS_CONFIG = {
    // Gráfico de ventas
    salesChart: {
        type: 'line',
        title: 'Tendencia de Ventas Neural',
        data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            datasets: [{
                label: 'Ventas Mensuales',
                data: [120000, 135000, 142000, 158000, 167000, 175000, 189000, 198000, 210000, 225000, 238000, 347850],
                borderColor: '#00ff88',
                backgroundColor: 'rgba(0, 255, 136, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#00ff88',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: 'white',
                        font: { size: 14 }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: 'white' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    ticks: { 
                        color: 'white',
                        callback: function(value) {
                            return '$' + (value / 1000) + 'k';
                        }
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    },
    
    // Gráfico de canales
    channelChart: {
        type: 'doughnut',
        title: 'Distribución por Canal',
        data: {
            labels: ['LinkedIn', 'Google Ads', 'Email', 'Referidos', 'Otros'],
            datasets: [{
                data: [35, 28, 20, 12, 5],
                backgroundColor: [
                    '#00ff88',
                    '#00d4ff',
                    '#ff6b6b',
                    '#ffd93d',
                    '#9b59b6'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'white',
                        font: { size: 12 },
                        padding: 20
                    }
                }
            }
        }
    }
};

// ============================================================================
// 🤖 CONFIGURACIÓN DE IA
// ============================================================================

const AI_CONFIG = {
    // Configuración del asistente
    assistant: {
        name: 'Asistente Neural de Ventas',
        avatar: 'fas fa-robot',
        color: '#00ff88',
        animation: true,
        pulse: true
    },
    
    // Recomendaciones automáticas
    recommendations: [
        {
            id: 'budget_optimization',
            title: 'Optimización de Presupuesto',
            icon: 'fas fa-lightbulb',
            color: '#ffd93d',
            text: 'Redistribuir 35% del presupuesto de Google Ads hacia LinkedIn para maximizar ROI en B2B.',
            priority: 'high',
            category: 'marketing'
        },
        {
            id: 'funnel_conversion',
            title: 'Funnel de Conversión',
            icon: 'fas fa-chart-line',
            color: '#00ff88',
            text: 'Implementar secuencia de email automatizada en el paso 3 del funnel para aumentar conversiones.',
            priority: 'medium',
            category: 'sales'
        },
        {
            id: 'customer_retention',
            title: 'Retención de Clientes',
            icon: 'fas fa-users',
            color: '#00d4ff',
            text: 'Activar programa de fidelización para clientes con LTV > $5,000 para reducir churn.',
            priority: 'high',
            category: 'retention'
        }
    ],
    
    // Predicciones neurales
    predictions: [
        {
            id: 'next_month_revenue',
            metric: 'Ingresos Próximo Mes',
            value: 412450,
            confidence: 96.2,
            format: 'currency',
            currency: 'USD'
        },
        {
            id: 'expected_customers',
            metric: 'Nuevos Clientes Esperados',
            value: 2180,
            confidence: 91.7,
            format: 'number'
        },
        {
            id: 'projected_conversion',
            metric: 'Tasa de Conversión Proyectada',
            value: 41.2,
            confidence: 93.5,
            format: 'percentage',
            decimals: 1
        }
    ]
};

// ============================================================================
// 🎭 CONFIGURACIÓN DE ANIMACIONES
// ============================================================================

const ANIMATIONS_CONFIG = {
    // Configuración de partículas
    particles: {
        enabled: true,
        number: 100,
        color: '#ffffff',
        opacity: 0.1,
        size: 3,
        speed: 2,
        interactivity: {
            hover: true,
            click: true,
            mode: 'repulse'
        }
    },
    
    // Animaciones de entrada
    entrance: {
        enabled: true,
        delay: 200, // ms entre elementos
        duration: 800, // ms duración
        effects: ['fadeIn', 'slideInLeft', 'slideInRight']
    },
    
    // Animaciones de hover
    hover: {
        enabled: true,
        scale: 1.05,
        duration: 300,
        easing: 'ease-out'
    },
    
    // Efectos de transición
    transitions: {
        enabled: true,
        duration: 300,
        easing: 'ease-in-out'
    }
};

// ============================================================================
// 🔧 CONFIGURACIÓN DE FUNCIONALIDADES
// ============================================================================

const FEATURES_CONFIG = {
    // Exportación de datos
    export: {
        enabled: true,
        formats: ['json', 'png', 'pdf'],
        filename: 'neural-dashboard-data',
        includeTimestamp: true
    },
    
    // Pantalla completa
    fullscreen: {
        enabled: true,
        button: true,
        keyboard: true // F11
    },
    
    // Actualización manual
    refresh: {
        enabled: true,
        button: true,
        keyboard: true, // F5
        animation: true
    },
    
    // Zoom en gráficos
    zoom: {
        enabled: true,
        resetButton: true,
        mouseWheel: true,
        pinch: true
    },
    
    // Notificaciones
    notifications: {
        enabled: true,
        position: 'top-right',
        duration: 5000,
        sound: false
    }
};

// ============================================================================
// 📱 CONFIGURACIÓN RESPONSIVE
// ============================================================================

const RESPONSIVE_CONFIG = {
    // Breakpoints
    breakpoints: {
        mobile: 768,
        tablet: 1024,
        desktop: 1200
    },
    
    // Configuración por dispositivo
    mobile: {
        metricsPerRow: 1,
        chartsPerRow: 1,
        fontSize: '0.9rem',
        padding: '15px'
    },
    
    tablet: {
        metricsPerRow: 2,
        chartsPerRow: 1,
        fontSize: '1rem',
        padding: '20px'
    },
    
    desktop: {
        metricsPerRow: 4,
        chartsPerRow: 2,
        fontSize: '1.1rem',
        padding: '25px'
    }
};

// ============================================================================
// 🌐 CONFIGURACIÓN DE API
// ============================================================================

const API_CONFIG = {
    // Endpoints
    endpoints: {
        metrics: '/api/metrics',
        predictions: '/api/predictions',
        recommendations: '/api/recommendations',
        export: '/api/export'
    },
    
    // WebSocket
    websocket: {
        enabled: true,
        url: 'wss://api.neural-dashboard.com/ws',
        reconnect: true,
        reconnectInterval: 5000
    },
    
    // Configuración de requests
    requests: {
        timeout: 10000,
        retries: 3,
        retryDelay: 1000
    }
};

// ============================================================================
// 🎯 CONFIGURACIÓN DE ALERTAS
// ============================================================================

const ALERTS_CONFIG = {
    // Umbrales de alerta
    thresholds: {
        revenue: {
            high: 500000,
            low: 200000,
            critical: 100000
        },
        conversion: {
            high: 50,
            low: 20,
            critical: 10
        },
        customers: {
            high: 3000,
            low: 1000,
            critical: 500
        }
    },
    
    // Configuración de notificaciones
    notifications: {
        email: {
            enabled: false,
            recipients: ['admin@company.com']
        },
        slack: {
            enabled: false,
            webhook: 'https://hooks.slack.com/services/...'
        },
        browser: {
            enabled: true,
            sound: false
        }
    }
};

// ============================================================================
// 🔐 CONFIGURACIÓN DE SEGURIDAD
// ============================================================================

const SECURITY_CONFIG = {
    // Autenticación
    auth: {
        enabled: false,
        method: 'jwt', // jwt, oauth, basic
        token: null,
        refreshToken: null
    },
    
    // CORS
    cors: {
        enabled: true,
        origins: ['http://localhost:3000', 'https://yourdomain.com']
    },
    
    // Validación de datos
    validation: {
        enabled: true,
        sanitize: true,
        escape: true
    }
};

// ============================================================================
// 📊 CONFIGURACIÓN DE ANALYTICS
// ============================================================================

const ANALYTICS_CONFIG = {
    // Google Analytics
    googleAnalytics: {
        enabled: false,
        trackingId: 'GA-XXXXXXXXX'
    },
    
    // Eventos personalizados
    events: {
        enabled: true,
        track: [
            'dashboard_view',
            'metric_click',
            'chart_interaction',
            'export_data',
            'prediction_view'
        ]
    },
    
    // Métricas de rendimiento
    performance: {
        enabled: true,
        track: [
            'load_time',
            'render_time',
            'interaction_time'
        ]
    }
};

// ============================================================================
// 🎨 CONFIGURACIÓN DE PERSONALIZACIÓN
// ============================================================================

const CUSTOMIZATION_CONFIG = {
    // Logo personalizado
    logo: {
        enabled: false,
        url: '/assets/logo.png',
        width: '200px',
        height: '60px'
    },
    
    // Título personalizado
    title: {
        text: 'Neural Sales Dashboard AI Pro',
        fontSize: '2.5rem',
        fontWeight: '700'
    },
    
    // Favicon personalizado
    favicon: {
        enabled: false,
        url: '/assets/favicon.ico'
    }
};

// ============================================================================
// 📋 CONFIGURACIÓN COMPLETA
// ============================================================================

const NEURAL_DASHBOARD_CONFIG = {
    theme: THEME_CONFIG,
    metrics: METRICS_CONFIG,
    charts: CHARTS_CONFIG,
    ai: AI_CONFIG,
    animations: ANIMATIONS_CONFIG,
    features: FEATURES_CONFIG,
    responsive: RESPONSIVE_CONFIG,
    api: API_CONFIG,
    alerts: ALERTS_CONFIG,
    security: SECURITY_CONFIG,
    analytics: ANALYTICS_CONFIG,
    customization: CUSTOMIZATION_CONFIG,
    
    // Configuración general
    general: {
        version: '1.0.0',
        debug: false,
        language: 'es',
        timezone: 'America/Mexico_City'
    }
};

// ============================================================================
// 🚀 FUNCIONES DE UTILIDAD
// ============================================================================

/**
 * Obtiene la configuración completa del dashboard
 * @returns {Object} Configuración completa
 */
function getConfig() {
    return NEURAL_DASHBOARD_CONFIG;
}

/**
 * Obtiene una configuración específica
 * @param {string} section - Sección de configuración
 * @returns {Object} Configuración de la sección
 */
function getConfigSection(section) {
    return NEURAL_DASHBOARD_CONFIG[section] || null;
}

/**
 * Actualiza una configuración específica
 * @param {string} section - Sección de configuración
 * @param {Object} config - Nueva configuración
 */
function updateConfig(section, config) {
    if (NEURAL_DASHBOARD_CONFIG[section]) {
        Object.assign(NEURAL_DASHBOARD_CONFIG[section], config);
    }
}

/**
 * Resetea la configuración a los valores por defecto
 */
function resetConfig() {
    // Recargar la página para resetear
    window.location.reload();
}

/**
 * Exporta la configuración actual
 * @returns {string} Configuración en formato JSON
 */
function exportConfig() {
    return JSON.stringify(NEURAL_DASHBOARD_CONFIG, null, 2);
}

/**
 * Importa una configuración
 * @param {string} configJson - Configuración en formato JSON
 */
function importConfig(configJson) {
    try {
        const config = JSON.parse(configJson);
        Object.assign(NEURAL_DASHBOARD_CONFIG, config);
        console.log('Configuración importada exitosamente');
    } catch (error) {
        console.error('Error al importar configuración:', error);
    }
}

// ============================================================================
// 📤 EXPORTACIÓN
// ============================================================================

// Exportar para uso en el dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NEURAL_DASHBOARD_CONFIG;
}

// Exportar para uso en el navegador
if (typeof window !== 'undefined') {
    window.NeuralDashboardConfig = NEURAL_DASHBOARD_CONFIG;
    window.getConfig = getConfig;
    window.getConfigSection = getConfigSection;
    window.updateConfig = updateConfig;
    window.resetConfig = resetConfig;
    window.exportConfig = exportConfig;
    window.importConfig = importConfig;
}

// ============================================================================
// 🎯 INICIALIZACIÓN
// ============================================================================

// Aplicar configuración al cargar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🧠 Neural Dashboard Config cargado');
    console.log('📊 Configuración:', NEURAL_DASHBOARD_CONFIG);
    
    // Aplicar tema personalizado si está configurado
    if (NEURAL_DASHBOARD_CONFIG.customization.logo.enabled) {
        applyCustomLogo();
    }
    
    // Aplicar título personalizado
    if (NEURAL_DASHBOARD_CONFIG.customization.title.text) {
        applyCustomTitle();
    }
});

/**
 * Aplica el logo personalizado
 */
function applyCustomLogo() {
    const logo = NEURAL_DASHBOARD_CONFIG.customization.logo;
    const logoElement = document.querySelector('.neural-title');
    if (logoElement && logo.url) {
        logoElement.innerHTML = `
            <img src="${logo.url}" 
                 alt="Logo" 
                 style="width: ${logo.width}; height: ${logo.height};">
            <div class="neural-pulse"></div>
            ${NEURAL_DASHBOARD_CONFIG.customization.title.text}
        `;
    }
}

/**
 * Aplica el título personalizado
 */
function applyCustomTitle() {
    const title = NEURAL_DASHBOARD_CONFIG.customization.title;
    const titleElement = document.querySelector('.neural-title');
    if (titleElement) {
        titleElement.style.fontSize = title.fontSize;
        titleElement.style.fontWeight = title.fontWeight;
        titleElement.textContent = title.text;
    }
}
