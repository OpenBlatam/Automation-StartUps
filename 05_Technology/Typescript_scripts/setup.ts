import { config } from 'dotenv';

// Cargar variables de entorno para las pruebas
config({ path: '.env.test' });

// Configurar variables de entorno por defecto para las pruebas
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-jwt-secret';
process.env.VALID_API_KEYS = 'test-key-1,test-key-2,test-key-3';
process.env.ALLOWED_ORIGINS = 'http://localhost:3000,http://localhost:3001';
process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/test_feedback_db';
process.env.REDIS_URL = 'redis://localhost:6379';
process.env.SMTP_HOST = 'smtp.test.com';
process.env.SMTP_PORT = '587';
process.env.SMTP_USER = 'test@test.com';
process.env.SMTP_PASS = 'test-password';

// Configurar timeouts para las pruebas
jest.setTimeout(10000);

// Mock de console.log para evitar ruido en las pruebas
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

beforeAll(() => {
  console.log = jest.fn();
  console.error = jest.fn();
});

afterAll(() => {
  console.log = originalConsoleLog;
  console.error = originalConsoleError;
});

// Mock de servicios externos
jest.mock('../services/realTimeNotificationService', () => ({
  realTimeNotificationService: {
    registerWebSocketClient: jest.fn(),
    unregisterWebSocketClient: jest.fn(),
    sendNotification: jest.fn()
  }
}));

jest.mock('../services/consciousnessWebinarService', () => ({
  consciousnessWebinarService: {
    getActiveWebinars: jest.fn().mockResolvedValue([]),
    createWebinar: jest.fn(),
    updateWebinar: jest.fn(),
    deleteWebinar: jest.fn()
  }
}));

// Configurar mocks para Prisma
jest.mock('@prisma/client', () => ({
  PrismaClient: jest.fn().mockImplementation(() => ({
    customerFeedback: {
      create: jest.fn(),
      findMany: jest.fn(),
      findUnique: jest.fn(),
      update: jest.fn(),
      delete: jest.fn()
    },
    $disconnect: jest.fn()
  }))
}));

// Mock de Redis
jest.mock('redis', () => ({
  createClient: jest.fn().mockReturnValue({
    connect: jest.fn(),
    disconnect: jest.fn(),
    get: jest.fn(),
    set: jest.fn(),
    del: jest.fn(),
    exists: jest.fn(),
    expire: jest.fn()
  })
}));

// Mock de nodemailer
jest.mock('nodemailer', () => ({
  createTransporter: jest.fn().mockReturnValue({
    sendMail: jest.fn().mockResolvedValue({ messageId: 'test-message-id' })
  })
}));

// Mock de WebSocket
jest.mock('ws', () => ({
  WebSocketServer: jest.fn().mockImplementation(() => ({
    on: jest.fn(),
    close: jest.fn()
  })),
  WebSocket: jest.fn()
}));

// Mock de axios
jest.mock('axios', () => ({
  post: jest.fn().mockResolvedValue({ data: { success: true } }),
  get: jest.fn().mockResolvedValue({ data: { success: true } })
}));

// Configurar cleanup después de cada prueba
afterEach(() => {
  jest.clearAllMocks();
});

// Configurar cleanup global
afterAll(async () => {
  // Limpiar recursos si es necesario
  await new Promise(resolve => setTimeout(resolve, 100));
});






