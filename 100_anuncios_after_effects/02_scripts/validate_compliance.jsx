// Validate Compliance Script
// Valida compliance legal y de marca en todos los anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Validate Compliance");
    
    var comps = app.project.items;
    var violations = [];
    var checked = 0;
    
    // Reglas de compliance
    var complianceRules = {
        minCTASize: [360, 112],
        minTextSize: 48,
        requiredElements: ["CTA", "Text"],
        prohibitedWords: ["garantía", "garantizado", "100%", "siempre"],
        safeZoneTop: 150,
        safeZoneBottom: 150
    };
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            checked++;
            var compViolations = [];
            
            // Verificar elementos requeridos
            var hasCTA = false;
            var hasText = false;
            var texts = [];
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                if (layer.name.indexOf("CTA") !== -1) hasCTA = true;
                if (layer instanceof TextLayer) {
                    hasText = true;
                    var textProp = layer.property("Source Text");
                    if (textProp) {
                        var textDoc = textProp.value;
                        if (textDoc && textDoc.text) {
                            texts.push(textDoc.text.toLowerCase());
                            
                            // Verificar tamaño mínimo
                            if (textDoc.fontSize < complianceRules.minTextSize) {
                                compViolations.push("Texto muy pequeño: " + layer.name + " (" + textDoc.fontSize + "px)");
                            }
                        }
                    }
                }
            }
            
            if (!hasCTA) compViolations.push("Falta CTA");
            if (!hasText) compViolations.push("Falta texto");
            
            // Verificar palabras prohibidas
            var allText = texts.join(" ");
            for (var k = 0; k < complianceRules.prohibitedWords.length; k++) {
                if (allText.indexOf(complianceRules.prohibitedWords[k]) !== -1) {
                    compViolations.push("Palabra prohibida: '" + complianceRules.prohibitedWords[k] + "'");
                }
            }
            
            // Verificar safe zones
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer instanceof TextLayer) {
                    var pos = layer.property("Position").value;
                    if (pos[1] < complianceRules.safeZoneTop) {
                        compViolations.push("Texto fuera de safe zone superior: " + layer.name);
                    }
                    if (pos[1] > comp.height - complianceRules.safeZoneBottom) {
                        compViolations.push("Texto fuera de safe zone inferior: " + layer.name);
                    }
                }
            }
            
            if (compViolations.length > 0) {
                violations.push({
                    comp: comp.name,
                    violations: compViolations
                });
            }
        }
    }
    
    var report = "✅ VALIDACIÓN DE COMPLIANCE\n\n";
    report += "Composiciones verificadas: " + checked + "\n";
    report += "Sin problemas: " + (checked - violations.length) + "\n";
    report += "Con problemas: " + violations.length + "\n\n";
    
    if (violations.length > 0) {
        report += "PROBLEMAS ENCONTRADOS:\n\n";
        for (var i = 0; i < violations.length; i++) {
            report += "📁 " + violations[i].comp + ":\n";
            for (var j = 0; j < violations[i].violations.length; j++) {
                report += "  ⚠️ " + violations[i].violations[j] + "\n";
            }
            report += "\n";
        }
    } else {
        report += "✅ ¡Todos los anuncios cumplen con las reglas de compliance!";
    }
    
    var reportFile = new File("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/06_documentacion/compliance_report.txt");
    reportFile.open("w");
    reportFile.encoding = "UTF-8";
    reportFile.write(report);
    reportFile.close();
    
    alert(report);
    
    app.endUndoGroup();
})();

