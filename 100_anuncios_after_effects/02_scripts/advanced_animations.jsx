// Advanced Animations Script
// Aplica animaciones avanzadas a los anuncios automáticamente
// Uso: File > Scripts > Run Script File

(function() {
    app.beginUndoGroup("Apply Advanced Animations");
    
    var comps = app.project.items;
    var animationsApplied = 0;
    
    // Tipos de animación disponibles
    var animationTypes = [
        "fadeInSlideUp",
        "zoomInFade",
        "slideFromLeft",
        "bounceIn",
        "elasticIn",
        "scalePulse"
    ];
    
    for (var i = 0; i < comps.length; i++) {
        if (comps[i] instanceof CompItem && comps[i].name.indexOf("Comp_") === 0) {
            var comp = comps[i];
            var layers = comp.layers;
            var animationType = animationTypes[i % animationTypes.length];
            
            for (var j = 1; j <= layers.length; j++) {
                var layer = layers[j];
                
                if (layer instanceof TextLayer) {
                    applyAnimation(layer, animationType, comp);
                    animationsApplied++;
                }
            }
        }
    }
    
    alert("✅ Aplicadas " + animationsApplied + " animaciones avanzadas!");
    
    app.endUndoGroup();
    
    function applyAnimation(layer, type, comp) {
        var inPoint = layer.inPoint;
        var duration = 0.5; // duración de la animación en segundos
        
        switch(type) {
            case "fadeInSlideUp":
                // Fade in + Slide up
                layer.property("Opacity").setValueAtTime(inPoint, 0);
                layer.property("Opacity").setValueAtTime(inPoint + duration, 100);
                
                var pos = layer.property("Position").value;
                layer.property("Position").setValueAtTime(inPoint, [pos[0], pos[1] + 100]);
                layer.property("Position").setValueAtTime(inPoint + duration, pos);
                break;
                
            case "zoomInFade":
                // Zoom in + Fade
                layer.property("Opacity").setValueAtTime(inPoint, 0);
                layer.property("Opacity").setValueAtTime(inPoint + duration, 100);
                
                layer.property("Scale").setValueAtTime(inPoint, [50, 50]);
                layer.property("Scale").setValueAtTime(inPoint + duration, [100, 100]);
                break;
                
            case "slideFromLeft":
                // Slide from left
                var pos = layer.property("Position").value;
                layer.property("Position").setValueAtTime(inPoint, [-500, pos[1]]);
                layer.property("Position").setValueAtTime(inPoint + duration, pos);
                
                layer.property("Opacity").setValueAtTime(inPoint, 0);
                layer.property("Opacity").setValueAtTime(inPoint + duration, 100);
                break;
                
            case "bounceIn":
                // Bounce in effect
                layer.property("Scale").setValueAtTime(inPoint, [0, 0]);
                layer.property("Scale").setValueAtTime(inPoint + duration * 0.6, [120, 120]);
                layer.property("Scale").setValueAtTime(inPoint + duration, [100, 100]);
                
                layer.property("Opacity").setValueAtTime(inPoint, 0);
                layer.property("Opacity").setValueAtTime(inPoint + duration * 0.3, 100);
                break;
                
            case "elasticIn":
                // Elastic in effect
                layer.property("Scale").setValueAtTime(inPoint, [0, 0]);
                layer.property("Scale").setValueAtTime(inPoint + duration * 0.4, [150, 150]);
                layer.property("Scale").setValueAtTime(inPoint + duration * 0.7, [80, 80]);
                layer.property("Scale").setValueAtTime(inPoint + duration, [100, 100]);
                
                layer.property("Opacity").setValueAtTime(inPoint, 0);
                layer.property("Opacity").setValueAtTime(inPoint + duration * 0.2, 100);
                break;
                
            case "scalePulse":
                // Scale pulse
                layer.property("Scale").setValueAtTime(inPoint, [80, 80]);
                layer.property("Scale").setValueAtTime(inPoint + duration * 0.5, [110, 110]);
                layer.property("Scale").setValueAtTime(inPoint + duration, [100, 100]);
                
                layer.property("Opacity").setValueAtTime(inPoint, 0);
                layer.property("Opacity").setValueAtTime(inPoint + duration * 0.3, 100);
                break;
        }
        
        // Aplicar easing a todas las propiedades animadas
        var props = ["Opacity", "Position", "Scale"];
        for (var k = 0; k < props.length; k++) {
            var prop = layer.property(props[k]);
            if (prop && prop.numKeys > 0) {
                for (var key = 1; key <= prop.numKeys; key++) {
                    prop.setTemporalEaseAtKey(key, 
                        [new KeyframeEase(0.33, 33.33), new KeyframeEase(0.33, 33.33)],
                        [new KeyframeEase(0.33, 33.33), new KeyframeEase(0.33, 33.33)]
                    );
                }
            }
        }
    }
})();


