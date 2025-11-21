// Create Template Library Script
// Crea biblioteca de templates reutilizables desde los mejores anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Create Template Library");
    
    var comps = app.project.items;
    var templatesCreated = 0;
    var templateFolder = new Folder("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/01_plantillas/templates_library/");
    
    if (!templateFolder.exists) {
        templateFolder.create();
    }
    
    // Criterios para templates (anuncios completos y bien estructurados)
    var templateCandidates = [];
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var score = 0;
            var hasCTA = false;
            var hasText = false;
            var hasMusic = false;
            var hasLogo = false;
            var layerCount = comp.layers.length;
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer.name.indexOf("CTA") !== -1) {
                    hasCTA = true;
                    score += 20;
                }
                if (layer instanceof TextLayer) {
                    hasText = true;
                    score += 15;
                }
                if (layer.name.indexOf("Music") !== -1) {
                    hasMusic = true;
                    score += 10;
                }
                if (layer.name.indexOf("Logo") !== -1) {
                    hasLogo = true;
                    score += 10;
                }
            }
            
            // Bonus por estructura completa
            if (hasCTA && hasText && hasMusic && hasLogo) score += 25;
            if (layerCount >= 5 && layerCount <= 15) score += 10; // Estructura balanceada
            
            if (score >= 50) {
                templateCandidates.push({
                    comp: comp,
                    score: score
                });
            }
        }
    }
    
    // Ordenar por score y tomar los mejores
    templateCandidates.sort(function(a, b) {
        return b.score - a.score;
    });
    
    var topTemplates = templateCandidates.slice(0, Math.min(10, templateCandidates.length));
    
    // Crear templates
    for (var i = 0; i < topTemplates.length; i++) {
        var candidate = topTemplates[i];
        var comp = candidate.comp;
        
        // Crear copia como template
        var templateComp = comp.duplicate();
        var templateName = "Template_" + padNumber(i + 1, 2) + "_" + comp.name.replace("Comp_", "");
        templateComp.name = templateName;
        
        // Reemplazar textos específicos con placeholders
        for (var j = 1; j <= templateComp.layers.length; j++) {
            var layer = templateComp.layers[j];
            if (layer instanceof TextLayer) {
                var textProp = layer.property("Source Text");
                if (textProp) {
                    var textDoc = textProp.value;
                    if (textDoc && textDoc.text) {
                        // Reemplazar números específicos
                        textDoc.text = textDoc.text.replace(/\d+/g, "[NUMBER]");
                        // Reemplazar palabras clave
                        textDoc.text = textDoc.text.replace(/\b(anuncio|producto|servicio)\b/gi, "[PRODUCT]");
                        textProp.setValue(textDoc);
                    }
                }
            }
        }
        
        templatesCreated++;
    }
    
    // Generar índice de templates
    var indexContent = "# Biblioteca de Templates\n\n";
    indexContent += "Total de templates: " + templatesCreated + "\n\n";
    indexContent += "## Templates Disponibles\n\n";
    
    for (var i = 0; i < topTemplates.length; i++) {
        indexContent += (i + 1) + ". " + topTemplates[i].comp.name + " (Score: " + topTemplates[i].score + ")\n";
    }
    
    var indexFile = new File(templateFolder.fsName + "/INDEX.md");
    indexFile.open("w");
    indexFile.encoding = "UTF-8";
    indexFile.write(indexContent);
    indexFile.close();
    
    alert("✅ Biblioteca de templates creada!\n\n" +
          "Templates creados: " + templatesCreated + "\n" +
          "Score mínimo: " + (topTemplates.length > 0 ? topTemplates[topTemplates.length - 1].score : 0) + "\n\n" +
          "Ubicación: " + templateFolder.fsName);
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();

