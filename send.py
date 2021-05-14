import time
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from logger import LOG
from settings import Settings


class Mail(object):
    def __init__(self, sender_email=Settings.SENDER_EMAIL, sender_password=Settings.SENDER_PASSWORD, 
        smtp_server=Settings.SMTP_SERVER, smtp_port=Settings.SMTP_PORT):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def _get_login_context(self):
        context = ssl.create_default_context()
        return smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context)

    def send_mail(self, subject, to, body, attachment=None, bcc=None):
        message = MIMEMultipart()

        message["From"] = self.sender_email
        message["To"] = to
        message["Subject"] = subject
        message["Bcc"] = bcc

        message.attach(MIMEText(body, "plain"))

        if attachment:
            with open(attachment, "rb") as attachement_file:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachement_file.read())
                encoders.encode_base64(part)

                part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment.split('/')[-1]}",
                    )
            message.attach(part)

        text = message.as_string()

        with self._get_login_context() as server:
            LOG.info("Login to the smtp server")
            server.login(self.sender_email, self.sender_password)
            LOG.info("sending mail")
            server.sendmail(self.sender_email, to, text)
    