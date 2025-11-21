// Create Playlist Structure Script
// Crea estructura de playlists organizadas por categoría
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Create Playlist Structure");
    
    var comps = app.project.items;
    var playlists = {};
    var playlistCreated = 0;
    
    // Categorías de playlists
    var playlistCategories = {
        "Awareness": [],
        "Conversion": [],
        "Education": [],
        "Social Proof": [],
        "Retention": [],
        "Seasonal": [],
        "A/B Testing": []
    };
    
    // Organizar composiciones por categoría
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var compName = comp.name.toLowerCase();
            var category = "General";
            
            // Determinar categoría
            if (compName.indexOf("awareness") !== -1 || compName.indexOf("conciencia") !== -1) {
                category = "Awareness";
            } else if (compName.indexOf("conversion") !== -1 || compName.indexOf("venta") !== -1) {
                category = "Conversion";
            } else if (compName.indexOf("education") !== -1 || compName.indexOf("tutorial") !== -1) {
                category = "Education";
            } else if (compName.indexOf("testimonial") !== -1 || compName.indexOf("caso") !== -1) {
                category = "Social Proof";
            } else if (compName.indexOf("retention") !== -1 || compName.indexOf("fideliz") !== -1) {
                category = "Retention";
            } else if (compName.indexOf("black") !== -1 || compName.indexOf("navidad") !== -1) {
                category = "Seasonal";
            } else if (compName.indexOf("variant") !== -1 || compName.indexOf("ab") !== -1) {
                category = "A/B Testing";
            }
            
            if (playlistCategories[category]) {
                playlistCategories[category].push(comp);
            }
        }
    }
    
    // Crear estructura de carpetas y archivos de playlist
    var playlistFolder = new Folder("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/05_exports/playlists/");
    if (!playlistFolder.exists) {
        playlistFolder.create();
    }
    
    // Generar archivos de playlist (M3U format)
    for (var category in playlistCategories) {
        if (playlistCategories[category].length > 0) {
            var playlistContent = "#EXTM3U\n";
            playlistContent += "#EXTINF:-1," + category + " Playlist\n";
            playlistContent += "#PLAYLIST:" + category + "\n\n";
            
            for (var j = 0; j < playlistCategories[category].length; j++) {
                var comp = playlistCategories[category][j];
                var match = comp.name.match(/Comp_(\d+)_/);
                var adNumber = match ? match[1] : padNumber(j + 1, 3);
                
                playlistContent += "#EXTINF:-1,Anuncio " + adNumber + "\n";
                playlistContent += "anuncio_" + adNumber + ".mp4\n";
            }
            
            // Guardar playlist
            var playlistFile = new File(playlistFolder.fsName + "/" + category.toLowerCase().replace(/\s+/g, "_") + ".m3u");
            playlistFile.open("w");
            playlistFile.encoding = "UTF-8";
            playlistFile.write(playlistContent);
            playlistFile.close();
            
            playlistCreated++;
        }
    }
    
    // Generar reporte de playlists
    var report = "📋 ESTRUCTURA DE PLAYLISTS CREADA\n\n";
    report += "Playlists creadas: " + playlistCreated + "\n\n";
    report += "Distribución:\n";
    for (var category in playlistCategories) {
        if (playlistCategories[category].length > 0) {
            report += "  • " + category + ": " + playlistCategories[category].length + " anuncios\n";
        }
    }
    
    alert(report);
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


