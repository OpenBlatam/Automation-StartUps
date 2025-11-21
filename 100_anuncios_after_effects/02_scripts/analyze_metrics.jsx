// Analyze Metrics Script
// Analiza métricas y genera reporte de los anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Analyze Metrics");
    
    var comps = app.project.items;
    var metrics = {
        total: 0,
        withCTA: 0,
        withText: 0,
        withMusic: 0,
        withLogo: 0,
        durations: [],
        layerCounts: [],
        animationCounts: []
    };
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            metrics.total++;
            
            var hasCTA = false;
            var hasText = false;
            var hasMusic = false;
            var hasLogo = false;
            var layerCount = comp.layers.length;
            var animationCount = 0;
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                
                // Verificar CTA
                if (layer.name.indexOf("CTA") !== -1 || layer.name.indexOf("cta") !== -1) {
                    hasCTA = true;
                }
                
                // Verificar texto
                if (layer instanceof TextLayer) {
                    hasText = true;
                }
                
                // Verificar música
                if (layer.name.indexOf("Music") !== -1 || layer.name.indexOf("music") !== -1) {
                    hasMusic = true;
                }
                
                // Verificar logo
                if (layer.name.indexOf("Logo") !== -1 || layer.name.indexOf("logo") !== -1) {
                    hasLogo = true;
                }
                
                // Contar animaciones (keyframes)
                var props = ["Position", "Scale", "Opacity", "Rotation"];
                for (var k = 0; k < props.length; k++) {
                    var prop = layer.property(props[k]);
                    if (prop && prop.numKeys > 0) {
                        animationCount += prop.numKeys;
                    }
                }
            }
            
            if (hasCTA) metrics.withCTA++;
            if (hasText) metrics.withText++;
            if (hasMusic) metrics.withMusic++;
            if (hasLogo) metrics.withLogo++;
            
            metrics.durations.push(comp.duration);
            metrics.layerCounts.push(layerCount);
            metrics.animationCounts.push(animationCount);
        }
    }
    
    // Calcular promedios
    var avgDuration = metrics.durations.length > 0 ? 
        metrics.durations.reduce(function(a, b) { return a + b; }, 0) / metrics.durations.length : 0;
    var avgLayers = metrics.layerCounts.length > 0 ?
        metrics.layerCounts.reduce(function(a, b) { return a + b; }, 0) / metrics.layerCounts.length : 0;
    var avgAnimations = metrics.animationCounts.length > 0 ?
        metrics.animationCounts.reduce(function(a, b) { return a + b; }, 0) / metrics.animationCounts.length : 0;
    
    // Generar reporte
    var report = "📊 REPORTE DE MÉTRICAS - 100 ANUNCIOS\n\n";
    report += "═══════════════════════════════════════\n\n";
    report += "📈 ESTADÍSTICAS GENERALES\n";
    report += "───────────────────────────────────────\n";
    report += "Total de anuncios: " + metrics.total + "\n";
    report += "Con CTA: " + metrics.withCTA + " (" + Math.round(metrics.withCTA/metrics.total*100) + "%)\n";
    report += "Con texto: " + metrics.withText + " (" + Math.round(metrics.withText/metrics.total*100) + "%)\n";
    report += "Con música: " + metrics.withMusic + " (" + Math.round(metrics.withMusic/metrics.total*100) + "%)\n";
    report += "Con logo: " + metrics.withLogo + " (" + Math.round(metrics.withLogo/metrics.total*100) + "%)\n\n";
    
    report += "⏱️ DURACIÓN\n";
    report += "───────────────────────────────────────\n";
    report += "Promedio: " + avgDuration.toFixed(2) + " segundos\n";
    report += "Mínima: " + Math.min.apply(null, metrics.durations).toFixed(2) + " segundos\n";
    report += "Máxima: " + Math.max.apply(null, metrics.durations).toFixed(2) + " segundos\n\n";
    
    report += "🎬 CAPAS\n";
    report += "───────────────────────────────────────\n";
    report += "Promedio de capas por anuncio: " + avgLayers.toFixed(1) + "\n";
    report += "Mínimo: " + Math.min.apply(null, metrics.layerCounts) + " capas\n";
    report += "Máximo: " + Math.max.apply(null, metrics.layerCounts) + " capas\n\n";
    
    report += "✨ ANIMACIONES\n";
    report += "───────────────────────────────────────\n";
    report += "Promedio de keyframes por anuncio: " + avgAnimations.toFixed(1) + "\n";
    report += "Total de keyframes: " + metrics.animationCounts.reduce(function(a, b) { return a + b; }, 0) + "\n\n";
    
    report += "✅ CALIDAD\n";
    report += "───────────────────────────────────────\n";
    var qualityScore = 0;
    if (metrics.withCTA === metrics.total) qualityScore += 25;
    if (metrics.withText === metrics.total) qualityScore += 25;
    if (metrics.withMusic === metrics.total) qualityScore += 25;
    if (metrics.withLogo === metrics.total) qualityScore += 25;
    report += "Puntuación de calidad: " + qualityScore + "/100\n";
    
    if (qualityScore === 100) {
        report += "🎉 ¡Excelente! Todos los anuncios están completos.\n";
    } else if (qualityScore >= 75) {
        report += "👍 Bueno. Algunos anuncios necesitan elementos adicionales.\n";
    } else {
        report += "⚠️ Necesita mejoras. Revisa los anuncios incompletos.\n";
    }
    
    // Guardar reporte
    var reportFile = new File("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/06_documentacion/metrics_report.txt");
    reportFile.open("w");
    reportFile.write(report);
    reportFile.close();
    
    alert(report);
    
    app.endUndoGroup();
})();


