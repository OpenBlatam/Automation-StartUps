// Apply CTA Templates Script
// Aplica plantillas de CTA predefinidas a todos los anuncios
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Apply CTA Templates");
    
    var comps = app.project.items;
    var ctasApplied = 0;
    
    // Plantillas de CTA
    var ctaTemplates = [
        {
            text: "Inscríbete hoy",
            color: [0.18, 0.53, 0.87, 1], // Azul
            size: [400, 120],
            style: "rounded"
        },
        {
            text: "Compra ahora",
            color: [1.0, 0.2, 0.2, 1], // Rojo
            size: [400, 120],
            style: "sharp"
        },
        {
            text: "Prueba gratis",
            color: [0.0, 0.8, 0.4, 1], // Verde
            size: [400, 120],
            style: "rounded"
        },
        {
            text: "Descubre cómo",
            color: [0.42, 0.36, 0.91, 1], // Púrpura
            size: [400, 120],
            style: "rounded"
        },
        {
            text: "Únete ahora",
            color: [1.0, 0.84, 0.0, 1], // Dorado
            size: [400, 120],
            style: "sharp"
        }
    ];
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var template = ctaTemplates[i % ctaTemplates.length];
            
            // Buscar CTA existente o crear nuevo
            var ctaLayer = null;
            var ctaButton = null;
            
            for (var j = 1; j <= comp.layers.length; j++) {
                var layer = comp.layers[j];
                if (layer.name.indexOf("CTA") !== -1 || layer.name.indexOf("cta") !== -1) {
                    if (layer instanceof TextLayer) {
                        ctaLayer = layer;
                    } else if (layer.name === "CTA_Button") {
                        ctaButton = layer;
                    }
                }
            }
            
            // Crear o actualizar texto CTA
            if (!ctaLayer) {
                ctaLayer = comp.layers.addText(template.text);
                ctaLayer.name = "CTA_Text";
            }
            
            var textProp = ctaLayer.property("Source Text");
            var textDoc = new TextDocument();
            textDoc.text = template.text;
            textDoc.fontSize = 48;
            textDoc.fillColor = [1, 1, 1, 1]; // Texto blanco
            textDoc.font = "Poppins-Bold";
            textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
            textProp.setValue(textDoc);
            
            // Posicionar CTA
            ctaLayer.property("Position").setValue([comp.width/2, comp.height - 200]);
            
            // Crear o actualizar botón CTA
            if (!ctaButton) {
                ctaButton = comp.layers.addShape();
                ctaButton.name = "CTA_Button";
                var shapeGroup = ctaButton.property("Contents").addProperty("ADBE Vector Group");
                var rect = shapeGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
                rect.property("Size").setValue(template.size);
                
                // Aplicar estilo rounded si es necesario
                if (template.style === "rounded") {
                    var roundness = shapeGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
                    // Añadir round corners effect
                }
                
                var fill = shapeGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
                fill.property("Color").setValue(template.color);
            } else {
                // Actualizar color del botón existente
                try {
                    var contents = ctaButton.property("Contents");
                    var group = contents.property("ADBE Vector Group");
                    if (group) {
                        var fill = group.property("Contents").property("ADBE Vector Graphic - Fill");
                        if (fill) {
                            fill.property("Color").setValue(template.color);
                        }
                    }
                } catch (e) {
                    // Continuar si hay error
                }
            }
            
            // Posicionar botón
            ctaButton.property("Position").setValue([comp.width/2, comp.height - 200]);
            
            // Añadir animación de aparición
            var ctaTime = 12; // Aparece a los 12 segundos
            ctaLayer.property("Opacity").setValueAtTime(0, 0);
            ctaLayer.property("Opacity").setValueAtTime(ctaTime, 100);
            ctaButton.property("Opacity").setValueAtTime(0, 0);
            ctaButton.property("Opacity").setValueAtTime(ctaTime, 100);
            
            // Añadir expresión de pulso al botón
            var scaleProp = ctaButton.property("Scale");
            scaleProp.expression = "freq = 0.67;\namp = 5;\nvalue + Math.sin(time * freq * Math.PI * 2) * amp;";
            
            ctasApplied++;
        }
    }
    
    alert("✅ Aplicadas " + ctasApplied + " plantillas de CTA!");
    
    app.endUndoGroup();
})();


