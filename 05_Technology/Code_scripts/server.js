/**
 * Server Entry Point - CFDI 4.0 IA 2025
 * Versión: 1.0
 * Autor: Sistema de Facturación IA Avanzada
 * Fecha: 2025-01-16
 */

require('dotenv').config();
const APICFDI4IA = require('./API_CFDI_4.0_IA_2025');

// Inicializar servidor
const server = new APICFDI4IA();

// Iniciar servidor
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`🚀 Servidor CFDI 4.0 IA iniciado en puerto ${PORT}`);
    console.log(`📊 Salud: http://localhost:${PORT}/api/health`);
    console.log(`📚 Documentación: http://localhost:${PORT}/api/docs`);
    console.log(`🔐 Entorno: ${process.env.NODE_ENV || 'development'}`);
});

// Manejo de errores no capturados
process.on('unhandledRejection', (err) => {
    console.error('❌ Error no capturado:', err);
});

process.on('uncaughtException', (err) => {
    console.error('❌ Excepción no capturada:', err);
    process.exit(1);
});



