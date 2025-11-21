// Smart Color Palette Script
// Aplica paletas de color inteligentes basadas en psicología del color
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Smart Color Palette");
    
    var comps = app.project.items;
    var palettesApplied = 0;
    
    // Paletas de color por objetivo psicológico
    var colorPalettes = {
        "trust": {
            name: "Confianza",
            primary: [0.18, 0.53, 0.87, 1],    // Azul confianza
            secondary: [0.09, 0.16, 0.27, 1],  // Azul oscuro
            accent: [0.0, 0.8, 0.4, 1],       // Verde éxito
            text: [1, 1, 1, 1]                 // Blanco
        },
        "energy": {
            name: "Energía",
            primary: [1.0, 0.2, 0.2, 1],      // Rojo energía
            secondary: [1.0, 0.84, 0.0, 1],   // Dorado
            accent: [1.0, 0.42, 0.0, 1],      // Naranja
            text: [1, 1, 1, 1]
        },
        "growth": {
            name: "Crecimiento",
            primary: [0.0, 0.8, 0.4, 1],       // Verde crecimiento
            secondary: [0.0, 0.6, 0.3, 1],     // Verde oscuro
            accent: [1.0, 0.84, 0.0, 1],      // Dorado
            text: [0.1, 0.1, 0.1, 1]          // Negro
        },
        "premium": {
            name: "Premium",
            primary: [0.42, 0.36, 0.91, 1],   // Púrpura premium
            secondary: [0.15, 0.12, 0.18, 1],  // Púrpura oscuro
            accent: [1.0, 0.84, 0.0, 1],      // Dorado
            text: [1, 1, 1, 1]
        },
        "calm": {
            name: "Calma",
            primary: [0.4, 0.7, 0.9, 1],      // Azul claro
            secondary: [0.2, 0.5, 0.7, 1],      // Azul medio
            accent: [0.0, 0.8, 0.4, 1],       // Verde
            text: [0.1, 0.1, 0.1, 1]
        }
    };
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var compName = comp.name.toLowerCase();
            
            // Determinar paleta basada en categoría
            var paletteKey = "trust"; // Default
            if (compName.indexOf("conversion") !== -1 || compName.indexOf("venta") !== -1) {
                paletteKey = "energy";
            } else if (compName.indexOf("growth") !== -1 || compName.indexOf("crecimiento") !== -1) {
                paletteKey = "growth";
            } else if (compName.indexOf("premium") !== -1 || compName.indexOf("vip") !== -1) {
                paletteKey = "premium";
            } else if (compName.indexOf("education") !== -1 || compName.indexOf("tutorial") !== -1) {
                paletteKey = "calm";
            }
            
            var palette = colorPalettes[paletteKey];
            
            // Aplicar paleta
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                // Background
                if (layer.name === "Background") {
                    try {
                        var solid = layer.source;
                        if (solid instanceof FootageItem && solid.mainSource instanceof SolidSource) {
                            solid.mainSource.color = palette.secondary;
                        }
                    } catch (e) {
                        // Continuar si hay error
                    }
                }
                
                // CTA Button
                if (layer.name === "CTA_Button") {
                    try {
                        var contents = layer.property("Contents");
                        var group = contents.property("ADBE Vector Group");
                        if (group) {
                            var fill = group.property("Contents").property("ADBE Vector Graphic - Fill");
                            if (fill) {
                                fill.property("Color").setValue(palette.primary);
                            }
                        }
                    } catch (e) {
                        // Continuar si hay error
                    }
                }
                
                // Texto principal
                if (layer instanceof TextLayer && layer.name.indexOf("Hook") !== -1) {
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc) {
                            textDoc.fillColor = palette.text;
                            textProp.setValue(textDoc);
                        }
                    }
                }
            }
            
            palettesApplied++;
        }
    }
    
    alert("✅ Aplicadas " + palettesApplied + " paletas de color inteligentes!\n\n" +
          "Paletas aplicadas según categoría:\n" +
          "• Confianza (azul)\n" +
          "• Energía (rojo/dorado)\n" +
          "• Crecimiento (verde)\n" +
          "• Premium (púrpura/dorado)\n" +
          "• Calma (azul claro)");
    
    app.endUndoGroup();
})();

