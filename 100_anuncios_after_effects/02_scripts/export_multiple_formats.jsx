// Export Multiple Formats Script
// Exporta cada anuncio a múltiples formatos simultáneamente
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Export Multiple Formats");
    
    // CONFIGURAR: Rutas de salida
    var baseOutputPath = "/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/05_exports/";
    
    // Formatos a exportar
    var formats = [
        {
            name: "MP4",
            folder: "mp4",
            template: "H.264 - Match Render Settings - 15 Mbps",
            extension: ".mp4"
        },
        {
            name: "MOV",
            folder: "mov",
            template: "QuickTime - Match Render Settings - 15 Mbps",
            extension: ".mov"
        },
        {
            name: "PNG Sequence",
            folder: "png_sequence",
            template: "PNG Sequence",
            extension: "_%04d.png"
        }
    ];
    
    // Crear carpetas si no existen
    for (var f = 0; f < formats.length; f++) {
        var folder = new Folder(baseOutputPath + formats[f].folder);
        if (!folder.exists) {
            folder.create();
        }
    }
    
    var comps = app.project.items;
    var itemsAdded = 0;
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            
            // Extraer número del anuncio
            var match = comp.name.match(/Comp_(\d+)_/);
            var adNumber = match ? match[1] : padNumber(i + 1, 3);
            
            // Añadir a cola para cada formato
            for (var f = 0; f < formats.length; f++) {
                var format = formats[f];
                var rqItem = app.project.renderQueue.items.add(comp);
                rqItem.render = true;
                
                var om = rqItem.outputModule(1);
                var fileName = "anuncio_" + adNumber + format.extension;
                var outputFile = new File(baseOutputPath + format.folder + "/" + fileName);
                
                om.file = outputFile;
                
                try {
                    om.applyTemplate(format.template);
                } catch (e) {
                    // Si el template no existe, usar configuración manual
                    if (format.name === "MP4") {
                        om.format = "H.264";
                    } else if (format.name === "MOV") {
                        om.format = "QuickTime";
                    } else if (format.name === "PNG Sequence") {
                        om.format = "PNG Sequence";
                    }
                }
                
                itemsAdded++;
            }
        }
    }
    
    if (itemsAdded > 0) {
        var report = "✅ Exportación múltiple configurada!\n\n";
        report += "Formatos: " + formats.length + "\n";
        report += "Items en cola: " + itemsAdded + "\n";
        report += "Anuncios: " + (itemsAdded / formats.length) + "\n\n";
        report += "Formatos configurados:\n";
        for (var f = 0; f < formats.length; f++) {
            report += "  • " + formats[f].name + " → " + formats[f].folder + "/\n";
        }
        report += "\n¿Deseas iniciar el render ahora?";
        
        var proceed = confirm(report);
        
        if (proceed) {
            app.project.renderQueue.render();
            alert("🚀 Render iniciado! Revisa la cola de render para ver el progreso.");
        } else {
            alert("✅ " + itemsAdded + " items añadidos a la cola de render.\n\nInicia el render manualmente desde la cola de render.");
        }
    } else {
        alert("⚠️ No se encontraron composiciones para exportar.");
    }
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


