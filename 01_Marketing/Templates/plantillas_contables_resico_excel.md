---
title: "Plantillas Contables Resico Excel"
category: "01_marketing"
tags: ["business", "marketing", "template"]
created: "2025-10-29"
path: "01_marketing/Templates/plantillas_contables_resico_excel.md"
---

# Plantillas Contables RESICO - Excel/Google Sheets
## Herramientas Prácticas para PYME México 2025

---

## 1. PLANTILLA DE REGISTRO DIARIO DE INGRESOS Y EGRESOS

### 1.1 Estructura de la Plantilla
```
HOJA: "Registro Diario"
COLUMNAS:
A: Fecha (DD/MM/AAAA)
B: Concepto
C: Cliente/Proveedor
D: Método de Pago
E: Importe (sin IVA)
F: IVA (16%)
G: Total
H: Categoría (Ingreso/Egreso)
I: Negocio (Curso/Webinar/SaaS/Bulk)
J: Observaciones
```

### 1.2 Fórmulas Automáticas
```excel
F2: =E2*0.16
G2: =E2+F2
H2: =IF(E2>0,"Ingreso","Egreso")
```

### 1.3 Validaciones de Datos
- **Fecha**: Formato DD/MM/AAAA
- **Importe**: Números positivos
- **IVA**: Cálculo automático 16%
- **Categoría**: Lista desplegable
- **Negocio**: Lista desplegable

---

## 2. PLANTILLA DE RESUMEN MENSUAL

### 2.1 Estructura de la Plantilla
```
HOJA: "Resumen Mensual"
SECCIONES:
- Resumen General
- Ingresos por Negocio
- Egresos por Categoría
- Cálculo de Impuestos
- Flujo de Caja
```

### 2.2 Fórmulas de Resumen
```excel
Total Ingresos: =SUMIF(H:H,"Ingreso",E:E)
Total Egresos: =SUMIF(H:H,"Egreso",E:E)
Utilidad Bruta: =Total_Ingresos-Total_Egresos
Impuesto RESICO: =Total_Ingresos*0.025
Utilidad Neta: =Utilidad_Bruta-Impuesto_RESICO
```

### 2.3 Desglose por Negocio
```excel
Curso IA: =SUMIFS(E:E,H:H,"Ingreso",I:I,"Curso")
Webinar IA: =SUMIFS(E:E,H:H,"Ingreso",I:I,"Webinar")
SaaS Marketing: =SUMIFS(E:E,H:H,"Ingreso",I:I,"SaaS")
IA Bulk: =SUMIFS(E:E,H:H,"Ingreso",I:I,"Bulk")
```

---

## 3. PLANTILLA DE FLUJO DE CAJA

### 3.1 Estructura de la Plantilla
```
HOJA: "Flujo de Caja"
COLUMNAS:
A: Fecha
B: Concepto
C: Ingresos
D: Egresos
E: Saldo Acumulado
F: Saldo en Banco
G: Diferencia
```

### 3.2 Fórmulas de Flujo
```excel
E2: =E1+C2-D2
G2: =E2-F2
```

### 3.3 Proyecciones
```excel
Ingresos Proyectados: =PROMEDIO(C:C)*30
Egresos Proyectados: =PROMEDIO(D:D)*30
Saldo Final Proyectado: =Ingresos_Proyectados-Egresos_Proyectados
```

---

## 4. PLANTILLA DE CONTROL DE INVENTARIOS

### 4.1 Para Curso de IA
```
HOJA: "Inventario Curso"
COLUMNAS:
A: Fecha
B: Concepto
C: Entrada
D: Salida
E: Saldo
F: Costo Unitario
G: Valor Total
```

### 4.2 Para SaaS Marketing
```
HOJA: "Inventario SaaS"
COLUMNAS:
A: Fecha
B: Cliente
C: Plan
D: Estado
E: Fecha Inicio
F: Fecha Fin
G: Ingreso Mensual
```

### 4.3 Para IA Bulk
```
HOJA: "Inventario Documentos"
COLUMNAS:
A: Fecha
B: Cliente
C: Tipo Documento
D: Cantidad
E: Precio Unitario
F: Total
G: Estado
```

---

