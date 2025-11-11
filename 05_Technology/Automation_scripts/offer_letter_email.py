#!/usr/bin/env python3
"""
Sistema de Envío de Cartas de Oferta por Email
Permite enviar cartas de oferta directamente por email
"""

import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import os


def send_offer_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    attachment_path: Optional[str] = None,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    from_email: Optional[str] = None,
    cc_emails: Optional[List[str]] = None
) -> bool:
    """Envía una carta de oferta por email."""
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email or smtp_user or "noreply@company.com"
        msg['To'] = to_email
        
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
        
        # Agregar cuerpo de texto
        text_part = MIMEText(body_text, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Agregar cuerpo HTML si está disponible
        if body_html:
            html_part = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Agregar adjunto si está disponible
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
        
        # Enviar email
        if not smtp_user or not smtp_password:
            print("⚠ Advertencia: SMTP credentials no proporcionadas")
            print("   Configura SMTP_USER y SMTP_PASSWORD como variables de entorno")
            return False
        
        print(f"📧 Enviando email a {to_email}...")
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        
        recipients = [to_email]
        if cc_emails:
            recipients.extend(cc_emails)
        
        server.send_message(msg, from_addr=msg['From'], to_addrs=recipients)
        server.quit()
        
        print(f"✅ Email enviado exitosamente a {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}", file=sys.stderr)
        return False


def send_offer_from_file(
    to_email: str,
    offer_file: str,
    candidate_name: str,
    position_title: str,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    from_email: Optional[str] = None,
    company_name: str = "[Company Name]"
) -> bool:
    """Envía una carta de oferta desde un archivo."""
    
    # Leer archivo
    try:
        with open(offer_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}", file=sys.stderr)
        return False
    
    # Crear asunto y cuerpo
    subject = f"Offer Letter - {position_title} - {company_name}"
    
    # Preparar cuerpo del email
    email_body = f"""
Dear {candidate_name},

Please find attached your offer letter for the position of {position_title} at {company_name}.

We are excited about the possibility of you joining our team!

Best regards,
{company_name} HR Team
"""
    
    # Enviar
    return send_offer_email(
        to_email=to_email,
        subject=subject,
        body_text=email_body + "\n\n" + content,
        attachment_path=offer_file,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        from_email=from_email
    )


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Envía cartas de oferta por email')
    parser.add_argument('--to', required=True,
                       help='Email del destinatario')
    parser.add_argument('--file', dest='offer_file',
                       help='Archivo de carta de oferta a enviar')
    parser.add_argument('--subject',
                       help='Asunto del email')
    parser.add_argument('--body',
                       help='Cuerpo del email')
    parser.add_argument('--html', dest='html_file',
                       help='Archivo HTML a enviar')
    parser.add_argument('--attachment', dest='attachment',
                       help='Archivo adjunto (PDF, etc.)')
    parser.add_argument('--candidate-name', dest='candidate_name',
                       help='Nombre del candidato')
    parser.add_argument('--position', dest='position_title',
                       help='Título del puesto')
    parser.add_argument('--company', dest='company_name',
                       help='Nombre de la empresa')
    parser.add_argument('--from', dest='from_email',
                       help='Email del remitente')
    parser.add_argument('--cc', dest='cc_emails',
                       help='Emails CC (separados por comas)')
    parser.add_argument('--smtp-server', dest='smtp_server',
                       default='smtp.gmail.com',
                       help='Servidor SMTP (default: smtp.gmail.com)')
    parser.add_argument('--smtp-port', dest='smtp_port',
                       type=int, default=587,
                       help='Puerto SMTP (default: 587)')
    parser.add_argument('--smtp-user', dest='smtp_user',
                       help='Usuario SMTP (o usar env SMTP_USER)')
    parser.add_argument('--smtp-password', dest='smtp_password',
                       help='Contraseña SMTP (o usar env SMTP_PASSWORD)')
    
    args = parser.parse_args()
    
    # Obtener credenciales de variables de entorno si no se proporcionan
    smtp_user = args.smtp_user or os.getenv('SMTP_USER')
    smtp_password = args.smtp_password or os.getenv('SMTP_PASSWORD')
    from_email = args.from_email or smtp_user
    
    if not smtp_user or not smtp_password:
        print("❌ Error: Se requieren credenciales SMTP", file=sys.stderr)
        print("   Usa --smtp-user y --smtp-password o variables de entorno SMTP_USER y SMTP_PASSWORD", file=sys.stderr)
        sys.exit(1)
    
    # Enviar desde archivo
    if args.offer_file:
        candidate_name = args.candidate_name or "[Candidate Name]"
        position_title = args.position_title or "[Position Title]"
        company_name = args.company_name or "[Company Name]"
        
        success = send_offer_from_file(
            to_email=args.to,
            offer_file=args.offer_file,
            candidate_name=candidate_name,
            position_title=position_title,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            from_email=from_email,
            company_name=company_name
        )
    else:
        # Enviar con cuerpo personalizado
        subject = args.subject or "Offer Letter"
        body = args.body or "Please find your offer letter attached."
        
        # Leer HTML si está disponible
        html_content = None
        if args.html_file:
            with open(args.html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
        success = send_offer_email(
            to_email=args.to,
            subject=subject,
            body_text=body,
            body_html=html_content,
            attachment_path=args.attachment,
            smtp_server=args.smtp_server,
            smtp_port=args.smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            from_email=from_email,
            cc_emails=args.cc_emails.split(',') if args.cc_emails else None
        )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()



