// Performance Analyzer Script
// Analiza el rendimiento de las composiciones y sugiere optimizaciones
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Performance Analyzer");
    
    var comps = app.project.items;
    var analysis = {
        total: 0,
        issues: [],
        recommendations: []
    };
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            analysis.total++;
            
            var compIssues = [];
            var layerCount = comp.layers.length;
            var effectCount = 0;
            var expressionCount = 0;
            var highResFootage = 0;
            
            // Analizar cada capa
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                // Contar efectos
                if (layer.effect && layer.effect.numProperties > 0) {
                    effectCount += layer.effect.numProperties;
                }
                
                // Contar expresiones
                var props = ["Position", "Scale", "Opacity", "Rotation"];
                for (var k = 0; k < props.length; k++) {
                    var prop = layer.property(props[k]);
                    if (prop && prop.expressionEnabled) {
                        expressionCount++;
                    }
                }
                
                // Verificar resolución de footage
                if (layer.source instanceof FootageItem) {
                    var source = layer.source;
                    if (source.width > 1920 || source.height > 1920) {
                        highResFootage++;
                    }
                }
            }
            
            // Identificar problemas de rendimiento
            if (layerCount > 20) {
                compIssues.push("Muchas capas (" + layerCount + "). Considera usar precomps.");
            }
            
            if (effectCount > 10) {
                compIssues.push("Muchos efectos (" + effectCount + "). Puede afectar rendimiento.");
            }
            
            if (highResFootage > 0) {
                compIssues.push("Footage de alta resolución detectado. Considera usar proxies.");
            }
            
            if (compIssues.length > 0) {
                analysis.issues.push({
                    comp: comp.name,
                    issues: compIssues,
                    stats: {
                        layers: layerCount,
                        effects: effectCount,
                        expressions: expressionCount
                    }
                });
            }
        }
    }
    
    // Generar recomendaciones
    if (analysis.issues.length > 0) {
        analysis.recommendations.push("Usar precomps para grupos de capas relacionadas");
        analysis.recommendations.push("Desactivar efectos no esenciales durante edición");
        analysis.recommendations.push("Usar proxies para footage de alta resolución");
        analysis.recommendations.push("Optimizar expresiones complejas");
    }
    
    // Generar reporte
    var report = "⚡ ANÁLISIS DE RENDIMIENTO\n\n";
    report += "Composiciones analizadas: " + analysis.total + "\n";
    report += "Composiciones con problemas: " + analysis.issues.length + "\n\n";
    
    if (analysis.issues.length > 0) {
        report += "PROBLEMAS ENCONTRADOS:\n\n";
        for (var i = 0; i < Math.min(analysis.issues.length, 10); i++) {
            var issue = analysis.issues[i];
            report += "📁 " + issue.comp + ":\n";
            report += "   Capas: " + issue.stats.layers + "\n";
            report += "   Efectos: " + issue.stats.effects + "\n";
            report += "   Expresiones: " + issue.stats.expressions + "\n";
            for (var j = 0; j < issue.issues.length; j++) {
                report += "   ⚠️ " + issue.issues[j] + "\n";
            }
            report += "\n";
        }
        
        if (analysis.issues.length > 10) {
            report += "... y " + (analysis.issues.length - 10) + " más\n\n";
        }
        
        report += "RECOMENDACIONES:\n\n";
        for (var i = 0; i < analysis.recommendations.length; i++) {
            report += "• " + analysis.recommendations[i] + "\n";
        }
    } else {
        report += "✅ ¡Todas las composiciones están optimizadas!";
    }
    
    // Guardar reporte
    var reportFile = new File("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/06_documentacion/performance_report.txt");
    reportFile.open("w");
    reportFile.encoding = "UTF-8";
    reportFile.write(report);
    reportFile.close();
    
    alert(report);
    
    app.endUndoGroup();
})();

