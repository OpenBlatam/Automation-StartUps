// Backup Project Script
// Crea backup automático del proyecto con timestamp
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Backup Project");
    
    var project = app.project;
    
    if (!project.file) {
        alert("⚠️ El proyecto no está guardado. Por favor, guarda el proyecto primero.");
        return;
    }
    
    var originalFile = project.file;
    var originalPath = originalFile.parent;
    var originalName = originalFile.name.replace(/\.[^\.]+$/, ""); // Sin extensión
    
    // Crear carpeta de backups si no existe
    var backupFolder = new Folder(originalPath.fsName + "/backups/");
    if (!backupFolder.exists) {
        backupFolder.create();
    }
    
    // Generar nombre con timestamp
    var now = new Date();
    var timestamp = now.getFullYear() + 
                   padNumber(now.getMonth() + 1, 2) + 
                   padNumber(now.getDate(), 2) + "_" +
                   padNumber(now.getHours(), 2) +
                   padNumber(now.getMinutes(), 2) +
                   padNumber(now.getSeconds(), 2);
    
    var backupName = originalName + "_backup_" + timestamp + ".aep";
    var backupFile = new File(backupFolder.fsName + "/" + backupName);
    
    // Guardar proyecto como backup
    project.save(backupFile);
    
    // Limpiar backups antiguos (mantener solo los últimos 10)
    var backupFiles = backupFolder.getFiles("*.aep");
    if (backupFiles.length > 10) {
        // Ordenar por fecha de modificación
        backupFiles.sort(function(a, b) {
            return b.modified.getTime() - a.modified.getTime();
        });
        
        // Eliminar los más antiguos
        for (var i = 10; i < backupFiles.length; i++) {
            backupFiles[i].remove();
        }
    }
    
    alert("✅ Backup creado exitosamente!\n\n" +
          "Archivo: " + backupName + "\n" +
          "Ubicación: " + backupFolder.fsName + "\n\n" +
          "Backups guardados: " + backupFiles.length);
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


