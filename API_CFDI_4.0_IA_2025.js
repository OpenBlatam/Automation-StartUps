/**
 * API REST Completa CFDI 4.0 - Servicios de IA México 2025
 * Versión: 3.0
 * Autor: Sistema de Facturación IA Avanzada
 * Fecha: 2025-01-16
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const xml2js = require('xml2js');
const validator = require('./Validador_CFDI_4.0_IA_2025');

class APICFDI4IA {
    constructor() {
        this.app = express();
        this.port = process.env.PORT || 3000;
        this.secretKey = process.env.JWT_SECRET || 'cfdi-ia-2025-secret-key';
        this.cfdiDatabase = new Map();
        this.users = new Map();
        this.stats = {
            totalCFDI: 0,
            totalFacturado: 0,
            errores: 0,
            usuariosActivos: 0
        };
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupSecurity();
    }

    setupMiddleware() {
        // Seguridad
        this.app.use(helmet());
        this.app.use(cors({
            origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
            credentials: true
        }));

        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutos
            max: 100, // máximo 100 requests por IP
            message: 'Demasiadas solicitudes desde esta IP'
        });
        this.app.use('/api/', limiter);

        // Parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

        // Logging
        this.app.use((req, res, next) => {
            console.log(`${new Date().toISOString()} - ${req.method} ${req.path} - IP: ${req.ip}`);
            next();
        });
    }

    setupSecurity() {
        // Autenticación JWT
        this.app.use('/api/protected', (req, res, next) => {
            const token = req.headers.authorization?.split(' ')[1];
            if (!token) {
                return res.status(401).json({ error: 'Token de acceso requerido' });
            }

            try {
                const decoded = jwt.verify(token, this.secretKey);
                req.user = decoded;
                next();
            } catch (error) {
                return res.status(401).json({ error: 'Token inválido' });
            }
        });
    }

    setupRoutes() {
        // Rutas públicas
        this.app.get('/api/health', this.healthCheck.bind(this));
        this.app.post('/api/auth/login', this.login.bind(this));
        this.app.post('/api/auth/register', this.register.bind(this));
        this.app.get('/api/cfdi/templates', this.getTemplates.bind(this));
        this.app.get('/api/cfdi/validate/:uuid', this.validateCFDI.bind(this));

        // Rutas protegidas
        this.app.post('/api/protected/cfdi/generate', this.generateCFDI.bind(this));
        this.app.get('/api/protected/cfdi/list', this.listCFDI.bind(this));
        this.app.get('/api/protected/cfdi/:uuid', this.getCFDI.bind(this));
        this.app.put('/api/protected/cfdi/:uuid', this.updateCFDI.bind(this));
        this.app.delete('/api/protected/cfdi/:uuid', this.deleteCFDI.bind(this));
        this.app.post('/api/protected/cfdi/bulk', this.bulkGenerate.bind(this));
        this.app.get('/api/protected/stats', this.getStats.bind(this));
        this.app.get('/api/protected/dashboard', this.getDashboard.bind(this));
        this.app.post('/api/protected/cfdi/export', this.exportCFDI.bind(this));
        this.app.post('/api/protected/cfdi/import', this.importCFDI.bind(this));
    }

    // Métodos de autenticación
    async login(req, res) {
        try {
            const { email, password } = req.body;
            const user = this.users.get(email);
            
            if (!user || !await bcrypt.compare(password, user.password)) {
                return res.status(401).json({ error: 'Credenciales inválidas' });
            }

            const token = jwt.sign(
                { email: user.email, role: user.role },
                this.secretKey,
                { expiresIn: '24h' }
            );

            res.json({
                success: true,
                token,
                user: {
                    email: user.email,
                    role: user.role,
                    name: user.name
                }
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async register(req, res) {
        try {
            const { email, password, name, role = 'user' } = req.body;
            
            if (this.users.has(email)) {
                return res.status(400).json({ error: 'Usuario ya existe' });
            }

            const hashedPassword = await bcrypt.hash(password, 10);
            this.users.set(email, {
                email,
                password: hashedPassword,
                name,
                role,
                createdAt: new Date()
            });

            res.json({ success: true, message: 'Usuario registrado exitosamente' });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    // Métodos de CFDI
    async generateCFDI(req, res) {
        try {
            const { servicio, cliente, monto, descuentos = 0 } = req.body;
            
            // Validar datos de entrada
            if (!servicio || !cliente || !monto) {
                return res.status(400).json({ error: 'Datos incompletos' });
            }

            // Generar CFDI
            const cfdi = this.createCFDI(servicio, cliente, monto, descuentos);
            
            // Validar CFDI
            const validador = new validator.ValidadorCFDI4IA();
            const validacion = validador.validarCFDI(cfdi);
            
            if (!validacion.valido) {
                return res.status(400).json({ 
                    error: 'CFDI inválido', 
                    detalles: validacion.errores 
                });
            }

            // Timbrar CFDI
            const cfdiTimbrado = await this.timbrarCFDI(cfdi);
            
            // Guardar en base de datos
            const uuid = cfdiTimbrado.complementos.timbreFiscalDigital.uuid;
            this.cfdiDatabase.set(uuid, {
                ...cfdiTimbrado,
                usuario: req.user.email,
                fechaCreacion: new Date(),
                status: 'activo'
            });

            // Actualizar estadísticas
            this.stats.totalCFDI++;
            this.stats.totalFacturado += parseFloat(monto);

            res.json({
                success: true,
                cfdi: cfdiTimbrado,
                uuid,
                validacion: {
                    score: validacion.score,
                    advertencias: validacion.advertencias
                }
            });

        } catch (error) {
            this.stats.errores++;
            res.status(500).json({ error: error.message });
        }
    }

    createCFDI(servicio, cliente, monto, descuentos) {
        const folio = this.generateFolio();
        const fecha = new Date().toISOString();
        const subTotal = monto - descuentos;
        const iva = subTotal * 0.16;
        const total = subTotal + iva;

        return {
            version: '4.0',
            serie: servicio.serie || 'AI',
            folio,
            fecha,
            sello: '[SELLO_DIGITAL]',
            formaPago: '03',
            noCertificado: '30001000000400002434',
            certificado: '[CERTIFICADO_DIGITAL]',
            subTotal: subTotal.toFixed(2),
            moneda: 'MXN',
            total: total.toFixed(2),
            tipoDeComprobante: 'I',
            exportacion: '01',
            metodoPago: 'PUE',
            lugarExpedicion: '01000',
            confirmacion: this.generateConfirmacion(),
            emisor: {
                rfc: 'AI789123TEC',
                nombre: 'INTELIGENCIA ARTIFICIAL MEXICO S.A. DE C.V.',
                regimenFiscal: '601'
            },
            receptor: {
                rfc: cliente.rfc,
                nombre: cliente.nombre,
                domicilioFiscalReceptor: cliente.codigoPostal,
                regimenFiscalReceptor: cliente.regimenFiscal,
                usoCFDI: cliente.usoCFDI
            },
            conceptos: [{
                claveProdServ: '84111506',
                noIdentificacion: servicio.codigo,
                cantidad: '1',
                claveUnidad: 'E48',
                unidad: 'Servicio',
                descripcion: servicio.descripcion,
                valorUnitario: monto.toFixed(2),
                importe: monto.toFixed(2),
                descuento: descuentos.toFixed(2),
                objetoImp: '02',
                impuestos: {
                    traslados: [{
                        base: subTotal.toFixed(2),
                        impuesto: '002',
                        tipoFactor: 'Tasa',
                        tasaOCuota: '0.160000',
                        importe: iva.toFixed(2)
                    }]
                }
            }],
            impuestos: {
                totalImpuestosTrasladados: iva.toFixed(2),
                traslados: [{
                    impuesto: '002',
                    tipoFactor: 'Tasa',
                    tasaOCuota: '0.160000',
                    importe: iva.toFixed(2)
                }]
            }
        };
    }

    async timbrarCFDI(cfdi) {
        // Simulación de timbrado
        const uuid = this.generateUUID();
        const fechaTimbrado = new Date().toISOString();
        
        return {
            ...cfdi,
            complementos: {
                timbreFiscalDigital: {
                    version: '1.1',
                    uuid,
                    fechaTimbrado,
                    rfcProvCertif: 'AI789123TEC',
                    selloCFD: '[SELLO_CFD]',
                    noCertificadoSAT: '30001000000400002434',
                    selloSAT: '[SELLO_SAT]'
                }
            }
        };
    }

    async bulkGenerate(req, res) {
        try {
            const { servicios } = req.body;
            const resultados = [];

            for (const servicio of servicios) {
                try {
                    const cfdi = this.createCFDI(servicio.servicio, servicio.cliente, servicio.monto, servicio.descuentos || 0);
                    const cfdiTimbrado = await this.timbrarCFDI(cfdi);
                    
                    const uuid = cfdiTimbrado.complementos.timbreFiscalDigital.uuid;
                    this.cfdiDatabase.set(uuid, {
                        ...cfdiTimbrado,
                        usuario: req.user.email,
                        fechaCreacion: new Date(),
                        status: 'activo'
                    });

                    resultados.push({
                        folio: cfdi.folio,
                        uuid,
                        status: 'success',
                        total: cfdi.total
                    });

                    this.stats.totalCFDI++;
                    this.stats.totalFacturado += parseFloat(cfdi.total);

                } catch (error) {
                    resultados.push({
                        folio: servicio.folio,
                        error: error.message,
                        status: 'error'
                    });
                    this.stats.errores++;
                }
            }

            res.json({
                success: true,
                procesados: resultados.length,
                exitosos: resultados.filter(r => r.status === 'success').length,
                errores: resultados.filter(r => r.status === 'error').length,
                resultados
            });

        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async getDashboard(req, res) {
        try {
            const cfdiUsuario = Array.from(this.cfdiDatabase.values())
                .filter(cfdi => cfdi.usuario === req.user.email);

            const dashboard = {
                resumen: {
                    totalCFDI: cfdiUsuario.length,
                    totalFacturado: cfdiUsuario.reduce((sum, cfdi) => sum + parseFloat(cfdi.total), 0),
                    promedioCFDI: cfdiUsuario.length > 0 ? 
                        cfdiUsuario.reduce((sum, cfdi) => sum + parseFloat(cfdi.total), 0) / cfdiUsuario.length : 0
                },
                tendencias: {
                    ultimos7Dias: this.getTendencias(cfdiUsuario, 7),
                    ultimos30Dias: this.getTendencias(cfdiUsuario, 30)
                },
                servicios: this.getServiciosPopulares(cfdiUsuario),
                validaciones: {
                    scorePromedio: this.getScorePromedio(cfdiUsuario),
                    erroresComunes: this.getErroresComunes(cfdiUsuario)
                }
            };

            res.json(dashboard);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    // Métodos auxiliares
    generateFolio() {
        return `CFDI-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    generateUUID() {
        return crypto.randomUUID();
    }

    generateConfirmacion() {
        return Math.random().toString(36).substr(2, 8).toUpperCase();
    }

    getTendencias(cfdiList, dias) {
        const fechaLimite = new Date();
        fechaLimite.setDate(fechaLimite.getDate() - dias);
        
        return cfdiList
            .filter(cfdi => new Date(cfdi.fechaCreacion) >= fechaLimite)
            .reduce((acc, cfdi) => {
                const fecha = new Date(cfdi.fechaCreacion).toISOString().split('T')[0];
                acc[fecha] = (acc[fecha] || 0) + 1;
                return acc;
            }, {});
    }

    getServiciosPopulares(cfdiList) {
        const servicios = {};
        cfdiList.forEach(cfdi => {
            const servicio = cfdi.conceptos[0].descripcion;
            servicios[servicio] = (servicios[servicio] || 0) + 1;
        });
        
        return Object.entries(servicios)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([servicio, count]) => ({ servicio, count }));
    }

    getScorePromedio(cfdiList) {
        // Simulación de score promedio
        return Math.floor(Math.random() * 20) + 80;
    }

    getErroresComunes(cfdiList) {
        return [
            { error: 'RFC inválido', count: Math.floor(Math.random() * 5) },
            { error: 'Fecha incorrecta', count: Math.floor(Math.random() * 3) },
            { error: 'Monto con decimales incorrectos', count: Math.floor(Math.random() * 2) }
        ];
    }

    // Métodos de utilidad
    healthCheck(req, res) {
        res.json({
            status: 'OK',
            timestamp: new Date().toISOString(),
            version: '3.0',
            uptime: process.uptime(),
            stats: this.stats
        });
    }

    async getTemplates(req, res) {
        const templates = [
            {
                id: 'medicina',
                nombre: 'Medicina Personalizada',
                descripcion: 'Servicios de IA en medicina y salud',
                precioBase: 50000,
                serie: 'MED'
            },
            {
                id: 'fintech',
                nombre: 'Fintech & Blockchain',
                descripcion: 'Servicios financieros con IA',
                precioBase: 40000,
                serie: 'FINT'
            },
            {
                id: 'agricultura',
                nombre: 'Agricultura Inteligente',
                descripcion: 'IA para agricultura de precisión',
                precioBase: 30000,
                serie: 'AGRO'
            }
        ];

        res.json(templates);
    }

    async validateCFDI(req, res) {
        try {
            const { uuid } = req.params;
            const cfdi = this.cfdiDatabase.get(uuid);
            
            if (!cfdi) {
                return res.status(404).json({ error: 'CFDI no encontrado' });
            }

            const validador = new validator.ValidadorCFDI4IA();
            const validacion = validador.validarCFDI(cfdi);
            
            res.json({
                uuid,
                valido: validacion.valido,
                score: validacion.score,
                errores: validacion.errores,
                advertencias: validacion.advertencias
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async listCFDI(req, res) {
        try {
            const { page = 1, limit = 10, search = '' } = req.query;
            const cfdiUsuario = Array.from(this.cfdiDatabase.values())
                .filter(cfdi => cfdi.usuario === req.user.email);

            let filteredCFDI = cfdiUsuario;
            if (search) {
                filteredCFDI = cfdiUsuario.filter(cfdi => 
                    cfdi.receptor.nombre.toLowerCase().includes(search.toLowerCase()) ||
                    cfdi.conceptos[0].descripcion.toLowerCase().includes(search.toLowerCase())
                );
            }

            const startIndex = (page - 1) * limit;
            const endIndex = startIndex + parseInt(limit);
            const paginatedCFDI = filteredCFDI.slice(startIndex, endIndex);

            res.json({
                cfdi: paginatedCFDI,
                pagination: {
                    page: parseInt(page),
                    limit: parseInt(limit),
                    total: filteredCFDI.length,
                    pages: Math.ceil(filteredCFDI.length / limit)
                }
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async getCFDI(req, res) {
        try {
            const { uuid } = req.params;
            const cfdi = this.cfdiDatabase.get(uuid);
            
            if (!cfdi) {
                return res.status(404).json({ error: 'CFDI no encontrado' });
            }

            if (cfdi.usuario !== req.user.email) {
                return res.status(403).json({ error: 'Acceso denegado' });
            }

            res.json(cfdi);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async updateCFDI(req, res) {
        try {
            const { uuid } = req.params;
            const updates = req.body;
            
            const cfdi = this.cfdiDatabase.get(uuid);
            if (!cfdi) {
                return res.status(404).json({ error: 'CFDI no encontrado' });
            }

            if (cfdi.usuario !== req.user.email) {
                return res.status(403).json({ error: 'Acceso denegado' });
            }

            const updatedCFDI = { ...cfdi, ...updates, fechaModificacion: new Date() };
            this.cfdiDatabase.set(uuid, updatedCFDI);

            res.json(updatedCFDI);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async deleteCFDI(req, res) {
        try {
            const { uuid } = req.params;
            const cfdi = this.cfdiDatabase.get(uuid);
            
            if (!cfdi) {
                return res.status(404).json({ error: 'CFDI no encontrado' });
            }

            if (cfdi.usuario !== req.user.email) {
                return res.status(403).json({ error: 'Acceso denegado' });
            }

            this.cfdiDatabase.delete(uuid);
            res.json({ success: true, message: 'CFDI eliminado exitosamente' });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async getStats(req, res) {
        try {
            const cfdiUsuario = Array.from(this.cfdiDatabase.values())
                .filter(cfdi => cfdi.usuario === req.user.email);

            const stats = {
                usuario: {
                    totalCFDI: cfdiUsuario.length,
                    totalFacturado: cfdiUsuario.reduce((sum, cfdi) => sum + parseFloat(cfdi.total), 0),
                    promedioCFDI: cfdiUsuario.length > 0 ? 
                        cfdiUsuario.reduce((sum, cfdi) => sum + parseFloat(cfdi.total), 0) / cfdiUsuario.length : 0
                },
                global: this.stats
            };

            res.json(stats);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async exportCFDI(req, res) {
        try {
            const { format = 'json', uuids = [] } = req.body;
            const cfdiUsuario = Array.from(this.cfdiDatabase.values())
                .filter(cfdi => cfdi.usuario === req.user.email);

            let cfdiToExport = cfdiUsuario;
            if (uuids.length > 0) {
                cfdiToExport = cfdiUsuario.filter(cfdi => uuids.includes(cfdi.complementos.timbreFiscalDigital.uuid));
            }

            if (format === 'xml') {
                const builder = new xml2js.Builder();
                const xml = builder.buildObject({ cfdi: cfdiToExport });
                res.setHeader('Content-Type', 'application/xml');
                res.setHeader('Content-Disposition', 'attachment; filename="cfdi-export.xml"');
                res.send(xml);
            } else {
                res.setHeader('Content-Type', 'application/json');
                res.setHeader('Content-Disposition', 'attachment; filename="cfdi-export.json"');
                res.json(cfdiToExport);
            }
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    async importCFDI(req, res) {
        try {
            const { cfdi } = req.body;
            const resultados = [];

            for (const cfdiItem of cfdi) {
                try {
                    const validador = new validator.ValidadorCFDI4IA();
                    const validacion = validador.validarCFDI(cfdiItem);
                    
                    if (validacion.valido) {
                        const uuid = cfdiItem.complementos?.timbreFiscalDigital?.uuid || this.generateUUID();
                        this.cfdiDatabase.set(uuid, {
                            ...cfdiItem,
                            usuario: req.user.email,
                            fechaCreacion: new Date(),
                            status: 'importado'
                        });
                        
                        resultados.push({ uuid, status: 'success' });
                    } else {
                        resultados.push({ 
                            folio: cfdiItem.folio, 
                            status: 'error', 
                            errores: validacion.errores 
                        });
                    }
                } catch (error) {
                    resultados.push({ 
                        folio: cfdiItem.folio, 
                        status: 'error', 
                        error: error.message 
                    });
                }
            }

            res.json({
                success: true,
                procesados: resultados.length,
                exitosos: resultados.filter(r => r.status === 'success').length,
                errores: resultados.filter(r => r.status === 'error').length,
                resultados
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }

    start() {
        this.app.listen(this.port, () => {
            console.log(`🚀 API CFDI 4.0 IA iniciada en puerto ${this.port}`);
            console.log(`📊 Estadísticas: ${JSON.stringify(this.stats)}`);
            console.log(`🔐 Autenticación JWT habilitada`);
            console.log(`🛡️  Seguridad avanzada activada`);
        });
    }
}

// Inicializar API
const api = new APICFDI4IA();
api.start();

module.exports = APICFDI4IA;

