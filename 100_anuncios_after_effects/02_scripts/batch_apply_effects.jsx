// Batch Apply Effects Script
// Aplica efectos visuales profesionales a todos los anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Batch Apply Effects");
    
    var comps = app.project.items;
    var effectsApplied = 0;
    
    // Efectos disponibles
    var effectPresets = [
        {
            name: "Subtle Glow",
            effects: [
                { name: "Glow", properties: { "Glow Intensity": 0.5, "Glow Radius": 20 } }
            ]
        },
        {
            name: "Sharp Focus",
            effects: [
                { name: "Unsharp Mask", properties: { "Amount": 50, "Radius": 1.0 } }
            ]
        },
        {
            name: "Color Grading",
            effects: [
                { name: "Color Balance", properties: { "Shadow Red Balance": 5 } }
            ]
        }
    ];
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var preset = effectPresets[i % effectPresets.length];
            
            // Aplicar efectos a la composición (adjustment layer)
            var adjLayer = comp.layers.addSolid([1, 1, 1, 0], "Effects_" + preset.name, comp.width, comp.height, 1);
            adjLayer.adjustmentLayer = true;
            adjLayer.enabled = true;
            
            // Aplicar cada efecto del preset
            for (var e = 0; e < preset.effects.length; e++) {
                var effectInfo = preset.effects[e];
                try {
                    var effect = adjLayer.property("Effects").addProperty(effectInfo.name);
                    
                    // Aplicar propiedades del efecto
                    if (effectInfo.properties) {
                        for (var propName in effectInfo.properties) {
                            var prop = effect.property(propName);
                            if (prop) {
                                prop.setValue(effectInfo.properties[propName]);
                            }
                        }
                    }
                } catch (e) {
                    // Continuar si el efecto no está disponible
                }
            }
            
            effectsApplied++;
        }
    }
    
    alert("✅ Aplicados efectos a " + effectsApplied + " composiciones!\n\n" +
          "Efectos aplicados:\n" +
          "• Subtle Glow\n" +
          "• Sharp Focus\n" +
          "• Color Grading");
    
    app.endUndoGroup();
})();

