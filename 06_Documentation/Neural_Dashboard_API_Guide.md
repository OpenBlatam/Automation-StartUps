# 🔌 Neural Sales Dashboard - Guía de API

## 📡 Integración de APIs

### **Configuración Base**
```javascript
const API_CONFIG = {
    baseUrl: 'https://api.sintra-ai.com',
    endpoints: {
        salesData: '/api/sales-data',
        realTimeUpdates: '/ws/sales-realtime',
        exportData: '/api/export/dashboard'
    },
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'
    }
};
```

## 🎯 Endpoints Principales

### **1. Obtener Datos de Ventas**
```javascript
async function fetchSalesData(period, product, team) {
    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.salesData}`, {
        method: 'POST',
        headers: API_CONFIG.headers,
        body: JSON.stringify({
            period: period,
            product: product,
            team: team,
            timestamp: new Date().toISOString()
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}
```

### **2. WebSocket para Tiempo Real**
```javascript
class RealTimeConnection {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        this.ws = new WebSocket(`${API_CONFIG.baseUrl.replace('https', 'wss')}${API_CONFIG.endpoints.realTimeUpdates}`);
        
        this.ws.onopen = () => {
            console.log('✅ Conexión WebSocket establecida');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleRealTimeUpdate(data);
        };
        
        this.ws.onclose = () => {
            console.log('❌ Conexión WebSocket cerrada');
            this.attemptReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('🚨 Error WebSocket:', error);
        };
    }
    
    handleRealTimeUpdate(data) {
        // Actualizar KPIs en tiempo real
        updateKPIs(data.kpis);
        updateCharts(data.charts);
        showNotification(data.notification);
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`🔄 Reintentando conexión (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, 5000);
        }
    }
}
```

## 📊 Estructura de Datos

### **Formato de Respuesta de Ventas**
```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "period": "30d",
    "kpis": {
        "totalRevenue": {
            "value": 127450,
            "target": 150000,
            "change": 12.5,
            "changeType": "positive",
            "trend": "up"
        },
        "conversionRate": {
            "value": 23.4,
            "target": 25,
            "change": 3.2,
            "changeType": "positive",
            "trend": "up"
        }
    },
    "charts": {
        "salesChannels": {
            "labels": ["LinkedIn", "Google Ads", "Email Marketing"],
            "data": [47, 32, 28]
        }
    },
    "insights": [
        {
            "type": "opportunity",
            "title": "Oportunidad de Crecimiento",
            "description": "LinkedIn muestra 40% más conversión",
            "action": "Aumentar presupuesto 25%"
        }
    ]
}
```

### **Formato de Actualización en Tiempo Real**
```json
{
    "type": "kpi_update",
    "timestamp": "2024-01-15T10:31:00Z",
    "data": {
        "kpiId": "totalRevenue",
        "newValue": 127650,
        "change": 0.16,
        "alert": {
            "level": "info",
            "message": "Ingresos actualizados"
        }
    }
}
```

## 🔐 Autenticación

### **API Key Authentication**
```javascript
class APIClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = API_CONFIG.baseUrl;
    }
    
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            ...API_CONFIG.headers,
            'Authorization': `Bearer ${this.apiKey}`,
            ...options.headers
        };
        
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    }
}
```

### **JWT Token Authentication**
```javascript
class JWTAuth {
    constructor() {
        this.token = localStorage.getItem('auth_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }
    
    async refreshAuthToken() {
        const response = await fetch(`${API_CONFIG.baseUrl}/auth/refresh`, {
            method: 'POST',
            headers: API_CONFIG.headers,
            body: JSON.stringify({
                refresh_token: this.refreshToken
            })
        });
        
        const data = await response.json();
        this.token = data.access_token;
        localStorage.setItem('auth_token', this.token);
    }
    
    async makeAuthenticatedRequest(endpoint, options = {}) {
        const headers = {
            ...API_CONFIG.headers,
            'Authorization': `Bearer ${this.token}`,
            ...options.headers
        };
        
        try {
            return await fetch(`${API_CONFIG.baseUrl}${endpoint}`, {
                ...options,
                headers
            });
        } catch (error) {
            if (error.status === 401) {
                await this.refreshAuthToken();
                return await fetch(`${API_CONFIG.baseUrl}${endpoint}`, {
                    ...options,
                    headers: {
                        ...headers,
                        'Authorization': `Bearer ${this.token}`
                    }
                });
            }
            throw error;
        }
    }
}
```

## 📈 Manejo de Errores

### **Error Handling Centralizado**
```javascript
class ErrorHandler {
    static handle(error, context = '') {
        console.error(`🚨 Error en ${context}:`, error);
        
        switch (error.status) {
            case 401:
                this.handleUnauthorized();
                break;
            case 403:
                this.handleForbidden();
                break;
            case 404:
                this.handleNotFound();
                break;
            case 500:
                this.handleServerError();
                break;
            default:
                this.handleGenericError(error);
        }
    }
    
    static handleUnauthorized() {
        showNotification('🔐 Sesión expirada. Por favor, inicia sesión nuevamente.', 'error');
        redirectToLogin();
    }
    
    static handleForbidden() {
        showNotification('🚫 No tienes permisos para acceder a estos datos.', 'error');
    }
    
    static handleNotFound() {
        showNotification('❌ Recurso no encontrado.', 'error');
    }
    
    static handleServerError() {
        showNotification('🚨 Error del servidor. Intenta nuevamente más tarde.', 'error');
    }
    
    static handleGenericError(error) {
        showNotification(`❌ Error: ${error.message}`, 'error');
    }
}
```

## 🔄 Cache y Optimización

### **Sistema de Cache**
```javascript
class DataCache {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutos
    }
    
    set(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }
    
    get(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;
        
        if (Date.now() - cached.timestamp > this.cacheTimeout) {
            this.cache.delete(key);
            return null;
        }
        
        return cached.data;
    }
    
    clear() {
        this.cache.clear();
    }
}
```

### **Optimización de Requests**
```javascript
class RequestOptimizer {
    constructor() {
        this.pendingRequests = new Map();
        this.debounceTimeout = 300; // 300ms
    }
    
    debounce(key, requestFunction) {
        if (this.pendingRequests.has(key)) {
            clearTimeout(this.pendingRequests.get(key));
        }
        
        const timeoutId = setTimeout(() => {
            requestFunction();
            this.pendingRequests.delete(key);
        }, this.debounceTimeout);
        
        this.pendingRequests.set(key, timeoutId);
    }
    
    throttle(key, requestFunction, limit = 1000) {
        if (!this.pendingRequests.has(key)) {
            requestFunction();
            this.pendingRequests.set(key, setTimeout(() => {
                this.pendingRequests.delete(key);
            }, limit));
        }
    }
}
```

## 📤 Exportación de Datos

### **Exportar Dashboard Completo**
```javascript
async function exportDashboard(format = 'json') {
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.exportData}`, {
            method: 'POST',
            headers: API_CONFIG.headers,
            body: JSON.stringify({
                format: format,
                includeCharts: true,
                includePredictions: true,
                timestamp: new Date().toISOString()
            })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dashboard-export-${new Date().toISOString().split('T')[0]}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        ErrorHandler.handle(error, 'exportDashboard');
    }
}
```

## 🧪 Testing y Debugging

### **Mock Data para Desarrollo**
```javascript
const MOCK_DATA = {
    kpis: {
        totalRevenue: { value: 127450, target: 150000, change: 12.5 },
        conversionRate: { value: 23.4, target: 25, change: 3.2 },
        newCustomers: { value: 47, target: 50, change: 8 }
    },
    charts: {
        salesChannels: {
            labels: ['LinkedIn', 'Google Ads', 'Email Marketing'],
            data: [47, 32, 28]
        }
    }
};

// Usar datos mock en desarrollo
if (process.env.NODE_ENV === 'development') {
    window.MOCK_DATA = MOCK_DATA;
}
```

### **Logging y Debugging**
```javascript
class Logger {
    static log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            data
        };
        
        console.log(`[${timestamp}] ${level.toUpperCase()}: ${message}`, data);
        
        // Enviar logs al servidor en producción
        if (process.env.NODE_ENV === 'production') {
            this.sendToServer(logEntry);
        }
    }
    
    static sendToServer(logEntry) {
        fetch(`${API_CONFIG.baseUrl}/logs`, {
            method: 'POST',
            headers: API_CONFIG.headers,
            body: JSON.stringify(logEntry)
        }).catch(error => {
            console.error('Error enviando log:', error);
        });
    }
}
```

## 🚀 Implementación Completa

### **Inicialización del Dashboard**
```javascript
class NeuralDashboard {
    constructor(apiKey) {
        this.apiClient = new APIClient(apiKey);
        this.cache = new DataCache();
        this.realTimeConnection = new RealTimeConnection();
        this.errorHandler = new ErrorHandler();
    }
    
