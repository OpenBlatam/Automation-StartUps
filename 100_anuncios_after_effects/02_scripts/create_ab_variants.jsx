// Create A/B Variants Script
// Crea variantes A/B automáticamente para testing
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Create A/B Variants");
    
    var comps = app.project.items;
    var variantsCreated = 0;
    
    // Configuraciones de variantes
    var variantConfigs = [
        {
            name: "Hook_Alternativo",
            changeType: "hook",
            variations: [
                "El 90% de las empresas no sabe usar IA",
                "¿Sabías que el 90% de las empresas falla con IA?",
                "El secreto que el 90% de empresas desconoce"
            ]
        },
        {
            name: "CTA_Alternativo",
            changeType: "cta",
            variations: [
                "Inscríbete hoy",
                "Empieza ahora",
                "Únete gratis"
            ]
        },
        {
            name: "Color_Alternativo",
            changeType: "color",
            variations: [
                [0.18, 0.53, 0.87, 1], // Azul
                [0.0, 0.8, 0.4, 1],    // Verde
                [1.0, 0.2, 0.2, 1]     // Rojo
            ]
        }
    ];
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var originalComp = comps[i];
            
            // Crear variantes para cada configuración
            for (var v = 0; v < variantConfigs.length; v++) {
                var config = variantConfigs[v];
                
                // Crear nueva composición como copia
                var variantName = originalComp.name + "_" + config.name + "_V" + (v + 1);
                var variantComp = originalComp.duplicate();
                variantComp.name = variantName;
                
                // Aplicar variación según tipo
                switch(config.changeType) {
                    case "hook":
                        applyHookVariant(variantComp, config.variations[v % config.variations.length]);
                        break;
                    case "cta":
                        applyCTAVariant(variantComp, config.variations[v % config.variations.length]);
                        break;
                    case "color":
                        applyColorVariant(variantComp, config.variations[v % config.variations.length]);
                        break;
                }
                
                variantsCreated++;
            }
        }
    }
    
    alert("✅ Creadas " + variantsCreated + " variantes A/B!\n\nCada anuncio ahora tiene 3 variantes para testing.");
    
    app.endUndoGroup();
    
    function applyHookVariant(comp, newHook) {
        for (var j = 1; j <= comp.layers.length; j++) {
            var layer = comp.layers[j];
            if (layer instanceof TextLayer && 
                (layer.name.indexOf("Hook") !== -1 || layer.name.indexOf("hook") !== -1 || j === 1)) {
                var textProp = layer.property("Source Text");
                if (textProp) {
                    var textDoc = textProp.value;
                    if (textDoc) {
                        textDoc.text = newHook;
                        textProp.setValue(textDoc);
                        break;
                    }
                }
            }
        }
    }
    
    function applyCTAVariant(comp, newCTA) {
        for (var j = 1; j <= comp.layers.length; j++) {
            var layer = comp.layers[j];
            if (layer instanceof TextLayer && 
                (layer.name.indexOf("CTA") !== -1 || layer.name.indexOf("cta") !== -1)) {
                var textProp = layer.property("Source Text");
                if (textProp) {
                    var textDoc = textProp.value;
                    if (textDoc) {
                        textDoc.text = newCTA;
                        textProp.setValue(textDoc);
                        break;
                    }
                }
            }
        }
    }
    
    function applyColorVariant(comp, newColor) {
        for (var j = 1; j <= comp.layers.length; j++) {
            var layer = comp.layers[j];
            if (layer.name === "CTA_Button") {
                try {
                    var contents = layer.property("Contents");
                    var group = contents.property("ADBE Vector Group");
                    if (group) {
                        var fill = group.property("Contents").property("ADBE Vector Graphic - Fill");
                        if (fill) {
                            fill.property("Color").setValue(newColor);
                        }
                    }
                } catch (e) {
                    // Continuar si hay error
                }
            }
        }
    }
})();


