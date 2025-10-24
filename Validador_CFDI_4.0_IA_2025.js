/**
 * Validador Avanzado CFDI 4.0 - Servicios de IA México 2025
 * Versión: 2.0
 * Autor: Sistema de Validación IA
 * Fecha: 2025-01-16
 */

class ValidadorCFDI4IA {
    constructor() {
        this.errores = [];
        this.advertencias = [];
        this.validaciones = {
            rfc: /^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$/,
            fecha: /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/,
            monto: /^\d+\.\d{2}$/,
            uuid: /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
            codigoPostal: /^\d{5}$/,
            serie: /^[A-Z0-9]{1,25}$/,
            folio: /^[A-Z0-9]{1,40}$/
        };
        
        this.catalogos = {
            formasPago: ['01', '02', '03', '04', '05', '06', '08', '12', '13', '14', '15', '17', '23', '24', '25', '26', '27', '28', '29', '30', '31', '99'],
            metodosPago: ['PUE', 'PPD', 'PIP'],
            tiposComprobante: ['I', 'E', 'T', 'N', 'P'],
            monedas: ['MXN', 'USD', 'EUR', 'GBP', 'JPY'],
            usosCFDI: ['G01', 'G02', 'G03', 'I01', 'I02', 'I03', 'I04', 'I05', 'I06', 'I07', 'I08', 'D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10', 'P01'],
            regimenesFiscales: ['601', '603', '605', '606', '608', '610', '611', '612', '614', '615', '616', '620', '621', '622', '623', '624', '625', '626']
        };
    }

    /**
     * Valida un CFDI completo
     * @param {Object} cfdi - Objeto CFDI a validar
     * @returns {Object} Resultado de la validación
     */
    validarCFDI(cfdi) {
        this.errores = [];
        this.advertencias = [];

        // Validaciones principales
        this.validarEstructuraBasica(cfdi);
        this.validarEmisor(cfdi.emisor);
        this.validarReceptor(cfdi.receptor);
        this.validarConceptos(cfdi.conceptos);
        this.validarImpuestos(cfdi.impuestos);
        this.validarComplementos(cfdi.complementos);

        return {
            valido: this.errores.length === 0,
            errores: this.errores,
            advertencias: this.advertencias,
            score: this.calcularScore()
        };
    }

    /**
     * Valida la estructura básica del CFDI
     */
    validarEstructuraBasica(cfdi) {
        // Validar versión
        if (cfdi.version !== '4.0') {
            this.errores.push('La versión debe ser 4.0');
        }

        // Validar fecha
        if (!this.validaciones.fecha.test(cfdi.fecha)) {
            this.errores.push('Formato de fecha inválido. Use YYYY-MM-DDTHH:MM:SS');
        }

        // Validar serie y folio
        if (!this.validaciones.serie.test(cfdi.serie)) {
            this.errores.push('Formato de serie inválido');
        }

        if (!this.validaciones.folio.test(cfdi.folio)) {
            this.errores.push('Formato de folio inválido');
        }

        // Validar totales
        if (!this.validaciones.monto.test(cfdi.subTotal)) {
            this.errores.push('Formato de SubTotal inválido');
        }

        if (!this.validaciones.monto.test(cfdi.total)) {
            this.errores.push('Formato de Total inválido');
        }

        // Validar que Total = SubTotal + Impuestos
        const subTotal = parseFloat(cfdi.subTotal);
        const total = parseFloat(cfdi.total);
        const impuestos = cfdi.impuestos?.totalImpuestosTrasladados || 0;
        
        if (Math.abs(total - (subTotal + parseFloat(impuestos))) > 0.01) {
            this.errores.push('El Total no coincide con SubTotal + Impuestos');
        }
    }

    /**
     * Valida los datos del emisor
     */
    validarEmisor(emisor) {
        if (!emisor) {
            this.errores.push('Datos del emisor son obligatorios');
            return;
        }

        // Validar RFC
        if (!this.validaciones.rfc.test(emisor.rfc)) {
            this.errores.push('RFC del emisor inválido');
        }

        // Validar nombre
        if (!emisor.nombre || emisor.nombre.length > 254) {
            this.errores.push('Nombre del emisor inválido o excede 254 caracteres');
        }

        // Validar régimen fiscal
        if (!this.catalogos.regimenesFiscales.includes(emisor.regimenFiscal)) {
            this.errores.push('Régimen fiscal del emisor inválido');
        }
    }

