/**
 * Validators - CFDI 4.0 IA 2025
 * Utilidades de validación comunes
 */

/**
 * Validar email
 * @param {string} email - Email a validar
 * @returns {boolean} True si es válido
 */
function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Validar RFC mexicano
 * @param {string} rfc - RFC a validar
 * @returns {boolean} True si es válido
 */
function isValidRFC(rfc) {
  if (!rfc || typeof rfc !== 'string') return false;
  const rfcRegex = /^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$/;
  return rfcRegex.test(rfc.toUpperCase());
}

/**
 * Validar UUID
 * @param {string} uuid - UUID a validar
 * @returns {boolean} True si es válido
 */
function isValidUUID(uuid) {
  if (!uuid || typeof uuid !== 'string') return false;
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

/**
 * Validar código postal mexicano
 * @param {string} codigoPostal - Código postal a validar
 * @returns {boolean} True si es válido
 */
function isValidCodigoPostal(codigoPostal) {
  if (!codigoPostal || typeof codigoPostal !== 'string') return false;
  const cpRegex = /^\d{5}$/;
  return cpRegex.test(codigoPostal);
}

/**
 * Validar fecha ISO
 * @param {string} fecha - Fecha en formato ISO
 * @returns {boolean} True si es válido
 */
function isValidFechaISO(fecha) {
  if (!fecha || typeof fecha !== 'string') return false;
  const fechaRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/;
  return fechaRegex.test(fecha) && !isNaN(Date.parse(fecha));
}

/**
 * Validar número de cuenta
 * @param {string} numero - Número de cuenta
 * @returns {boolean} True si es válido
 */
function isValidNumeroCuenta(numero) {
  if (!numero || typeof numero !== 'string') return false;
  const numRegex = /^\d{10,18}$/;
  return numRegex.test(numero);
}

/**
 * Validar CURP
 * @param {string} curp - CURP a validar
 * @returns {boolean} True si es válido
 */
function isValidCURP(curp) {
  if (!curp || typeof curp !== 'string') return false;
  const curpRegex = /^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9][0-9]$/;
  return curpRegex.test(curp.toUpperCase());
}

/**
 * Validar monto
 * @param {string|number} monto - Monto a validar
 * @returns {boolean} True si es válido
 */
function isValidMonto(monto) {
  if (monto === null || monto === undefined) return false;
  const valor = typeof monto === 'string' ? monto : monto.toString();
  const montoRegex = /^\d+(\.\d{2})?$/;
  return montoRegex.test(valor) && parseFloat(monto) > 0;
}

/**
 * Validar porcentaje
 * @param {string|number} porcentaje - Porcentaje a validar
 * @returns {boolean} True si es válido
 */
function isValidPorcentaje(porcentaje) {
  if (porcentaje === null || porcentaje === undefined) return false;
  const valor = typeof porcentaje === 'string' ? porcentaje : porcentaje.toString();
  const porcentajeRegex = /^\d+(\.\d+)?$/;
  const num = parseFloat(valor);
  return porcentajeRegex.test(valor) && num >= 0 && num <= 100;
}

/**
 * Sanitizar string
 * @param {string} str - String a sanitizar
 * @returns {string} String sanitizado
 */
function sanitizeString(str) {
  if (!str || typeof str !== 'string') return '';
  return str.trim().replace(/[<>]/g, '');
}

/**
 * Validar objeto
 * @param {any} obj - Objeto a validar
 * @returns {boolean} True si es un objeto válido
 */
function isValidObject(obj) {
  return obj !== null && typeof obj === 'object' && !Array.isArray(obj);
}

/**
 * Validar array
 * @param {any} arr - Array a validar
 * @returns {boolean} True si es un array válido
 */
function isValidArray(arr) {
  return Array.isArray(arr) && arr.length > 0;
}

module.exports = {
  isValidEmail,
  isValidRFC,
  isValidUUID,
  isValidCodigoPostal,
  isValidFechaISO,
  isValidNumeroCuenta,
  isValidCURP,
  isValidMonto,
  isValidPorcentaje,
  sanitizeString,
  isValidObject,
  isValidArray
};



