import { PrismaClient } from '@prisma/client';
import { customerFeedbackService, CustomerFeedback } from './customerFeedbackService';

const prisma = new PrismaClient();

export interface DataSource {
  id: string;
  name: string;
  type: 'social_media' | 'survey' | 'review' | 'support' | 'email' | 'webinar' | 'course';
  platform: string;
  config: {
    apiKey?: string;
    apiSecret?: string;
    webhookUrl?: string;
    credentials?: any;
    filters?: any;
    mapping?: any;
  };
  status: 'active' | 'inactive' | 'error';
  lastSync: Date;
  syncFrequency: number; // minutes
  region: string;
  language: string;
}

export interface IntegrationJob {
  id: string;
  sourceId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  recordsProcessed: number;
  recordsFailed: number;
  error?: string;
  metadata: any;
}

export interface DataMapping {
  sourceField: string;
  targetField: string;
  transformation?: string;
  required: boolean;
  defaultValue?: any;
}

export class DataIntegrationService {
  private dataSources: Map<string, DataSource> = new Map();
  private integrationJobs: Map<string, IntegrationJob> = new Map();
  private syncIntervals: Map<string, NodeJS.Timeout> = new Map();

  // Configurar fuente de datos
  async configureDataSource(sourceData: Partial<DataSource>): Promise<DataSource> {
    const source: DataSource = {
      id: `source_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: sourceData.name || 'Unnamed Source',
      type: sourceData.type || 'survey',
      platform: sourceData.platform || 'internal',
      config: sourceData.config || {},
      status: 'active',
      lastSync: new Date(),
      syncFrequency: sourceData.syncFrequency || 60, // 1 hora por defecto
      region: sourceData.region || 'LATAM',
      language: sourceData.language || 'es',
      ...sourceData
    };

    this.dataSources.set(source.id, source);

    // Iniciar sincronización automática
    this.startAutoSync(source.id);

    return source;
  }

  // Iniciar sincronización automática
  private startAutoSync(sourceId: string): void {
    const source = this.dataSources.get(sourceId);
    if (!source || source.status !== 'active') return;

    const interval = setInterval(async () => {
      await this.syncDataSource(sourceId);
    }, source.syncFrequency * 60 * 1000);

    this.syncIntervals.set(sourceId, interval);
  }

  // Sincronizar fuente de datos
  async syncDataSource(sourceId: string): Promise<IntegrationJob> {
    const source = this.dataSources.get(sourceId);
    if (!source) {
      throw new Error('Data source not found');
    }

    const job: IntegrationJob = {
      id: `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      sourceId,
      status: 'running',
      startTime: new Date(),
      recordsProcessed: 0,
      recordsFailed: 0,
      metadata: {}
    };

    this.integrationJobs.set(job.id, job);

    try {
      // Ejecutar sincronización según el tipo de fuente
      const results = await this.executeSync(source, job);
      
      job.status = 'completed';
      job.endTime = new Date();
      job.recordsProcessed = results.processed;
      job.recordsFailed = results.failed;
      job.metadata = results.metadata;

      // Actualizar última sincronización
      source.lastSync = new Date();
      this.dataSources.set(sourceId, source);

    } catch (error) {
      job.status = 'failed';
      job.endTime = new Date();
      job.error = error instanceof Error ? error.message : 'Unknown error';
    }

    this.integrationJobs.set(job.id, job);
    return job;
  }

  // Ejecutar sincronización según tipo de fuente
  private async executeSync(source: DataSource, job: IntegrationJob): Promise<{
    processed: number;
    failed: number;
    metadata: any;
  }> {
    let processed = 0;
    let failed = 0;
    const metadata: any = {};

    switch (source.type) {
      case 'social_media':
        return await this.syncSocialMedia(source, job);
      
      case 'survey':
        return await this.syncSurvey(source, job);
      
      case 'review':
        return await this.syncReviews(source, job);
      
      case 'support':
        return await this.syncSupportTickets(source, job);
      
      case 'email':
        return await this.syncEmailFeedback(source, job);
      
      case 'webinar':
        return await this.syncWebinarFeedback(source, job);
      
      case 'course':
        return await this.syncCourseFeedback(source, job);
      
      default:
        throw new Error(`Unsupported data source type: ${source.type}`);
    }
  }

