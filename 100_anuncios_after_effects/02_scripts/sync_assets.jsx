// Sync Assets Script
// Sincroniza assets (logo, música) entre todas las composiciones
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Sync Assets");
    
    var comps = app.project.items;
    var synced = 0;
    
    // Buscar assets maestros
    var masterLogo = null;
    var masterMusic = null;
    
    for (var i = 1; i <= app.project.items.length; i++) {
        var item = app.project.items[i];
        if (item instanceof FootageItem) {
            if (item.name.indexOf("Logo") !== -1 || item.name.indexOf("logo") !== -1) {
                masterLogo = item;
            }
            if (item.name.indexOf("Music") !== -1 || item.name.indexOf("music") !== -1) {
                masterMusic = item;
            }
        }
    }
    
    if (!masterLogo && !masterMusic) {
        alert("⚠️ No se encontraron assets maestros (logo o música).\n\nImporta los assets primero.");
        return;
    }
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var compSynced = false;
            
            // Sincronizar logo
            if (masterLogo) {
                var hasLogo = false;
                var existingLogo = null;
                
                for (var j = 1; j <= comp.layers.length; j++) {
                    var layer = comp.layers[j];
                    if (layer.source === masterLogo) {
                        hasLogo = true;
                        existingLogo = layer;
                        break;
                    }
                    if (layer.name.indexOf("Logo") !== -1 && layer.source !== masterLogo) {
                        existingLogo = layer;
                    }
                }
                
                if (!hasLogo) {
                    if (existingLogo) {
                        existingLogo.replaceSource(masterLogo, false);
                    } else {
                        var newLogo = comp.layers.add(masterLogo);
                        newLogo.name = "Logo";
                        newLogo.property("Scale").setValue([15, 15]);
                        newLogo.property("Position").setValue([100, 100]);
                    }
                    compSynced = true;
                }
            }
            
            // Sincronizar música
            if (masterMusic) {
                var hasMusic = false;
                var existingMusic = null;
                
                for (var j = 1; j <= comp.layers.length; j++) {
                    var layer = comp.layers[j];
                    if (layer.source === masterMusic) {
                        hasMusic = true;
                        break;
                    }
                    if (layer.name.indexOf("Music") !== -1 && layer.source !== masterMusic) {
                        existingMusic = layer;
                    }
                }
                
                if (!hasMusic) {
                    if (existingMusic) {
                        existingMusic.replaceSource(masterMusic, false);
                    } else {
                        var newMusic = comp.layers.add(masterMusic);
                        newMusic.name = "Music_Background";
                        newMusic.moveToEnd();
                    }
                    compSynced = true;
                }
            }
            
            if (compSynced) synced++;
        }
    }
    
    var report = "✅ Sincronización completada!\n\n";
    report += "Composiciones sincronizadas: " + synced + "\n";
    if (masterLogo) report += "Logo: " + masterLogo.name + "\n";
    if (masterMusic) report += "Música: " + masterMusic.name + "\n";
    
    alert(report);
    
    app.endUndoGroup();
})();

