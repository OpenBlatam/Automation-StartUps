import app from './app';
import { createServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import { realTimeNotificationService } from './services/realTimeNotificationService';
import { advancedAnalyticsService } from './services/advancedAnalyticsService';
import { consciousnessWebinarService } from './services/consciousnessWebinarService';

const PORT = process.env.PORT || 3001;
const HOST = process.env.HOST || '0.0.0.0';

const server = createServer(app);
const wss = new WebSocketServer({ server });

// WebSocket para notificaciones en tiempo real
wss.on('connection', (ws: WebSocket, req) => {
  console.log('WebSocket client connected');
  
  // Identificación del usuario (puede ser mejorada con JWT)
  const userId = req.headers['x-user-id'] as string || `anonymous_${Date.now()}`;
  realTimeNotificationService.registerWebSocketClient(userId, ws);

  ws.on('message', async (message: string) => {
    try {
      const parsedMessage = JSON.parse(message);
      console.log(`Received message from ${userId}:`, parsedMessage);

      switch (parsedMessage.type) {
        case 'subscribe_feedback':
          ws.send(JSON.stringify({ 
            event: 'subscription_confirmed', 
            topic: 'feedback',
            timestamp: new Date().toISOString()
          }));
          break;
          
        case 'subscribe_analytics':
          const report = await advancedAnalyticsService.getConsolidatedInsights('7d');
          ws.send(JSON.stringify({ 
            event: 'initial_analytics_report', 
            data: report,
            timestamp: new Date().toISOString()
          }));
          ws.send(JSON.stringify({ 
            event: 'subscription_confirmed', 
            topic: 'analytics',
            timestamp: new Date().toISOString()
          }));
          break;
          
        case 'get_dashboard_data':
          const dashboardData = await advancedAnalyticsService.getConsolidatedInsights('1d');
          ws.send(JSON.stringify({ 
            event: 'dashboard_data', 
            data: dashboardData,
            timestamp: new Date().toISOString()
          }));
          break;
          
        case 'analyze_feedback':
          // Análisis en tiempo real de feedback
          const feedbackData = parsedMessage.data;
          if (feedbackData) {
            const insights = await advancedAnalyticsService.processAdvancedFeedback(feedbackData);
            ws.send(JSON.stringify({ 
              event: 'analysis_result', 
              data: insights,
              timestamp: new Date().toISOString()
            }));
          }
          break;
          
        case 'subscribe_webinars':
          // Suscripción a actualizaciones de webinars
          ws.send(JSON.stringify({ 
            event: 'webinar_subscription_confirmed',
            timestamp: new Date().toISOString()
          }));
          break;
          
        case 'get_active_webinars':
          const activeWebinars = await consciousnessWebinarService.getActiveWebinars();
          ws.send(JSON.stringify({ 
            event: 'active_webinars', 
            data: activeWebinars,
            timestamp: new Date().toISOString()
          }));
          break;
          
        case 'ping':
          ws.send(JSON.stringify({ 
            event: 'pong',
            timestamp: new Date().toISOString()
          }));
          break;
          
        default:
          ws.send(JSON.stringify({ 
            error: 'Unknown message type',
            supportedTypes: [
              'subscribe_feedback',
              'subscribe_analytics', 
              'get_dashboard_data',
              'analyze_feedback',
              'subscribe_webinars',
              'get_active_webinars',
              'ping'
            ],
            timestamp: new Date().toISOString()
          }));
          break;
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      ws.send(JSON.stringify({ 
        error: 'Invalid JSON message',
        timestamp: new Date().toISOString()
      }));
    }
  });

  ws.on('close', () => {
    console.log('WebSocket client disconnected');
    realTimeNotificationService.unregisterWebSocketClient(userId);
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });

  // Enviar mensaje de bienvenida
  ws.send(JSON.stringify({
    event: 'connection_established',
    message: 'Connected to AI Marketing Feedback System',
    features: {
      realTimeFeedback: true,
      advancedAnalytics: true,
      culturalAnalysis: true,
      emotionalIntelligence: true,
      predictiveMetrics: true,
      consciousnessWebinars: true
    },
    timestamp: new Date().toISOString()
  }));
});

// Iniciar servidor
server.listen(PORT, HOST, () => {
  console.log(`🚀 AI Marketing Feedback System running on http://${HOST}:${PORT}`);
  console.log(`📡 WebSocket server running on ws://${HOST}:${PORT}`);
  console.log(`🔗 Health check: http://${HOST}:${PORT}/health`);
  console.log(`📊 Advanced Analytics: http://${HOST}:${PORT}/api/advanced`);
  console.log(`💬 Feedback API: http://${HOST}:${PORT}/api/feedback`);
  console.log(`🧠 Consciousness Webinars: http://${HOST}:${PORT}/api/webinars`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔐 Features enabled:`);
  console.log(`   ✅ Real-time notifications`);
  console.log(`   ✅ Advanced analytics`);
  console.log(`   ✅ Cultural analysis`);
  console.log(`   ✅ Emotional intelligence`);
  console.log(`   ✅ Predictive metrics`);
  console.log(`   ✅ Consciousness webinars`);
  console.log(`   ✅ WebSocket support`);
  console.log(`   ✅ Rate limiting`);
  console.log(`   ✅ Spam detection`);
});

// Manejo de cierre graceful
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
    process.exit(0);
  });
});

// Manejo de errores no capturados
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

export default server;







