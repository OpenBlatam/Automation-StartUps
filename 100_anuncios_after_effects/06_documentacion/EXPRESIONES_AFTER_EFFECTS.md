# 🎬 Expresiones Útiles para After Effects

> Colección de expresiones para animar los 100 anuncios

---

## 📐 Expresiones de Animación

### Pulso Continuo (para CTA)

**Aplicar a:** Scale property

```javascript
// Pulso suave cada 1.5 segundos
freq = 0.67; // frecuencia
amp = 5; // amplitud en porcentaje
value + Math.sin(time * freq * Math.PI * 2) * amp;
```

**Variante - Pulso más rápido:**
```javascript
freq = 1; // 1 segundo
amp = 3;
value + Math.sin(time * freq * Math.PI * 2) * amp;
```

---

### Fade In Suave

**Aplicar a:** Opacity property

```javascript
// Fade in en 0.5 segundos
ease(time, inPoint, inPoint + 0.5, 0, 100);
```

**Variante - Fade in más lento:**
```javascript
ease(time, inPoint, inPoint + 1, 0, 100);
```

---

### Slide Up

**Aplicar a:** Position property (Y)

```javascript
// Slide desde abajo
startY = 2200;
endY = 960;
ease(time, inPoint, inPoint + 0.5, startY, endY);
```

**Variante - Slide desde arriba:**
```javascript
startY = -200;
endY = 960;
ease(time, inPoint, inPoint + 0.5, startY, endY);
```

---

### Slide Horizontal

**Aplicar a:** Position property (X)

```javascript
// Slide desde izquierda
startX = -500;
endX = 540;
ease(time, inPoint, inPoint + 0.5, startX, endX);
```

---

### Zoom In

**Aplicar a:** Scale property

```javascript
// Zoom desde 80% a 100%
ease(time, inPoint, inPoint + 0.5, [80, 80], [100, 100]);
```

**Variante - Zoom dramático:**
```javascript
ease(time, inPoint, inPoint + 0.8, [50, 50], [100, 100]);
```

---

### Rotación Continua

**Aplicar a:** Rotation property

```javascript
// Rotación lenta continua
time * 10; // 10 grados por segundo
```

**Variante - Rotación más rápida:**
```javascript
time * 30; // 30 grados por segundo
```

---

## 🎨 Expresiones de Efectos

### Glow Pulsante

**Aplicar a:** Glow > Intensity

```javascript
// Glow que pulsa
baseIntensity = 2;
pulse = Math.sin(time * 2) * 0.5;
baseIntensity + pulse;
```

---

### Blur Dinámico

**Aplicar a:** Fast Blur > Blurriness

```javascript
// Blur que se desvanece
ease(time, inPoint, inPoint + 1, 20, 0);
```

---

### Color Shift

**Aplicar a:** Color Balance > Midtones

```javascript
// Cambio de color gradual
shift = Math.sin(time * 0.5) * 10;
[shift, 0, -shift];
```

---

## 🔢 Expresiones de Contadores

### Contador Numérico

**Aplicar a:** Text > Source Text

```javascript
// Contador de 0 a 2000 en 3 segundos
startValue = 0;
endValue = 2000;
duration = 3;
currentValue = Math.floor(ease(time, inPoint, inPoint + duration, startValue, endValue));
currentValue.toLocaleString();
```

**Variante - Con símbolo:**
```javascript
startValue = 0;
endValue = 2000;
duration = 3;
currentValue = Math.floor(ease(time, inPoint, inPoint + duration, startValue, endValue));
"+" + currentValue.toLocaleString();
```

---

### Contador de Dinero

**Aplicar a:** Text > Source Text

```javascript
// Contador de $5,000 a $50,000
startValue = 5000;
endValue = 50000;
duration = 3;
currentValue = Math.floor(ease(time, inPoint, inPoint + duration, startValue, endValue));
"$" + currentValue.toLocaleString();
```

---

### Contador de Porcentaje

**Aplicar a:** Text > Source Text

```javascript
// Contador de 0% a 90%
startValue = 0;
endValue = 90;
duration = 2;
currentValue = Math.floor(ease(time, inPoint, inPoint + duration, startValue, endValue));
currentValue + "%";
```

---

## ⏱️ Expresiones de Timing

### Delay Simple

**Aplicar a:** Cualquier propiedad

```javascript
// Delay de 1 segundo
delay = 1;
if (time >= delay) {
    value;
} else {
    0; // o valor inicial
}
```

---

### Loop de Animación

**Aplicar a:** Cualquier propiedad animada

```javascript
// Loop cada 2 segundos
loopTime = 2;
t = time % loopTime;
// Usar 't' en lugar de 'time' en tu animación
```

---

### Trigger en Tiempo Específico

**Aplicar a:** Opacity o cualquier propiedad

```javascript
// Aparece a los 12 segundos
triggerTime = 12;
if (time >= triggerTime) {
    100; // valor final
} else {
    0; // valor inicial
}
```

---

## 🎯 Expresiones Avanzadas

### Seguir Mouse (para interactividad)

**Aplicar a:** Position property

```javascript
// Seguir posición del mouse (requiere plugin o expresión avanzada)
// Nota: Esto requiere configuración adicional
```

---

### Efecto Parallax

**Aplicar a:** Position property

```javascript
// Movimiento parallax basado en posición de otra capa
parentLayer = thisComp.layer("Control Layer");
offset = 0.1; // intensidad del parallax
[value[0] + (parentLayer.position[0] - 540) * offset, value[1]];
```

---

### Oscilación Suave

**Aplicar a:** Position o cualquier propiedad

```javascript
// Oscilación tipo péndulo
amplitude = 50;
frequency = 1;
value + Math.sin(time * frequency * Math.PI * 2) * amplitude;
```

---

## 📚 Recursos Adicionales

### Funciones Útiles

```javascript
// Ease in out
function easeInOut(t, b, c, d) {
    t /= d/2;
    if (t < 1) return c/2*t*t + b;
    t--;
    return -c/2 * (t*(t-2) - 1) + b;
}

// Bounce
function bounce(t, b, c, d) {
    if ((t/=d) < (1/2.75)) {
        return c*(7.5625*t*t) + b;
    } else if (t < (2/2.75)) {
        return c*(7.5625*(t-=(1.5/2.75))*t + .75) + b;
    } else if (t < (2.5/2.75)) {
        return c*(7.5625*(t-=(2.25/2.75))*t + .9375) + b;
    } else {
        return c*(7.5625*(t-=(2.625/2.75))*t + .984375) + b;
    }
}
```

---

## 💡 Tips de Uso

1. **Copiar y pegar:** Selecciona la propiedad, presiona Alt/Option y haz clic en el cronómetro
2. **Editar:** Haz doble clic en la expresión para editarla
3. **Desactivar:** Presiona el botón "=" para desactivar temporalmente
4. **Comentarios:** Usa `//` para comentar código
5. **Debugging:** Usa `value` para ver el valor actual

---

**¡Expresiones listas para usar! 🚀**


