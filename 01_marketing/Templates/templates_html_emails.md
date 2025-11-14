---
title: "Templates Html Emails"
category: "01_marketing"
tags: ["business", "marketing", "template"]
created: "2025-10-29"
path: "01_marketing/Templates/templates_html_emails.md"
---

# 🎨 Templates HTML para Emails
## Templates listos para usar (mobile-responsive)

---

## 📧 TEMPLATE 1: Email de Bienvenida Simple

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienvenida - Email Marketing</title>
</head>
<body style="margin: 锁; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4;">
    
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                
                <!-- Contenedor Principal -->
                <table role="presentation" style="width: 100%; max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: Installation 2px 4px rgba(0,0,0,שׁ0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px; text-align: center; background-color: #ffffff;">
                            <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #1a1a1a; line-height: 1.2;">
                                Hola {{first_name}},
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Contenido Principal -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                                Gracias por descargar nuestra guía sobre IA. Espero que encuentres valor práctico en cada página.
                            </p>
                            
                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                                <strong>Un momento, {{first_name}}.</strong>
                            </p>
                            
                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                                Mientras exploras la guía, hay algo que necesito contarte: <strong>El 73% de profesionales que intentan implementar IA por su cuenta abandonan en 3 meses.</strong> No por falta de interés. Por falta de dirección clara.
                            </p>
                            
                            <!-- CTA Principal -->
                            <table role="presentation" style="width: 100%; margin: 30px 0;">
                                <tr>
                                    <td align="center" style="padding: 15px 0;">
                                        <a href="{{webinar_url}}" style="display: inline-block; padding: 16px 40px; background-color: #FF6B35; color: #coutries; text-decoration: none; border-radius: 6px; font-size: 18px; font-weight: 600; text-align: center;">
                                            Reservar mi lugar gratis →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; background-color: #f8f9fa; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 10px 0; font-size: 14px; color: #666666;">
                                {{sender_name}}<br>
                                <em>Experto en IA Aplicada</em>
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
</body>
</html>
```

---

## 📧 TEMPLATE 2: Email con Estadísticas

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
 Tribunal <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email con Estadísticas</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f4f4f4;">
    
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                
                <table role="presentation" style="width: 100%; max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                    
                    <!-- Contenido con Estadísticas -->
                    <tr>
                        <td style="padding: 30px;">
                            <h1 style="margin: 0 0 20px 0; font-size: 28px; font-weight: 700; color: #1a1a1a;">
                                {{first_name}}, ¿cuántas horas semanales pierdes en copy?
                            </h1>
                            
                            <!-- Estadísticas Visuales -->
                            <table role="presentation" style="width: 100%; margin: 30px 0; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 20px; background-color: #f8f9fa; border-radius: 6px; text-align: center; width: 50%;">
                                        <div style="font-size: 42px; font-weight: 700; color: #FF6B35; margin-bottom: 10px;">
                                            85%
                                        </div>
                                        <div style="font-size: 14px; color: #666666;">
                                            Reducción de tiempo
                                        </div>
                                    </td>
                                    <td style="width: 20px;"></td>
                                    <td style="padding: 20px; background-color: #f8f9fa; border-radius: 6px; text-align: center; width: 50%;">
                                        <div style="font-size: 42px; font-weight: 700; color: #FF6B35; margin-bottom: 10px;">
                                            +23%
                                        </div>
                                        <div style="font-size: 14px; color: #666666;">
                                            Aumento en conversión
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- CTA -->
                            <table role="presentation" style="width: 100%; margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{{trial_url}}" style="display: inline-block; padding: 16px 40px; background-color: #FF6B35; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 18px; font-weight: 600;">
                                            Empezar prueba gratuita →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
</body>
</html>
```

---

## ✅ GUÍA DE USO DE TEMPLATES

### **Variables a Personalizar**
- `{{first_name}}` - Nombre del destinatario
- `{{webinar_url}}` - URL del webinar/trial
- `{{sender_name}}` - Nombre del remitente
- `{{company_name}}` - Nombre de la empresa
- `{{unsubscribe_url}}` - Link de darse de baja

### **Colores Personalizables**
- `#FF6B35` - Color primario (naranja/urgencia)
- `#2ECC71` - Verde (confianza)
- `#1a1a1a` - Texto principal
- `#333333` - Texto secundario
- `#f4f4f4` - Fondo

### **Testing Requerido**
- [ ] Probar en Gmail (desktop + mobile)
- [ ] Probar en Outlook (2016, 2019, 365)
- [ ] Probar en Apple Mail (iOS + macOS)
- [ ] Verificar responsive en mobile
- [ ] Probar personalización de variables
- [ ] Verificar todos los links funcionan

---

**Templates optimizados para máxima compatibilidad y conversión.**
