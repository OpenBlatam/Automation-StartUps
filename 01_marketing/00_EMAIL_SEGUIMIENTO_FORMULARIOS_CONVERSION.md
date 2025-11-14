# 📝 Formularios de Conversión Optimizados

## 🎯 Formularios por Objetivo

### Formulario 1: Cálculo de ROI (Email #1)

**Objetivo:** Calcular ROI y capturar lead

**Versión Mínima (1 Campo):**
```
┌─────────────────────────────────────────┐
│  ¿Cuántas horas semanales pasas en      │
│  tareas que podrías automatizar?        │
│                                          │
│  [___] horas/semana                     │
│                                          │
│  [Calcular mi ROI]                      │
│                                          │
│  (Opcional: Email para recibir análisis)│
│  [email@ejemplo.com]                    │
└─────────────────────────────────────────┘
```

**Versión Completa (3 Campos):**
```
┌─────────────────────────────────────────┐
│  Calcula tu ROI Personalizado           │
│                                          │
│  1. Horas semanales automatizables:     │
│     [___] horas                          │
│                                          │
│  2. Tu tarifa por hora:                 │
│     $[___]                               │
│                                          │
│  3. Email para recibir análisis:        │
│     [email@ejemplo.com]                  │
│                                          │
│  [Calcular mi ROI Gratis]               │
│                                          │
│  ✓ Sin spam  ✓ Análisis en 2 min        │
└─────────────────────────────────────────┘
```

**Código HTML:**

```html
<form id="roiForm" class="conversion-form">
    <div class="form-group">
        <label>Horas semanales en tareas automatizables:</label>
        <input type="number" id="horas" placeholder="Ej: 15" required min="1" max="168">
    </div>
    
    <div class="form-group">
        <label>Tu tarifa por hora ($):</label>
        <input type="number" id="tarifa" placeholder="Ej: 25" required min="1">
    </div>
    
    <div class="form-group">
        <label>Email para recibir análisis completo:</label>
        <input type="email" id="email" placeholder="tu@email.com" required>
    </div>
    
    <button type="submit" class="btn-primary">
        📊 Calcular mi ROI Gratis
    </button>
    
    <p class="form-note">
        ✓ Sin spam  ✓ Análisis en 2 minutos  ✓ 100% gratuito
    </p>
</form>
```

---

### Formulario 2: Agendar Llamada (Todos los Emails)

**Objetivo:** Agendar llamada de 15 minutos

**Versión Simple:**
```
┌─────────────────────────────────────────┐
│  ¿Cuándo te funciona mejor?             │
│                                          │
│  [Calendario Integrado - Calendly]      │
│                                          │
│  O escríbenos:                          │
│  [email@ejemplo.com]                    │
│  [Enviar]                               │
└─────────────────────────────────────────┘
```

**Versión con Calendly Embed:**

```html
<div class="calendar-container">
    <!-- Calendly inline widget -->
    <div class="calendly-inline-widget" 
         data-url="https://calendly.com/tu-usuario/15min" 
         style="min-width:320px;height:630px;">
    </div>
    <script type="text/javascript" src="https://assets.calendly.com/assets/external/widget.js" async></script>
</div>
```

**Versión Formulario Personalizado:**

```html
<form id="calendarForm" class="conversion-form">
    <div class="form-group">
        <label>Nombre:</label>
        <input type="text" id="nombre" placeholder="Tu nombre" required>
    </div>
    
    <div class="form-group">
        <label>Email:</label>
        <input type="email" id="email" placeholder="tu@email.com" required>
    </div>
    
    <div class="form-group">
        <label>¿Qué día te funciona mejor?</label>
        <select id="dia" required>
            <option value="">Selecciona un día</option>
            <option value="lunes">Lunes</option>
            <option value="martes">Martes</option>
            <option value="miercoles">Miércoles</option>
            <option value="jueves">Jueves</option>
            <option value="viernes">Viernes</option>
        </select>
    </div>
    
    <div class="form-group">
        <label>¿Qué hora te funciona mejor?</label>
        <select id="hora" required>
            <option value="">Selecciona una hora</option>
            <option value="9-10">9:00 - 10:00 AM</option>
            <option value="10-11">10:00 - 11:00 AM</option>
            <option value="11-12">11:00 AM - 12:00 PM</option>
            <option value="2-3">2:00 - 3:00 PM</option>
            <option value="3-4">3:00 - 4:00 PM</option>
        </select>
    </div>
    
    <div class="form-group">
        <label>¿Sobre qué quieres hablar? (Opcional)</label>
        <textarea id="mensaje" placeholder="Ej: Quiero calcular mi ROI específico..." rows="3"></textarea>
    </div>
    
    <button type="submit" class="btn-primary">
        📅 Agendar Llamada de 15 min
    </button>
    
    <p class="form-note">
        ✓ Confirmación instantánea  ✓ Sin compromiso  ✓ Agenda en tu zona horaria
    </p>
</form>
```

