/**
 * API Tests - CFDI 4.0 IA 2025
 */

const request = require('supertest');
const APICFDI4IA = require('../API_CFDI_4.0_IA_2025');

describe('API CFDI 4.0 IA - Basic Tests', () => {
  let api;
  
  beforeAll(() => {
    api = new APICFDI4IA();
  });
  
  afterAll(() => {
    // Cleanup
  });
  
  describe('Health Check', () => {
    test('GET /api/health should return 200', async () => {
      const res = await request(api.app).get('/api/health');
      expect(res.statusCode).toBe(200);
      expect(res.body).toHaveProperty('status');
    });
  });
  
  describe('Authentication', () => {
    test('POST /api/auth/register should create new user', async () => {
      const newUser = {
        email: 'test@example.com',
        password: 'password123',
        nombre: 'Test User'
      };
      
      const res = await request(api.app)
        .post('/api/auth/register')
        .send(newUser);
      
      expect(res.statusCode).toBe(201);
      expect(res.body).toHaveProperty('token');
    });
    
    test('POST /api/auth/login should return token', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123'
      };
      
      const res = await request(api.app)
        .post('/api/auth/login')
        .send(credentials);
      
      expect(res.statusCode).toBe(200);
      expect(res.body).toHaveProperty('token');
    });
  });
  
  describe('CFDI Templates', () => {
    test('GET /api/cfdi/templates should return templates', async () => {
      const res = await request(api.app).get('/api/cfdi/templates');
      expect(res.statusCode).toBe(200);
      expect(Array.isArray(res.body)).toBe(true);
    });
  });
});

describe('API CFDI 4.0 IA - Protected Routes', () => {
  let api;
  let token;
  
  beforeAll(async () => {
    api = new APICFDI4IA();
    
    // Register and get token
    const res = await request(api.app)
      .post('/api/auth/register')
      .send({
        email: 'protected@example.com',
        password: 'password123',
        nombre: 'Protected User'
      });
    token = res.body.token;
  });
  
  test('GET /api/protected/cfdi/list should require authentication', async () => {
    const res = await request(api.app)
      .get('/api/protected/cfdi/list');
    expect(res.statusCode).toBe(401);
  });
  
  test('GET /api/protected/cfdi/list should return list with token', async () => {
    const res = await request(api.app)
      .get('/api/protected/cfdi/list')
      .set('Authorization', `Bearer ${token}`);
    expect(res.statusCode).toBe(200);
  });
  
  test('POST /api/protected/cfdi/generate should create CFDI', async () => {
    const cfdiData = {
      emisor: {
        rfc: 'ABC123456789',
        nombre: 'Test Company',
        regimenFiscal: '601'
      },
      receptor: {
        rfc: 'XYZ987654321',
        nombre: 'Test Client',
        usoCFDI: 'G01'
      },
      conceptos: [
        {
          cantidad: 1,
          unidad: 'PZA',
          descripcion: 'Test Product',
          valorUnitario: '100.00',
          importe: '100.00'
        }
      ],
      total: '116.00',
      impuestos: {
        totalImpuestosTrasladados: '16.00',
        traslados: [
          {
            base: '100.00',
            impuesto: '002',
            tipoFactor: 'Tasa',
            tasaOCuota: '0.160000',
            importe: '16.00'
          }
        ]
      }
    };
    
    const res = await request(api.app)
      .post('/api/protected/cfdi/generate')
      .set('Authorization', `Bearer ${token}`)
      .send(cfdiData);
    
    expect(res.statusCode).toBe(201);
    expect(res.body).toHaveProperty('uuid');
  });
});



