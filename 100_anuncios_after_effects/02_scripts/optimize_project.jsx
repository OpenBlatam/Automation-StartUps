// Optimize Project Script
// Optimiza el proyecto para mejor rendimiento
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Optimize Project");
    
    var comps = app.project.items;
    var optimized = 0;
    var optimizations = [];
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var compOptimizations = [];
            
            // Optimizar capas
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                // Desactivar motion blur si no es necesario
                if (layer.motionBlur) {
                    layer.motionBlur = false;
                    compOptimizations.push("Motion blur desactivado en " + layer.name);
                }
                
                // Optimizar calidad de capas
                if (layer.quality === LayerQuality.BEST) {
                    // Mantener BEST para texto, pero optimizar otros
                    if (!(layer instanceof TextLayer)) {
                        layer.quality = LayerQuality.HIGH;
                        compOptimizations.push("Calidad optimizada en " + layer.name);
                    }
                }
                
                // Desactivar efectos innecesarios
                if (layer.effect && layer.effect.numProperties > 0) {
                    // Revisar efectos y desactivar los que no se usan
                    for (var k = 1; k <= layer.effect.numProperties; k++) {
                        var effect = layer.effect.property(k);
                        if (effect && effect.enabled) {
                            // Mantener efectos activos, solo documentar
                        }
                    }
                }
            }
            
            // Optimizar composición
            if (comp.motionBlurSwitches) {
                comp.motionBlurSwitches = false;
                compOptimizations.push("Motion blur switches desactivados");
            }
            
            if (compOptims.length > 0) {
                optimized++;
                optimizations.push({
                    comp: comp.name,
                    optimizations: compOptimizations
                });
            }
        }
    }
    
    // Limpiar items no usados
    var unusedItems = [];
    for (var i = 1; i <= app.project.items.length; i++) {
        var item = app.project.items[i];
        if (item instanceof FootageItem) {
            var used = false;
            for (var j = 0; j < comps.length; j++) {
                if (comps[j] instanceof CompItem) {
                    for (var k = 1; k <= comps[j].layers.length; k++) {
                        if (comps[j].layers[k].source === item) {
                            used = true;
                            break;
                        }
                    }
                }
                if (used) break;
            }
            if (!used) {
                unusedItems.push(item.name);
            }
        }
    }
    
    var report = "⚡ OPTIMIZACIÓN COMPLETADA\n\n";
    report += "Composiciones optimizadas: " + optimized + "\n";
    report += "Items no usados encontrados: " + unusedItems.length + "\n\n";
    
    if (unusedItems.length > 0) {
        report += "Items no usados (considerar eliminar):\n";
        for (var i = 0; i < Math.min(unusedItems.length, 10); i++) {
            report += "  • " + unusedItems[i] + "\n";
        }
        if (unusedItems.length > 10) {
            report += "  ... y " + (unusedItems.length - 10) + " más\n";
        }
    }
    
    if (optimizations.length > 0) {
        report += "\nOptimizaciones aplicadas:\n";
        for (var i = 0; i < Math.min(optimizations.length, 5); i++) {
            report += "\n📁 " + optimizations[i].comp + ":\n";
            for (var j = 0; j < optimizations[i].optimizations.length; j++) {
                report += "  • " + optimizations[i].optimizations[j] + "\n";
            }
        }
    }
    
    alert(report);
    
    app.endUndoGroup();
})();


