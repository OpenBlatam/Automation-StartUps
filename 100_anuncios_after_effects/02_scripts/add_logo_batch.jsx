// Add Logo Batch Script
// Añade logo a todos los anuncios automáticamente
// Uso: File > Scripts > Run Script File
// CONFIGURAR: Seleccionar archivo de logo antes de ejecutar

(function() {
    app.beginUndoGroup("Add Logo Batch");
    
    // CONFIGURAR: Seleccionar archivo de logo
    var logoFile = File.openDialog("Selecciona el archivo de logo (PNG, SVG, etc.)");
    
    if (!logoFile) {
        alert("⚠️ No se seleccionó archivo de logo. Script cancelado.");
        return;
    }
    
    // Importar logo si no está ya importado
    var logoItem = null;
    for (var i = 1; i <= app.project.items.length; i++) {
        if (app.project.items[i] instanceof FootageItem) {
            if (app.project.items[i].file && app.project.items[i].file.fsName === logoFile.fsName) {
                logoItem = app.project.items[i];
                break;
            }
        }
    }
    
    if (!logoItem) {
        logoItem = app.project.importFile(new ImportOptions(logoFile));
    }
    
    var comps = app.project.items;
    var logosAdded = 0;
    
    // Configuración del logo
    var logoScale = 15; // porcentaje del ancho de la composición
    var logoPosition = [100, 100]; // posición desde esquina superior izquierda
    var logoOpacity = 80; // porcentaje
    var fadeInDuration = 0.5; // segundos
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            
            // Verificar si ya tiene logo
            var hasLogo = false;
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer.name.indexOf("Logo") !== -1 || layer.name.indexOf("logo") !== -1) {
                    hasLogo = true;
                    break;
                }
            }
            
            if (!hasLogo) {
                // Añadir logo
                var logoLayer = comp.layers.add(logoItem);
                logoLayer.name = "Logo";
                
                // Calcular escala basada en ancho de composición
                var logoWidth = logoLayer.source.width;
                var logoHeight = logoLayer.source.height;
                var targetWidth = (comp.width * logoScale) / 100;
                var scale = (targetWidth / logoWidth) * 100;
                
                logoLayer.property("Scale").setValue([scale, scale]);
                
                // Posicionar logo (esquina superior izquierda con margen)
                logoLayer.property("Position").setValue([
                    logoPosition[0] + (logoWidth * scale / 200),
                    logoPosition[1] + (logoHeight * scale / 200)
                ]);
                
                // Ajustar opacidad
                logoLayer.property("Opacity").setValue(logoOpacity);
                
                // Añadir fade in
                logoLayer.property("Opacity").setValueAtTime(0, 0);
                logoLayer.property("Opacity").setValueAtTime(fadeInDuration, logoOpacity);
                
                // Mover al principio (arriba de todo excepto background)
                var bgIndex = 1;
                for (var j = 1; j <= comp.layers.length; j++) {
                    if (comp.layers[j].name === "Background") {
                        bgIndex = j;
                        break;
                    }
                }
                logoLayer.moveAfter(comp.layers[bgIndex]);
                
                logosAdded++;
            }
        }
    }
    
    alert("✅ Logo añadido a " + logosAdded + " composiciones!\n\nArchivo: " + logoFile.name + "\nEscala: " + logoScale + "%\nOpacidad: " + logoOpacity + "%");
    
    app.endUndoGroup();
})();