  // Sincronizar redes sociales
  private async syncSocialMedia(source: DataSource, job: IntegrationJob): Promise<{
    processed: number;
    failed: number;
    metadata: any;
  }> {
    let processed = 0;
    let failed = 0;
    const metadata: any = {};

    try {
      // Simulación de integración con APIs de redes sociales
      // En producción, integrar con Facebook Graph API, Instagram Basic Display API, LinkedIn API, etc.
      
      const socialData = await this.fetchSocialMediaData(source);
      
      for (const post of socialData) {
        try {
          const feedback: Partial<CustomerFeedback> = {
            source: 'social_media',
            platform: source.platform,
            content: post.content,
            language: source.language,
            region: source.region,
            metadata: {
              rating: post.rating,
              tags: post.tags,
              categories: post.categories,
              urgency: post.urgency || 'low',
              responseRequired: post.responseRequired || false
            }
          };

          await customerFeedbackService.processFeedback(feedback);
          processed++;
        } catch (error) {
          console.error('Error processing social media post:', error);
          failed++;
        }
      }

      metadata.socialMediaData = {
        totalPosts: socialData.length,
        platform: source.platform,
        region: source.region
      };

    } catch (error) {
      console.error('Error syncing social media:', error);
      throw error;
    }

    return { processed, failed, metadata };
  }

  // Sincronizar encuestas
  private async syncSurvey(source: DataSource, job: IntegrationJob): Promise<{
    processed: number;
    failed: number;
    metadata: any;
  }> {
    let processed = 0;
    let failed = 0;
    const metadata: any = {};

    try {
      // Simulación de integración con plataformas de encuestas
      // En producción, integrar con Typeform, SurveyMonkey, Google Forms, etc.
      
      const surveyData = await this.fetchSurveyData(source);
      
      for (const response of surveyData) {
        try {
          const feedback: Partial<CustomerFeedback> = {
            source: 'survey',
            platform: source.platform,
            content: response.feedback,
            language: source.language,
            region: source.region,
            metadata: {
              rating: response.rating,
              tags: response.tags,
              categories: response.categories,
              urgency: response.urgency || 'low',
              responseRequired: response.responseRequired || false
            }
          };

          await customerFeedbackService.processFeedback(feedback);
          processed++;
        } catch (error) {
          console.error('Error processing survey response:', error);
          failed++;
        }
      }

      metadata.surveyData = {
        totalResponses: surveyData.length,
        platform: source.platform,
        region: source.region
      };

    } catch (error) {
      console.error('Error syncing survey:', error);
      throw error;
    }

    return { processed, failed, metadata };
  }

  // Sincronizar reseñas
  private async syncReviews(source: DataSource, job: IntegrationJob): Promise<{
    processed: number;
    failed: number;
    metadata: any;
  }> {
    let processed = 0;
    let failed = 0;
    const metadata: any = {};

    try {
      // Simulación de integración con plataformas de reseñas
      // En producción, integrar con Google My Business, Trustpilot, Yelp, etc.
      
      const reviewData = await this.fetchReviewData(source);
      
      for (const review of reviewData) {
        try {
          const feedback: Partial<CustomerFeedback> = {
            source: 'review',
            platform: source.platform,
            content: review.content,
            language: source.language,
            region: source.region,
            metadata: {
              rating: review.rating,
              tags: review.tags,
              categories: review.categories,
              urgency: review.urgency || 'low',
              responseRequired: review.responseRequired || false
            }
          };

          await customerFeedbackService.processFeedback(feedback);
          processed++;
        } catch (error) {
          console.error('Error processing review:', error);
          failed++;
        }
      }

      metadata.reviewData = {
        totalReviews: reviewData.length,
        platform: source.platform,
        region: source.region
      };

    } catch (error) {
      console.error('Error syncing reviews:', error);
      throw error;
    }

    return { processed, failed, metadata };
  }

  // Sincronizar tickets de soporte
  private async syncSupportTickets(source: DataSource, job: IntegrationJob): Promise<{
    processed: number;
    failed: number;
    metadata: any;
  }> {
    let processed = 0;
    let failed = 0;
    const metadata: any = {};

    try {
      // Simulación de integración con sistemas de soporte
      // En producción, integrar con Zendesk, Freshdesk, Intercom, etc.
      
      const supportData = await this.fetchSupportData(source);
      
      for (const ticket of supportData) {
        try {
          const feedback: Partial<CustomerFeedback> = {
            source: 'support_ticket',
            platform: source.platform,
            content: ticket.content,
            language: source.language,
            region: source.region,
            metadata: {
              rating: ticket.rating,
              tags: ticket.tags,
              categories: ticket.categories,
              urgency: ticket.urgency || 'medium',
              responseRequired: true
            }
          };

          await customerFeedbackService.processFeedback(feedback);
          processed++;
        } catch (error) {
          console.error('Error processing support ticket:', error);
          failed++;
        }
      }

      metadata.supportData = {
        totalTickets: supportData.length,
        platform: source.platform,
        region: source.region
      };

    } catch (error) {
      console.error('Error syncing support tickets:', error);
      throw error;
    }

    return { processed, failed, metadata };
  }

