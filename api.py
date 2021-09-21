import json
import time
from flask import send_file, jsonify

from logger import LOG

from transform import Transformer
from send import Mail
from settings import Settings


tr = Transformer()
mailer = Mail()

def get_readable_time(epoch_time):
    return f"{time.strftime('%d %b %Y %H:%M', time.localtime(epoch_time))}"

def generate_csv(created_from, created_to=None, download=False):
    if not created_to:
        created_to = int(time.time())
        LOG.info("Created to not sent")
    
    file_name, count, total_price, created_to = tr.generate_csv_order_file(created_from, created_to)

    if not download:
        subject = f"Recieved {count} orders from {get_readable_time(created_from)} to {get_readable_time(created_to)} worth {total_price}"
        body = f"Hi Stylor,\n\nYou have {subject.lower()}, please check and verify the attachment.\n\nRegards,\nBot Kashif"
        
        LOG.info(f" Subject {subject}")

        mailer.send_mail(subject, Settings.RECIEVER_EMAIL, body, file_name)  
        return "success"
    
    return send_file(file_name, attachment_filename=file_name.split('/')[-1])

def generate_total(created_from, created_to=None):
    if not created_to:
        created_to = int(time.time())
        LOG.info("Created to not sent")
    
    order_list, order_count, total_price = tr.get_order_list(created_from, created_to)

    influencer_order_ids = set()
    influencer_total_cost = 0

    for order in order_list:
        order_id, selling_price = order[0], order[25]

        if "ISTY" in order_id:
            # Influencer order
            influencer_order_ids.add(order_id)
            influencer_total_cost += selling_price
    
    resp = {"start_date": get_readable_time(created_from),
            "end_date": get_readable_time(created_to),
            "total": {"count": order_count, "price_value": total_price},
            "influencer": {"count": len(influencer_order_ids), "price_value": influencer_total_cost},
            "customer": {"count": order_count - len(influencer_order_ids), "price_value": total_price - influencer_total_cost}}
    
    return jsonify(resp)


def basic_auth(username, password, required_scopes=None):
    if username == Settings.API_USER and password == Settings.API_PASSWORD:
        return {'sub': Settings.API_USER}

    return None
    

    
    