---

### Formulario 3: Solicitar Caso de Estudio (Email #2)

**Objetivo:** Enviar caso de estudio específico

**Versión Mínima:**
```
┌─────────────────────────────────────────┐
│  ¿Qué caso de estudio te interesa?      │
│                                          │
│  [ ] Marketing                           │
│  [ ] Consultoría                         │
│  [ ] Tech/Startup                        │
│                                          │
│  Email: [email@ejemplo.com]             │
│                                          │
│  [Enviar Caso de Estudio]               │
└─────────────────────────────────────────┘
```

**Versión Completa:**

```html
<form id="casoEstudioForm" class="conversion-form">
    <div class="form-group">
        <label>Tu nombre:</label>
        <input type="text" id="nombre" placeholder="Tu nombre" required>
    </div>
    
    <div class="form-group">
        <label>Email:</label>
        <input type="email" id="email" placeholder="tu@email.com" required>
    </div>
    
    <div class="form-group">
        <label>¿Qué caso de estudio te interesa más?</label>
        <select id="caso" required>
            <option value="">Selecciona un caso</option>
            <option value="marketing">Marketing - María (240% engagement)</option>
            <option value="consultoria">Consultoría - Carlos (3 proyectos más)</option>
            <option value="tech">Tech/Startup - Ana ($9,600/año ahorrados)</option>
        </select>
    </div>
    
    <div class="form-group">
        <label>Tu industria (opcional, para personalizar mejor):</label>
        <input type="text" id="industria" placeholder="Ej: Marketing, Consultoría...">
    </div>
    
    <button type="submit" class="btn-primary">
        📄 Enviar Caso de Estudio
    </button>
    
    <p class="form-note">
        ✓ PDF detallado  ✓ Enviado en 2 minutos  ✓ 100% gratuito
    </p>
</form>
```

---

## 🎨 Optimizaciones de Conversión

### Principios Aplicados:

1. **Mínimos Campos:** Solo lo esencial
2. **Progresivo:** Empezar con 1 campo, agregar opcionales
3. **Claro:** Labels descriptivos, placeholders útiles
4. **Confianza:** Notas de seguridad, sin spam
5. **Urgencia:** "Limitado", "Últimas horas"
6. **Valor:** "Gratis", "Sin compromiso", "En 2 minutos"

### Elementos Visuales:

```css
.conversion-form {
    max-width: 500px;
    margin: 0 auto;
    padding: 30px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.form-group {
    margin-bottom: 20px;
}

label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #333;
}

input, select, textarea {
    width: 100%;
    padding: 12px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.3s;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: #667eea;
}

.btn-primary {
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.form-note {
    margin-top: 15px;
    font-size: 14px;
    color: #666;
    text-align: center;
}
```

---

## 📊 Tracking de Conversiones

### Google Analytics Events:

```javascript
// Trackear envío de formulario
document.getElementById('roiForm').addEventListener('submit', function(e) {
    // Google Analytics
    gtag('event', 'form_submit', {
        'event_category': 'ROI Calculator',
        'event_label': 'ROI Form'
    });
    
    // Facebook Pixel
    fbq('track', 'Lead');
    
    // Custom tracking
    // ...
});
```

---

## ✅ Checklist de Formularios

### Pre-Lanzamiento:
- [ ] Formulario simple (máximo 3 campos)
- [ ] Validación de campos
- [ ] Mensajes de error claros
- [ ] Mensaje de éxito visible
- [ ] Mobile responsive
- [ ] Tracking configurado
- [ ] Test de envío

### Post-Lanzamiento:
- [ ] Monitorear tasa de conversión
- [ ] A/B test de campos
- [ ] Optimizar basado en datos
- [ ] Reducir fricción

---

**Formularios optimizados listos para maximizar conversión.** 🚀

