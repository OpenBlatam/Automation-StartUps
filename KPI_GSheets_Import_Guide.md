## Google Sheets: Importar KPI CSV (Enhanced)

Pasos (2 minutos)
1) Crea una hoja nueva → Datos → Importar → Subir `KPI_Dashboard_Template_Enhanced.csv`.
2) Selecciona "Reemplazar hoja" y separador automático.
3) Asegura formato de columnas:
   - fechas: Date
   - deal_value_usd: Number (2 decimales)
   - tasas (reply_rate, etc.): Percent con 1-2 decimales
4) Inserta gráficos: Reply Rate por día, Booked Rate por variante, Revenue/Send por oferta.

Sugerencias
- Fija filtros por `offer`, `channel`, `cta_group`.
- Agrega validación de datos para `cta_group` (C1-C4) y `channel`.
- Añade campo calculado "status": IF(reply_rate>=0.12,"OK","WIP").


