// Replace Text Script
// Reemplaza placeholders en todos los anuncios con valores personalizados
// Uso: File > Scripts > Run Script File
// CONFIGURAR: Editar el objeto 'replacements' con tus valores

(function() {
    app.beginUndoGroup("Replace Text");
    
    // CONFIGURAR AQUÍ: Reemplazos personalizados
    var replacements = {
        "[NOMBRE PRODUCTO]": "Tu Producto",
        "[NOMBRE DEL PRODUCTO]": "Tu Producto",
        "[PRODUCTO]": "Tu Producto",
        "[ESLOGAN]": "Tu Eslogan Aquí",
        "[COLOR MARCA-acento]": "#2E86DE",
        "[COLOR MARCA-claro]": "#F8F9FA",
        "[COLOR MARCA-oscuro]": "#1A1A1A",
        "[CLIENTE]": "Cliente Ejemplo",
        "[INFLUENCER]": "Influencer Ejemplo",
        "[CODIGO]": "DESCUENTO20"
    };
    
    var comps = app.project.items;
    var replacementsCount = 0;
    var compsProcessed = 0;
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem) {
            var comp = comps[i];
            var layers = comp.layers;
            var compHasReplacements = false;
            
            for (var j = 1; j <= layers.length; j++) {
                var layer = layers[j];
                
                if (layer instanceof TextLayer) {
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc && textDoc.text) {
                            var originalText = textDoc.text;
                            var newText = originalText;
                            
                            // Aplicar todos los reemplazos
                            for (var key in replacements) {
                                if (newText.indexOf(key) !== -1) {
                                    newText = newText.replace(new RegExp(escapeRegExp(key), "g"), replacements[key]);
                                    compHasReplacements = true;
                                    replacementsCount++;
                                }
                            }
                            
                            // Actualizar texto si hubo cambios
                            if (newText !== originalText) {
                                textDoc.text = newText;
                                textProp.setValue(textDoc);
                            }
                        }
                    }
                }
            }
            
            if (compHasReplacements) {
                compsProcessed++;
            }
        }
    }
    
    alert(
        "✅ Reemplazo de texto completado!\n\n" +
        "Composiciones procesadas: " + compsProcessed + "\n" +
        "Reemplazos realizados: " + replacementsCount
    );
    
    app.endUndoGroup();
    
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
})();


