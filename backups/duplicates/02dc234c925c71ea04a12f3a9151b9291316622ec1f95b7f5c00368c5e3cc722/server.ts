import app from './app';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { customerFeedbackService } from './services/customerFeedbackService';
import { dataIntegrationService } from './services/dataIntegrationService';

const PORT = process.env.PORT || 3001;
const HOST = process.env.HOST || '0.0.0.0';

// Crear servidor HTTP
const server = createServer(app);

// Crear servidor WebSocket
const wss = new WebSocketServer({ 
  server,
  path: '/ws'
});

// Manejar conexiones WebSocket
wss.on('connection', (ws, req) => {
  console.log('Nueva conexión WebSocket establecida');
  
  // Enviar mensaje de bienvenida
  ws.send(JSON.stringify({
    type: 'connection_established',
    message: 'Conexión WebSocket establecida correctamente',
    timestamp: new Date()
  }));

  // Manejar mensajes del cliente
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      
      switch (data.type) {
        case 'subscribe_feedback':
          // Suscribirse a actualizaciones de feedback
          ws.send(JSON.stringify({
            type: 'subscription_confirmed',
            channel: 'feedback_updates',
            message: 'Suscrito a actualizaciones de feedback'
          }));
          break;
          
        case 'subscribe_analytics':
          // Suscribirse a actualizaciones de analytics
          ws.send(JSON.stringify({
            type: 'subscription_confirmed',
            channel: 'analytics_updates',
            message: 'Suscrito a actualizaciones de analytics'
          }));
          break;
          
        case 'get_dashboard_data':
          // Enviar datos del dashboard
          try {
            const metrics = await customerFeedbackService.getFeedbackAnalytics('30d');
            ws.send(JSON.stringify({
              type: 'dashboard_data',
              data: metrics,
              timestamp: new Date()
            }));
          } catch (error) {
            ws.send(JSON.stringify({
              type: 'error',
              message: 'Error obteniendo datos del dashboard',
              error: error instanceof Error ? error.message : 'Unknown error'
            }));
          }
          break;
          
        case 'get_integration_status':
          // Enviar estado de integración
          try {
            const status = await dataIntegrationService.getIntegrationStatus();
            ws.send(JSON.stringify({
              type: 'integration_status',
              data: status,
              timestamp: new Date()
            }));
          } catch (error) {
            ws.send(JSON.stringify({
              type: 'error',
              message: 'Error obteniendo estado de integración',
              error: error instanceof Error ? error.message : 'Unknown error'
            }));
          }
          break;
          
        default:
          ws.send(JSON.stringify({
            type: 'error',
            message: 'Tipo de mensaje no reconocido',
            receivedType: data.type
          }));
      }
    } catch (error) {
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Error procesando mensaje',
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  });

  // Manejar cierre de conexión
  ws.on('close', () => {
    console.log('Conexión WebSocket cerrada');
  });

  // Manejar errores
  ws.on('error', (error) => {
    console.error('Error en WebSocket:', error);
  });
});

// Iniciar servidor
server.listen(PORT, HOST, () => {
  console.log(`🚀 Servidor de Feedback de IA Marketing iniciado`);
  console.log(`📍 Puerto: ${PORT}`);
  console.log(`🌐 Host: ${HOST}`);
  console.log(`🔗 HTTP: http://${HOST}:${PORT}`);
  console.log(`🔌 WebSocket: ws://${HOST}:${PORT}/ws`);
  console.log(`📊 Health Check: http://${HOST}:${PORT}/health`);
  console.log(`📈 API Docs: http://${HOST}:${PORT}/api-docs`);
  console.log(`🌍 Entorno: ${process.env.NODE_ENV || 'development'}`);
});

// Manejo de cierre graceful
process.on('SIGTERM', () => {
  console.log('SIGTERM recibido, cerrando servidor...');
  server.close(() => {
    console.log('Servidor cerrado');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT recibido, cerrando servidor...');
  server.close(() => {
    console.log('Servidor cerrado');
    process.exit(0);
  });
});

// Manejo de errores no capturados
process.on('uncaughtException', (error) => {
  console.error('Error no capturado:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Promesa rechazada no manejada:', reason);
  process.exit(1);
});

export { server, wss };
