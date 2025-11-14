# 🎨 Recursos de Diseño Visual

## 🎯 Elementos Visuales para Emails

### 1. Headers Visuales

**Opción 1: Gradiente Moderno**
```html
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 30px; 
            text-align: center; 
            border-radius: 8px 8px 0 0;">
    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">
        El Cálculo que Nadie Hace
    </h1>
</div>
```

**Opción 2: Minimalista**
```html
<div style="border-left: 4px solid #27ae60; 
            padding: 20px; 
            background: #f8f9fa;">
    <h1 style="color: #333; margin: 0; font-size: 24px;">
        Tu ROI Personalizado
    </h1>
</div>
```

---

### 2. Cajas de Destacado

**ROI Box:**
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" 
       style="background-color: #f8f9fa; 
              border-left: 4px solid #27ae60; 
              padding: 20px; 
              margin: 20px 0; 
              border-radius: 4px;">
    <tr>
        <td>
            <h2 style="color: #333; font-size: 20px; margin: 0 0 15px 0;">
                Tu ROI Personalizado
            </h2>
            <table role="presentation" width="100%">
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
                        <span style="color: #666;">Sin IA:</span>
                        <strong style="color: #333; float: right;">60 hrs/mes = $1,200</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;">
                        <span style="color: #27ae60; font-size: 18px; font-weight: bold;">
                            Ahorro: $800/mes = $9,360/año
                        </span>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
```

**Testimonial Box:**
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" 
       style="background-color: #ffffff; 
              border: 2px solid #e0e0e0; 
              padding: 25px; 
              margin: 20px 0; 
              border-radius: 8px;">
    <tr>
        <td>
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <img src="{foto_cliente}" 
                     alt="{nombre_cliente}" 
                     style="width: 60px; height: 60px; border-radius: 50%; margin-right: 15px;">
                <div>
                    <strong style="color: #333; font-size: 16px;">
                        {nombre_cliente}
                    </strong><br>
                    <span style="color: #666; font-size: 14px;">
                        {rol}, {empresa}
                    </span>
                </div>
            </div>
            <p style="color: #333; font-size: 16px; line-height: 1.6; margin: 0; font-style: italic;">
                "{testimonial_texto}"
            </p>
        </td>
    </tr>
</table>
```

---

### 3. Botones CTA

**Estilo 1: Gradiente**
```html
<a href="{link}" 
   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
          color: #ffffff; 
          padding: 15px 40px; 
          text-decoration: none; 
          border-radius: 8px; 
          font-weight: bold; 
          font-size: 16px; 
          display: inline-block; 
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
    📅 Agendar llamada de 15 min
</a>
```

**Estilo 2: Simple**
```html
<a href="{link}" 
   style="background-color: #27ae60; 
          color: #ffffff; 
          padding: 14px 32px; 
          text-decoration: none; 
          border-radius: 6px; 
          font-weight: 600; 
          font-size: 16px; 
          display: inline-block;">
    Calcular mi ROI
</a>
```

**Estilo 3: Urgencia**
```html
<a href="{link}" 
   style="background-color: #e74c3c; 
          color: #ffffff; 
          padding: 16px 36px; 
          text-decoration: none; 
          border-radius: 8px; 
          font-weight: bold; 
          font-size: 18px; 
          display: inline-block; 
          animation: pulse 2s infinite;">
    ⏰ Aprovechar Oferta - Solo {X} días
</a>
```

---

### 4. Iconos y Emojis

**Iconos para Emails:**
```
📊 ROI/Análisis
💰 Ahorro/Dinero
⏰ Urgencia/Tiempo
✅ Beneficios/Check
📈 Crecimiento/Tendencias
🎯 Objetivos/Metas
💡 Ideas/Insights
🔥 Urgencia/Caliente
```

**Uso Recomendado:**
- Máximo 2-3 emojis por email
- Usar en CTAs y puntos clave
- Evitar exceso

---

### 5. Barras de Progreso

