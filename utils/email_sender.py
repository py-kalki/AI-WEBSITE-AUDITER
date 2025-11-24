import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailSender:
    def __init__(self, smtp_server=None, smtp_port=None, smtp_user=None, smtp_password=None):
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", 587))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")

    def send_email(self, to_email, subject, body):
        """
        Send an email using SMTP.
        
        Args:
            to_email (str): Recipient email.
            subject (str): Email subject.
            body (str): Email body (HTML or Text).
            
        Returns:
            bool: True if successful, False otherwise.
            str: Error message if failed.
        """
        if not self.smtp_user or not self.smtp_password:
            return False, "SMTP credentials not configured."

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_user, to_email, text)
            server.quit()
            
            return True, "Email sent successfully."
        except Exception as e:
            return False, str(e)
