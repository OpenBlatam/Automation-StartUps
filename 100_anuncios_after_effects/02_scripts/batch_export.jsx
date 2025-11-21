// Batch Export Script
// Exporta todos los anuncios automáticamente a MP4
// Uso: File > Scripts > Run Script File
// IMPORTANTE: Ajustar la ruta de salida según tu sistema

(function() {
    app.beginUndoGroup("Batch Export");
    
    // CONFIGURAR RUTA DE SALIDA AQUÍ
    var baseOutputPath = "/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/05_exports/mp4/";
    
    // Verificar que la carpeta existe
    var outputFolder = new Folder(baseOutputPath);
    if (!outputFolder.exists) {
        outputFolder.create();
    }
    
    var comps = app.project.items;
    var renderQueue = app.project.renderQueue;
    var itemsAdded = 0;
    
    // Limpiar cola de render existente
    renderQueue.items.length = 0;
    
    // Template de exportación H.264
    var h264Template = "H.264 - Match Render Settings - 15 Mbps";
    
    // Añadir todas las composiciones a la cola
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            
            // Extraer número del anuncio del nombre
            var match = comp.name.match(/Comp_(\d+)_/);
            var adNumber = match ? match[1] : padNumber(i + 1, 3);
            
            // Crear item de render
            var rqItem = renderQueue.items.add(comp);
            rqItem.render = true;
            
            // Configurar output module
            var om = rqItem.outputModule(1);
            var fileName = "anuncio_" + adNumber + ".mp4";
            var outputFile = new File(baseOutputPath + fileName);
            
            om.file = outputFile;
            
            // Aplicar template H.264
            try {
                om.applyTemplate(h264Template);
            } catch (e) {
                // Si el template no existe, usar configuración manual
                om.format = "H.264";
                om.formatOptions = {
                    "Video Codec": "H.264",
                    "Video Bitrate": "15 Mbps",
                    "Audio Codec": "AAC",
                    "Audio Bitrate": "192 kbps"
                };
            }
            
            itemsAdded++;
        }
    }
    
    if (itemsAdded > 0) {
        var proceed = confirm(
            "Se añadieron " + itemsAdded + " composiciones a la cola de render.\n\n" +
            "¿Deseas iniciar el render ahora?\n\n" +
            "Ruta de salida: " + baseOutputPath
        );
        
        if (proceed) {
            renderQueue.render();
            alert("✅ Render iniciado! Revisa la cola de render para ver el progreso.");
        } else {
            alert("✅ " + itemsAdded + " items añadidos a la cola de render.\n\nInicia el render manualmente desde la cola de render.");
        }
    } else {
        alert("⚠️ No se encontraron composiciones para exportar.\n\nAsegúrate de que las composiciones tengan nombres que empiecen con 'Comp_'");
    }
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


