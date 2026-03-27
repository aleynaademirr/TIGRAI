import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import secrets
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)
class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.app_name = "TIGRAI"
    def generate_reset_token(self) -> str:
        return secrets.token_urlsafe(32)
    def get_token_expiry(self) -> datetime:
        return datetime.utcnow() + timedelta(hours=1)
    def send_password_reset_email(self, to_email: str, reset_token: str, username: str) -> bool:
        try:
            # Token'ın sadece ilk 8 karakterini gönder (Kullanıcı dostu olması için)
            short_token = reset_token[:8].upper()
            
            subject = f"{self.app_name} - Şifre Sıfırlama Kodu"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <h2 style="color: #333333; text-align: center;">Şifre Sıfırlama İsteği</h2>
                        <p style="color: #666666; font-size: 16px;">Merhaba <strong>{username}</strong>,</p>
                        <p style="color: #666666; font-size: 16px;">Hesabınızın şifresini sıfırlamak için bir istek aldık. Aşağıdaki kodu uygulamaya girerek şifrenizi yenileyebilirsiniz:</p>
                        
                        <div style="background-color: #f8f9fa; border: 2px dashed #007bff; padding: 15px; text-align: center; margin: 25px 0; border-radius: 5px;">
                            <span style="font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #007bff;">{short_token}</span>
                        </div>
                        
                        <p style="color: #666666; font-size: 14px;">Bu kodu siz talep etmediyseniz, bu e-postayı görmezden gelebilirsiniz.</p>
                        <hr style="border: none; border-top: 1px solid #eeeeee; margin: 20px 0;">
                        <p style="color: #999999; font-size: 12px; text-align: center;">© 2024 TIGRAI Uygulaması</p>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            Merhaba {username},
            
            Şifre sıfırlama kodunuz: {short_token}
            
            Bu kodu uygulamaya girerek şifrenizi yenileyebilirsiniz.
            """
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            
            message.attach(part1)
            message.attach(part2)
            
            if not self.sender_email or not self.sender_password:
                logger.warning("Email credentials not configured. Printing token to console instead.")
                logger.info(f"PASSWORD RESET TOKEN for {to_email}: {short_token}")
                # DEBUG: Konsola da bas ki görelim
                print(f"\n======== EMAIL SIMULATION ========")
                print(f"TO: {to_email}")
                print(f"CODE: {short_token}")
                print(f"==================================\n")
                return True  
                
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
                
            logger.info(f"Password reset email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            short_token = reset_token[:8].upper()
            logger.info(f"PASSWORD RESET TOKEN for {to_email}: {short_token}")
            print(f"FAILED EMAIL FALLBACK CODE: {short_token}")
            return False
email_service = EmailService()