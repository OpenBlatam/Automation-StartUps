# Notion Template – Outline

Bases de datos
- Leads (table)
  - Props: Nombre, Email, Empresa, Rol, País, Score, Fuente, UTM Source, UTM Campaign, Etapa, Owner, Último evento (relation), Último evento fecha (rollup)
- Eventos (table)
  - Props: Tipo, Producto, Timestamp, Lead (relation)
- Ofertas (table)
  - Props: Nombre, Producto, Escalón, Precio, URL checkout
- Compras (table)
  - Props: Monto, Fecha, Lead (relation), Oferta (relation)
- Webinars (table)
  - Props: Título, Fecha, Registrados, Asistentes, Asistencia (formula)
- Demos (table)
  - Props: Fecha, Resultado, Notas, Siguiente Paso, Lead (relation)
- Tareas (board)
  - Props: Tipo, Due Date, Estado, Owner, Lead (relation)

Relaciones y rollups
- Leads ↔ Eventos (1:N) rollup: Último evento/fecha
- Leads ↔ Compras (1:N) rollup: ingresos por escalón (TRP/CORE/HT)
- Compras ↔ Ofertas (N:1) para escalón/producto
- Demos ↔ Leads (N:1)

Vistas recomendadas
- Leads Hoy (filtro: tareas pendientes OR recent activity ≤ 7 días)
- High Intent (score ≥ 6)
- No‑show Demos (resultado = no_show)
- Post‑Webinar (no asistentes)
- Pipeline por etapa (LM/TRP/CORE/HT)

Formulas
- Asistencia (Webinars) = if(Registrados>0, Asistentes/Registrados, 0)
- Funnel Stage (Leads) = if(ingresos_HT>0, "HT", if(ingresos_CORE>0, "CORE", if(ingresos_TRP>0, "TRP", "LM")))

SOP Pages
- Go‑Live 24h (embed: automation/go_live_24h_checklist.md)
- Contingencia (embed: automation/contingency_plan_automation.md)
- A/B Matrix (embed: automation/ab_test_matrix.md)
- Dashboard KPIs (enlace: automation/dashboard_kpis.md)

Notas
- Usa “Template” de página para crear Lead con subtareas (follow‑ups)
- Agrega botones de Notion automations para crear Eventos/Tareas rápidas
