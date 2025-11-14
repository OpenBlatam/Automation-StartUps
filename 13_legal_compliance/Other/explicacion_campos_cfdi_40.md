---
title: "Explicacion Campos Cfdi 40"
category: "13_legal_compliance"
tags: []
created: "2025-10-29"
path: "13_legal_compliance/Other/explicacion_campos_cfdi_40.md"
---

# Explicación de Campos Obligatorios CFDI 4.0 - México 2025

## Tabla de Campos Obligatorios del CFDI 4.0

| Campo | Ubicación | Descripción | Ejemplo | Obligatorio |
|-------|-----------|-------------|---------|-------------|
| **Version** | Raíz | Versión del CFDI (siempre 4.0) | "4.0" | ✅ |
| **Serie** | Raíz | Serie del comprobante fiscal | "CIA", "SIA", "BULK" | ✅ |
| **Folio** | Raíz | Número consecutivo del comprobante | "2025-001" | ✅ |
| **Fecha** | Raíz | Fecha y hora de expedición (ISO 8601) | "2025-01-15T10:30:00" | ✅ |
| **Sello** | Raíz | Sello digital del emisor | "[SELLO_DIGITAL]" | ✅ |
| **FormaPago** | Raíz | Forma de pago (catálogo SAT) | "03" (Transferencia) | ✅ |
| **NoCertificado** | Raíz | Número de certificado del emisor | "30001000000400002434" | ✅ |
| **Certificado** | Raíz | Certificado digital del emisor | "[CERTIFICADO_DIGITAL]" | ✅ |
| **SubTotal** | Raíz | Suma de importes antes de impuestos | "5000.00" | ✅ |
| **Moneda** | Raíz | Código de moneda (ISO 4217) | "MXN" | ✅ |
| **Total** | Raíz | Importe total del comprobante | "5800.00" | ✅ |
| **TipoDeComprobante** | Raíz | Tipo de comprobante | "I" (Ingreso) | ✅ |
| **Exportacion** | Raíz | Indica si es exportación | "01" (No aplica) | ✅ |
| **MetodoPago** | Raíz | Método de pago | "PUE" (Pago en una exhibición) | ✅ |
| **LugarExpedicion** | Raíz | Código postal del lugar de expedición | "01000" | ✅ |
| **Confirmacion** | Raíz | Confirmación del comprobante | "12345678" | ✅ |

## Campos del Emisor

| Campo | Descripción | Ejemplo | Obligatorio |
|-------|-------------|---------|-------------|
| **Rfc** | RFC del emisor | "ABC123456T1B" | ✅ |
| **Nombre** | Razón social del emisor | "ACADEMIA DE IA S.A. DE C.V." | ✅ |
| **RegimenFiscal** | Régimen fiscal del emisor | "601" (General de Ley Personas Morales) | ✅ |

## Campos del Receptor

| Campo | Descripción | Ejemplo | Obligatorio |
|-------|-------------|---------|-------------|
| **Rfc** | RFC del receptor | "XYZ987654ABC" | ✅ |
| **Nombre** | Nombre o razón social del receptor | "JUAN PÉREZ GARCÍA" | ✅ |
| **DomicilioFiscalReceptor** | Código postal del receptor | "01000" | ✅ |
| **RegimenFiscalReceptor** | Régimen fiscal del receptor | "612" (Personas Físicas con Actividades Empresariales) | ✅ |
| **UsoCFDI** | Uso que le dará al CFDI | "G01" (Adquisición de mercancías) | ✅ |

## Campos de Conceptos

| Campo | Descripción | Ejemplo | Obligatorio |
|-------|-------------|---------|-------------|
| **ClaveProdServ** | Clave del producto o servicio (catálogo SAT) | "84111506" (Servicios de consultoría) | ✅ |
| **NoIdentificacion** | Número de identificación del producto | "CURSO-IA-001" | ❌ |
| **Cantidad** | Cantidad del concepto | "1" | ✅ |
| **ClaveUnidad** | Clave de la unidad de medida | "E48" (Servicio) | ✅ |
| **Unidad** | Descripción de la unidad | "Curso", "Suscripción" | ✅ |
| **Descripcion** | Descripción detallada del concepto | "Curso Avanzado de IA" | ✅ |
| **ValorUnitario** | Valor unitario del concepto | "3000.00" | ✅ |
| **Importe** | Importe total del concepto | "3000.00" | ✅ |
| **Descuento** | Descuento aplicado | "0.00" | ❌ |
| **ObjetoImp** | Objeto del impuesto | "02" (Sí objeto del impuesto) | ✅ |

## Campos de Impuestos