  // Sincronizar feedback por email
  private async syncEmailFeedback(source: DataSource, job: IntegrationJob): Promise<{
    processed: number;
    failed: number;
    metadata: any;
  }> {
    let processed = 0;
    let failed = 0;
    const metadata: any = {};

    try {
      // Simulación de integración con sistemas de email
      // En producción, integrar con Gmail API, Outlook API, etc.
      
      const emailData = await this.fetchEmailData(source);
      
      for (const email of emailData) {
        try {
          const feedback: Partial<CustomerFeedback> = {
            source: 'email',
            platform: source.platform,
            content: email.content,
            language: source.language,
            region: source.region,
            metadata: {
              rating: email.rating,
              tags: email.tags,
              categories: email.categories,
              urgency: email.urgency || 'low',
              responseRequired: email.responseRequired || false
            }
          };

          await customerFeedbackService.processFeedback(feedback);
          processed++;
        } catch (error) {
          console.error('Error processing email feedback:', error);
          failed++;
        }
      }

      metadata.emailData = {
        totalEmails: emailData.length,
        platform: source.platform,
        region: source.region
      };

    } catch (error) {
      console.error('Error syncing email feedback:', error);
      throw error;
    }

    return { processed, failed, metadata };
  }

  // Sincronizar feedback de webinars
  private async syncWebinarFeedback(source: DataSource, job: IntegrationJob): Promise<{
    processed: number;
    failed: number;
    metadata: any;
  }> {
    let processed = 0;
    let failed = 0;
    const metadata: any = {};

    try {
      // Integración con sistema de webinars existente
      const webinarData = await this.fetchWebinarData(source);
      
      for (const feedback of webinarData) {
        try {
          const processedFeedback: Partial<CustomerFeedback> = {
            source: 'webinar',
            platform: source.platform,
            content: feedback.content,
            language: source.language,
            region: source.region,
            webinarId: feedback.webinarId,
            metadata: {
              rating: feedback.rating,
              tags: feedback.tags,
              categories: feedback.categories,
              urgency: feedback.urgency || 'low',
              responseRequired: feedback.responseRequired || false
            }
          };

          await customerFeedbackService.processFeedback(processedFeedback);
          processed++;
        } catch (error) {
          console.error('Error processing webinar feedback:', error);
          failed++;
        }
      }

      metadata.webinarData = {
        totalFeedback: webinarData.length,
        platform: source.platform,
        region: source.region
      };

    } catch (error) {
      console.error('Error syncing webinar feedback:', error);
      throw error;
    }

    return { processed, failed, metadata };
  }

  // Sincronizar feedback de cursos
  private async syncCourseFeedback(source: DataSource, job: IntegrationJob): Promise<{
    processed: number;
    failed: number;
    metadata: any;
  }> {
    let processed = 0;
    let failed = 0;
    const metadata: any = {};

    try {
      // Integración con sistema de cursos
      const courseData = await this.fetchCourseData(source);
      
      for (const feedback of courseData) {
        try {
          const processedFeedback: Partial<CustomerFeedback> = {
            source: 'course_feedback',
            platform: source.platform,
            content: feedback.content,
            language: source.language,
            region: source.region,
            courseId: feedback.courseId,
            metadata: {
              rating: feedback.rating,
              tags: feedback.tags,
              categories: feedback.categories,
              urgency: feedback.urgency || 'low',
              responseRequired: feedback.responseRequired || false
            }
          };

          await customerFeedbackService.processFeedback(processedFeedback);
          processed++;
        } catch (error) {
          console.error('Error processing course feedback:', error);
          failed++;
        }
      }

      metadata.courseData = {
        totalFeedback: courseData.length,
        platform: source.platform,
        region: source.region
      };

    } catch (error) {
      console.error('Error syncing course feedback:', error);
      throw error;
    }

    return { processed, failed, metadata };
  }

  // Métodos de simulación para obtener datos (en producción, implementar APIs reales)
  private async fetchSocialMediaData(source: DataSource): Promise<any[]> {
    // Simulación de datos de redes sociales
    return [
      {
        content: 'Excelente curso de IA marketing, muy recomendado!',
        rating: 5,
        tags: ['curso', 'ia', 'marketing'],
        categories: ['educacion'],
        urgency: 'low',
        responseRequired: false
      },
      {
        content: 'El contenido es muy bueno pero la plataforma tiene algunos bugs',
        rating: 4,
        tags: ['contenido', 'plataforma', 'bugs'],
        categories: ['tecnologia'],
        urgency: 'medium',
        responseRequired: true
      }
    ];
  }