**Barra de Plazas:**
```html
<div style="background-color: #f0f0f0; 
            border-radius: 10px; 
            height: 30px; 
            margin: 20px 0; 
            position: relative; 
            overflow: hidden;">
    <div style="background: linear-gradient(90deg, #e74c3c 0%, #c0392b 100%); 
                height: 100%; 
                width: 80%; 
                border-radius: 10px; 
                display: flex; 
                align-items: center; 
                justify-content: center;">
        <span style="color: white; font-weight: bold; font-size: 14px;">
            8 de 10 plazas ocupadas
        </span>
    </div>
</div>
```

---

### 6. Countdown Timers

**Countdown Visual:**
```html
<div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
            margin: 20px 0;">
    <div style="font-size: 48px; font-weight: bold; color: white; margin-bottom: 10px;">
        <span id="days">2</span>d 
        <span id="hours">14</span>h 
        <span id="minutes">32</span>m 
        <span id="seconds">15</span>s
    </div>
    <div style="color: white; font-size: 16px;">
        Oferta cierra en
    </div>
</div>
```

---

## 🎨 Paleta de Colores Recomendada

### Colores Principales:

```css
/* Primario */
--primary: #667eea;
--primary-dark: #5568d3;

/* Secundario */
--secondary: #764ba2;
--secondary-dark: #5a3a7a;

/* Éxito/Verde */
--success: #27ae60;
--success-dark: #229954;

/* Urgencia/Rojo */
--urgent: #e74c3c;
--urgent-dark: #c0392b;

/* Neutros */
--text: #333333;
--text-light: #666666;
--text-lighter: #999999;
--bg: #f8f9fa;
--border: #e0e0e0;
```

---

## 📱 Diseño Responsive

### Media Queries:

```css
@media only screen and (max-width: 600px) {
    .container {
        width: 100% !important;
        padding: 10px !important;
    }
    
    h1 {
        font-size: 24px !important;
    }
    
    .btn {
        width: 100% !important;
        padding: 12px !important;
    }
    
    table {
        width: 100% !important;
    }
}
```

---

## 🎯 Elementos Visuales por Email

### Email #1 (ROI):

**Elementos:**
- Caja de ROI destacada
- Iconos: 📊 💰
- Colores: Verde (éxito)
- Números grandes y claros

### Email #2 (Social Proof):

**Elementos:**
- Foto del cliente
- Cita destacada
- Iconos: ✅ 🎯
- Colores: Azul (confianza)

### Email #3 (Urgencia):

**Elementos:**
- Countdown timer
- Barra de progreso
- Iconos: ⏰ 🔥
- Colores: Rojo (urgencia)

---

## 📊 Infografías para Emails

### Infografía de ROI:

```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
        <td align="center" style="padding: 20px;">
            <table role="presentation" width="500" cellpadding="0" cellspacing="0" 
                   style="background: #f8f9fa; border-radius: 8px; padding: 20px;">
                <tr>
                    <td align="center">
                        <div style="font-size: 48px; font-weight: bold; color: #e74c3c;">
                            $9,360
                        </div>
                        <div style="font-size: 18px; color: #666; margin-top: 10px;">
                            Ahorro Anual
                        </div>
                    </td>
                </tr>
                <tr>
                    <td style="padding-top: 20px; border-top: 2px solid #e0e0e0;">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <div style="font-size: 24px; font-weight: bold; color: #333;">
                                    60h
                                </div>
                                <div style="font-size: 14px; color: #666;">
                                    Sin IA
                                </div>
                            </div>
                            <div style="font-size: 32px; color: #999;">
                                →
                            </div>
                            <div>
                                <div style="font-size: 24px; font-weight: bold; color: #27ae60;">
                                    20h
                                </div>
                                <div style="font-size: 14px; color: #666;">
                                    Con IA
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
```

---

## ✅ Checklist de Diseño

### Pre-Envío:

- [ ] Diseño responsive (mobile-first)
- [ ] Colores consistentes
- [ ] Tipografía legible
- [ ] Imágenes optimizadas
- [ ] CTAs visibles
- [ ] Test en diferentes clientes de email
- [ ] Verificar en móvil
- [ ] Verificar en desktop

### Post-Envío:

- [ ] Monitorear tasa de renderizado
- [ ] A/B test de diseños
- [ ] Optimizar basado en datos
- [ ] Documentar aprendizajes

---

**Recursos de diseño visual completos para emails profesionales.** 🎨