## 5. PLANTILLA DE DECLARACIONES FISCALES

### 5.1 DIEM (Declaración de Ingresos y Egresos)
```
HOJA: "DIEM"
SECCIONES:
- Ingresos del Mes
- Egresos del Mes
- Cálculo de Impuesto
- Datos para Declaración
```

### 5.2 Fórmulas DIEM
```excel
Ingresos Totales: =SUMIF(H:H,"Ingreso",E:E)
Egresos Totales: =SUMIF(H:H,"Egreso",E:E)
Impuesto RESICO: =Ingresos_Totales*0.025
```

### 5.3 Datos para SAT
```excel
RFC: [TU_RFC]
Nombre: [TU_NOMBRE]
Período: [MES/AÑO]
Ingresos: =Ingresos_Totales
Impuesto: =Impuesto_RESICO
```

---

## 6. PLANTILLA DE ANÁLISIS DE RENTABILIDAD

### 6.1 Por Negocio
```
HOJA: "Rentabilidad"
COLUMNAS:
A: Negocio
B: Ingresos
C: Costos Directos
D: Gastos Operativos
E: Utilidad Bruta
F: Margen %
G: ROI %
```

### 6.2 Fórmulas de Rentabilidad
```excel
Utilidad Bruta: =B2-C2-D2
Margen %: =E2/B2*100
ROI %: =E2/(C2+D2)*100
```

### 6.3 Comparativo Mensual
```excel
Crecimiento: =(B2-B1)/B1*100
Tendencia: =TENDENCIA(B:B,A:A)
```

---

## 7. PLANTILLA DE PRESUPUESTO

### 7.1 Presupuesto Anual
```
HOJA: "Presupuesto"
COLUMNAS:
A: Concepto
B: Presupuesto Anual
C: Realizado YTD
D: Diferencia
E: % Ejecutado
F: Proyección Final
```

### 7.2 Fórmulas de Presupuesto
```excel
Diferencia: =C2-B2
% Ejecutado: =C2/B2*100
Proyección: =C2*12/MES_ACTUAL
```

### 7.3 Alertas
```excel
Alerta: =IF(E2>100,"SOBREPASADO",IF(E2>80,"ATENCIÓN","OK"))
```

---

## 8. PLANTILLA DE CONTROL DE CLIENTES

### 8.1 Base de Datos de Clientes
```
HOJA: "Clientes"
COLUMNAS:
A: ID Cliente
B: Nombre/Razón Social
C: RFC
D: Email
E: Teléfono
F: Negocio
G: Fecha Registro
H: Última Compra
I: Total Compras
J: Estado
```

### 8.2 Fórmulas de Clientes
```excel
Total Compras: =SUMIFS(E:E,C:C,A2)
Última Compra: =MAXIFS(A:A,C:C,A2)
Días desde Última: =HOY()-H2
```

### 8.3 Segmentación
```excel
VIP: =IF(I2>50000,"VIP","Regular")
Activo: =IF(J2="Activo","Sí","No")
```

---

## 9. PLANTILLA DE CONTROL DE PROVEEDORES

### 9.1 Base de Datos de Proveedores
```
HOJA: "Proveedores"
COLUMNAS:
A: ID Proveedor
B: Nombre/Razón Social
C: RFC
D: Email
E: Teléfono
F: Servicio/Producto
G: Fecha Registro
H: Última Compra
I: Total Compras
J: Estado
```

### 9.2 Fórmulas de Proveedores
```excel
Total Compras: =SUMIFS(E:E,C:C,A2)
Última Compra: =MAXIFS(A:A,C:C,A2)
Días desde Última: =HOY()-H2
```

### 9.3 Evaluación
```excel
Calificación: =IF(I2>10000,"A",IF(I2>5000,"B","C"))
```

---

## 10. PLANTILLA DE DASHBOARD EJECUTIVO

### 10.1 Métricas Principales
```
HOJA: "Dashboard"
SECCIONES:
- Resumen Financiero
- KPIs por Negocio
- Tendencias
- Alertas
```

### 10.2 Gráficos Automáticos
- **Gráfico de Ingresos**: Por negocio y mes
- **Gráfico de Utilidades**: Tendencias mensuales
- **Gráfico de Clientes**: Crecimiento acumulado
- **Gráfico de Gastos**: Por categoría

