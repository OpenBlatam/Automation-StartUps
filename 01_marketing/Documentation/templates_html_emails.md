---
title: "Templates Html Emails"
category: "01_marketing"
tags: ["business", "marketing", "template"]
created: "2025-10-29"
path: "01_marketing/templates_html_emails.md"
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
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <table role="presentation" style="width: 100%; max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="padding: 30px; text-align: center;">
                            <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #1a1a1a;">Hola {{first_name}},</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                                Gracias por descargar nuestra guía sobre IA. Espero que encuentres valor práctico en cada página.
                            </p>
                            <table role="presentation" style="width: 100%; margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{{webinar_url}}" style="display: inline-block; padding: 16px 40px; background-color: #FF6B35; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 18px; font-weight: 600;">Reservar mi lugar gratis →</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px; background-color: #f8f9fa; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0; font-size: 14px; color: #666666;">{{sender_name}}<br><em>Experto en IA Aplicada</em></p>
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

## ✅ GUÍA DE USO

**Variables:** `{{first_name}}`, `{{webinar_url}}`, `{{sender_name}}`
**Testing:** Gmail, Outlook, Apple Mail, Mobile responsive

---

**Templates optimizados y listos para usar.**

