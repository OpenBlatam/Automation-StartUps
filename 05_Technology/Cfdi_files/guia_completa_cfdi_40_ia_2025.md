---
title: "Guia Completa Cfdi 40 Ia 2025"
category: "05_technology"
tags: ["guide", "technical", "technology"]
created: "2025-10-29"
path: "05_technology/Cfdi_files/guia_completa_cfdi_40_ia_2025.md"
---

# Guía Completa CFDI 4.0 - Servicios de IA México 2025

## 📋 Resumen de CFDI Creados

| # | Archivo | Servicio | Total (MXN) | Tecnologías |
|---|---------|----------|-------------|-------------|
| 1 | CFDI_IA_Medicina_Personalizada_2025.xml | Medicina Personalizada | $52,200 | Diagnóstico IA, Genómica, Descubrimiento de Fármacos |
| 2 | CFDI_IA_Fintech_Blockchain_2025.xml | Fintech & Blockchain | $44,080 | Trading Algorítmico, Smart Contracts, DeFi |
| 3 | CFDI_IA_Agricultura_Inteligente_2025.xml | Agricultura Inteligente | $29,000 | Agricultura de Precisión, Drones, IoT Agrícola |
| 4 | CFDI_IA_Energia_Sostenible_2025.xml | Energía Sostenible | $48,720 | Smart Grid, Energías Renovables, Gestión de Carbono |
| 5 | CFDI_IA_Educacion_Personalizada_2025.xml | Educación Personalizada | $22,040 | Aprendizaje Adaptativo, Tutoría Virtual, VR Educativa |

## 🔍 Campos Obligatorios CFDI 4.0 - Explicación Detallada

### Campos del Comprobante (Raíz)

| Campo | Descripción | Ejemplo | Obligatorio | Validación |
|-------|-------------|---------|-------------|------------|
| **Version** | Versión del CFDI (siempre 4.0) | "4.0" | ✅ | Debe ser exactamente "4.0" |
| **Serie** | Serie del comprobante fiscal | "MED", "FINT", "AGRO" | ✅ | Máximo 25 caracteres alfanuméricos |
| **Folio** | Número consecutivo del comprobante | "2025-001" | ✅ | Único por serie, formato libre |
| **Fecha** | Fecha y hora de expedición (ISO 8601) | "2025-01-15T08:30:00" | ✅ | Formato: YYYY-MM-DDTHH:MM:SS |
| **Sello** | Sello digital del emisor | "[SELLO_DIGITAL]" | ✅ | Cadena base64 del sello digital |
| **FormaPago** | Forma de pago (catálogo SAT) | "03" (Transferencia) | ✅ | Ver catálogo c_FormaPago |
| **NoCertificado** | Número de certificado del emisor | "30001000000400002434" | ✅ | 20 dígitos del certificado |
| **Certificado** | Certificado digital del emisor | "[CERTIFICADO_DIGITAL]" | ✅ | Cadena base64 del certificado |
| **SubTotal** | Suma de importes antes de impuestos | "45000.00" | ✅ | Decimal con 2 posiciones |
| **Moneda** | Código de moneda (ISO 4217) | "MXN" | ✅ | Ver catálogo c_Moneda |
| **Total** | Importe total del comprobante | "52200.00" | ✅ | SubTotal + Impuestos |
| **TipoDeComprobante** | Tipo de comprobante | "I" (Ingreso) | ✅ | I=Ingreso, E=Egreso, T=Traslado |
| **Exportacion** | Indica si es exportación | "01" (No aplica) | ✅ | Ver catálogo c_TipoExportacion |
| **MetodoPago** | Método de pago | "PUE" (Pago en una exhibición) | ✅ | Ver catálogo c_MetodoPago |
| **LugarExpedicion** | Código postal del lugar de expedición | "01000" | ✅ | 5 dígitos del código postal |
| **Confirmacion** | Confirmación del comprobante | "12345678" | ✅ | 8 caracteres alfanuméricos |

### Campos del Emisor

| Campo | Descripción | Ejemplo | Obligatorio | Validación |
|-------|-------------|---------|-------------|------------|
| **Rfc** | RFC del emisor | "MED789123TEC" | ✅ | RFC válido según reglas SAT |
| **Nombre** | Razón social del emisor | "MEDICINA INTELIGENTE MEXICO S.A. DE C.V." | ✅ | Máximo 254 caracteres |
| **RegimenFiscal** | Régimen fiscal del emisor | "601" (General de Ley Personas Morales) | ✅ | Ver catálogo c_RegimenFiscal |

### Campos del Receptor

| Campo | Descripción | Ejemplo | Obligatorio | Validación |
|-------|-------------|---------|-------------|------------|
| **Rfc** | RFC del receptor | "HOS456789ABC" | ✅ | RFC válido según reglas SAT |
| **Nombre** | Nombre o razón social del receptor | "HOSPITAL DIGITAL MÉXICO S.A. DE C.V." | ✅ | Máximo 254 caracteres |
| **DomicilioFiscalReceptor** | Código postal del receptor | "01000" | ✅ | 5 dígitos del código postal |
| **RegimenFiscalReceptor** | Régimen fiscal del receptor | "601" (General de Ley Personas Morales) | ✅ | Ver catálogo c_RegimenFiscal |
| **UsoCFDI** | Uso que le dará al CFDI | "G01" (Adquisición de mercancías) | ✅ | Ver catálogo c_UsoCFDI |

### Campos de Conceptos

