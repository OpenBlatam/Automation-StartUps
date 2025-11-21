// Batch Update Timing Script
// Actualiza timing de elementos en todos los anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Batch Update Timing");
    
    var comps = app.project.items;
    var updated = 0;
    
    // Configuración de timing estándar
    var timingConfig = {
        hookAppears: 0,
        hookDuration: 3,
        ctaAppears: 12,
        ctaDuration: 3
    };
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var compUpdated = false;
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                // Actualizar timing de hook
                if (layer instanceof TextLayer && 
                    (layer.name.indexOf("Hook") !== -1 || j === 1)) {
                    var currentIn = layer.inPoint;
                    if (Math.abs(currentIn - timingConfig.hookAppears) > 0.1) {
                        layer.inPoint = timingConfig.hookAppears;
                        layer.outPoint = timingConfig.hookAppears + timingConfig.hookDuration;
                        compUpdated = true;
                    }
                }
                
                // Actualizar timing de CTA
                if (layer.name.indexOf("CTA") !== -1) {
                    var currentIn = layer.inPoint;
                    if (Math.abs(currentIn - timingConfig.ctaAppears) > 0.1) {
                        layer.inPoint = timingConfig.ctaAppears;
                        layer.outPoint = timingConfig.ctaAppears + timingConfig.ctaDuration;
                        compUpdated = true;
                    }
                }
            }
            
            if (compUpdated) updated++;
        }
    }
    
    alert("✅ Timing actualizado en " + updated + " composiciones!\n\n" +
          "Hook: " + timingConfig.hookAppears + "s\n" +
          "CTA: " + timingConfig.ctaAppears + "s");
    
    app.endUndoGroup();
})();

