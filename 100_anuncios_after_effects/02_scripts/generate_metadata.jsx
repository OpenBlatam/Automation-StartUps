// Generate Metadata Script
// Genera archivos de metadata automáticamente para cada anuncio
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Generate Metadata");
    
    var comps = app.project.items;
    var metadataGenerated = 0;
    var outputFolder = new Folder("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/05_exports/metadata/");
    
    if (!outputFolder.exists) {
        outputFolder.create();
    }
    
    // Plantilla de metadata
    var metadataTemplate = {
        "title": "",
        "description": "",
        "tags": [],
        "category": "",
        "duration": 0,
        "resolution": "1080x1920",
        "frameRate": 30,
        "format": "MP4",
        "created": "",
        "version": "1.0",
        "platforms": ["Instagram", "TikTok", "Facebook", "YouTube Shorts"],
        "cta": "",
        "hook": "",
        "hasMusic": false,
        "hasLogo": false,
        "hasSubtitles": false
    };
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            
            // Extraer número del anuncio
            var match = comp.name.match(/Comp_(\d+)_/);
            var adNumber = match ? match[1] : padNumber(i + 1, 3);
            
            var metadata = JSON.parse(JSON.stringify(metadataTemplate));
            
            // Llenar metadata
            metadata.title = "Anuncio " + adNumber;
            metadata.duration = comp.duration;
            metadata.frameRate = 1 / comp.frameDuration;
            metadata.created = new Date().toISOString();
            
            // Extraer información de capas
            var hookText = "";
            var ctaText = "";
            var hasMusic = false;
            var hasLogo = false;
            var tags = [];
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                // Extraer hook
                if (layer instanceof TextLayer && 
                    (layer.name.indexOf("Hook") !== -1 || j === 1)) {
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc && textDoc.text) {
                            hookText = textDoc.text;
                            metadata.hook = hookText;
                        }
                    }
                }
                
                // Extraer CTA
                if (layer instanceof TextLayer && 
                    layer.name.indexOf("CTA") !== -1) {
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc && textDoc.text) {
                            ctaText = textDoc.text;
                            metadata.cta = ctaText;
                        }
                    }
                }
                
                // Verificar música
                if (layer.name.indexOf("Music") !== -1) {
                    hasMusic = true;
                    metadata.hasMusic = true;
                }
                
                // Verificar logo
                if (layer.name.indexOf("Logo") !== -1) {
                    hasLogo = true;
                    metadata.hasLogo = true;
                }
            }
            
            // Generar descripción automática
            metadata.description = hookText + " " + ctaText;
            
            // Generar tags automáticos
            if (hookText.toLowerCase().indexOf("ia") !== -1) tags.push("IA");
            if (hookText.toLowerCase().indexOf("marketing") !== -1) tags.push("Marketing");
            if (hookText.toLowerCase().indexOf("curso") !== -1) tags.push("Curso");
            if (hookText.toLowerCase().indexOf("webinar") !== -1) tags.push("Webinar");
            metadata.tags = tags;
            
            // Determinar categoría
            var compName = comp.name.toLowerCase();
            if (compName.indexOf("awareness") !== -1) metadata.category = "Awareness";
            else if (compName.indexOf("conversion") !== -1) metadata.category = "Conversion";
            else if (compName.indexOf("education") !== -1) metadata.category = "Education";
            else if (compName.indexOf("testimonial") !== -1) metadata.category = "Social Proof";
            else metadata.category = "General";
            
            // Guardar metadata como JSON
            var jsonFile = new File(outputFolder.fsName + "/anuncio_" + adNumber + "_metadata.json");
            jsonFile.open("w");
            jsonFile.encoding = "UTF-8";
            jsonFile.write(JSON.stringify(metadata, null, 2));
            jsonFile.close();
            
            metadataGenerated++;
        }
    }
    
    alert("✅ Generados " + metadataGenerated + " archivos de metadata!\n\nUbicación: " + outputFolder.fsName);
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


