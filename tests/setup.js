/**
 * Test Setup File - CFDI 4.0 IA 2025
 */

// Configurar variables de entorno para tests
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-secret-key';
process.env.PORT = '3000';

// Mock console methods si es necesario
const originalLog = console.log;
const originalError = console.error;
const originalWarn = console.warn;

global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
};

// Restaurar console en afterAll
afterAll(() => {
  console.log = originalLog;
  console.error = originalError;
  console.warn = originalWarn;
});

// Aumentar timeout para operaciones asíncronas
jest.setTimeout(30000);

// Limpiar mocks después de cada test
afterEach(() => {
  jest.clearAllMocks();
});



