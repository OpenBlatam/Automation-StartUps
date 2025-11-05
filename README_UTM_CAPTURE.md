# utm_capture.js - Guía de uso

Script JavaScript para capturar UTMs desde URL, guardar first/last touch y autocompletar formularios.

---

## Instalación rápida

### 1. Incluir el script
Añade antes de `</body>` en tu HTML:

```html
<script src="utm_capture.js"></script>
```

O inline (si prefieres no tener archivo separado):

```html
<script>
  // Copia el contenido completo de utm_capture.js aquí
</script>
```

### 2. Añadir inputs ocultos en formularios

```html
<form id="contact-form" method="POST" action="/submit">
  <input type="email" name="email" required />
  <input type="text" name="name" required />
  
  <!-- Campos UTM (ocultos) -->
  <input type="hidden" name="utm_source" />
  <input type="hidden" name="utm_medium" />
  <input type="hidden" name="utm_campaign" />
  <input type="hidden" name="utm_content" />
  <input type="hidden" name="utm_term" />
  <input type="hidden" name="landing_url" />
  <input type="hidden" name="referrer_url" />
  
  <!-- First touch (opcional) -->
  <input type="hidden" name="first_utm_source" />
  <input type="hidden" name="first_utm_medium" />
  <input type="hidden" name="first_utm_campaign" />
  <input type="hidden" name="first_utm_content" />
  <input type="hidden" name="first_utm_term" />
  
  <button type="submit">Enviar</button>
</form>
```

**Alternativa con atributos `data-utm`:**

```html
<input type="hidden" data-utm="utm_source" />
<input type="hidden" data-utm="utm_campaign" />
```

---

## Funcionamiento

### Flujo automático

1. **Usuario llega con UTMs en URL**: `https://tusitio.com/?utm_source=facebook&utm_campaign=test_2025-11`
2. **Script captura** los UTMs y los guarda en `localStorage` como:
   - `utm_last` → última visita
   - `utm_first` → primera visita (solo se guarda una vez)
3. **Al cargar formulario**, los inputs ocultos se autocompletan automáticamente
4. **Al enviar formulario**, los UTMs viajan junto con los datos del usuario

### Ejemplo de URL con UTMs

```
https://tusitio.com/landing?
  utm_source=facebook&
  utm_medium=remarketing&
  utm_campaign=saasia_cart_7d_2025-11&
  utm_content=h1_beneficio_cta_rojo_fondo_claro&
  utm_term=mx_7d
```

---

## API global (opcional)

Si necesitas acceder a los UTMs desde JavaScript:

```javascript
// Obtener último touch
const lastUTM = UTMCapture.getLast();
console.log(lastUTM);
// { source: 'facebook', medium: 'remarketing', campaign: '...', ts: '...' }

// Obtener primer touch
const firstUTM = UTMCapture.getFirst();
console.log(firstUTM);

// Rellenar inputs manualmente (útil para formularios dinámicos)
UTMCapture.fillInputs(document.getElementById('my-form'));

// Limpiar todo (útil para testing)
UTMCapture.clearAll();
```

---

## Integración con CRM

### Webhook → HubSpot/Pipedrive

Cuando el formulario se envía, los UTMs viajan en el payload:

```json
{
  "email": "user@example.com",
  "name": "Juan Pérez",
  "utm_source": "facebook",
  "utm_medium": "remarketing",
  "utm_campaign": "saasia_cart_7d_2025-11",
  "utm_content": "h1_beneficio_cta_rojo_fondo_claro",
  "utm_term": "mx_7d",
  "landing_url": "https://tusitio.com/landing",
  "referrer_url": "https://facebook.com/"
}
```

### Mapeo en Make/Zapier

1. **Trigger**: Webhook (POST) desde tu formulario
2. **Parse**: Extraer campos `utm_*` del payload
3. **CRM Action**: Create/Update Contact con los UTMs mapeados

Ver `TOOLS_CRM_COMPARISON.md` para plantillas detalladas.

---

## Testing y debugging

### Verificar que funciona

1. Abre DevTools (F12) → Console
2. Navega a: `https://tusitio.com/?utm_source=test&utm_campaign=test_2025-11`
3. Ejecuta:
   ```javascript
   UTMCapture.getLast();
   ```
4. Deberías ver los UTMs guardados

### Ver localStorage

```javascript
// En DevTools Console
console.log(localStorage.getItem('utm_last'));
console.log(localStorage.getItem('utm_first'));
```

### Limpiar datos de prueba

```javascript
UTMCapture.clearAll();
// o manualmente:
localStorage.removeItem('utm_last');
localStorage.removeItem('utm_first');
localStorage.removeItem('utm_last_updated_at');
```

---

## Troubleshooting

### Problema: Los inputs no se autocompletan
- ✅ Verifica que los `name` de los inputs coincidan exactamente (`utm_source`, no `utmSource`)
- ✅ Asegúrate de que el script se carga antes de que el formulario se renderice
- ✅ Revisa la consola por errores JavaScript

### Problema: `utm_first` se sobreescribe
- ✅ El script solo guarda `utm_first` si no existe. Si quieres resetear, limpia localStorage manualmente

### Problema: UTMs no se guardan en localStorage
- ✅ Verifica que el navegador permita localStorage (no en modo incógnito bloqueado)
- ✅ Revisa la consola por errores de CORS o seguridad

---

## Mejores prácticas

1. **Siempre incluye inputs ocultos** en todos los formularios de registro/contacto
2. **No modifiques los nombres** de los campos (`utm_source`, `utm_medium`, etc.) si ya los usas en CRM
3. **Prueba en staging** antes de deploy a producción
4. **Mapea `first_utm_*` y `last_utm_*`** en tu CRM para análisis de attribution

---

## Referencias

- Guía completa UTMs: `UTM_GUIDE_OUTREACH.md`
- Integración CRM: `TOOLS_CRM_COMPARISON.md`
- Script Python/JS: Ver sección "Scripts listos" en `TOOLS_CRM_COMPARISON.md`



