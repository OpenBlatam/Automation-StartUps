import { EventEmitter } from 'events';

export interface VisualizationConfig {
  id: string;
  name: string;
  description: string;
  type: 'chart' | 'table' | 'map' | 'gauge' | 'treemap' | 'heatmap' | 'network' | 'custom';
  chartType: 'line' | 'bar' | 'pie' | 'scatter' | 'area' | 'donut' | 'radar' | 'bubble' | 'funnel' | 'sankey';
  dataSource: {
    type: 'api' | 'database' | 'file' | 'stream';
    endpoint?: string;
    query?: string;
    file?: string;
    stream?: string;
  };
  dimensions: {
    x: string;
    y: string;
    z?: string;
    color?: string;
    size?: string;
    label?: string;
  };
  filters: VisualizationFilter[];
  aggregations: VisualizationAggregation[];
  styling: VisualizationStyling;
  interactions: VisualizationInteraction[];
  animations: VisualizationAnimation[];
  responsive: boolean;
  realTime: boolean;
  refreshInterval?: number;
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface VisualizationFilter {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than' | 'between' | 'in' | 'not_in';
  value: any;
  enabled: boolean;
}

export interface VisualizationAggregation {
  field: string;
  function: 'sum' | 'avg' | 'count' | 'min' | 'max' | 'median' | 'std' | 'var';
  alias: string;
  enabled: boolean;
}

export interface VisualizationStyling {
  theme: 'light' | 'dark' | 'custom';
  colors: string[];
  fonts: {
    family: string;
    size: number;
    weight: string;
  };
  layout: {
    width: number;
    height: number;
    margin: {
      top: number;
      right: number;
      bottom: number;
      left: number;
    };
  };
  axes: {
    x: AxisConfig;
    y: AxisConfig;
    z?: AxisConfig;
  };
  legend: {
    enabled: boolean;
    position: 'top' | 'bottom' | 'left' | 'right';
    orientation: 'horizontal' | 'vertical';
  };
  tooltip: {
    enabled: boolean;
    format: string;
    customContent?: string;
  };
}

export interface AxisConfig {
  title: string;
  min?: number;
  max?: number;
  ticks: number;
  format: string;
  gridLines: boolean;
  labels: boolean;
}

export interface VisualizationInteraction {
  type: 'zoom' | 'pan' | 'select' | 'hover' | 'click' | 'brush' | 'crossfilter';
  enabled: boolean;
  config: Record<string, any>;
}

export interface VisualizationAnimation {
  type: 'fade' | 'slide' | 'scale' | 'rotate' | 'morph' | 'custom';
  duration: number;
  easing: string;
  enabled: boolean;
  config: Record<string, any>;
}

export interface VisualizationData {
  id: string;
  visualizationId: string;
  data: any[];
  metadata: {
    totalRecords: number;
    lastUpdated: Date;
    dataQuality: number;
    completeness: number;
  };
  cache: {
    enabled: boolean;
    ttl: number;
    lastCached: Date;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface Dashboard {
  id: string;
  name: string;
  description: string;
  layout: DashboardLayout;
  visualizations: string[];
  filters: DashboardFilter[];
  refreshInterval: number;
  realTime: boolean;
  permissions: {
    view: string[];
    edit: string[];
    admin: string[];
  };
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface DashboardLayout {
  type: 'grid' | 'flex' | 'custom';
  rows: number;
  columns: number;
  gap: number;
  items: DashboardItem[];
}

export interface DashboardItem {
  id: string;
  visualizationId: string;
  position: {
    row: number;
    column: number;
    rowSpan: number;
    columnSpan: number;
  };
  size: {
    width: number;
    height: number;
  };
  resizable: boolean;
  draggable: boolean;
}

export interface DashboardFilter {
  id: string;
  name: string;
  type: 'select' | 'multiselect' | 'date' | 'daterange' | 'number' | 'range' | 'text';
  field: string;
  options?: any[];
  defaultValue: any;
  enabled: boolean;
}

export interface VisualizationTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  type: string;
  chartType: string;
  config: Partial<VisualizationConfig>;
  sampleData: any[];
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export class AdvancedDataVisualizationService extends EventEmitter {
  private visualizations: Map<string, VisualizationConfig> = new Map();
  private data: Map<string, VisualizationData> = new Map();
  private dashboards: Map<string, Dashboard> = new Map();
  private templates: Map<string, VisualizationTemplate> = new Map();
  private isProcessing: boolean = false;
  private processingQueue: string[] = [];
  private processingInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeDefaultTemplates();
    this.startProcessing();
  }

  private initializeDefaultTemplates(): void {
    // Template para gráfico de líneas
    const lineChartTemplate: VisualizationTemplate = {
      id: 'line_chart_template',
      name: 'Line Chart Template',
      description: 'Template for creating line charts',
      category: 'charts',
      type: 'chart',
      chartType: 'line',
      config: {
        type: 'chart',
        chartType: 'line',
        dataSource: {
          type: 'api',
          endpoint: '/api/data'
        },
        dimensions: {
          x: 'date',
          y: 'value'
        },
        styling: {
          theme: 'light',
          colors: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12'],
          fonts: {
            family: 'Arial',
            size: 12,
            weight: 'normal'
          },
          layout: {
            width: 800,
            height: 400,
            margin: { top: 20, right: 30, bottom: 40, left: 50 }
          },
          axes: {
            x: {
              title: 'Date',
              ticks: 10,
              format: '%Y-%m-%d',
              gridLines: true,
              labels: true
            },
            y: {
              title: 'Value',
              ticks: 8,
              format: '.2f',
              gridLines: true,
              labels: true
            }
          },
          legend: {
            enabled: true,
            position: 'top',
            orientation: 'horizontal'
          },
          tooltip: {
            enabled: true,
            format: '{x}: {y}'
          }
        },
        interactions: [
          { type: 'zoom', enabled: true, config: {} },
          { type: 'pan', enabled: true, config: {} },
          { type: 'hover', enabled: true, config: {} }
        ],
        animations: [
          { type: 'fade', duration: 500, easing: 'ease-in-out', enabled: true, config: {} }
        ],
        responsive: true,
        realTime: false
      },
      sampleData: [
        { date: '2024-01-01', value: 100 },
        { date: '2024-01-02', value: 120 },
        { date: '2024-01-03', value: 90 },
        { date: '2024-01-04', value: 150 },
        { date: '2024-01-05', value: 180 }
      ],
      tags: ['chart', 'line', 'time-series'],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    // Template para gráfico de barras
    const barChartTemplate: VisualizationTemplate = {
      id: 'bar_chart_template',
      name: 'Bar Chart Template',
      description: 'Template for creating bar charts',
      category: 'charts',
      type: 'chart',
      chartType: 'bar',
      config: {
        type: 'chart',
        chartType: 'bar',
        dataSource: {
          type: 'api',
          endpoint: '/api/data'
        },
        dimensions: {
          x: 'category',
          y: 'value'
        },
        styling: {
          theme: 'light',
          colors: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12'],
          fonts: {
            family: 'Arial',
            size: 12,
            weight: 'normal'
          },
          layout: {
            width: 800,
            height: 400,
            margin: { top: 20, right: 30, bottom: 40, left: 50 }
          },
          axes: {
            x: {
              title: 'Category',
              ticks: 10,
              format: '',
              gridLines: false,
              labels: true
            },
            y: {
              title: 'Value',
              ticks: 8,
              format: '.2f',
              gridLines: true,
              labels: true
            }
          },
          legend: {
            enabled: true,
            position: 'top',
            orientation: 'horizontal'
          },
          tooltip: {
            enabled: true,
            format: '{x}: {y}'
          }
        },
        interactions: [
          { type: 'click', enabled: true, config: {} },
          { type: 'hover', enabled: true, config: {} }
        ],
        animations: [
          { type: 'slide', duration: 300, easing: 'ease-out', enabled: true, config: {} }
        ],
        responsive: true,
        realTime: false
      },
      sampleData: [
        { category: 'A', value: 100 },
        { category: 'B', value: 120 },
        { category: 'C', value: 90 },
        { category: 'D', value: 150 },
        { category: 'E', value: 180 }
      ],
      tags: ['chart', 'bar', 'categorical'],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    // Template para mapa de calor
    const heatmapTemplate: VisualizationTemplate = {
      id: 'heatmap_template',
      name: 'Heatmap Template',
      description: 'Template for creating heatmaps',
      category: 'charts',
      type: 'heatmap',
      chartType: 'heatmap',
      config: {
        type: 'heatmap',
        chartType: 'heatmap',
        dataSource: {
          type: 'api',
          endpoint: '/api/data'
        },
        dimensions: {
          x: 'x',
          y: 'y',
          color: 'value'
        },
        styling: {
          theme: 'light',
          colors: ['#ffffff', '#ff0000'],
          fonts: {
            family: 'Arial',
            size: 12,
            weight: 'normal'
          },
          layout: {
            width: 800,
            height: 400,
            margin: { top: 20, right: 30, bottom: 40, left: 50 }
          },
          axes: {
            x: {
              title: 'X Axis',
              ticks: 10,
              format: '',
              gridLines: true,
              labels: true
            },
            y: {
              title: 'Y Axis',
              ticks: 8,
              format: '',
              gridLines: true,
              labels: true
            }
          },
          legend: {
            enabled: true,
            position: 'right',
            orientation: 'vertical'
          },
          tooltip: {
            enabled: true,
            format: 'X: {x}, Y: {y}, Value: {value}'
          }
        },
        interactions: [
          { type: 'hover', enabled: true, config: {} },
          { type: 'click', enabled: true, config: {} }
        ],
        animations: [
          { type: 'fade', duration: 200, easing: 'ease-in', enabled: true, config: {} }
        ],
        responsive: true,
        realTime: false
      },
      sampleData: [
        { x: 0, y: 0, value: 10 },
        { x: 1, y: 0, value: 20 },
        { x: 2, y: 0, value: 30 },
        { x: 0, y: 1, value: 40 },
        { x: 1, y: 1, value: 50 },
        { x: 2, y: 1, value: 60 }
      ],
      tags: ['chart', 'heatmap', 'correlation'],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.templates.set(lineChartTemplate.id, lineChartTemplate);
    this.templates.set(barChartTemplate.id, barChartTemplate);
    this.templates.set(heatmapTemplate.id, heatmapTemplate);
  }

  private startProcessing(): void {
    this.processingInterval = setInterval(() => {
      this.processQueue();
    }, 5000); // Cada 5 segundos
  }

  stopProcessing(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.processingQueue.length === 0) return;

    this.isProcessing = true;
    const visualizationId = this.processingQueue.shift();

    try {
      await this.processVisualization(visualizationId!);
    } catch (error) {
      console.error('Error processing visualization:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  private async processVisualization(visualizationId: string): Promise<void> {
    const config = this.visualizations.get(visualizationId);
    if (!config) return;

    // Simular procesamiento de datos
    const data = await this.fetchData(config);
    const processedData = this.processData(data, config);
    
    const visualizationData: VisualizationData = {
      id: `data_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      visualizationId,
      data: processedData,
      metadata: {
        totalRecords: processedData.length,
        lastUpdated: new Date(),
        dataQuality: 0.95,
        completeness: 0.98
      },
      cache: {
        enabled: true,
        ttl: 300000, // 5 minutos
        lastCached: new Date()
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.data.set(visualizationId, visualizationData);
    this.emit('visualization_processed', visualizationData);
  }

  private async fetchData(config: VisualizationConfig): Promise<any[]> {
    // Simular obtención de datos
    return [
      { date: '2024-01-01', value: 100, category: 'A' },
      { date: '2024-01-02', value: 120, category: 'B' },
      { date: '2024-01-03', value: 90, category: 'A' },
      { date: '2024-01-04', value: 150, category: 'C' },
      { date: '2024-01-05', value: 180, category: 'B' }
    ];
  }

  private processData(data: any[], config: VisualizationConfig): any[] {
    // Aplicar filtros
    let processedData = data;
    
    for (const filter of config.filters) {
      if (!filter.enabled) continue;
      
      processedData = processedData.filter(item => {
        const value = item[filter.field];
        switch (filter.operator) {
          case 'equals':
            return value === filter.value;
          case 'not_equals':
            return value !== filter.value;
          case 'contains':
            return String(value).includes(String(filter.value));
          case 'greater_than':
            return value > filter.value;
          case 'less_than':
            return value < filter.value;
          case 'between':
            return value >= filter.value[0] && value <= filter.value[1];
          case 'in':
            return filter.value.includes(value);
          case 'not_in':
            return !filter.value.includes(value);
          default:
            return true;
        }
      });
    }

    // Aplicar agregaciones
    for (const aggregation of config.aggregations) {
      if (!aggregation.enabled) continue;
      
      // Simular agregación
      const values = processedData.map(item => item[aggregation.field]);
      let result: number;
      
      switch (aggregation.function) {
        case 'sum':
          result = values.reduce((sum, val) => sum + val, 0);
          break;
        case 'avg':
          result = values.reduce((sum, val) => sum + val, 0) / values.length;
          break;
        case 'count':
          result = values.length;
          break;
        case 'min':
          result = Math.min(...values);
          break;
        case 'max':
          result = Math.max(...values);
          break;
        default:
          result = 0;
      }
      
      processedData = [{ [aggregation.alias]: result }];
    }

    return processedData;
  }

  // Crear visualización
  createVisualization(config: Omit<VisualizationConfig, 'id' | 'createdAt' | 'updatedAt'>): string {
    const id = `viz_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newConfig: VisualizationConfig = {
      ...config,
      id,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.visualizations.set(id, newConfig);
    this.emit('visualization_created', newConfig);

    // Agregar a cola de procesamiento
    if (!this.processingQueue.includes(id)) {
      this.processingQueue.push(id);
    }

    return id;
  }

  // Crear dashboard
  createDashboard(dashboard: Omit<Dashboard, 'id' | 'createdAt' | 'updatedAt'>): string {
    const id = `dash_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newDashboard: Dashboard = {
      ...dashboard,
      id,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.dashboards.set(id, newDashboard);
    this.emit('dashboard_created', newDashboard);
    return id;
  }

  // Obtener visualizaciones
  getVisualizations(): VisualizationConfig[] {
    return Array.from(this.visualizations.values());
  }

  // Obtener dashboards
  getDashboards(): Dashboard[] {
    return Array.from(this.dashboards.values());
  }

  // Obtener templates
  getTemplates(): VisualizationTemplate[] {
    return Array.from(this.templates.values());
  }

  // Obtener datos de visualización
  getVisualizationData(visualizationId: string): VisualizationData | undefined {
    return this.data.get(visualizationId);
  }

  // Obtener estadísticas
  getStats(): {
    totalVisualizations: number;
    totalDashboards: number;
    totalTemplates: number;
    totalDataPoints: number;
    averageDataQuality: number;
    realTimeVisualizations: number;
  } {
    const visualizations = Array.from(this.visualizations.values());
    const dashboards = Array.from(this.dashboards.values());
    const templates = Array.from(this.templates.values());
    const data = Array.from(this.data.values());

    const totalDataPoints = data.reduce((sum, d) => sum + d.data.length, 0);
    const averageDataQuality = data.length > 0 
      ? data.reduce((sum, d) => sum + d.metadata.dataQuality, 0) / data.length 
      : 0;

    const realTimeVisualizations = visualizations.filter(v => v.realTime).length;

    return {
      totalVisualizations: visualizations.length,
      totalDashboards: dashboards.length,
      totalTemplates: templates.length,
      totalDataPoints,
      averageDataQuality,
      realTimeVisualizations
    };
  }
}

export const advancedDataVisualizationService = new AdvancedDataVisualizationService();





