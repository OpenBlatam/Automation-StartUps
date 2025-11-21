// Generate Production Report Script
// Genera reporte completo de producción con estadísticas detalladas
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Generate Production Report");
    
    var comps = app.project.items;
    var report = {
        summary: {},
        byCategory: {},
        byPlatform: {},
        quality: {},
        timeline: {}
    };
    
    var totalComps = 0;
    var categories = {};
    var platforms = ["Instagram", "TikTok", "Facebook", "YouTube", "LinkedIn"];
    
    // Analizar todas las composiciones
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            totalComps++;
            var comp = comps[i];
            
            // Categorizar
            var category = "General";
            var compName = comp.name.toLowerCase();
            if (compName.indexOf("awareness") !== -1) category = "Awareness";
            else if (compName.indexOf("conversion") !== -1) category = "Conversion";
            else if (compName.indexOf("education") !== -1) category = "Education";
            else if (compName.indexOf("testimonial") !== -1) category = "Social Proof";
            else if (compName.indexOf("retention") !== -1) category = "Retention";
            
            if (!categories[category]) categories[category] = 0;
            categories[category]++;
            
            // Contar elementos
            var hasCTA = false;
            var hasText = false;
            var hasMusic = false;
            var hasLogo = false;
            var layerCount = comp.layers.length;
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer.name.indexOf("CTA") !== -1) hasCTA = true;
                if (layer instanceof TextLayer) hasText = true;
                if (layer.name.indexOf("Music") !== -1) hasMusic = true;
                if (layer.name.indexOf("Logo") !== -1) hasLogo = true;
            }
            
            // Actualizar reporte
            if (!report.byCategory[category]) {
                report.byCategory[category] = {
                    total: 0,
                    withCTA: 0,
                    withText: 0,
                    withMusic: 0,
                    withLogo: 0
                };
            }
            
            report.byCategory[category].total++;
            if (hasCTA) report.byCategory[category].withCTA++;
            if (hasText) report.byCategory[category].withText++;
            if (hasMusic) report.byCategory[category].withMusic++;
            if (hasLogo) report.byCategory[category].withLogo++;
        }
    }
    
    // Generar reporte en texto
    var reportText = "📊 REPORTE DE PRODUCCIÓN COMPLETO\n";
    reportText += "═══════════════════════════════════════\n\n";
    reportText += "📅 Fecha: " + new Date().toLocaleString() + "\n";
    reportText += "📁 Proyecto: " + (app.project.file ? app.project.file.name : "Sin guardar") + "\n\n";
    
    reportText += "📈 RESUMEN GENERAL\n";
    reportText += "───────────────────────────────────────\n";
    reportText += "Total de anuncios: " + totalComps + "\n\n";
    
    reportText += "📂 POR CATEGORÍA\n";
    reportText += "───────────────────────────────────────\n";
    for (var cat in report.byCategory) {
        var catData = report.byCategory[cat];
        reportText += cat + ":\n";
        reportText += "  Total: " + catData.total + "\n";
        reportText += "  Con CTA: " + catData.withCTA + " (" + Math.round(catData.withCTA/catData.total*100) + "%)\n";
        reportText += "  Con texto: " + catData.withText + " (" + Math.round(catData.withText/catData.total*100) + "%)\n";
        reportText += "  Con música: " + catData.withMusic + " (" + Math.round(catData.withMusic/catData.total*100) + "%)\n";
        reportText += "  Con logo: " + catData.withLogo + " (" + Math.round(catData.withLogo/catData.total*100) + "%)\n\n";
    }
    
    reportText += "✅ ESTADO DE PRODUCCIÓN\n";
    reportText += "───────────────────────────────────────\n";
    var completionRate = (totalComps / 100) * 100;
    reportText += "Progreso: " + totalComps + "/100 (" + completionRate.toFixed(1) + "%)\n";
    
    if (completionRate === 100) {
        reportText += "🎉 ¡Producción completa!\n";
    } else if (completionRate >= 75) {
        reportText += "👍 Casi completo, faltan " + (100 - totalComps) + " anuncios\n";
    } else {
        reportText += "⚠️ En progreso, faltan " + (100 - totalComps) + " anuncios\n";
    }
    
    // Guardar reporte
    var reportFile = new File("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/06_documentacion/production_report.txt");
    reportFile.open("w");
    reportFile.encoding = "UTF-8";
    reportFile.write(reportText);
    reportFile.close();
    
    // También guardar como JSON
    var jsonFile = new File("/Users/adan/Documents/documentos_blatam/100_anuncios_after_effects/06_documentacion/production_report.json");
    jsonFile.open("w");
    jsonFile.encoding = "UTF-8";
    jsonFile.write(JSON.stringify(report, null, 2));
    jsonFile.close();
    
    alert(reportText);
    
    app.endUndoGroup();
})();


