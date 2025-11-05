/**
 * Basic Usage Example - CFDI 4.0 IA 2025
 * Ejemplo básico de uso de la API
 */

const APICFDI4IA = require('../API_CFDI_4.0_IA_2025');
const ValidadorCFDI4IA = require('../Validador_CFDI_4.0_IA_2025');

// ============================================
// EJEMPLO 1: Iniciar servidor
// ============================================
async function iniciarServidor() {
  console.log('🚀 Iniciando servidor...');
  
  const api = new APICFDI4IA();
  api.listen(3000, () => {
    console.log('✅ Servidor iniciado en puerto 3000');
    console.log('📊 Health: http://localhost:3000/api/health');
  });
}

// ============================================
// EJEMPLO 2: Validar CFDI
// ============================================
function validarCFDI() {
  console.log('📋 Validando CFDI...');
  
  const validador = new ValidadorCFDI4IA();
  
  const cfdi = {
    emisor: {
      rfc: 'ABC123456789',
      nombre: 'Empresa Demo S.A. de C.V.',
      regimenFiscal: '601'
    },
    receptor: {
      rfc: 'XYZ987654321',
      nombre: 'Cliente Demo Inc.',
      usoCFDI: 'G01'
    },
    conceptos: [
      {
        cantidad: 1,
        unidad: 'PZA',
        descripcion: 'Producto de prueba',
        valorUnitario: '100.00',
        importe: '100.00'
      }
    ],
    total: '116.00'
  };
  
  const resultado = validador.validarCFDI(cfdi);
  
  if (resultado.valido) {
    console.log('✅ CFDI válido');
  } else {
    console.log('❌ CFDI inválido:');
    console.log(resultado.errores);
  }
}

// ============================================
// EJEMPLO 3: Generar CFDI
// ============================================
async function generarCFDI() {
  console.log('📝 Generando CFDI...');
  
  const cfdiData = {
    emisor: {
      rfc: 'ABC123456789',
      nombre: 'Mi Empresa S.A. de C.V.',
      regimenFiscal: '601',
      domicilioFiscal: {
        codigoPostal: '01234'
      }
    },
    receptor: {
      rfc: 'XYZ987654321',
      nombre: 'Cliente Ejemplo Inc.',
      usoCFDI: 'G01',
      domicilio: {
        codigoPostal: '56789'
      }
    },
    conceptos: [
      {
        cantidad: 2,
        unidad: 'PZA',
        descripcion: 'Producto ejemplo',
        valorUnitario: '50.00',
        importe: '100.00'
      }
    ],
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
    },
    total: '116.00',
    subtotal: '100.00'
  };
  
  // Simular generación
  console.log('✅ CFDI generado:');
  console.log(JSON.stringify(cfdiData, null, 2));
}

// ============================================
// EJEMPLO 4: Consultar estadísticas
// ============================================
async function consultarEstadisticas() {
  console.log('📊 Consultando estadísticas...');
  
  // Simular consulta
  const stats = {
    totalCFDI: 150,
    totalFacturado: 1500000,
    errores: 5,
    usuariosActivos: 25
  };
  
  console.log('✅ Estadísticas:');
  console.log(stats);
}

// ============================================
// EJEMPLO 5: Exportar CFDI
// ============================================
async function exportarCFDI() {
  console.log('📤 Exportando CFDI...');
  
  const cfdiList = [
    { uuid: '123', total: '1000.00' },
    { uuid: '456', total: '2000.00' },
    { uuid: '789', total: '3000.00' }
  ];
  
  console.log('✅ CFDI exportados:');
  console.log(JSON.stringify(cfdiList, null, 2));
}

// ============================================
// EJECUTAR EJEMPLOS
// ============================================
async function main() {
  console.log('🎯 Ejemplos de uso - CFDI 4.0 IA 2025\n');
  
  // Ejemplo 1: Validar
  validarCFDI();
  console.log('\n---\n');
  
  // Ejemplo 2: Generar
  await generarCFDI();
  console.log('\n---\n');
  
  // Ejemplo 3: Estadísticas
  await consultarEstadisticas();
  console.log('\n---\n');
  
  // Ejemplo 4: Exportar
  await exportarCFDI();
  
  console.log('\n✅ Ejemplos completados');
}

// Ejecutar si es script principal
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  iniciarServidor,
  validarCFDI,
  generarCFDI,
  consultarEstadisticas,
  exportarCFDI
};



