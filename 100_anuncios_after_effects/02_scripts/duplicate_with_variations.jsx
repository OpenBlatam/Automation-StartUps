// Duplicate With Variations Script
// Duplica anuncios con variaciones automáticas (texto, color, timing)
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Duplicate With Variations");
    
    var comps = app.project.items;
    var duplicated = 0;
    
    // Configuración de variaciones
    var variationConfig = {
        textVariations: [
            { search: "hoy", replace: "ahora" },
            { search: "gratis", replace: "sin costo" },
            { search: "únete", replace: "inscríbete" }
        ],
        colorVariations: [
            [0.18, 0.53, 0.87, 1], // Azul
            [0.0, 0.8, 0.4, 1],    // Verde
            [1.0, 0.2, 0.2, 1],    // Rojo
            [1.0, 0.84, 0.0, 1]    // Dorado
        ],
        timingVariations: [
            { offset: -0.5 }, // Aparece 0.5s antes
            { offset: 0.5 },  // Aparece 0.5s después
            { offset: 0 }     // Sin cambio
        ]
    };
    
    // Crear array de composiciones originales
    var originalComps = [];
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && 
            comps[i].name.indexOf("Comp_") === 0 &&
            comps[i].name.indexOf("_V") === -1) { // Excluir variantes existentes
            originalComps.push(comps[i]);
        }
    }
    
    // Crear variaciones
    for (var i = 0; i < originalComps.length; i++) {
        var originalComp = originalComps[i];
        
        // Crear 2 variaciones por anuncio
        for (var v = 1; v <= 2; v++) {
            var variantComp = originalComp.duplicate();
            variantComp.name = originalComp.name + "_V" + v;
            
            // Aplicar variación de texto
            var textVar = variationConfig.textVariations[v % variationConfig.textVariations.length];
            for (var j = 1; j <= variantComp.layers.length; j++) {
                var layer = variantComp.layers[j];
                if (layer instanceof TextLayer) {
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc && textDoc.text) {
                            var newText = textDoc.text.replace(
                                new RegExp(textVar.search, "gi"),
                                textVar.replace
                            );
                            if (newText !== textDoc.text) {
                                textDoc.text = newText;
                                textProp.setValue(textDoc);
                            }
                        }
                    }
                }
            }
            
            // Aplicar variación de color
            var colorVar = variationConfig.colorVariations[v % variationConfig.colorVariations.length];
            for (var j = 1; j <= variantComp.layers.length; j++) {
                var layer = variantComp.layers[j];
                if (layer.name === "CTA_Button") {
                    try {
                        var contents = layer.property("Contents");
                        var group = contents.property("ADBE Vector Group");
                        if (group) {
                            var fill = group.property("Contents").property("ADBE Vector Graphic - Fill");
                            if (fill) {
                                fill.property("Color").setValue(colorVar);
                            }
                        }
                    } catch (e) {
                        // Continuar si hay error
                    }
                }
            }
            
            // Aplicar variación de timing
            var timingVar = variationConfig.timingVariations[v % variationConfig.timingVariations.length];
            for (var j = 1; j <= variantComp.layers.length; j++) {
                var layer = variantComp.layers[j];
                if (layer instanceof TextLayer && layer.name.indexOf("CTA") !== -1) {
                    var currentInPoint = layer.inPoint;
                    var newInPoint = Math.max(0, currentInPoint + timingVar.offset);
                    layer.inPoint = newInPoint;
                }
            }
            
            duplicated++;
        }
    }
    
    alert("✅ Creadas " + duplicated + " variaciones!\n\n" + 
          originalComps.length + " anuncios originales × 2 variaciones = " + 
          (originalComps.length * 2) + " variaciones totales");
    
    app.endUndoGroup();
})();


