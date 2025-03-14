import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def send_email(to_email, subject, html_content, text_content=None):
    """
    Send an email using SMTP

    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_content (str): HTML content of the email
        text_content (str): Plain text content (optional)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # In development mode, just print to console
    if current_app.config.get('TESTING') or current_app.config.get('DEBUG'):
        print(f"\n----- EMAIL TO: {to_email} -----")
        print(f"Subject: {subject}")
        print(f"Content: {html_content}")
        print("----- END EMAIL -----\n")
        return True

    # Get email configuration
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    sender_email = os.environ.get('SENDER_EMAIL', smtp_username)

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    # Add text and HTML parts
    if text_content:
        part1 = MIMEText(text_content, 'plain')
        msg.attach(part1)

    part2 = MIMEText(html_content, 'html')
    msg.attach(part2)

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send email
        server.sendmail(sender_email, to_email, msg.as_string())
        server.close()
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False


def send_password_reset_email(user, reset_url):
    """
    Send a password reset email to a user

    Args:
        user: User model instance
        reset_url (str): URL for password reset

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Fale Com Jesus - Redefinição de Senha"

    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3f51b5;">Redefinição de Senha</h2>
            <p>Olá {user.first_name or 'usuário'},</p>
            <p>Recebemos uma solicitação para redefinir sua senha na aplicação Fale Com Jesus.</p>
            <p>Para redefinir sua senha, clique no link abaixo ou copie e cole na barra de endereços do seu navegador:</p>
            <p>
                <a href="{reset_url}" style="background-color: #3f51b5; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">
                    Redefinir minha senha
                </a>
            </p>
            <p>Este link é válido por apenas 1 hora.</p>
            <p>Se você não solicitou a redefinição de senha, você pode ignorar este email.</p>
            <p>Atenciosamente,<br>Equipe Fale Com Jesus</p>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Redefinição de Senha
    
    Olá {user.first_name or 'usuário'},
    
    Recebemos uma solicitação para redefinir sua senha na aplicação Fale Com Jesus.
    
    Para redefinir sua senha, acesse o link abaixo:
    {reset_url}
    
    Este link é válido por apenas 1 hora.
    
    Se você não solicitou a redefinição de senha, você pode ignorar este email.
    
    Atenciosamente,
    Equipe Fale Com Jesus
    """

    return send_email(user.email, subject, html_content, text_content)
