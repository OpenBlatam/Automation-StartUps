// Bulk Create Ads Script for After Effects
// Crea 100 composiciones automáticamente con estructura base
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Bulk Create 100 Ads");
    
    // Configuración base
    var baseWidth = 1080;
    var baseHeight = 1920;
    var frameRate = 30;
    var duration = 15; // segundos en frames
    var durationInFrames = duration * frameRate;
    
    // Colores base (RGB 0-1)
    var bgColorDark = [0.18, 0.16, 0.20, 1]; // Color marca oscuro
    var bgColorLight = [0.97, 0.97, 0.98, 1]; // Color marca claro
    var textColorDark = [0.1, 0.1, 0.1, 1]; // Texto oscuro
    var textColorLight = [1, 1, 1, 1]; // Texto claro
    var accentColor = [0.18, 0.53, 0.87, 1]; // Color acento azul
    
    // Hooks variados para los primeros 20 anuncios
    var hooks = [
        "El 90% de las empresas no sabe usar IA",
        "2 días vs. 5 minutos con IA",
        "¿Listo para dominar IA en semanas?",
        "El secreto que solo el 1% conoce",
        "De $5,000 a $50,000 mensuales",
        "Automatiza el 80% de tu marketing",
        "Te extrañamos. Tenemos algo nuevo",
        "¿Quieres resultados 10x más rápidos?",
        "Gana $100 por cada amigo que invites",
        "Nuevo: [PRODUCTO] 2.0 ya está aquí",
        "Más de 2,000 empresas confían en nosotros",
        "Aprende IA desde cero en 4 semanas",
        "POV: Tu empresa después de implementar IA",
        "El secreto que las empresas no quieren que sepas",
        "Transformación empresarial - Historia real",
        "Cómo implementar IA en tu negocio",
        "Aprende a crear campañas de IA en 10 minutos",
        "Testimonio real: Cómo triplicamos las ventas",
        "Demo en vivo: Crear campaña de IA en 10 minutos",
        "Caso completo: De $5K a $50K mensuales"
    ];
    
    // Crear 100 composiciones
    for (var i = 1; i <= 100; i++) {
        var compName = "Comp_" + padNumber(i, 3) + "_Ad_" + i;
        var comp = app.project.items.addComp(compName, baseWidth, baseHeight, 1, duration, frameRate);
        
        // Crear background layer
        var bgColor = (i % 2 === 0) ? bgColorLight : bgColorDark;
        var bgSolid = comp.layers.addSolid(bgColor, "Background", baseWidth, baseHeight, 1);
        bgSolid.moveToEnd();
        
        // Crear texto hook
        var hookText = (i <= hooks.length) ? hooks[i - 1] : "Anuncio " + i;
        var textLayer = comp.layers.addText(hookText);
        var textProp = textLayer.property("Source Text");
        var textDoc = new TextDocument();
        textDoc.text = hookText;
        textDoc.fontSize = 96;
        textDoc.fillColor = (i % 2 === 0) ? textColorDark : textColorLight;
        textDoc.font = "Poppins-Bold";
        textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
        textProp.setValue(textDoc);
        
        // Posicionar texto en centro
        textLayer.property("Position").setValue([baseWidth/2, baseHeight/2 - 200]);
        
        // Añadir animación fade in
        textLayer.property("Opacity").setValueAtTime(0, 0);
        textLayer.property("Opacity").setValueAtTime(0.5, 100);
        
        // Añadir animación scale
        textLayer.property("Scale").setValueAtTime(0, [80, 80]);
        textLayer.property("Scale").setValueAtTime(0.5, [100, 100]);
        
        // Crear CTA placeholder
        var ctaLayer = comp.layers.addText("CTA Placeholder");
        var ctaProp = ctaLayer.property("Source Text");
        var ctaDoc = new TextDocument();
        ctaDoc.text = "Inscríbete hoy";
        ctaDoc.fontSize = 48;
        ctaDoc.fillColor = textColorLight;
        ctaDoc.font = "Poppins-Bold";
        ctaDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
        ctaProp.setValue(ctaDoc);
        
        // Posicionar CTA en parte inferior
        ctaLayer.property("Position").setValue([baseWidth/2, baseHeight - 200]);
        
        // CTA aparece a los 12 segundos
        ctaLayer.property("Opacity").setValueAtTime(0, 0);
        ctaLayer.property("Opacity").setValueAtTime(12, 100);
        
        // Crear botón CTA (rectángulo)
        var ctaButton = comp.layers.addShape();
        ctaButton.name = "CTA_Button";
        var shapeGroup = ctaButton.property("Contents").addProperty("ADBE Vector Group");
        var rect = shapeGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("Size").setValue([400, 120]);
        var fill = shapeGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("Color").setValue(accentColor);
        
        // Posicionar botón
        ctaButton.property("Position").setValue([baseWidth/2, baseHeight - 200]);
        ctaButton.property("Opacity").setValueAtTime(0, 0);
        ctaButton.property("Opacity").setValueAtTime(12, 100);
        
        // Añadir marcador al inicio
        comp.markerProperty.setValueAtTime(0, new MarkerValue("Anuncio " + i));
        
        // Añadir marcador para CTA
        comp.markerProperty.setValueAtTime(12, new MarkerValue("CTA"));
    }
    
    alert("✅ Creadas 100 composiciones exitosamente!");
    
    app.endUndoGroup();
    
    function padNumber(num, size) {
        var s = "000" + num;
        return s.substr(s.length - size);
    }
})();


