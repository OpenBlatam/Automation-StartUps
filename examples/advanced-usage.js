/**
 * Advanced Usage Example - CFDI 4.0 IA 2025
 * Ejemplos avanzados de uso
 */

const AutomatizacionIACFDI = require('../Automatizacion_IA_CFDI_2025');
const IntegracionERPCFDI = require('../Integracion_ERP_CFDI_2025');

// ============================================
// EJEMPLO 1: Predicción de errores con IA
// ============================================
async function predecirErrores() {
  console.log('🤖 Prediciendo errores con IA...');
  
  const automatizacion = new AutomatizacionIACFDI();
  
  const cfdi = {
    emisor: { rfc: 'ABC123456789', nombre: 'Test' },
    receptor: { rfc: 'XYZ987654321', nombre: 'Test' },
    conceptos: [{ cantidad: 1, descripcion: 'Test' }]
  };
  
  const prediccion = await automatizacion.predecirErrores(cfdi);
  
  console.log('📊 Predicción:');
  console.log('Probabilidad de error:', prediccion.probabilidadError);
  console.log('Errores predichos:', prediccion.erroresPredichos);
  console.log('Recomendaciones:', prediccion.recomendaciones);
}

// ============================================
// EJEMPLO 2: Optimización automática
// ============================================
async function optimizarCFDI() {
  console.log('⚡ Optimizando CFDI...');
  
  const automatizacion = new AutomatizacionIACFDI();
  
  const cfdi = {
    emisor: { rfc: 'ABC123456789' },
    receptor: { rfc: 'XYZ987654321' },
    conceptos: [{ cantidad: 10, valorUnitario: '100.00' }],
    total: '1160.00'
  };
  
  const optimizado = await automatizacion.optimizarCFDI(cfdi);
  
  console.log('✅ Optimización completada:');
  console.log('Score antes:', optimizado.scoreAntes);
  console.log('Score después:', optimizado.scoreDespues);
  console.log('Ahorro estimado:', optimizado.ahorroEstimado);
}

// ============================================
// EJEMPLO 3: Integración con ERP
// ============================================
async function integrarConERP() {
  console.log('🔗 Integrando con ERP...');
  
  const integracion = new IntegracionERPCFDI();
  
  const datosERP = {
    // Datos del ERP
    cliente: 'ABC123',
    productos: [
      { codigo: 'PROD001', cantidad: 5, precio: 100 }
    ]
  };
  
  const resultado = await integracion.integrarConERP('sap', datosERP);
  
  console.log('✅ Integración completada:');
  console.log(resultado);
}

// ============================================
// EJEMPLO 4: Generación masiva
// ============================================
async function generarMasivo() {
  console.log('📦 Generando CFDI masivo...');
  
  const automatizacion = new AutomatizacionIACFDI();
  
  const requisitos = [
    { emisor: 'ABC123', receptor: 'XYZ789' },
    { emisor: 'DEF456', receptor: 'UVW012' },
    { emisor: 'GHI789', receptor: 'RST345' }
  ];
  
  const resultados = await Promise.all(
    requisitos.map(req => automatizacion.generarCFDIAutomatico(req))
  );
  
  console.log('✅ Generación masiva completada:');
  console.log('Total generados:', resultados.length);
  console.log('Exitosos:', resultados.filter(r => r.cfdi).length);
}

// ============================================
// EJEMPLO 5: Sincronización bidireccional
// ============================================
async function sincronizarBidireccional() {
  console.log('🔄 Sincronizando bidireccionalmente...');
  
  const integracion = new IntegracionERPCFDI();
  
  const configuracion = {
    frecuencia: 'diaria',
    sincronizarFacturas: true,
    sincronizarClientes: true
  };
  
  const resultado = await integracion.sincronizarBidireccional('oracle', configuracion);
  
  console.log('✅ Sincronización completada:');
  console.log('Datos procesados:', resultado.datosProcesados);
  console.log('Errores:', resultado.errores);
}

// ============================================
// EJECUTAR
// ============================================
async function main() {
  console.log('🎯 Ejemplos avanzados - CFDI 4.0 IA 2025\n');
  
  try {
    await predecirErrores();
    console.log('\n---\n');
    
    await optimizarCFDI();
    console.log('\n---\n');
    
    await integrarConERP();
    console.log('\n---\n');
    
    await generarMasivo();
    console.log('\n---\n');
    
    await sincronizarBidireccional();
    
    console.log('\n✅ Todos los ejemplos completados');
  } catch (error) {
    console.error('❌ Error en ejemplos:', error);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  predecirErrores,
  optimizarCFDI,
  integrarConERP,
  generarMasivo,
  sincronizarBidireccional
};



