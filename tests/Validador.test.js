/**
 * Validador Tests - CFDI 4.0 IA 2025
 */

const ValidadorCFDI4IA = require('../Validador_CFDI_4.0_IA_2025');

describe('Validador CFDI 4.0 IA - Unit Tests', () => {
  let validador;
  
  beforeEach(() => {
    validador = new ValidadorCFDI4IA();
  });
  
  test('should validate RFC correctly', () => {
    const validRFCs = [
      'ABC123456789',
      'XEXX010101000',
      'ABCD123456EF1'
    ];
    
    validRFCs.forEach(rfc => {
      expect(validador.validaciones.rfc.test(rfc)).toBe(true);
    });
  });
  
  test('should reject invalid RFC', () => {
    const invalidRFCs = [
      'ABC',
      '123456789',
      'INVALID',
      ''
    ];
    
    invalidRFCs.forEach(rfc => {
      expect(validador.validaciones.rfc.test(rfc)).toBe(false);
    });
  });
  
  test('should validate complete CFDI', () => {
    const cfdiValido = {
      emisor: {
        rfc: 'ABC123456789',
        nombre: 'Test Company'
      },
      receptor: {
        rfc: 'XYZ987654321',
        nombre: 'Test Client'
      },
      conceptos: [
        {
          cantidad: 1,
          unidad: 'PZA',
          descripcion: 'Test',
          valorUnitario: '100.00'
        }
      ],
      total: '116.00'
    };
    
    const resultado = validador.validarCFDI(cfdiValido);
    expect(resultado.valido).toBe(true);
    expect(resultado.errores.length).toBe(0);
  });
  
  test('should detect errors in invalid CFDI', () => {
    const cfdiInvalido = {
      emisor: {
        rfc: 'INVALID',
        nombre: ''
      },
      receptor: {
        rfc: 'INVALID',
        nombre: ''
      },
      conceptos: []
    };
    
    const resultado = validador.validarCFDI(cfdiInvalido);
    expect(resultado.valido).toBe(false);
    expect(resultado.errores.length).toBeGreaterThan(0);
  });
  
  test('should validate forms de pago', () => {
    const validas = ['01', '03', '04', '05', '06', '08', '99'];
    
    validas.forEach(forma => {
      expect(validador.catalogos.formasPago).toContain(forma);
    });
  });
  
  test('should validate metodos de pago', () => {
    const metodos = ['PUE', 'PPD', 'PIP'];
    
    metodos.forEach(metodo => {
      expect(validador.catalogos.metodosPago).toContain(metodo);
    });
  });
});

describe('Validador CFDI 4.0 IA - Integration Tests', () => {
  let validador;
  
  beforeEach(() => {
    validador = new ValidadorCFDI4IA();
  });
  
  test('should validate complex CFDI structure', () => {
    const cfdi = {
      fecha: '2025-01-16T10:00:00',
      formaPago: '03',
      metodoPago: 'PUE',
      tipoComprobante: 'I',
      moneda: 'MXN',
      emisor: {
        rfc: 'ABC123456789',
        nombre: 'Test Company S.A. de C.V.',
        regimenFiscal: '601',
        domicilioFiscal: {
          codigoPostal: '01234'
        }
      },
      receptor: {
        rfc: 'XYZ987654321',
        nombre: 'Test Client Inc.',
        residenciaFiscal: 'MXN',
        numRegIdTrib: '',
        usoCFDI: 'G01'
      },
      conceptos: [
        {
          cantidad: 10,
          unidad: 'PZA',
          claveProdServ: '01010101',
          noIdentificacion: 'TEST-001',
          descripcion: 'Producto de prueba',
          valorUnitario: '100.00',
          importe: '1000.00',
          impuestos: {
            traslados: [
              {
                base: '1000.00',
                impuesto: '002',
                tipoFactor: 'Tasa',
                tasaOCuota: '0.160000',
                importe: '160.00'
              }
            ]
          }
        }
      ],
      impuestos: {
        totalImpuestosTrasladados: '160.00',
        traslados: [
          {
            impuesto: '002',
            tipoFactor: 'Tasa',
            tasaOCuota: '0.160000',
            importe: '160.00'
          }
        ]
      },
      complementos: {
        timbreFiscalDigital: {
          uuid: '12345678-1234-1234-1234-123456789012',
          fechaTimbrado: '2025-01-16T10:01:00',
          rfcProvCertif: 'ABCD123456789',
          selloCFD: 'sello-test-123',
          noCertificadoSAT: '0000100000040123456789'
        }
      },
      total: '1160.00',
      subtotal: '1000.00'
    };
    
    const resultado = validador.validarCFDI(cfdi);
    expect(resultado.valido).toBe(true);
  });
});