### 10.3 Indicadores Visuales
```excel
Semáforo: =IF(E2>0,"🟢",IF(E2=0,"🟡","🔴"))
Flecha: =IF(E2>E1,"↗️",IF(E2<E1,"↘️","➡️"))
```

---

## 11. PLANTILLA DE CONTROL DE IMPUESTOS

### 11.1 Registro de Impuestos
```
HOJA: "Impuestos"
COLUMNAS:
A: Período
B: Ingresos
C: Impuesto RESICO
D: IVA Cobrado
E: IVA Pagado
F: Diferencia IVA
G: Total a Pagar
H: Fecha Pago
I: Estado
```

### 11.2 Fórmulas de Impuestos
```excel
Impuesto RESICO: =B2*0.025
Diferencia IVA: =D2-E2
Total a Pagar: =C2+F2
```

### 11.3 Alertas de Vencimiento
```excel
Vencimiento: =IF(H2="","PENDIENTE","PAGADO")
Días Vencido: =IF(H2="",HOY()-FECHA_VENCIMIENTO,0)
```

---

## 12. PLANTILLA DE ANÁLISIS DE TENDENCIAS

### 12.1 Análisis Mensual
```
HOJA: "Tendencias"
COLUMNAS:
A: Mes
B: Ingresos
C: Egresos
D: Utilidad
E: Crecimiento %
F: Tendencia
G: Proyección
```

### 12.2 Fórmulas de Tendencias
```excel
Crecimiento: =(B2-B1)/B1*100
Tendencia: =TENDENCIA(B:B,A:A)
Proyección: =TENDENCIA(B:B,A:A,13)
```

### 12.3 Análisis Estacional
```excel
Promedio: =PROMEDIO(B:B)
Desviación: =DESVEST(B:B)
Coeficiente: =DESVEST(B:B)/PROMEDIO(B:B)
```

---

## 13. INSTRUCCIONES DE USO

### 13.1 Configuración Inicial
1. **Descargar plantillas** desde Google Sheets o Excel
2. **Configurar datos básicos** (RFC, nombre, etc.)
3. **Establecer categorías** de ingresos y egresos
4. **Configurar fórmulas** automáticas
5. **Probar con datos de prueba**

### 13.2 Uso Diario
1. **Registrar todas las operaciones** en "Registro Diario"
2. **Verificar cálculos automáticos**
3. **Revisar alertas y validaciones**
4. **Actualizar saldos bancarios**

### 13.3 Uso Mensual
1. **Revisar resumen mensual**
2. **Preparar declaraciones fiscales**
3. **Actualizar presupuestos**
4. **Analizar tendencias**

### 13.4 Uso Anual
1. **Consolidar información anual**
2. **Preparar declaración anual**
3. **Actualizar presupuestos**
4. **Planificar siguiente año**

---

## 14. BACKUP Y SEGURIDAD

### 14.1 Backup Automático
- **Google Sheets**: Backup automático en la nube
- **Excel**: Configurar OneDrive o Google Drive
- **Frecuencia**: Diaria automática

### 14.2 Seguridad
- **Contraseñas**: Proteger hojas sensibles
- **Acceso**: Limitar usuarios autorizados
- **Versiones**: Mantener historial de cambios

### 14.3 Recuperación
- **Puntos de restauración**: Semanales
- **Copias de seguridad**: Múltiples ubicaciones
- **Procedimientos**: Documentados

---

## 15. INTEGRACIÓN CON SISTEMAS

### 15.1 Bancos
- **Importación**: CSV de movimientos bancarios
- **Conciliación**: Automática con saldos
- **Alertas**: Diferencias detectadas

### 15.2 Facturación
- **Exportación**: Datos para facturación
- **Importación**: Facturas emitidas
- **Sincronización**: Automática

### 15.3 Contabilidad
- **Exportación**: Para contador
- **Importación**: Desde sistemas contables
- **Compatibilidad**: Múltiples formatos

---

*Plantillas Contables RESICO - Herramientas Prácticas*
*Versión 1.0 - Enero 2025*