  private async fetchSurveyData(source: DataSource): Promise<any[]> {
    // Simulación de datos de encuestas
    return [
      {
        feedback: 'Muy satisfecho con el curso, aprendí mucho sobre IA aplicada al marketing',
        rating: 5,
        tags: ['satisfaccion', 'aprendizaje'],
        categories: ['educacion'],
        urgency: 'low',
        responseRequired: false
      }
    ];
  }

  private async fetchReviewData(source: DataSource): Promise<any[]> {
    // Simulación de datos de reseñas
    return [
      {
        content: 'Curso increíble, el instructor es muy profesional',
        rating: 5,
        tags: ['instructor', 'profesional'],
        categories: ['educacion'],
        urgency: 'low',
        responseRequired: false
      }
    ];
  }

  private async fetchSupportData(source: DataSource): Promise<any[]> {
    // Simulación de datos de soporte
    return [
      {
        content: 'No puedo acceder a mi cuenta, necesito ayuda urgente',
        rating: 1,
        tags: ['acceso', 'cuenta', 'urgente'],
        categories: ['soporte'],
        urgency: 'high',
        responseRequired: true
      }
    ];
  }

  private async fetchEmailData(source: DataSource): Promise<any[]> {
    // Simulación de datos de email
    return [
      {
        content: 'Gracias por el curso, fue muy útil para mi empresa',
        rating: 5,
        tags: ['gratitud', 'utilidad'],
        categories: ['educacion'],
        urgency: 'low',
        responseRequired: false
      }
    ];
  }

  private async fetchWebinarData(source: DataSource): Promise<any[]> {
    // Simulación de datos de webinars
    return [
      {
        content: 'El webinar fue muy informativo, me gustaría más contenido así',
        rating: 4,
        tags: ['webinar', 'informativo'],
        categories: ['educacion'],
        urgency: 'low',
        responseRequired: false,
        webinarId: 'webinar_123'
      }
    ];
  }

  private async fetchCourseData(source: DataSource): Promise<any[]> {
    // Simulación de datos de cursos
    return [
      {
        content: 'El módulo de IA fue excelente, pero necesito más ejemplos prácticos',
        rating: 4,
        tags: ['modulo', 'ia', 'ejemplos'],
        categories: ['educacion'],
        urgency: 'medium',
        responseRequired: true,
        courseId: 'course_456'
      }
    ];
  }

  // Obtener fuentes de datos
  async getDataSources(): Promise<DataSource[]> {
    return Array.from(this.dataSources.values());
  }

  // Obtener fuente de datos por ID
  async getDataSourceById(id: string): Promise<DataSource | null> {
    return this.dataSources.get(id) || null;
  }

  // Actualizar fuente de datos
  async updateDataSource(id: string, updates: Partial<DataSource>): Promise<DataSource | null> {
    const source = this.dataSources.get(id);
    if (!source) return null;

    const updatedSource = { ...source, ...updates };
    this.dataSources.set(id, updatedSource);

    // Reiniciar sincronización si cambió la frecuencia
    if (updates.syncFrequency && updates.syncFrequency !== source.syncFrequency) {
      this.stopAutoSync(id);
      this.startAutoSync(id);
    }

    return updatedSource;
  }

  // Eliminar fuente de datos
  async deleteDataSource(id: string): Promise<boolean> {
    this.stopAutoSync(id);
    return this.dataSources.delete(id);
  }

  // Detener sincronización automática
  private stopAutoSync(sourceId: string): void {
    const interval = this.syncIntervals.get(sourceId);
    if (interval) {
      clearInterval(interval);
      this.syncIntervals.delete(sourceId);
    }
  }

  // Obtener trabajos de integración
  async getIntegrationJobs(): Promise<IntegrationJob[]> {
    return Array.from(this.integrationJobs.values());
  }

  // Obtener trabajo de integración por ID
  async getIntegrationJobById(id: string): Promise<IntegrationJob | null> {
    return this.integrationJobs.get(id) || null;
  }

  // Obtener estado de integración
  async getIntegrationStatus(): Promise<{
    totalSources: number;
    activeSources: number;
    lastSync: Date | null;
    totalJobs: number;
    runningJobs: number;
    failedJobs: number;
  }> {
    const sources = Array.from(this.dataSources.values());
    const jobs = Array.from(this.integrationJobs.values());

    return {
      totalSources: sources.length,
      activeSources: sources.filter(s => s.status === 'active').length,
      lastSync: sources.length > 0 ? new Date(Math.max(...sources.map(s => s.lastSync.getTime()))) : null,
      totalJobs: jobs.length,
      runningJobs: jobs.filter(j => j.status === 'running').length,
      failedJobs: jobs.filter(j => j.status === 'failed').length
    };
  }
}

export const dataIntegrationService = new DataIntegrationService();