    /**
     * Valida los datos del receptor
     */
    validarReceptor(receptor) {
        if (!receptor) {
            this.errores.push('Datos del receptor son obligatorios');
            return;
        }

        // Validar RFC
        if (!this.validaciones.rfc.test(receptor.rfc)) {
            this.errores.push('RFC del receptor inválido');
        }

        // Validar nombre
        if (!receptor.nombre || receptor.nombre.length > 254) {
            this.errores.push('Nombre del receptor inválido o excede 254 caracteres');
        }

        // Validar código postal
        if (!this.validaciones.codigoPostal.test(receptor.domicilioFiscalReceptor)) {
            this.errores.push('Código postal del receptor inválido');
        }

        // Validar régimen fiscal
        if (!this.catalogos.regimenesFiscales.includes(receptor.regimenFiscalReceptor)) {
            this.errores.push('Régimen fiscal del receptor inválido');
        }

        // Validar uso de CFDI
        if (!this.catalogos.usosCFDI.includes(receptor.usoCFDI)) {
            this.errores.push('Uso de CFDI inválido');
        }
    }

    /**
     * Valida los conceptos
     */
    validarConceptos(conceptos) {
        if (!conceptos || conceptos.length === 0) {
            this.errores.push('Debe incluir al menos un concepto');
            return;
        }

        conceptos.forEach((concepto, index) => {
            // Validar cantidad
            if (parseFloat(concepto.cantidad) <= 0) {
                this.errores.push(`Concepto ${index + 1}: Cantidad debe ser mayor a 0`);
            }

            // Validar valor unitario
            if (parseFloat(concepto.valorUnitario) < 0) {
                this.errores.push(`Concepto ${index + 1}: Valor unitario no puede ser negativo`);
            }

            // Validar importe
            const cantidad = parseFloat(concepto.cantidad);
            const valorUnitario = parseFloat(concepto.valorUnitario);
            const descuento = parseFloat(concepto.descuento || 0);
            const importeCalculado = (cantidad * valorUnitario) - descuento;
            const importe = parseFloat(concepto.importe);

            if (Math.abs(importe - importeCalculado) > 0.01) {
                this.errores.push(`Concepto ${index + 1}: El importe no coincide con el cálculo`);
            }

            // Validar descripción
            if (!concepto.descripcion || concepto.descripcion.length > 1000) {
                this.errores.push(`Concepto ${index + 1}: Descripción inválida o excede 1000 caracteres`);
            }
        });
    }

    /**
     * Valida los impuestos
     */
    validarImpuestos(impuestos) {
        if (!impuestos) {
            this.advertencias.push('No se encontraron impuestos');
            return;
        }

        // Validar IVA (16%)
        const iva = impuestos.traslados?.find(t => t.impuesto === '002');
        if (iva) {
            if (parseFloat(iva.tasaOCuota) !== 0.16) {
                this.errores.push('La tasa de IVA debe ser 16% (0.160000)');
            }

            const base = parseFloat(iva.base);
            const tasa = parseFloat(iva.tasaOCuota);
            const importeCalculado = base * tasa;
            const importe = parseFloat(iva.importe);

            if (Math.abs(importe - importeCalculado) > 0.01) {
                this.errores.push('El importe del IVA no coincide con el cálculo');
            }
        }
    }

    /**
     * Valida los complementos
     */
    validarComplementos(complementos) {
        if (!complementos) {
            this.advertencias.push('No se encontraron complementos');
            return;
        }

        // Validar Timbre Fiscal Digital
        const timbre = complementos.timbreFiscalDigital;
        if (!timbre) {
            this.errores.push('Timbre Fiscal Digital es obligatorio');
            return;
        }

        // Validar UUID
        if (!this.validaciones.uuid.test(timbre.uuid)) {
            this.errores.push('UUID del timbre inválido');
        }

        // Validar fecha de timbrado
        if (!this.validaciones.fecha.test(timbre.fechaTimbrado)) {
            this.errores.push('Formato de fecha de timbrado inválido');
        }

        // Validar complementos específicos
        if (complementos.pagos) {
            this.validarComplementoPagos(complementos.pagos);
        }

        if (complementos.nomina) {
            this.validarComplementoNomina(complementos.nomina);
        }
    }