| Campo | Descripción | Ejemplo | Obligatorio | Validación |
|-------|-------------|---------|-------------|------------|
| **ClaveProdServ** | Clave del producto o servicio | "84111506" (Servicios de consultoría) | ✅ | Ver catálogo c_ClaveProdServ |
| **NoIdentificacion** | Número de identificación del producto | "DIAGNOSTIC-IA-001" | ❌ | Máximo 100 caracteres |
| **Cantidad** | Cantidad del concepto | "1" | ✅ | Decimal positivo |
| **ClaveUnidad** | Clave de la unidad de medida | "E48" (Servicio) | ✅ | Ver catálogo c_ClaveUnidad |
| **Unidad** | Descripción de la unidad | "Sistema", "Plataforma" | ✅ | Máximo 20 caracteres |
| **Descripcion** | Descripción detallada del concepto | "Sistema de Diagnóstico Médico con IA..." | ✅ | Máximo 1000 caracteres |
| **ValorUnitario** | Valor unitario del concepto | "18000.00" | ✅ | Decimal con 2 posiciones |
| **Importe** | Importe total del concepto | "18000.00" | ✅ | Cantidad × ValorUnitario |
| **Descuento** | Descuento aplicado | "0.00" | ❌ | Decimal con 2 posiciones |
| **ObjetoImp** | Objeto del impuesto | "02" (Sí objeto del impuesto) | ✅ | Ver catálogo c_ObjetoImp |

### Campos de Impuestos

| Campo | Descripción | Ejemplo | Obligatorio | Validación |
|-------|-------------|---------|-------------|------------|
| **Base** | Base del impuesto | "18000.00" | ✅ | Decimal con 2 posiciones |
| **Impuesto** | Tipo de impuesto | "002" (IVA) | ✅ | Ver catálogo c_Impuesto |
| **TipoFactor** | Tipo de factor | "Tasa" | ✅ | Tasa, Cuota, Exento |
| **TasaOCuota** | Tasa o cuota del impuesto | "0.160000" (16%) | ✅ | Decimal con 6 posiciones |
| **Importe** | Importe del impuesto | "2880.00" | ✅ | Base × TasaOCuota |

### Complemento Timbre Fiscal Digital

| Campo | Descripción | Ejemplo | Obligatorio | Validación |
|-------|-------------|---------|-------------|------------|
| **UUID** | Identificador único del comprobante | "12345678-1234-1234-1234-123456789012" | ✅ | Formato UUID estándar |
| **FechaTimbrado** | Fecha y hora del timbrado | "2025-01-15T08:35:00" | ✅ | Formato ISO 8601 |
| **RfcProvCertif** | RFC del proveedor de certificación | "MED789123TEC" | ✅ | RFC válido del PAC |
| **SelloCFD** | Sello del CFD | "[SELLO_CFD]" | ✅ | Cadena base64 |
| **NoCertificadoSAT** | Número de certificado del SAT | "30001000000400002434" | ✅ | 20 dígitos |
| **SelloSAT** | Sello del SAT | "[SELLO_SAT]" | ✅ | Cadena base64 |

## 📊 Catálogos SAT Actualizados 2025

### Formas de Pago (c_FormaPago)
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

### Uso de CFDI (c_UsoCFDI)
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
- **D05**: Intereses reales efectivamente pagos por créditos hipotecarios
- **D06**: Aportaciones voluntarias al SAR
- **D07**: Primas por seguros de gastos médicos
- **D08**: Gastos de transportación escolar obligatoria
- **D09**: Depósitos en cuentas para el ahorro
- **D10**: Pagos por servicios educativos (colegiaturas)
- **P01**: Por definir

### Regímenes Fiscales (c_RegimenFiscal)
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

## 🚀 Tecnologías de IA Incluidas

### 1. **Medicina Personalizada**
- Diagnóstico médico con IA
- Medicina genómica
- Descubrimiento de fármacos

### 2. **Fintech & Blockchain**
- Trading algorítmico
- Smart contracts
- DeFi (Finanzas Descentralizadas)
- Gestión de riesgos

### 3. **Agricultura Inteligente**
- Agricultura de precisión
- Drones agrícolas
- IoT agrícola
- Predicción de cosechas

### 4. **Energía Sostenible**
- Smart Grid
- Energías renovables
- Gestión de huella de carbono
- Optimización energética

### 5. **Educación Personalizada**
- Aprendizaje adaptativo
- Tutoría virtual
- Realidad virtual educativa
- Analytics educativo

## ⚠️ Notas Importantes

1. **Todos los campos marcados como obligatorios (✅) deben estar presentes**
2. **Los valores monetarios deben tener exactamente 2 decimales**
3. **Las fechas deben estar en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)**
4. **Los RFC deben ser válidos según las reglas del SAT**
5. **El timbrado es obligatorio para que el CFDI sea válido**
6. **Los catálogos del SAT pueden actualizarse, consultar siempre la versión vigente**
7. **Para servicios de IA, usar ClaveProdServ "84111506" (Servicios de consultoría)**
8. **La descripción debe ser clara y específica del servicio de IA proporcionado**

## 📈 Estadísticas de los CFDI Creados

- **Total de CFDI**: 5
- **Rango de precios**: $22,040 - $52,200 MXN
- **Promedio**: $39,208 MXN
- **Total facturado**: $196,040 MXN
- **IVA total**: $31,366.40 MXN
- **Tecnologías cubiertas**: 5 sectores principales de IA
- **Todos válidos** según normativas SAT 2025



