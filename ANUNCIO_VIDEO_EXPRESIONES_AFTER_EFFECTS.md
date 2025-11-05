# Expresiones After Effects — Animaciones Automáticas

> Código listo para copiar/pegar en After Effects para animar tus SVG 1080×1920.

---

## 🎬 Expresiones por Tipo de Animación

### 1. Counter Numérico (Métricas)

**Aplicar a**: Text layer con métrica (+27%, -32%, etc.)

**Expresión**:
```javascript
// Counter con ease-out
n = 0;
if (time >= 5.0) { // Iniciar en 5 segundos
  dur = 1.0; // Duración 1 segundo
  startTime = 5.0;
  endValue = 27; // Valor final (cambiar según métrica)
  progress = Math.min((time - startTime) / dur, 1);
  
  // Ease-out function
  easeOut = function(t) {
    return 1 - Math.pow(1 - t, 3);
  };
  
  if (progress <= 1) {
    n = Math.round(easeOut(progress) * endValue);
  } else {
    n = endValue;
  }
}
prefix = "+"; // o "-" para negativo
suffix = "%";
prefix + n + suffix;
```

**Variante con signo negativo**:
```javascript
// Para -32% CPA
endValue = -32;
prefix = "";
// (el signo va en el número)
```

---

### 2. Pulso Continuo (CTA Button)

**Aplicar a**: Scale property del CTA

**Expresión**:
```javascript
// Pulso suave desde tiempo de aparición
startTime = 9.4; // Cuando aparece el CTA
freq = 1.5; // Frecuencia: 1 ciclo cada 1.5 segundos
amp = 5; // Amplitud: 5% de scale
baseScale = 100;

if (time >= startTime) {
  baseScale + Math.sin((time - startTime) * 2 * Math.PI / freq) * amp;
} else {
  [80, 80]; // Scale inicial (0.8x)
}
```

---

### 3. Fade-in con Slide-up

**Aplicar a**: Position + Opacity de cualquier elemento

**Expresión Position Y**:
```javascript
startTime = 2.0; // Cuándo inicia
dur = 0.5; // Duración animación
startY = 470; // Posición inicial (más abajo)
endY = 440; // Posición final

if (time < startTime) {
  [value[0], startY];
} else if (time < startTime + dur) {
  progress = (time - startTime) / dur;
  easeOut = 1 - Math.pow(1 - progress, 3);
  [value[0], startY + (endY - startY) * easeOut];
} else {
  [value[0], endY];
}
```

**Expresión Opacity** (en mismo elemento):
```javascript
startTime = 2.0;
dur = 0.5;

if (time < startTime) {
  0;
} else if (time < startTime + dur) {
  ((time - startTime) / dur) * 100;
} else {
  100;
}
```

---

### 4. Slide-right (Testimonial)

**Aplicar a**: Position X del testimonial box

**Expresión**:
```javascript
startTime = 7.0;
dur = 0.4;
startX = 490; // X -50px (fuera de pantalla)
endX = 540; // X centrado

if (time < startTime) {
  [startX, value[1]];
} else if (time < startTime + dur) {
  progress = (time - startTime) / dur;
  easeOut = 1 - Math.pow(1 - progress, 2);
  [startX + (endX - startX) * easeOut, value[1]];
} else {
  [endX, value[1]];
}
```

---

### 5. Scale con Glow (Headline Accent)

**Aplicar a**: Scale + efecto Glow del "+20%"

**Expresión Scale**:
```javascript
startTime = 2.5;
dur = 0.4;
startScale = 80; // 0.8x
endScale = 100; // 1.0x

if (time < startTime) {
  [startScale, startScale];
} else if (time < startTime + dur) {
  progress = (time - startTime) / dur;
  easeOut = 1 - Math.pow(1 - progress, 2);
  scale = startScale + (endScale - startScale) * easeOut;
  [scale, scale];
} else {
  [endScale, endScale];
}
```

**Glow Effect** (aplicar efecto nativo de AE):
- Glow Intensity: `linear(time, 2.5, 2.9, 0, 150)`
- Glow Radius: `linear(time, 2.5, 2.9, 0, 30)`
- Glow Colors: A & B Colors
- Color A: `#3B82F6` (accent)

---

### 6. Barras Creciendo (Growth Chart)

**Aplicar a**: Scale Y de cada barra

