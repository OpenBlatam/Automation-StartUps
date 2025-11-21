// Cleanup Unused Script
// Limpia items no usados del proyecto
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Cleanup Unused");
    
    var unusedItems = [];
    var comps = [];
    
    // Recopilar todas las composiciones
    for (var i = 1; i <= app.project.items.length; i++) {
        if (app.project.items[i] instanceof CompItem) {
            comps.push(app.project.items[i]);
        }
    }
    
    // Verificar cada item
    for (var i = 1; i <= app.project.items.length; i++) {
        var item = app.project.items[i];
        
        if (item instanceof FootageItem || item instanceof FolderItem) {
            var used = false;
            
            // Verificar si se usa en alguna composición
            for (var j = 0; j < comps.length; j++) {
                var comp = comps[j];
                for (var k = 1; k <= comp.layers.length; k++) {
                    if (comp.layers[k].source === item) {
                        used = true;
                        break;
                    }
                }
                if (used) break;
            }
            
            if (!used && item.name.indexOf("Comp_") === -1) {
                unusedItems.push(item);
            }
        }
    }
    
    if (unusedItems.length > 0) {
        var proceed = confirm(
            "Se encontraron " + unusedItems.length + " items no usados.\n\n" +
            "¿Deseas eliminarlos?\n\n" +
            "(Se mostrarán los primeros 10)"
        );
        
        if (proceed) {
            var deleted = 0;
            for (var i = 0; i < unusedItems.length; i++) {
                try {
                    unusedItems[i].remove();
                    deleted++;
                } catch (e) {
                    // Continuar si hay error
                }
            }
            alert("✅ Eliminados " + deleted + " items no usados.");
        } else {
            var list = "Items no usados encontrados:\n\n";
            for (var i = 0; i < Math.min(unusedItems.length, 10); i++) {
                list += "• " + unusedItems[i].name + "\n";
            }
            if (unusedItems.length > 10) {
                list += "... y " + (unusedItems.length - 10) + " más";
            }
            alert(list);
        }
    } else {
        alert("✅ No se encontraron items no usados.");
    }
    
    app.endUndoGroup();
})();

