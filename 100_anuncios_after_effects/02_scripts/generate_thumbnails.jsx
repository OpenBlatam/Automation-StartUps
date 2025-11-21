// Generate Thumbnails Script
// Genera thumbnails automáticamente desde los anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Generate Thumbnails");
    
    var comps = app.project.items;
    var thumbnailsGenerated = 0;
    var outputFolder = new Folder("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/05_exports/thumbnails/");
    
    if (!outputFolder.exists) {
        outputFolder.create();
    }
    
    // Configuración de thumbnail
    var thumbnailTime = 2; // segundos - momento del video para el thumbnail
    var thumbnailWidth = 1080;
    var thumbnailHeight = 1920;
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            
            // Extraer número del anuncio
            var match = comp.name.match(/Comp_(\d+)_/);
            var adNumber = match ? match[1] : padNumber(i + 1, 3);
            
            // Crear composición de thumbnail (frame estático)
            var thumbComp = app.project.items.addComp(
                "Thumb_" + comp.name,
                thumbnailWidth,
                thumbnailHeight,
                1,
                1, // 1 frame
                comp.frameDuration
            );
            
            // Copiar todas las capas al frame específico
            for (var j = 1; j <= comp.layers.length; j++) {
                var originalLayer = comp.layers[j];
                var newLayer = thumbComp.layers.add(originalLayer);
                
                // Ajustar tiempo al frame del thumbnail
                newLayer.inPoint = 0;
                newLayer.outPoint = 1;
                
                // Si la capa tiene animaciones, capturar el estado en thumbnailTime
                if (originalLayer.inPoint <= thumbnailTime && originalLayer.outPoint >= thumbnailTime) {
                    // La capa está visible en ese momento
                } else {
                    // Ocultar si no está visible
                    newLayer.enabled = false;
                }
            }
            
            // Añadir a cola de render para exportar como PNG
            var rqItem = app.project.renderQueue.items.add(thumbComp);
            var om = rqItem.outputModule(1);
            var fileName = "thumbnail_" + adNumber + ".png";
            om.file = new File(outputFolder.fsName + "/" + fileName);
            om.applyTemplate("PNG Sequence");
            
            // Configurar para exportar solo 1 frame
            om.outputModule(1).setSettings({
                "Format": "PNG Sequence",
                "Starting Frame": 1,
                "Ending Frame": 1
            });
            
            thumbnailsGenerated++;
        }
    }
    
    if (thumbnailsGenerated > 0) {
        var proceed = confirm(
            "Se generaron " + thumbnailsGenerated + " thumbnails en la cola de render.\n\n" +
            "¿Deseas iniciar el render ahora?"
        );
        
        if (proceed) {
            app.project.renderQueue.render();
        }
    }
    
    alert("✅ " + thumbnailsGenerated + " thumbnails añadidos a la cola de render!\n\nUbicación: " + outputFolder.fsName);
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