    async initialize() {
        try {
            // Cargar datos iniciales
            await this.loadInitialData();
            
            // Establecer conexión en tiempo real
            this.realTimeConnection.connect();
            
            // Configurar actualizaciones automáticas
            this.setupAutoRefresh();
            
            Logger.log('info', 'Dashboard inicializado correctamente');
            
        } catch (error) {
            this.errorHandler.handle(error, 'initialize');
        }
    }
    
    async loadInitialData() {
        const cacheKey = 'initial_data';
        let data = this.cache.get(cacheKey);
        
        if (!data) {
            data = await this.apiClient.makeRequest('/api/sales-data');
            this.cache.set(cacheKey, data);
        }
        
        this.updateDashboard(data);
    }
    
    setupAutoRefresh() {
        setInterval(() => {
            this.loadInitialData();
        }, 30000); // Actualizar cada 30 segundos
    }
}

// Inicializar dashboard
const dashboard = new NeuralDashboard('YOUR_API_KEY');
dashboard.initialize();
```

---

## 🎉 ¡API Lista para Usar!

Tu Neural Sales Dashboard está configurado con una API robusta y escalable.

**Próximos pasos:**
1. 🔑 Configurar tu API key
2. 🔌 Conectar con tus endpoints
3. 🧪 Probar en modo desarrollo
4. 🚀 Desplegar en producción

¿Necesitas ayuda con la implementación? ¡Contáctanos!



