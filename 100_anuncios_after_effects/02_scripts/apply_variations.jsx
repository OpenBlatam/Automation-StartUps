// Apply Variations Script
// Aplica diferentes variaciones de color y estilo a los anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Apply Variations");
    
    var comps = app.project.items;
    
    // Definir variaciones de color y estilo
    var variations = [
        {
            name: "Estadística",
            bgColor: [0.18, 0.16, 0.20, 1], // Azul oscuro
            textColor: [1, 1, 1, 1],
            accentColor: [0.18, 0.53, 0.87, 1] // Azul brillante
        },
        {
            name: "Comparación",
            bgColor: [0.97, 0.97, 0.98, 1], // Blanco
            textColor: [0.1, 0.1, 0.1, 1],
            accentColor: [0.0, 0.8, 0.4, 1] // Verde
        },
        {
            name: "Pregunta",
            bgColor: [0.1, 0.1, 0.15, 1], // Negro azulado
            textColor: [1, 1, 1, 1],
            accentColor: [1.0, 0.2, 0.2, 1] // Rojo
        },
        {
            name: "Secreto",
            bgColor: [0.15, 0.12, 0.18, 1], // Púrpura oscuro
            textColor: [1, 1, 1, 1],
            accentColor: [0.42, 0.36, 0.91, 1] // Púrpura
        },
        {
            name: "Transformación",
            bgColor: [0.97, 0.95, 0.9, 1], // Beige claro
            textColor: [0.1, 0.1, 0.1, 1],
            accentColor: [1.0, 0.84, 0.0, 1] // Dorado
        }
    ];
    
    var compCount = 0;
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            compCount++;
            var comp = comps[i];
            var variation = variations[compCount % variations.length];
            
            // Buscar y actualizar background layer
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                if (layer.name === "Background" && layer instanceof AVLayer) {
                    // Cambiar color del solid
                    try {
                        var solid = layer.source;
                        if (solid instanceof FootageItem && solid.mainSource instanceof SolidSource) {
                            solid.mainSource.color = variation.bgColor;
                        }
                    } catch (e) {
                        // Si no se puede cambiar, crear nuevo solid
                        layer.remove();
                        var newBg = comp.layers.addSolid(
                            variation.bgColor,
                            "Background",
                            comp.width,
                            comp.height,
                            1
                        );
                        newBg.moveToEnd();
                    }
                }
                
                // Actualizar color de texto
                if (layer instanceof TextLayer) {
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc) {
                            textDoc.fillColor = variation.textColor;
                            textProp.setValue(textDoc);
                        }
                    }
                }
                
                // Actualizar color de CTA button
                if (layer.name === "CTA_Button") {
                    try {
                        var contents = layer.property("Contents");
                        if (contents) {
                            var group = contents.property("ADBE Vector Group");
                            if (group) {
                                var fill = group.property("Contents").property("ADBE Vector Graphic - Fill");
                                if (fill) {
                                    fill.property("Color").setValue(variation.accentColor);
                                }
                            }
                        }
                    } catch (e) {
                        // Continuar si hay error
                    }
                }
            }
        }
    }
    
    alert("✅ Aplicadas variaciones a " + compCount + " composiciones!");
    
    app.endUndoGroup();
})();


