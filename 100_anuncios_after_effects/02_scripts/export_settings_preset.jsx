// Export Settings Preset Script
// Crea y guarda presets de exportación personalizados
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Export Settings Preset");
    
    // Presets de exportación
    var presets = {
        "Social_Media_HD": {
            format: "H.264",
            width: 1080,
            height: 1920,
            frameRate: 30,
            bitrate: "15 Mbps",
            audioBitrate: "192 kbps"
        },
        "Social_Media_4K": {
            format: "H.264",
            width: 2160,
            height: 3840,
            frameRate: 30,
            bitrate: "50 Mbps",
            audioBitrate: "256 kbps"
        },
        "Web_Optimized": {
            format: "H.264",
            width: 1080,
            height: 1920,
            frameRate: 30,
            bitrate: "8 Mbps",
            audioBitrate: "128 kbps"
        }
    };
    
    // Guardar presets como JSON
    var presetFile = new File("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/06_documentacion/export_presets.json");
    presetFile.open("w");
    presetFile.encoding = "UTF-8";
    presetFile.write(JSON.stringify(presets, null, 2));
    presetFile.close();
    
    var report = "✅ Presets de exportación creados!\n\n";
    report += "Presets disponibles:\n";
    for (var key in presets) {
        report += "• " + key + "\n";
    }
    report += "\nGuardado en: " + presetFile.fsName;
    
    alert(report);
    
    app.endUndoGroup();
})();

