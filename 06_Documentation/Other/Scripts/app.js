/**
 * Sistema de Organización de Documentos - Interfaz Web
 * ===================================================
 * 
 * JavaScript para la funcionalidad de la interfaz web
 * Incluye navegación, búsqueda, filtros y gestión de archivos
 */

class DocumentManager {
    constructor() {
        this.currentFolder = 'overview';
        this.currentFilter = 'all';
        this.currentView = 'grid';
        this.files = [];
        this.searchResults = [];
        
        this.init();
    }

    init() {
        this.loadFileData();
        this.setupEventListeners();
        this.renderFiles();
        this.updateStats();
    }

    loadFileData() {
        // Datos de archivos simulados (en producción vendrían de una API)
        this.files = [
            // Marketing Content
            {
                name: 'Curso_IA_Marketing_Completo.md',
                path: '03_Marketing_Content/Cursos_IA_Marketing/',
                type: 'marketing',
                category: 'curso',
                size: '2.5MB',
                modified: '2024-10-08',
                icon: 'fas fa-graduation-cap',
                description: 'Curso completo de IA aplicada al marketing'
            },
            {
                name: 'Webinar_Curso_IA_Marketing_100_Pesos.md',
                path: '03_Marketing_Content/Webinars_Presentaciones/',
                type: 'marketing',
                category: 'webinar',
                size: '1.2MB',
                modified: '2024-10-08',
                icon: 'fas fa-video',
                description: 'Webinar promocional de $100 pesos'
            },
            {
                name: 'ai_webinar_narratives.md',
                path: '03_Marketing_Content/Copywriting_Narrativas/',
                type: 'marketing',
                category: 'copywriting',
                size: '850KB',
                modified: '2024-10-08',
                icon: 'fas fa-pen-fancy',
                description: 'Narrativas de marketing con IA'
            },
            
            // Financial Documents
            {
                name: 'Yearly_Financial_Goals_Worksheet.md',
                path: '05_Financial_Documents/Metas_Objetivos/',
                type: 'financial',
                category: 'metas',
                size: '320KB',
                modified: '2024-10-08',
                icon: 'fas fa-target',
                description: 'Plantilla de metas financieras anuales'
            },
            {
                name: 'Monthly_Budget_Template.md',
                path: '05_Financial_Documents/Plantillas/',
                type: 'financial',
                category: 'presupuesto',
                size: '180KB',
                modified: '2024-10-08',
                icon: 'fas fa-calculator',
                description: 'Plantilla de presupuesto mensual'
            },
            {
                name: 'Dashboard_Inteligente.csv',
                path: '05_Financial_Documents/CSV_Data/',
                type: 'financial',
                category: 'datos',
                size: '45KB',
                modified: '2024-10-08',
                icon: 'fas fa-chart-bar',
                description: 'Dashboard de datos financieros'
            },
            
            // Technical Documentation
            {
                name: 'API_DOCUMENTATION.md',
                path: '06_Technical_Documentation/APIs_Documentation/',
                type: 'technical',
                category: 'api',
                size: '1.8MB',
                modified: '2024-10-08',
                icon: 'fas fa-code',
                description: 'Documentación completa de APIs'
            },
            {
                name: 'PROMPT_ALPHA_FINANZAS.md',
                path: '06_Technical_Documentation/Prompts_IA/',
                type: 'technical',
                category: 'prompt',
                size: '650KB',
                modified: '2024-10-08',
                icon: 'fas fa-robot',
                description: 'Prompts de IA para finanzas'
            },
            {
                name: 'RESUMEN_EJECUTIVO_FINAL_COMPLETO_IA_MARKETING.md',
                path: '06_Technical_Documentation/Resumenes_Ejecutivos/',
                type: 'technical',
                category: 'resumen',
                size: '1.1MB',
                modified: '2024-10-08',
                icon: 'fas fa-file-alt',
                description: 'Resumen ejecutivo completo'
            },
            
            // Scripts
            {
                name: 'create_word_document.py',
                path: '01_Python_Scripts/',
                type: 'scripts',
                category: 'python',
                size: '12KB',
                modified: '2024-10-08',
                icon: 'fab fa-python',
                description: 'Generador de documentos Word'
            },
            {
                name: 'create_pdf.py',
                path: '01_Python_Scripts/',
                type: 'scripts',
                category: 'python',
                size: '8KB',
                modified: '2024-10-08',
                icon: 'fab fa-python',
                description: 'Generador de documentos PDF'
            },
            {
                name: 'optimize_super_extreme_final.ps1',
                path: '02_PowerShell_Scripts/',
                type: 'scripts',
                category: 'powershell',
                size: '15KB',
                modified: '2024-10-08',
                icon: 'fas fa-terminal',
                description: 'Script de optimización extrema'
            },
            
            // Ultimate Systems
            {
                name: 'ULTIMATE_UNIVERSAL_WISDOM_V43.py',
                path: '07_Ultimate_Systems/',
                type: 'ultimate',
                category: 'sistema',
                size: '18KB',
                modified: '2024-10-08',
                icon: 'fas fa-star',
                description: 'Sistema de sabiduría universal'
            },
            {
                name: 'TRASCENDENCIA_CUANTICA_DIVINA_ABSOLUTA_INFINITA_TRASCENDENTE_SUPREMA_UNIVERSAL_IA_MARKETING.md',
                path: '07_Ultimate_Systems/',
                type: 'ultimate',
                category: 'trascendencia',
                size: '43KB',
                modified: '2024-10-08',
                icon: 'fas fa-infinity',
                description: 'Sistema de trascendencia cuántica'
            },
            
            // Frameworks
            {
                name: 'STRATEGIC_PLANNING_FRAMEWORK.md',
                path: '08_Strategic_Frameworks/',
                type: 'frameworks',
                category: 'estrategia',
                size: '12KB',
                modified: '2024-10-08',
                icon: 'fas fa-sitemap',
                description: 'Framework de planificación estratégica'
            },
            {
                name: 'STRATEGIC_PARTNERSHIP_FRAMEWORK.md',
                path: '08_Strategic_Frameworks/',
                type: 'frameworks',
                category: 'alianzas',
                size: '13KB',
                modified: '2024-10-08',
                icon: 'fas fa-handshake',
                description: 'Framework de alianzas estratégicas'
            },
            
            // Implementation Guides
            {
                name: 'MEJORAS_ULTIMATE_AVANZADAS.md',
                path: '09_Implementation_Guides/Mejoras_Sistema/',
                type: 'implementation',
                category: 'mejoras',
                size: '22KB',
                modified: '2024-10-08',
                icon: 'fas fa-cogs',
                description: 'Guía de mejoras ultimate avanzadas'
            },
            {
                name: 'OPTIMIZACION_CUANTICA_DIVINA_ABSOLUTA_INFINITA_TRASCENDENTE_SUPREMA_UNIVERSAL_IA_MARKETING.md',
                path: '09_Implementation_Guides/Optimizaciones/',
                type: 'implementation',
                category: 'optimizacion',
                size: '33KB',
                modified: '2024-10-08',
                icon: 'fas fa-rocket',
                description: 'Optimización cuántica divina'
            }
        ];
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', (e) => {
            this.searchFiles(e.target.value);
        });

        // Filter tabs
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.setFilter(e.target.dataset.filter);
            });
        });

        // Folder navigation
        const folderItems = document.querySelectorAll('.folder-item');
        folderItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.setFolder(e.currentTarget.dataset.folder);
            });
        });

        // View toggle
        const viewBtns = document.querySelectorAll('.view-btn');
        viewBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setView(e.target.dataset.view);
            });
        });
    }

    searchFiles(query) {
        if (!query.trim()) {
            this.searchResults = [];
            this.renderFiles();
            return;
        }

        this.searchResults = this.files.filter(file => 
            file.name.toLowerCase().includes(query.toLowerCase()) ||
            file.description.toLowerCase().includes(query.toLowerCase()) ||
            file.category.toLowerCase().includes(query.toLowerCase())
        );

        this.renderFiles();
    }

    setFilter(filter) {
        this.currentFilter = filter;
        
        // Update active tab
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');

        this.renderFiles();
    }

    setFolder(folder) {
        this.currentFolder = folder;
        
        // Update active folder
        document.querySelectorAll('.folder-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-folder="${folder}"]`).classList.add('active');

        // Update content title
        const titles = {
            'overview': 'Vista General',
            'marketing': 'Marketing Content',
            'financial': 'Documentos Financieros',
            'technical': 'Documentación Técnica',
            'scripts': 'Scripts',
            'ultimate': 'Sistemas Ultimate',
            'frameworks': 'Frameworks Estratégicos',
            'implementation': 'Guías de Implementación'
        };
        
        document.getElementById('content-title').textContent = titles[folder] || 'Vista General';

        this.renderFiles();
    }

    setView(view) {
        this.currentView = view;
        
        // Update active view button
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');

        // Update container class
        const container = document.getElementById('files-container');
        container.className = view === 'list' ? 'files-list' : 'files-grid';

        this.renderFiles();
    }

    getFilteredFiles() {
        let files = this.files;

        // Apply search filter
        if (this.searchResults.length > 0) {
            files = this.searchResults;
        }

        // Apply category filter
        if (this.currentFilter !== 'all') {
            files = files.filter(file => file.type === this.currentFilter);
        }

        // Apply folder filter
        if (this.currentFolder !== 'overview') {
            const folderMap = {
                'marketing': 'marketing',
                'financial': 'financial',
                'technical': 'technical',
                'scripts': 'scripts',
                'ultimate': 'ultimate',
                'frameworks': 'frameworks',
                'implementation': 'implementation'
            };
            
            if (folderMap[this.currentFolder]) {
                files = files.filter(file => file.type === folderMap[this.currentFolder]);
            }
        }

        return files;
    }

    renderFiles() {
        const files = this.getFilteredFiles();
        const container = document.getElementById('files-container');
        
        if (files.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #666;">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 20px; opacity: 0.5;"></i>
                    <h3>No se encontraron archivos</h3>
                    <p>Intenta ajustar los filtros o la búsqueda</p>
                </div>
            `;
            return;
        }

        container.innerHTML = files.map(file => `
            <div class="file-card" onclick="openFile('${file.path}${file.name}')">
                <div class="file-icon">
                    <i class="${file.icon}"></i>
                </div>
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${file.description}</div>
                <div class="file-meta">Modificado: ${file.modified}</div>
                <div class="file-size">${file.size}</div>
            </div>
        `).join('');
    }

    updateStats() {
        // Update statistics (in production, these would come from the backend)
        const stats = {
            totalFiles: this.files.length,
            totalFolders: 35,
            totalCategories: 10,
            lastUpdate: new Date().toLocaleDateString('es-ES')
        };

        document.getElementById('total-files').textContent = stats.totalFiles.toLocaleString();
        document.getElementById('total-folders').textContent = stats.totalFolders;
        document.getElementById('total-categories').textContent = stats.totalCategories;
        document.getElementById('last-update').textContent = stats.lastUpdate;
    }
}

// Global functions for quick actions
function openFile(filePath) {
    // In production, this would open the file in the appropriate application
    console.log('Opening file:', filePath);
    
    // For now, show an alert
    alert(`Abriendo archivo: ${filePath}\n\nEn una implementación completa, esto abriría el archivo en la aplicación correspondiente.`);
}

function runMaintenance() {
    // In production, this would trigger the maintenance script
    console.log('Running maintenance...');
    
    // Show loading state
    const button = event.target.closest('.action-card');
    const originalContent = button.innerHTML;
    
    button.innerHTML = `
        <div class="action-icon"><i class="fas fa-spinner fa-spin"></i></div>
        <div class="action-title">Ejecutando...</div>
        <div class="action-desc">Mantenimiento en progreso</div>
    `;
    
    // Simulate maintenance process
    setTimeout(() => {
        button.innerHTML = `
            <div class="action-icon"><i class="fas fa-check"></i></div>
            <div class="action-title">Completado</div>
            <div class="action-desc">Mantenimiento exitoso</div>
        `;
        
        setTimeout(() => {
            button.innerHTML = originalContent;
        }, 2000);
    }, 3000);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new DocumentManager();
});

// Add some CSS for list view
const style = document.createElement('style');
style.textContent = `
    .files-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .files-list .file-card {
        display: flex;
        align-items: center;
        padding: 15px;
    }
    
    .files-list .file-icon {
        margin-right: 20px;
        margin-bottom: 0;
    }
    
    .files-list .file-name {
        flex: 1;
        margin-bottom: 0;
    }
    
    .files-list .file-meta {
        margin-right: 20px;
        margin-bottom: 0;
    }
`;
document.head.appendChild(style);






