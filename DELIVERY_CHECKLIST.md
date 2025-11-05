# Checklist de Entrega - Campaña Instagram 35% OFF

## ✅ Pre-entrega

### Archivos SVG
- [ ] Todos los SVG principales presentes (feed, stories, reels, carousel)
- [ ] Variantes (dark, A/B, últimas 24h, low-text) incluidas
- [ ] Placeholders de logo listos para reemplazar
- [ ] Safe areas activadas si es necesario

### Tokens y configuración
- [ ] `tokens.json` actualizado con datos reales
- [ ] URL correcta (con/sin UTM según necesidad)
- [ ] Handle de Instagram correcto
- [ ] Cupón aplicado
- [ ] CTA personalizado

### Tema de marca
- [ ] `brandColors` en tokens.json configurado
- [ ] Tema aplicado: `node tools/apply_theme.js`
- [ ] Colores verificados en preview

### QR y assets
- [ ] QR generado: `node tools/generate_qr.js`
- [ ] QR apunta a URL correcta con UTM
- [ ] Logo real reemplazado en todos los SVG

### Exportación
- [ ] PNG 1x exportados (1080px)
- [ ] PNG 2x exportados (2160px para 1080, 2700px para 1350, 3840px para 1920)
- [ ] Todos los tamaños incluidos (1080×1080, 1080×1350, 1080×1920)
- [ ] SVG optimizados con SVGO

### Validación
- [ ] Ejecutado: `bash tools/validate_all.sh` (sin errores)
- [ ] QA checklist completado: `design/instagram/qa/qa_checklist.md`
- [ ] Contraste verificado (AA mínimo)
- [ ] Safe areas respetadas
- [ ] Textos sin errores ortográficos

### Copys y contenido
- [ ] Copys revisados (ES/EN/PT según necesidad)
- [ ] Hashtags incluidos
- [ ] Alt text asignado para accesibilidad
- [ ] Calendario de publicación revisado

### Empaquetado
- [ ] ZIP final creado: `bash tools/package_assets.sh`
- [ ] Preview web funcionando: `exports/preview/index.html`
- [ ] Documentación completa incluida

## 📤 Entrega

### Estructura de entrega sugerida
```
entrega_instagram_35off_YYYYMMDD/
├── svg/                    # SVG editables
│   ├── feed/
│   ├── stories/
│   ├── ads/
│   └── ...
├── png/                    # PNG 1x y 2x
│   ├── 1x/
│   └── 2x/
├── copys/                  # Captions ES/EN/PT
├── calendar/               # Calendario CSV
├── docs/                   # Documentación
│   ├── README.md
│   ├── QA_CHECKLIST.md
│   └── ...
└── package.zip            # ZIP completo
```

### Información a entregar
- [ ] Instrucciones de uso
- [ ] Credenciales/tokens si aplica
- [ ] Link a preview web
- [ ] Fechas sugeridas de publicación
- [ ] Métricas objetivo (si aplica)

### Notas finales
- [ ] Variantes explicadas (dark, A/B, low-text)
- [ ] Recomendaciones de uso por formato
- [ ] Contacto para soporte

---

**Fecha de entrega**: _______________
**Entregado por**: _______________
**Recibido por**: _______________



