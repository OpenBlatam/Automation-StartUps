#!/usr/bin/env node
/**
 * Generate API Documentation
 */

const fs = require('fs');
const path = require('path');

const generateDocs = () => {
  const doc = `# 🔌 CFDI 4.0 IA 2025 - API Documentation

## Base URL
\`\`\`
https://api.cfdi4ia.com
\`\`\`

## Authentication
Most endpoints require JWT authentication.

\`\`\`
Authorization: Bearer YOUR_JWT_TOKEN
\`\`\`

---

## Public Endpoints

### Health Check
\`\`\`http
GET /api/health
\`\`\`

**Response:**
\`\`\`json
{
  "status": "ok",
  "timestamp": "2025-01-16T10:00:00Z"
}
\`\`\`

---

### Register User
\`\`\`http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "nombre": "John Doe"
}
\`\`\`

**Response:**
\`\`\`json
{
  "token": "jwt-token-here",
  "user": {
    "email": "user@example.com",
    "nombre": "John Doe"
  }
}
\`\`\`

---

### Login
\`\`\`http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
\`\`\`

**Response:**
\`\`\`json
{
  "token": "jwt-token-here",
  "user": {
    "email": "user@example.com",
    "nombre": "John Doe"
  }
}
\`\`\`

---

### Get Templates
\`\`\`http
GET /api/cfdi/templates
\`\`\`

**Response:**
\`\`\`json
[
  {
    "id": "factura",
    "nombre": "Factura",
    "descripcion": "CFDI de tipo Factura",
    "campos": [...]
  }
]
\`\`\`

---

### Validate CFDI
\`\`\`http
GET /api/cfdi/validate/:uuid
\`\`\`

**Response:**
\`\`\`json
{
  "valido": true,
  "score": 95,
  "errores": [],
  "advertencias": []
}
\`\`\`

---

## Protected Endpoints

### Generate CFDI
\`\`\`http
POST /api/protected/cfdi/generate
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "emisor": {
    "rfc": "ABC123456789",
    "nombre": "Empresa Test",
    "regimenFiscal": "601"
  },
  "receptor": {
    "rfc": "XYZ987654321",
    "nombre": "Cliente Test",
    "usoCFDI": "G01"
  },
  "conceptos": [{
    "cantidad": 1,
    "unidad": "PZA",
    "descripcion": "Producto Test",
    "valorUnitario": "100.00",
    "importe": "100.00"
  }],
  "total": "116.00"
}
\`\`\`

**Response:**
\`\`\`json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "cfdi": {...},
  "timestamp": "2025-01-16T10:00:00Z"
}
\`\`\`

---

### List CFDI
\`\`\`http
GET /api/protected/cfdi/list
Authorization: Bearer YOUR_TOKEN
\`\`\`

**Query Parameters:**
- \`limit\`: Number of results (default: 10)
- \`offset\`: Pagination offset (default: 0)

**Response:**
\`\`\`json
{
  "cfdi": [...],
  "total": 100,
  "limit": 10,
  "offset": 0
}
\`\`\`

---

### Get CFDI
\`\`\`http
GET /api/protected/cfdi/:uuid
Authorization: Bearer YOUR_TOKEN
\`\`\`

**Response:**
\`\`\`json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "emisor": {...},
  "receptor": {...},
  "conceptos": [...],
  "impuestos": {...},
  "fechaCreacion": "2025-01-16T10:00:00Z"
}
\`\`\`

---

### Update CFDI
\`\`\`http
PUT /api/protected/cfdi/:uuid
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "emisor": {...},
  "receptor": {...}
}
\`\`\`

---

### Delete CFDI
\`\`\`http
DELETE /api/protected/cfdi/:uuid
Authorization: Bearer YOUR_TOKEN
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "message": "CFDI eliminado correctamente"
}
\`\`\`

---

### Bulk Generate
\`\`\`http
POST /api/protected/cfdi/bulk
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "cfdi": [
    {...cfdi1},
    {...cfdi2}
  ]
}
\`\`\`

**Response:**
\`\`\`json
{
  "procesados": 10,
  "exitosos": 9,
  "errores": 1,
  "resultados": [...]
}
\`\`\`

---

### Get Stats
\`\`\`http
GET /api/protected/stats
Authorization: Bearer YOUR_TOKEN
\`\`\`

**Response:**
\`\`\`json
{
  "totalCFDI": 100,
  "totalFacturado": 1000000,
  "errores": 5,
  "usuariosActivos": 10,
  "personal": {
    "total": 50,
    "promedio": 50000
  },
  "global": {
    "totalCFDI": 10000,
    "totalFacturado": 100000000
  }
}
\`\`\`

---

### Get Dashboard
\`\`\`http
GET /api/protected/dashboard
Authorization: Bearer YOUR_TOKEN
\`\`\`

**Response:**
\`\`\`json
{
  "resumen": {...},
  "tendencias": [...],
  "analisis": {...}
}
\`\`\`

---

### Export CFDI
\`\`\`http
POST /api/protected/cfdi/export
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "format": "json",
  "uuids": ["uuid1", "uuid2"]
}
\`\`\`

**Response:** File download (JSON or XML)

---

### Import CFDI
\`\`\`http
POST /api/protected/cfdi/import
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "cfdi": [{...}, {...}]
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "procesados": 10,
  "exitosos": 9,
  "errores": 1,
  "resultados": [...]
}
\`\`\`

---

## Error Responses

All error responses follow this format:

\`\`\`json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-16T10:00:00Z"
}
\`\`\`

### Common Error Codes
- \`401\` - Unauthorized
- \`403\` - Forbidden
- \`404\` - Not Found
- \`429\` - Too Many Requests
- \`500\` - Internal Server Error
`;

  const outputPath = path.join(__dirname, '..', 'docs', 'API.md');
  const outputDir = path.dirname(outputPath);
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, doc, 'utf8');
  console.log('✅ API Documentation generated successfully!');
};

generateDocs();



