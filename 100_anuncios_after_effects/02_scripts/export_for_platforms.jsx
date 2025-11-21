// Export For Platforms Script
// Exporta anuncios optimizados para diferentes plataformas sociales
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Export For Platforms");
    
    var comps = app.project.items;
    var itemsAdded = 0;
    
    // Configuraciones por plataforma
    var platformConfigs = {
        "Instagram_Reels": {
            width: 1080,
            height: 1920,
            frameRate: 30,
            maxDuration: 90,
            format: "H.264",
            bitrate: "15 Mbps",
            folder: "instagram_reels"
        },
        "TikTok": {
            width: 1080,
            height: 1920,
            frameRate: 30,
            maxDuration: 60,
            format: "H.264",
            bitrate: "15 Mbps",
            folder: "tiktok"
        },
        "Facebook_Reels": {
            width: 1080,
            height: 1920,
            frameRate: 30,
            maxDuration: 90,
            format: "H.264",
            bitrate: "15 Mbps",
            folder: "facebook_reels"
        },
        "YouTube_Shorts": {
            width: 1080,
            height: 1920,
            frameRate: 30,
            maxDuration: 60,
            format: "H.264",
            bitrate: "20 Mbps",
            folder: "youtube_shorts"
        },
        "LinkedIn_Video": {
            width: 1080,
            height: 1920,
            frameRate: 30,
            maxDuration: 600,
            format: "H.264",
            bitrate: "15 Mbps",
            folder: "linkedin"
        }
    };
    
    // Crear carpetas
    var baseOutputPath = "/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/05_exports/platforms/";
    for (var platform in platformConfigs) {
        var folder = new Folder(baseOutputPath + platformConfigs[platform].folder);
        if (!folder.exists) {
            folder.create();
        }
    }
    
    // Procesar cada composición
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var match = comp.name.match(/Comp_(\d+)_/);
            var adNumber = match ? match[1] : padNumber(i + 1, 3);
            
            // Exportar para cada plataforma
            for (var platform in platformConfigs) {
                var config = platformConfigs[platform];
                
                // Verificar duración
                if (comp.duration <= config.maxDuration) {
                    var rqItem = app.project.renderQueue.items.add(comp);
                    rqItem.render = true;
                    
                    var om = rqItem.outputModule(1);
                    var fileName = "anuncio_" + adNumber + "_" + platform.toLowerCase().replace(/_/g, "_") + ".mp4";
                    var outputFile = new File(baseOutputPath + config.folder + "/" + fileName);
                    
                    om.file = outputFile;
                    
                    try {
                        om.applyTemplate("H.264 - Match Render Settings - " + config.bitrate);
                    } catch (e) {
                        om.format = "H.264";
                    }
                    
                    itemsAdded++;
                }
            }
        }
    }
    
    if (itemsAdded > 0) {
        var report = "✅ Exportación por plataformas configurada!\n\n";
        report += "Items en cola: " + itemsAdded + "\n";
        report += "Plataformas:\n";
        for (var platform in platformConfigs) {
            report += "  • " + platform + "\n";
        }
        report += "\n¿Deseas iniciar el render ahora?";
        
        var proceed = confirm(report);
        
        if (proceed) {
            app.project.renderQueue.render();
        }
    }
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


