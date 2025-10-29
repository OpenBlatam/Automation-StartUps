// JavaScript principal para el Sistema de Inventario

// Utilidades globales
const Utils = {
    // Formatear números como moneda
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    // Formatear fechas
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Formatear fecha y hora
    formatDateTime: function(date) {
        return new Date(date).toLocaleString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Mostrar alertas
    showAlert: function(type, message, duration = 5000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    },
    
    // Confirmar acción
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Debounce para búsquedas
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// API Helper
const API = {
    baseURL: '/api',
    
    // Método GET genérico
    get: async function(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            Utils.showAlert('error', 'Error al cargar datos');
            throw error;
        }
    },
    
    // Método POST genérico
    post: async function(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            Utils.showAlert('error', 'Error al enviar datos');
            throw error;
        }
    },
    
    // Método PUT genérico
    put: async function(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            Utils.showAlert('error', 'Error al actualizar datos');
            throw error;
        }
    },
    
    // Método DELETE genérico
    delete: async function(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API DELETE Error:', error);
            Utils.showAlert('error', 'Error al eliminar datos');
            throw error;
        }
    }
};

// Funciones específicas del sistema
const InventorySystem = {
    // Verificar alertas
    checkAlerts: async function() {
        try {
            const result = await API.post('/check_alerts');
            Utils.showAlert('success', result.message);
            setTimeout(() => location.reload(), 2000);
        } catch (error) {
            console.error('Error verificando alertas:', error);
        }
    },
    
    // Generar recomendaciones
    generateRecommendations: async function() {
        try {
            const recommendations = await API.get('/replenishment/recommendations');
            Utils.showAlert('success', `Se generaron ${recommendations.length} recomendaciones`);
            setTimeout(() => location.href = '/replenishment', 2000);
        } catch (error) {
            console.error('Error generando recomendaciones:', error);
        }
    },
    
    // Actualizar KPIs
    refreshKPIs: async function() {
        try {
            const kpis = await API.get('/kpis');
            Utils.showAlert('success', 'KPIs actualizados');
            setTimeout(() => location.href = '/kpis', 2000);
        } catch (error) {
            console.error('Error actualizando KPIs:', error);
        }
    },
    
    // Resolver alerta
    resolveAlert: async function(alertId) {
        try {
            await API.post(`/alerts/${alertId}/resolve`);
            Utils.showAlert('success', 'Alerta resuelta exitosamente');
            setTimeout(() => location.reload(), 1500);
        } catch (error) {
            console.error('Error resolviendo alerta:', error);
        }
    },
    
    // Procesar recomendación
    processRecommendation: async function(recommendationId) {
        try {
            await API.post(`/replenishment/recommendations/${recommendationId}/process`);
            Utils.showAlert('success', 'Recomendación procesada exitosamente');
            setTimeout(() => location.reload(), 1500);
        } catch (error) {
            console.error('Error procesando recomendación:', error);
        }
    }
};

// Funciones de gráficos
const Charts = {
    // Crear gráfico de líneas
    createLineChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                ...options
            }
        });
    },
    
    // Crear gráfico de barras
    createBarChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                ...options
            }
        });
    },
    
    // Crear gráfico de dona
    createDoughnutChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                },
                ...options
            }
        });
    },
    
    // Actualizar gráfico
    updateChart: function(chart, newData) {
        chart.data = newData;
        chart.update();
    }
};

// Funciones de filtrado y búsqueda
const Filters = {
    // Filtrar tabla por texto
    filterTable: function(tableId, searchTerm, columnIndex = 0) {
        const table = document.getElementById(tableId);
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            const cell = rows[i].getElementsByTagName('td')[columnIndex];
            if (cell) {
                const text = cell.textContent.toLowerCase();
                const shouldShow = text.includes(searchTerm.toLowerCase());
                rows[i].style.display = shouldShow ? '' : 'none';
            }
        }
    },
    
    // Filtrar por estado
    filterByStatus: function(tableId, status) {
        const table = document.getElementById(tableId);
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const rowStatus = row.getAttribute('data-status');
            const shouldShow = !status || rowStatus === status;
            row.style.display = shouldShow ? '' : 'none';
        }
    },
    
    // Limpiar filtros
    clearFilters: function(tableId) {
        const table = document.getElementById(tableId);
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            rows[i].style.display = '';
        }
    }
};

// Funciones de validación
const Validation = {
    // Validar email
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    // Validar número positivo
    isPositiveNumber: function(value) {
        return !isNaN(value) && parseFloat(value) > 0;
    },
    
    // Validar SKU
    isValidSKU: function(sku) {
        return /^[A-Z0-9-_]+$/i.test(sku) && sku.length >= 3;
    },
    
    // Validar formulario
    validateForm: function(formId) {
        const form = document.getElementById(formId);
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
};

// Funciones de carga y estados
const Loading = {
    // Mostrar spinner
    showSpinner: function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add('loading');
            element.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
        }
    },
    
    // Ocultar spinner
    hideSpinner: function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('loading');
        }
    },
    
    // Mostrar estado de carga en botón
    setButtonLoading: function(buttonId, loading = true) {
        const button = document.getElementById(buttonId);
        if (button) {
            if (loading) {
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Cargando...';
            } else {
                button.disabled = false;
                button.innerHTML = button.getAttribute('data-original-text') || 'Enviar';
            }
        }
    }
};

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers de Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Configurar validación de formularios
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Auto-hide alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    });
});

// Funciones globales para uso en templates
window.checkAlerts = InventorySystem.checkAlerts;
window.generateRecommendations = InventorySystem.generateRecommendations;
window.refreshKPIs = InventorySystem.refreshKPIs;
window.resolveAlert = InventorySystem.resolveAlert;
window.processRecommendation = InventorySystem.processRecommendation;
window.Utils = Utils;
window.API = API;
window.Charts = Charts;
window.Filters = Filters;
window.Validation = Validation;
window.Loading = Loading;



