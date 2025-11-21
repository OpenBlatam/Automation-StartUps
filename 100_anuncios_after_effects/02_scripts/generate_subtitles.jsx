// Generate Subtitles Script
// Genera archivos de subtítulos SRT automáticamente desde los textos de los anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Generate Subtitles");
    
    var comps = app.project.items;
    var subtitlesGenerated = 0;
    var outputFolder = new Folder("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/05_exports/subtitulos/");
    
    if (!outputFolder.exists) {
        outputFolder.create();
    }
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var subtitleContent = "";
            var subtitleIndex = 1;
            var frameRate = comp.frameDuration;
            
            // Extraer número del anuncio
            var match = comp.name.match(/Comp_(\d+)_/);
            var adNumber = match ? match[1] : padNumber(i + 1, 3);
            
            // Recopilar todos los textos de la composición
            var textLayers = [];
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer instanceof TextLayer) {
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc && textDoc.text) {
                            var inPoint = layer.inPoint;
                            var outPoint = layer.outPoint;
                            
                            textLayers.push({
                                text: textDoc.text,
                                inPoint: inPoint,
                                outPoint: outPoint,
                                name: layer.name
                            });
                        }
                    }
                }
            }
            
            // Ordenar por tiempo de aparición
            textLayers.sort(function(a, b) {
                return a.inPoint - b.inPoint;
            });
            
            // Generar contenido SRT
            for (var k = 0; k < textLayers.length; k++) {
                var textLayer = textLayers[k];
                
                // Convertir tiempo a formato SRT (HH:MM:SS,mmm)
                var startTime = formatSRTTime(textLayer.inPoint, frameRate);
                var endTime = formatSRTTime(textLayer.outPoint, frameRate);
                
                subtitleContent += subtitleIndex + "\n";
                subtitleContent += startTime + " --> " + endTime + "\n";
                subtitleContent += textLayer.text + "\n\n";
                
                subtitleIndex++;
            }
            
            // Guardar archivo SRT
            if (subtitleContent.length > 0) {
                var srtFile = new File(outputFolder.fsName + "/anuncio_" + adNumber + "_es.srt");
                srtFile.open("w");
                srtFile.encoding = "UTF-8";
                srtFile.write(subtitleContent);
                srtFile.close();
                
                subtitlesGenerated++;
            }
        }
    }
    
    alert("✅ Generados " + subtitlesGenerated + " archivos de subtítulos SRT!\n\nUbicación: " + outputFolder.fsName);
    
    app.endUndoGroup();
    
    function formatSRTTime(timeInSeconds, frameDuration) {
        var totalSeconds = Math.floor(timeInSeconds);
        var milliseconds = Math.floor((timeInSeconds - totalSeconds) * 1000);
        
        var hours = Math.floor(totalSeconds / 3600);
        var minutes = Math.floor((totalSeconds % 3600) / 60);
        var seconds = totalSeconds % 60;
        
        return padNumber(hours, 2) + ":" + 
               padNumber(minutes, 2) + ":" + 
               padNumber(seconds, 2) + "," + 
               padNumber(milliseconds, 3);
    }
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


