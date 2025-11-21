// Add Music Batch Script
// Añade música de fondo a todos los anuncios automáticamente
// Uso: File > Scripts > Run Script File
// CONFIGURAR: Seleccionar archivo de música antes de ejecutar

(function() {
    app.beginUndoGroup("Add Music Batch");
    
    // CONFIGURAR: Seleccionar archivo de música
    var musicFile = File.openDialog("Selecciona el archivo de música de fondo");
    
    if (!musicFile) {
        alert("⚠️ No se seleccionó archivo de música. Script cancelado.");
        return;
    }
    
    // Importar música si no está ya importada
    var musicItem = null;
    for (var i = 1; i <= app.project.items.length; i++) {
        if (app.project.items[i] instanceof FootageItem) {
            if (app.project.items[i].file && app.project.items[i].file.fsName === musicFile.fsName) {
                musicItem = app.project.items[i];
                break;
            }
        }
    }
    
    if (!musicItem) {
        musicItem = app.project.importFile(new ImportOptions(musicFile));
    }
    
    var comps = app.project.items;
    var musicAdded = 0;
    var volumeLevel = -8; // dB - ajustar según necesidad
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            
            // Verificar si ya tiene música
            var hasMusic = false;
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer.source === musicItem) {
                    hasMusic = true;
                    break;
                }
            }
            
            if (!hasMusic) {
                // Añadir música
                var musicLayer = comp.layers.add(musicItem);
                musicLayer.name = "Music_Background";
                
                // Ajustar duración para que coincida con la composición
                if (musicLayer.source.duration > comp.duration) {
                    musicLayer.outPoint = comp.duration;
                } else {
                    // Loop si la música es más corta
                    musicLayer.timeRemapEnabled = true;
                    var loops = Math.ceil(comp.duration / musicLayer.source.duration);
                    musicLayer.property("Time Remap").setValueAtTime(comp.duration, musicLayer.source.duration * loops);
                }
                
                // Ajustar volumen
                musicLayer.property("Audio Levels").setValue([volumeLevel, volumeLevel]);
                
                // Mover al final (debajo de todo)
                musicLayer.moveToEnd();
                
                // Añadir fade in/out
                var fadeDuration = 0.5; // segundos
                musicLayer.property("Audio Levels").setValueAtTime(0, [-100, -100]);
                musicLayer.property("Audio Levels").setValueAtTime(fadeDuration, [volumeLevel, volumeLevel]);
                
                if (musicLayer.outPoint < comp.duration) {
                    musicLayer.property("Audio Levels").setValueAtTime(comp.duration - fadeDuration, [volumeLevel, volumeLevel]);
                    musicLayer.property("Audio Levels").setValueAtTime(comp.duration, [-100, -100]);
                }
                
                musicAdded++;
            }
        }
    }
    
    alert("✅ Música añadida a " + musicAdded + " composiciones!\n\nArchivo: " + musicFile.name + "\nVolumen: " + volumeLevel + " dB");
    
    app.endUndoGroup();
})();