    /**
     * Valida complemento de pagos
     */
    validarComplementoPagos(pagos) {
        if (!pagos.version || pagos.version !== '2.0') {
            this.errores.push('Versión del complemento de pagos debe ser 2.0');
        }

        if (!pagos.pago || pagos.pago.length === 0) {
            this.errores.push('Debe incluir al menos un pago');
        }

        pagos.pago.forEach((pago, index) => {
            if (!this.validaciones.fecha.test(pago.fechaPago)) {
                this.errores.push(`Pago ${index + 1}: Formato de fecha inválido`);
            }

            if (!this.validaciones.monto.test(pago.monto)) {
                this.errores.push(`Pago ${index + 1}: Formato de monto inválido`);
            }
        });
    }

    /**
     * Valida complemento de nómina
     */
    validarComplementoNomina(nomina) {
        if (!nomina.version || nomina.version !== '1.2') {
            this.errores.push('Versión del complemento de nómina debe ser 1.2');
        }

        if (!nomina.numEmpleado) {
            this.errores.push('Número de empleado es obligatorio');
        }

        if (!nomina.curp || !/^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9]{2}$/.test(nomina.curp)) {
            this.errores.push('CURP inválida');
        }

        if (!nomina.salarioBaseCotApor || parseFloat(nomina.salarioBaseCotApor) <= 0) {
            this.errores.push('Salario base de cotización debe ser mayor a 0');
        }
    }

    /**
     * Calcula el score de validación
     */
    calcularScore() {
        const totalValidaciones = 50; // Número total de validaciones
        const errores = this.errores.length;
        const advertencias = this.advertencias.length;
        
        const score = Math.max(0, 100 - (errores * 10) - (advertencias * 2));
        return Math.round(score);
    }

    /**
     * Genera reporte de validación
     */
    generarReporte() {
        return {
            timestamp: new Date().toISOString(),
            version: '2.0',
            resultado: {
                valido: this.errores.length === 0,
                score: this.calcularScore(),
                errores: this.errores.length,
                advertencias: this.advertencias.length
            },
            detalles: {
                errores: this.errores,
                advertencias: this.advertencias
            },
            recomendaciones: this.generarRecomendaciones()
        };
    }

    /**
     * Genera recomendaciones basadas en los errores
     */
    generarRecomendaciones() {
        const recomendaciones = [];

        if (this.errores.some(e => e.includes('RFC'))) {
            recomendaciones.push('Verificar que los RFC sean válidos según las reglas del SAT');
        }

        if (this.errores.some(e => e.includes('fecha'))) {
            recomendaciones.push('Usar formato ISO 8601 para todas las fechas: YYYY-MM-DDTHH:MM:SS');
        }

        if (this.errores.some(e => e.includes('monto'))) {
            recomendaciones.push('Asegurar que todos los montos tengan exactamente 2 decimales');
        }

        if (this.errores.some(e => e.includes('UUID'))) {
            recomendaciones.push('Verificar que el UUID del timbre sea único y válido');
        }

        return recomendaciones;
    }
}

// Ejemplo de uso
const validador = new ValidadorCFDI4IA();

// CFDI de ejemplo para validar
const cfdiEjemplo = {
    version: '4.0',
    serie: 'AI-ADV',
    folio: '2025-001',
    fecha: '2025-01-16T14:30:00',
    subTotal: '125000.00',
    total: '145000.00',
    emisor: {
        rfc: 'AI789123TEC',
        nombre: 'INTELIGENCIA ARTIFICIAL AVANZADA MEXICO S.A. DE C.V.',
        regimenFiscal: '601'
    },
    receptor: {
        rfc: 'TEC456789ABC',
        nombre: 'TECHNOLOGY ENTERPRISE MÉXICO S.A. DE C.V.',
        domicilioFiscalReceptor: '01000',
        regimenFiscalReceptor: '601',
        usoCFDI: 'G01'
    },
    conceptos: [
        {
            cantidad: '1',
            valorUnitario: '50000.00',
            descuento: '5000.00',
            importe: '45000.00',
            descripcion: 'Plataforma Integral de Inteligencia Artificial Avanzada'
        }
    ],
    impuestos: {
        totalImpuestosTrasladados: '20000.00',
        traslados: [
            {
                impuesto: '002',
                tasaOCuota: '0.160000',
                base: '125000.00',
                importe: '20000.00'
            }
        ]
    },
    complementos: {
        timbreFiscalDigital: {
            uuid: '12345678-1234-1234-1234-123456789012',
            fechaTimbrado: '2025-01-16T14:35:00'
        }
    }
};

// Validar CFDI
const resultado = validador.validarCFDI(cfdiEjemplo);
console.log('Resultado de validación:', resultado);

// Generar reporte
const reporte = validador.generarReporte();
console.log('Reporte completo:', reporte);

module.exports = ValidadorCFDI4IA;



