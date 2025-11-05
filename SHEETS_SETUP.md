# SHEETS_SETUP — Configuración de Google Sheets

## 1) Asistencia
- Columnas: Email | Nombre | Asistio(Sí/No) | EstadoCert | WebinarID | Fecha
- Validaciones:
  - `Asistio`: lista {Sí,No}
  - `Email`: formato email
- Fórmulas útiles:
  - No‑show% (en KPIs): `=1 - (Asistentes/Confirmados)`
- Formato condicional:
  - `EstadoCert` = "error" → rojo; = "enviado" → verde

## 2) Pedidos (IA Bulk)
- Columnas: ID | Prompt | Estado(pendiente/completado/error) | EnlaceBrief | EnlaceArticulo | EnlacePost | Fecha
- Validaciones:
  - `Estado`: lista {pendiente,completado,error}
- Fórmulas:
  - Éxito%: `=COUNTIF(C:C,"completado")/COUNTA(C:C)`
- Formato condicional:
  - `Estado` = "error" → rojo; = "completado" → verde

## 3) CostosIA
- Columnas: JobID | Cliente | Modelo | TokensPrompt | TokensOutput | CostoUSD | DuracionSeg | Fecha
- Fórmulas:
  - Costo/doc: `=SUM(F:F)/MAX(1,COUNTUNIQUE(JobID))`
  - Tokens totales: `=SUM(D:D)+SUM(E:E)`
- Alertas (condicional):
  - `CostoUSD` > 0.15 → rojo

## 4) Leads
- Columnas: Email | Empresa | Cargo | Fuente | Score | Owner | Fecha
- Validaciones:
  - `Score`: número 0–100
- Formato condicional:
  - `Score` ≥ 70 → verde (prioritario)

## 5) KPIs (pestaña aparte)
- Columnas sugeridas: Fecha | Registrados | Confirmados | Asistentes | NoShow% | CertificadosT95(h) | Recovery% | FCR% | ExitoLotes% | CostoDoc
- Ejemplos:
  - `NoShow%`: `=1-(Asistentes/Confirmados)`
  - `ExitoLotes%`: `=Pedidos!Éxito%`
  - `CostoDoc`: `=SUM(CostosIA!F:F)/COUNT(Pedidos!A:A)`

## 6) Tips
- Proteger rangos de fórmulas
- Nombrar rangos (KPIs) para dashboards
- Compartir con cuenta de servicio (si aplica)
