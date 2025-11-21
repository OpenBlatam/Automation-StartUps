// Quick Stats Script
// Genera estadísticas rápidas del proyecto
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Quick Stats");
    
    var comps = app.project.items;
    var stats = {
        total: 0,
        withCTA: 0,
        withMusic: 0,
        withLogo: 0,
        avgLayers: 0,
        totalLayers: 0,
        categories: {}
    };
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            stats.total++;
            var comp = comps[i];
            stats.totalLayers += comp.layers.length;
            
            var category = "General";
            var compName = comp.name.toLowerCase();
            if (compName.indexOf("awareness") !== -1) category = "Awareness";
            else if (compName.indexOf("conversion") !== -1) category = "Conversion";
            else if (compName.indexOf("education") !== -1) category = "Education";
            else if (compName.indexOf("testimonial") !== -1) category = "Social Proof";
            else if (compName.indexOf("retention") !== -1) category = "Retention";
            
            if (!stats.categories[category]) stats.categories[category] = 0;
            stats.categories[category]++;
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer.name.indexOf("CTA") !== -1) stats.withCTA++;
                if (layer.name.indexOf("Music") !== -1) stats.withMusic++;
                if (layer.name.indexOf("Logo") !== -1) stats.withLogo++;
            }
        }
    }
    
    stats.avgLayers = stats.total > 0 ? Math.round(stats.totalLayers / stats.total) : 0;
    
    var report = "📊 ESTADÍSTICAS RÁPIDAS\n\n";
    report += "Total anuncios: " + stats.total + "\n";
    report += "Con CTA: " + stats.withCTA + " (" + Math.round(stats.withCTA/stats.total*100) + "%)\n";
    report += "Con música: " + stats.withMusic + " (" + Math.round(stats.withMusic/stats.total*100) + "%)\n";
    report += "Con logo: " + stats.withLogo + " (" + Math.round(stats.withLogo/stats.total*100) + "%)\n";
    report += "Promedio capas: " + stats.avgLayers + "\n\n";
    report += "Por categoría:\n";
    for (var cat in stats.categories) {
        report += "  • " + cat + ": " + stats.categories[cat] + "\n";
    }
    
    alert(report);
    
    app.endUndoGroup();
})();

