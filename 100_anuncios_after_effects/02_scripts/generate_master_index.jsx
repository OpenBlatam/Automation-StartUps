// Generate Master Index Script
// Genera índice maestro de todos los anuncios con información completa
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Generate Master Index");
    
    var comps = app.project.items;
    var index = [];
    var outputFile = new File("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/06_documentacion/MASTER_INDEX.json");
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var match = comp.name.match(/Comp_(\d+)_/);
            var adNumber = match ? match[1] : padNumber(i + 1, 3);
            
            var entry = {
                id: adNumber,
                name: comp.name,
                duration: comp.duration,
                frameRate: 1 / comp.frameDuration,
                resolution: comp.width + "x" + comp.height,
                layers: comp.layers.length,
                hasCTA: false,
                hasMusic: false,
                hasLogo: false,
                category: "General",
                hook: "",
                cta: "",
                createdAt: comp.parentFolder ? comp.parentFolder.name : "Unknown"
            };
            
            // Analizar contenido
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer.name.indexOf("CTA") !== -1) entry.hasCTA = true;
                if (layer.name.indexOf("Music") !== -1) entry.hasMusic = true;
                if (layer.name.indexOf("Logo") !== -1) entry.hasLogo = true;
                
                if (layer instanceof TextLayer) {
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc && textDoc.text) {
                            if (layer.name.indexOf("Hook") !== -1 || j === 1) {
                                entry.hook = textDoc.text;
                            }
                            if (layer.name.indexOf("CTA") !== -1) {
                                entry.cta = textDoc.text;
                            }
                        }
                    }
                }
            }
            
            // Determinar categoría
            var compName = comp.name.toLowerCase();
            if (compName.indexOf("awareness") !== -1) entry.category = "Awareness";
            else if (compName.indexOf("conversion") !== -1) entry.category = "Conversion";
            else if (compName.indexOf("education") !== -1) entry.category = "Education";
            else if (compName.indexOf("testimonial") !== -1) entry.category = "Social Proof";
            else if (compName.indexOf("retention") !== -1) entry.category = "Retention";
            
            index.push(entry);
        }
    }
    
    // Ordenar por ID
    index.sort(function(a, b) {
        return parseInt(a.id) - parseInt(b.id);
    });
    
    var masterIndex = {
        generated: new Date().toISOString(),
        total: index.length,
        version: "5.0",
        ads: index
    };
    
    outputFile.open("w");
    outputFile.encoding = "UTF-8";
    outputFile.write(JSON.stringify(masterIndex, null, 2));
    outputFile.close();
    
    alert("✅ Índice maestro generado!\n\nTotal: " + index.length + " anuncios\nUbicación: " + outputFile.fsName);
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();