**Expresión Barra 1** (izquierda):
```javascript
startTime = 13.0;
dur = 0.5;

if (time < startTime) {
  0;
} else if (time < startTime + dur) {
  easeOut = 1 - Math.pow(1 - (time - startTime) / dur, 2);
  easeOut * 100;
} else {
  100;
}
```

**Expresión Barra 2** (centro, delay 0.2s):
```javascript
startTime = 13.2; // Delay 0.2s
dur = 0.5;
// (resto igual)
```

**Expresión Barra 3** (derecha, delay 0.4s):
```javascript
startTime = 13.4; // Delay 0.4s
dur = 0.5;
// (resto igual)
```

---

### 7. Opacity Secuencial (Múltiples Elementos)

**Para métricas que aparecen una después de otra**:

**Expresión Métrica 1** (+27% Leads):
```javascript
startTime = 5.0;
dur = 0.3;

linear(time, startTime, startTime + dur, 0, 100);
```

**Expresión Métrica 2** (-32% CPA):
```javascript
startTime = 5.5; // Delay 0.5s después de primera
dur = 0.3;

linear(time, startTime, startTime + dur, 0, 100);
```

---

### 8. Ease-out Helper Function

**Función reutilizable** (añadir al inicio de cualquier expresión):
```javascript
// Ease-out cubic
easeOut = function(t) {
  return 1 - Math.pow(1 - t, 3);
};

// Uso:
progress = (time - startTime) / dur;
easedProgress = easeOut(progress);
```

**Variantes**:
```javascript
// Ease-in-out
easeInOut = function(t) {
  return t < 0.5 
    ? 2 * t * t 
    : 1 - Math.pow(-2 * t + 2, 2) / 2;
};

// Ease-in
easeIn = function(t) {
  return t * t;
};
```

---

## 📋 Aplicación Rápida en After Effects

### Paso 1: Seleccionar Capa
- Clic en la propiedad (Position, Scale, Opacity, etc.)
- Cmd/Ctrl + Alt + = (abrir expresión)

### Paso 2: Pegar Expresión
- Borrar contenido por defecto
- Pegar expresión correspondiente
- Ajustar `startTime` y valores según timing

### Paso 3: Ajustar Valores
- Cambiar `startTime` según storyboard
- Cambiar `endValue` (para counters)
- Cambiar `dur` (duración animación)

---

## 🎯 Timing de Referencia (Usar en Expresiones)

Basado en storyboard de `ANUNCIO_VIDEO_SVG_TO_VIDEO_STORYBOARD.md`:

| Elemento | startTime | dur | endValue |
|----------|-----------|-----|----------|
| Logo | 0.0 | 0.3 | - |
| Eyebrow | 1.0 | 0.4 | - |
| Headline | 2.0 | 0.5 | - |
| Headline-accent | 2.5 | 0.4 | - |
| Métrica 1 | 5.0 | 1.0 | 27 |
| Métrica 2 | 5.5 | 1.0 | -32 |
| Testimonial | 7.0 | 0.4 | - |
| CTA | 9.0 | 0.4 | - |
| Badge | 11.0 | 0.3 | - |
| Growth chart | 13.0 | 0.5 | - |

---

## ✅ Checklist de Aplicación

- [ ] Expresiones aplicadas a todas las propiedades animadas
- [ ] `startTime` ajustado según storyboard
- [ ] Valores (`endValue`, posiciones) verificados
- [ ] Easing aplicado (ease-out recomendado)
- [ ] Preview: Animaciones suaves, sin saltos
- [ ] Timing total: 15s exactos

---

## 🚀 Expresión Todo-en-Uno (Avanzado)

**Para capa completa con múltiples animaciones**:

```javascript
// Configuración centralizada
config = {
  logoStart: 0.0,
  eyebrowStart: 1.0,
  headlineStart: 2.0,
  metricsStart: 5.0,
  testimonialStart: 7.0,
  ctaStart: 9.0,
  badgeStart: 11.0
};

// Helper functions
easeOut = function(t) {
  return 1 - Math.pow(1 - t, 3);
};

// Aplicar según nombre de capa
layerName = thisLayer.name.toLowerCase();

if (layerName.indexOf("logo") >= 0) {
  // Logo animation
  linear(time, config.logoStart, config.logoStart + 0.3, 0, 100);
} else if (layerName.indexOf("eyebrow") >= 0) {
  // Eyebrow animation
  // (aplicar en Position Y)
} else if (layerName.indexOf("headline") >= 0) {
  // Headline animation
  // (aplicar según caso)
}
// ... etc
```

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Compatible con**: After Effects CC 2018+



