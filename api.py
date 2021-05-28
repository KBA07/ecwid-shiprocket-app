import time
from flask import send_file

from logger import LOG

from transform import Transformer
from send import Mail
from settings import Settings


tr = Transformer()
mailer = Mail()

def generate_csv(created_from, created_to=None, download=False):
    if not created_to:
        created_to = int(time.time())
        LOG.info("Created to not sent")
    
    file_name, count, total_price, created_to = tr.generate_csv_order_file(created_from, created_to)

    if not download:
        subject = f"Recieved {count} orders from {time.strftime('%d %b %Y %H:%M', time.localtime(created_from))} to {time.strftime('%d %b %Y %H:%M', time.localtime(created_to))} worth {total_price}"
        body = f"Hi Stylor,\n\nYou have {subject.lower()}, please check and verify the attachment.\n\nRegards,\nBot Kashif"
        
        LOG.info(f" Subject {subject}")

        mailer.send_mail(subject, Settings.RECIEVER_EMAIL, body, file_name)  
        return "success"
    
    return send_file(file_name, attachment_filename=file_name.split('/')[-1])

def basic_auth(username, password, required_scopes=None):
    if username == Settings.API_USER and password == Settings.API_PASSWORD:
        return {'sub': Settings.API_USER}

    return None
    

    
    
