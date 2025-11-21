// Batch Rename Script
// Renombra composiciones de forma masiva con patrones personalizados
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Batch Rename");
    
    var comps = app.project.items;
    var renamed = 0;
    
    // Patrones de renombrado disponibles
    var renamePatterns = [
        {
            name: "Por número secuencial",
            pattern: function(comp, index) {
                return "Anuncio_" + padNumber(index + 1, 3);
            }
        },
        {
            name: "Por categoría y número",
            pattern: function(comp, index) {
                var category = "General";
                var compName = comp.name.toLowerCase();
                
                if (compName.indexOf("awareness") !== -1) category = "Awareness";
                else if (compName.indexOf("conversion") !== -1) category = "Conversion";
                else if (compName.indexOf("education") !== -1) category = "Education";
                else if (compName.indexOf("testimonial") !== -1) category = "Testimonial";
                else if (compName.indexOf("retention") !== -1) category = "Retention";
                
                var match = comp.name.match(/Comp_(\d+)_/);
                var num = match ? match[1] : padNumber(index + 1, 3);
                
                return category + "_" + num;
            }
        },
        {
            name: "Por fecha y número",
            pattern: function(comp, index) {
                var now = new Date();
                var dateStr = now.getFullYear() + 
                             padNumber(now.getMonth() + 1, 2) + 
                             padNumber(now.getDate(), 2);
                var match = comp.name.match(/Comp_(\d+)_/);
                var num = match ? match[1] : padNumber(index + 1, 3);
                
                return dateStr + "_Anuncio_" + num;
            }
        }
    ];
    
    // Seleccionar patrón (por defecto: patrón 1)
    var selectedPattern = renamePatterns[0];
    
    // Renombrar composiciones
    var compArray = [];
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            compArray.push(comps[i]);
        }
    }
    
    // Ordenar por nombre original
    compArray.sort(function(a, b) {
        return a.name.localeCompare(b.name);
    });
    
    for (var i = 0; i < compArray.length; i++) {
        var comp = compArray[i];
        var newName = selectedPattern.pattern(comp, i);
        
        if (comp.name !== newName) {
            comp.name = newName;
            renamed++;
        }
    }
    
    alert("✅ Renombradas " + renamed + " composiciones!\n\nPatrón usado: " + selectedPattern.name);
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


