/**
 * Helpers - CFDI 4.0 IA 2025
 * Utilidades y funciones auxiliares
 */

/**
 * Generar UUID v4
 * @returns {string} UUID
 */
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Generar timestamp
 * @returns {string} Timestamp en formato ISO
 */
function generateTimestamp() {
  return new Date().toISOString();
}

/**
 * Formatear fecha
 * @param {Date} date - Fecha
 * @returns {string} Fecha formateada
 */
function formatDate(date) {
  return date.toISOString().split('T')[0];
}

/**
 * Formatear moneda
 * @param {number} amount - Monto
 * @returns {string} Monto formateado
 */
function formatCurrency(amount) {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN'
  }).format(amount);
}

/**
 * Calcular IVA
 * @param {number} subtotal - Subtotal
 * @param {number} rate - Tasa de IVA
 * @returns {number} IVA calculado
 */
function calculateIVA(subtotal, rate = 0.16) {
  return subtotal * rate;
}

/**
 * Redondear a 2 decimales
 * @param {number} num - Número
 * @returns {number} Número redondeado
 */
function roundToTwoDecimals(num) {
  return Math.round(num * 100) / 100;
}

/**
 * Delay async
 * @param {number} ms - Milisegundos
 * @returns {Promise} Promise
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry con backoff exponencial
 * @param {Function} fn - Función a ejecutar
 * @param {number} retries - Número de intentos
 * @returns {Promise} Resultado
 */
async function retryWithBackoff(fn, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === retries - 1) throw error;
      await delay(Math.pow(2, i) * 1000);
    }
  }
}

/**
 * Log con timestamp
 * @param {string} message - Mensaje
 * @param {string} level - Nivel (info, warn, error)
 */
function log(message, level = 'info') {
  const timestamp = generateTimestamp();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  
  switch (level) {
    case 'error':
      console.error(logMessage);
      break;
    case 'warn':
      console.warn(logMessage);
      break;
    default:
      console.log(logMessage);
  }
}

/**
 * Clonar objeto
 * @param {any} obj - Objeto
 * @returns {any} Clon del objeto
 */
function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Merge objetos
 * @param {any} target - Objeto objetivo
 * @param {any} source - Objeto fuente
 * @returns {any} Objeto mergeado
 */
function merge(target, source) {
  return { ...target, ...source };
}

/**
 * Capitalizar string
 * @param {string} str - String
 * @returns {string} String capitalizado
 */
function capitalize(str) {
  if (!str || typeof str !== 'string') return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Truncar string
 * @param {string} str - String
 * @param {number} maxLength - Longitud máxima
 * @returns {string} String truncado
 */
function truncate(str, maxLength = 50) {
  if (!str || typeof str !== 'string') return '';
  return str.length > maxLength ? str.substring(0, maxLength) + '...' : str;
}

module.exports = {
  generateUUID,
  generateTimestamp,
  formatDate,
  formatCurrency,
  calculateIVA,
  roundToTwoDecimals,
  delay,
  retryWithBackoff,
  log,
  clone,
  merge,
  capitalize,
  truncate
};



