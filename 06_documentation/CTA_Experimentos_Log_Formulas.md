## Fórmulas para `CTA_Experimentos_Log.csv` (Google Sheets)

Asumiendo encabezados:
`fecha,oferta,nicho,idioma,tono,variant_id,cta_group,cta_text,envios,respuestas,clicks,agendas,asistencias,ventas,observaciones`

- Reply Rate (%): `=IFERROR(respuestas/envios,0)`
- Click Rate (%): `=IFERROR(clicks/envios,0)`
- Agenda Rate (%): `=IFERROR(agendas/envios,0)`
- Show Rate (%): `=IFERROR(asistencias/agendas,0)`
- Conversion (%): `=IFERROR(ventas/envios,0)`

Ejemplo por fila (fila 2):
- Columna P (reply_rate): `=IFERROR(I2/J2,0)` → ajusta a tus columnas reales

Resumen por `variant_id`+`cta_group` (tabla dinámica o QUERY):
``` 
=QUERY(A1:O, 
  "select F,G,sum(I),sum(J),sum(K),sum(L),sum(M),sum(N), 
          sum(J)/sum(I), sum(K)/sum(I), sum(L)/sum(I), sum(M)/sum(L), sum(N)/sum(I) 
    where F is not null group by F,G label 
      sum(I) 'envios', sum(J) 'respuestas', sum(K) 'clicks', sum(L) 'agendas', sum(M) 'asistencias', sum(N) 'ventas', 
      sum(J)/sum(I) 'reply_rate', sum(K)/sum(I) 'click_rate', sum(L)/sum(I) 'agenda_rate', sum(M)/sum(L) 'show_rate', sum(N)/sum(I) 'conversion'", 1)
```

Regla de paro (stopping rule) sencilla A/B (min n=50/envíos por grupo):
- Si `reply_rate_B - reply_rate_A >= 0.05` y ambos `envios >= 50` → Ganador B
- Si `reply_rate_A - reply_rate_B >= 0.05` y ambos `envios >= 50` → Ganador A

Fórmula flag (fila agregada en resumen, suponiendo reply_rate_A en Q2, reply_rate_B en Q3 y envíos en H2/H3):
```
=IF(AND(H2>=50,H3>=50, Q3-Q2>=0.05), "Winner B", IF(AND(H2>=50,H3>=50, Q2-Q3>=0.05), "Winner A", "Continue"))
```

