// Auto Optimize CTA Script
// Optimiza automáticamente los CTAs basado en mejores prácticas
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Auto Optimize CTA");
    
    var comps = app.project.items;
    var optimized = 0;
    
    // Mejores prácticas de CTAs
    var ctaBestPractices = {
        minSize: [360, 112], // Tamaño mínimo recomendado
        optimalPosition: { x: 0.5, y: 0.88 }, // 88% desde arriba (centro inferior)
        colors: {
            highContrast: [
                [0.0, 0.8, 0.4, 1],  // Verde
                [1.0, 0.2, 0.2, 1],   // Rojo
                [0.18, 0.53, 0.87, 1] // Azul
            ]
        },
        fonts: ["Poppins-Bold", "Montserrat-Bold", "Inter-Bold"],
        animation: "pulse" // Tipo de animación recomendada
    };
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var ctaOptimized = false;
            
            // Buscar CTA button y texto
            var ctaButton = null;
            var ctaText = null;
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                if (layer.name === "CTA_Button" || layer.name.indexOf("CTA_Button") !== -1) {
                    ctaButton = layer;
                }
                
                if (layer instanceof TextLayer && layer.name.indexOf("CTA") !== -1) {
                    ctaText = layer;
                }
            }
            
            // Optimizar CTA button
            if (ctaButton) {
                // Verificar y ajustar tamaño
                try {
                    var contents = ctaButton.property("Contents");
                    var group = contents.property("ADBE Vector Group");
                    if (group) {
                        var rect = group.property("Contents").property("ADBE Vector Shape - Rect");
                        if (rect) {
                            var currentSize = rect.property("Size").value;
                            var minSize = ctaBestPractices.minSize;
                            
                            if (currentSize[0] < minSize[0] || currentSize[1] < minSize[1]) {
                                rect.property("Size").setValue([
                                    Math.max(currentSize[0], minSize[0]),
                                    Math.max(currentSize[1], minSize[1])
                                ]);
                                ctaOptimized = true;
                            }
                        }
                    }
                } catch (e) {
                    // Continuar si hay error
                }
                
                // Optimizar posición
                var currentPos = ctaButton.property("Position").value;
                var optimalY = comp.height * ctaBestPractices.optimalPosition.y;
                var optimalX = comp.width * ctaBestPractices.optimalPosition.x;
                
                if (Math.abs(currentPos[1] - optimalY) > 50) {
                    ctaButton.property("Position").setValue([optimalX, optimalY]);
                    ctaOptimized = true;
                }
                
                // Asegurar color de alto contraste
                try {
                    var contents = ctaButton.property("Contents");
                    var group = contents.property("ADBE Vector Group");
                    if (group) {
                        var fill = group.property("Contents").property("ADBE Vector Graphic - Fill");
                        if (fill) {
                            var currentColor = fill.property("Color").value;
                            // Verificar contraste (simplificado)
                            var brightness = (currentColor[0] + currentColor[1] + currentColor[2]) / 3;
                            if (brightness < 0.3 || brightness > 0.7) {
                                // Usar color de alto contraste
                                var newColor = ctaBestPractices.colors.highContrast[i % ctaBestPractices.colors.highContrast.length];
                                fill.property("Color").setValue(newColor);
                                ctaOptimized = true;
                            }
                        }
                    }
                } catch (e) {
                    // Continuar si hay error
                }
                
                // Añadir animación de pulso si no existe
                var scaleProp = ctaButton.property("Scale");
                if (!scaleProp.expressionEnabled) {
                    scaleProp.expression = "freq = 0.67;\namp = 5;\nvalue + Math.sin(time * freq * Math.PI * 2) * amp;";
                    scaleProp.expressionEnabled = true;
                    ctaOptimized = true;
                }
            }
            
            // Optimizar texto CTA
            if (ctaText) {
                var textProp = ctaText.property("Source Text");
                if (textProp) {
                    var textDoc = textProp.value;
                    
                    // Verificar tamaño de fuente (mínimo 48px)
                    if (textDoc.fontSize < 48) {
                        textDoc.fontSize = 48;
                        textProp.setValue(textDoc);
                        ctaOptimized = true;
                    }
                    
                    // Asegurar fuente bold
                    if (textDoc.font.indexOf("Bold") === -1 && textDoc.font.indexOf("Black") === -1) {
                        textDoc.font = ctaBestPractices.fonts[0];
                        textProp.setValue(textDoc);
                        ctaOptimized = true;
                    }
                    
                    // Asegurar color blanco para contraste
                    var textColor = textDoc.fillColor;
                    if (textColor[0] < 0.9 || textColor[1] < 0.9 || textColor[2] < 0.9) {
                        textDoc.fillColor = [1, 1, 1, 1]; // Blanco
                        textProp.setValue(textDoc);
                        ctaOptimized = true;
                    }
                }
            }
            
            if (ctaOptimized) optimized++;
        }
    }
    
    alert("✅ Optimizados " + optimized + " CTAs!\n\nMejoras aplicadas:\n" +
          "• Tamaño mínimo garantizado\n" +
          "• Posición optimizada\n" +
          "• Colores de alto contraste\n" +
          "• Animación de pulso\n" +
          "• Tipografía mejorada");
    
    app.endUndoGroup();
})();


