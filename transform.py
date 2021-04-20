import os
import csv
from time import time
from shutil import copyfile

from fetch import Orders
from settings import Settings
from logger import LOG


def get_payment_method(payment_status):
    if payment_status == "PAID":
        return "Prepaid"
    elif payment_status == "AWAITING_PAYMENT":
        return "COD"

def get_order_date(date_string):
    date, time, _ = date_string.split(" ")
    year, month, day = date.split("-")
    year = year[2:] # Hack to satisfy the Shiprocket bulk update
    hour, minute, _ = time.split(":")
    return f"{'-'.join([year, month, day])} {':'.join([hour, minute])}"


class IdGenerator(object):
    def __init__(self, ID_PREFIX=Settings.ID_PREFIX, INFLUENCER_ID_PREFIX=Settings.INFLUENCER_ID_PREFIX, 
        ID_FIRST_VALUE=Settings.ID_FIRST_VALUE):
        
        self.id_prefix = ID_PREFIX
        self.id_first_value = ID_FIRST_VALUE
        self.influencer_id_prefix = INFLUENCER_ID_PREFIX

        LOG.debug(f"ID Prefix:{self.id_prefix}, Influencer ID Prefix:{self.influencer_id_prefix}, ID Last Value:{self.id_first_value}")


    def generate_id(self, ecwid_order_id):
        order_id = self.id_first_value + int(ecwid_order_id)

        if Settings.INFLUENCER_COUPON_PREFIX in order.get("discountCoupon", {}).get("code", "XXXX"): # Gracefully handling the discount coupon
            return f"{self.influencer_id_prefix}{order_id}"

        return f"{self.id_prefix}{order_id}"


if __name__ == "__main__":
    id_obj = IdGenerator()
    
    dest_file = Settings.DESTINATION_FILE.format(int(time()))
    copyfile(Settings.SOURCE_FILE, dest_file)

    orders_obj = Orders(Settings.ECWID_HOST, Settings.ECWID_STORE_ID, Settings.ECWID_PRIVATE_TOKEN)

    for order in orders_obj.get_all_orders(created_from=1618840946):
        order_id = id_obj.generate_id(order['id'])
        order_date = get_order_date(order['createDate'])
        channel = Settings.CHANNEL
        payment_method = get_payment_method(order['paymentStatus'])
        cutomer_first_name = order['shippingPerson'].get('firstName') or order['shippingPerson'].get('name')
        cutomer_last_name = order['shippingPerson'].get('lastName')
        # customer_name = order['shippingPerson']['name']
        customer_email = order['email']
        number_length = len(order['shippingPerson']['phone'])
        customer_mobile =  order['shippingPerson']['phone'][number_length - 10:]
        customer_alternate_mobile = None
        address_line_1 = order['shippingPerson']['street']
        address_line_2 = None
        country =  order['shippingPerson']['countryName']
        state = order['shippingPerson']['stateOrProvinceName']
        city = order['shippingPerson']['city']
        pincode = order['shippingPerson']['postalCode'] 

        billing_address_line_1 = None
        billing_address_line_2 = None
        billing_country = None
        billing_state = None
        billing_city = None
        billing_pincode = None

        base_details = [order_id, order_date, channel, payment_method, cutomer_first_name, cutomer_last_name, customer_email, 
            customer_mobile, customer_alternate_mobile, address_line_1, address_line_2, country, state, city, pincode, 
            billing_address_line_1, billing_address_line_2, billing_country, billing_state, billing_city, billing_pincode]

        for item in order['items']:
            master_sku = item['sku']
            product_name = item['name']
            product_quantity = item['quantity']
            tax = item['tax'] if item['tax'] else None
            selling_price = item['price']
            discount = item.get('couponAmount') if Settings.SHOW_DISCOUNT else None
            shipping_charges = item.get('shipping') if item.get('shipping') else None
            cod_charges = None
            gift_wrap_charges = None
            total_discount_per_order = order['couponDiscount'] if Settings.SHOW_DISCOUNT else None
            length = item['dimensions']['length'] if item['dimensions']['length'] else Settings.DEFAULT_LENGTH
            breadth = item['dimensions']['width'] if item['dimensions']['width'] else Settings.DEFAULT_BREADTH
            height = item['dimensions']['height'] if item['dimensions']['height'] else Settings.DEFAULT_HEIGHT
            weight = item['weight'] if item['weight'] else Settings.DEFAULT_WEIGHT
            send_notification = Settings.SEND_NOTIFICATION
            comment = None
            hsn_code = None
            pickup_location_id = Settings.PICKUP_LOCATION_ID

            order_details = [master_sku, product_name, product_quantity, tax, selling_price, discount, shipping_charges, cod_charges,
                gift_wrap_charges, total_discount_per_order, length, breadth, height, weight, send_notification, comment, hsn_code, 
                pickup_location_id]

            total_detail = base_details + order_details
            with open(dest_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(total_detail)

        print(f"order id:{order_id}, order date: {order_date}, channel:{channel}, payment method:{payment_method}, customer email:{customer_email}, customer mobile:{customer_mobile}, order name:{order['items'][0].get('name')}")
