#!/usr/bin/env python3
"""
Sistema de notificaciones para alertas y reportes
Soporta: Slack, Email, Microsoft Teams, Discord
"""
import sys
import json
from pathlib import Path
from datetime import datetime

def send_slack_notification(webhook_url, message, channel=None, username="Asset Monitor"):
    """Envía notificación a Slack"""
    try:
        import requests
        
        payload = {
            "text": message,
            "username": username
        }
        
        if channel:
            payload["channel"] = channel
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Error Slack: {response.status_code}")
            return False
    except ImportError:
        print("⚠️  requests no instalado. Instala con: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Error enviando a Slack: {e}")
        return False

def send_email_notification(smtp_config, subject, body, recipients):
    """Envía email usando SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = smtp_config['from']
        msg['Subject'] = subject
        msg['To'] = ', '.join(recipients)
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['user'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

def send_teams_notification(webhook_url, title, message, theme_color="FF6B6B"):
    """Envía notificación a Microsoft Teams"""
    try:
        import requests
        
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": theme_color,
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "text": message,
                "markdown": True
            }]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Error Teams: {response.status_code}")
            return False
    except ImportError:
        print("⚠️  requests no instalado. Instala con: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Error enviando a Teams: {e}")
        return False

def format_alert_message(alerts_data):
    """Formatea mensaje de alertas"""
    summary = alerts_data.get('summary', {})
    critical = summary.get('critical_count', 0)
    high = summary.get('high_count', 0)
    
    message = f"🚨 *Alertas de Creativos*\n\n"
    message += f"📊 Total: {summary.get('total', 0)}\n"
    message += f"🔴 Críticas: {critical}\n"
    message += f"🟠 Altas: {high}\n"
    
    if critical > 0:
        message += f"\n⚠️ *Acción requerida*: {critical} alerta(s) crítica(s) detectada(s)"
    elif high > 0:
        message += f"\n⚠️ Revisar: {high} alerta(s) de alta prioridad"
    else:
        message += "\n✅ Sin alertas críticas"
    
    return message

def format_performance_message(performance_data):
    """Formatea mensaje de performance"""
    total = performance_data.get('total', 0)
    formats = performance_data.get('by_format', {})
    
    message = f"📊 *Reporte de Performance*\n\n"
    message += f"Total creativos: {total}\n\n"
    message += "*Distribución por formato:*\n"
    
    for formato, count in sorted(formats.items(), key=lambda x: x[1], reverse=True)[:5]:
        pct = (count / total * 100) if total > 0 else 0
        message += f"• {formato}: {count} ({pct:.1f}%)\n"
    
    return message

def load_config():
    """Carga configuración de notificaciones"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    config_path = root_dir / '.notifications_config.json'
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}

def create_config_template():
    """Crea template de configuración"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    config_path = root_dir / '.notifications_config.json'
    
    template = {
        "slack": {
            "webhook_url": "",
            "channel": "#alerts",
            "enabled": False
        },
        "email": {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "",
                "password": "",
                "from": ""
            },
            "recipients": [],
            "enabled": False
        },
        "teams": {
            "webhook_url": "",
            "enabled": False
        },
        "default_channel": "slack"
    }
    
    if not config_path.exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        print(f"✅ Template de configuración creado: {config_path}")
        print("   Edita el archivo con tus credenciales")
    else:
        print(f"⚠️  Configuración ya existe: {config_path}")
    
    return template

def main():
    print("=" * 80)
    print("📧 Sistema de Notificaciones")
    print("=" * 80)
    print()
    
    config = load_config()
    
    if not config:
        print("⚠️  No se encontró configuración")
        response = input("¿Crear template de configuración? (s/n): ")
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            create_config_template()
        return
    
    # Determinar tipo de notificación
    notification_type = sys.argv[1] if len(sys.argv) > 1 else 'alerts'
    channel = sys.argv[2] if len(sys.argv) > 2 else config.get('default_channel', 'slack')
    
    success = False
    
    if notification_type == 'alerts':
        # Leer datos de alertas (ejemplo)
        alerts_data = {
            'summary': {
                'total': 3,
                'critical_count': 1,
                'high_count': 2
            }
        }
        
        message = format_alert_message(alerts_data)
        
        if channel == 'slack' and config.get('slack', {}).get('enabled'):
            success = send_slack_notification(
                config['slack']['webhook_url'],
                message,
                config['slack'].get('channel')
            )
        elif channel == 'teams' and config.get('teams', {}).get('enabled'):
            success = send_teams_notification(
                config['teams']['webhook_url'],
                "Alertas de Creativos",
                message
            )
        elif channel == 'email' and config.get('email', {}).get('enabled'):
            email_config = config['email']
            success = send_email_notification(
                email_config['smtp'],
                "Alertas de Creativos",
                message,
                email_config['recipients']
            )
    
    elif notification_type == 'performance':
        # Leer datos de performance (ejemplo)
        performance_data = {
            'total': 32,
            'by_format': {
                '1200x627': 15,
                '1080x1080': 6,
                '1080x1920': 6
            }
        }
        
        message = format_performance_message(performance_data)
        
        if channel == 'slack' and config.get('slack', {}).get('enabled'):
            success = send_slack_notification(
                config['slack']['webhook_url'],
                message,
                config['slack'].get('channel')
            )
    
    if success:
        print(f"✅ Notificación enviada a {channel}")
    else:
        print(f"⚠️  No se pudo enviar notificación a {channel}")
        print("   Verifica la configuración en .notifications_config.json")
    
    print()

if __name__ == '__main__':
    main()