| Campo | Descripción | Ejemplo | Obligatorio |
|-------|-------------|---------|-------------|
| **Base** | Base del impuesto | "3000.00" | ✅ |
| **Impuesto** | Tipo de impuesto | "002" (IVA) | ✅ |
| **TipoFactor** | Tipo de factor | "Tasa" | ✅ |
| **TasaOCuota** | Tasa o cuota del impuesto | "0.160000" (16%) | ✅ |
| **Importe** | Importe del impuesto | "480.00" | ✅ |

## Complementos Obligatorios

| Campo | Descripción | Ejemplo | Obligatorio |
|-------|-------------|---------|-------------|
| **TimbreFiscalDigital** | Complemento de timbrado | Incluye UUID, fecha de timbrado, etc. | ✅ |
| **UUID** | Identificador único del comprobante | "12345678-1234-1234-1234-123456789012" | ✅ |
| **FechaTimbrado** | Fecha y hora del timbrado | "2025-01-15T10:35:00" | ✅ |
| **RfcProvCertif** | RFC del proveedor de certificación | "ABC123456T1B" | ✅ |
| **SelloCFD** | Sello del CFD | "[SELLO_CFD]" | ✅ |
| **NoCertificadoSAT** | Número de certificado del SAT | "30001000000400002434" | ✅ |
| **SelloSAT** | Sello del SAT | "[SELLO_SAT]" | ✅ |

## Catálogos SAT Importantes

### Formas de Pago
- **01**: Efectivo
- **02**: Cheque nominativo
- **03**: Transferencia electrónica de fondos
- **04**: Tarjeta de crédito
- **05**: Monedero electrónico
- **06**: Dinero electrónico
- **08**: Vales de despensa
- **12**: Dación en pago
- **13**: Pago por subrogación
- **14**: Pago por consignación
- **15**: Condonación
- **17**: Compensación
- **23**: Novación
- **24**: Confusión
- **25**: Remisión de deuda
- **26**: Prescripción o caducidad
- **27**: A satisfacción del acreedor
- **28**: Tarjeta de débito
- **29**: Tarjeta de servicios
- **30**: Aplicación de anticipos
- **31**: Intermediario pagos
- **99**: Por definir

### Uso de CFDI
- **G01**: Adquisición de mercancías
- **G02**: Devoluciones, descuentos o bonificaciones
- **G03**: Gastos en general
- **I01**: Construcciones
- **I02**: Mobilario y equipo de oficina por inversiones
- **I03**: Equipo de transporte
- **I04**: Equipo de computo y accesorios
- **I05**: Dados, troqueles, moldes, matrices y herramental
- **I06**: Comunicaciones telefónicas
- **I07**: Comunicaciones satelitales
- **I08**: Otra maquinaria y equipo
- **D01**: Honorarios médicos, dentales y gastos hospitalarios
- **D02**: Gastos médicos por incapacidad o discapacidad
- **D03**: Gastos funerales
- **D04**: Donativos
- **D05**: Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)
- **D06**: Aportaciones voluntarias al SAR
- **D07**: Primas por seguros de gastos médicos
- **D08**: Gastos de transportación escolar obligatoria
- **D09**: Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones
- **D10**: Pagos por servicios educativos (colegiaturas)
- **P01**: Por definir

### Regímenes Fiscales
- **601**: General de Ley Personas Morales
- **603**: Personas Morales con Fines no Lucrativos
- **605**: Sueldos y Salarios e Ingresos Asimilados a Salarios
- **606**: Arrendamiento
- **608**: Demás ingresos
- **610**: Residentes en el Extranjero sin Establecimiento Permanente en México
- **611**: Ingresos por Dividendos (socios y accionistas)
- **612**: Personas Físicas con Actividades Empresariales y Profesionales
- **614**: Ingresos por intereses
- **615**: Régimen de los ingresos por obtención de premios
- **616**: Sin obligaciones fiscales
- **620**: Sociedades Cooperativas de Producción que optan por diferir sus ingresos
- **621**: Incorporación Fiscal
- **622**: Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras
- **623**: Opcional para Grupos de Sociedades
- **624**: Coordinados
- **625**: Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas
- **626**: Régimen Simplificado de Confianza

## Notas Importantes

1. **Todos los campos marcados como obligatorios (✅) deben estar presentes en el CFDI**
2. **Los campos opcionales (❌) pueden omitirse si no aplican**
3. **Los valores monetarios deben tener exactamente 2 decimales**
4. **Las fechas deben estar en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)**
5. **Los RFC deben ser válidos según las reglas del SAT**
6. **El timbrado es obligatorio para que el CFDI sea válido**
7. **Los catálogos del SAT pueden actualizarse, consultar siempre la versión vigente**
