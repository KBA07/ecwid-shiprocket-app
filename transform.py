import sys
import os
import csv
from time import time
from shutil import copyfile

from fetch import EcwidAPI
from settings import Settings
from logger import LOG


class Transformer(object):
    def __init__(self, host=Settings.ECWID_HOST, store_id=Settings.ECWID_STORE_ID, access_token=Settings.ECWID_PRIVATE_TOKEN, 
        ID_PREFIX=Settings.ID_PREFIX, INFLUENCER_ID_PREFIX=Settings.INFLUENCER_ID_PREFIX, ID_FIRST_VALUE=Settings.ID_FIRST_VALUE):

        self.ecwid_api_obj = EcwidAPI(host, store_id, access_token)

        self.id_prefix = ID_PREFIX
        self.id_first_value = ID_FIRST_VALUE
        self.influencer_id_prefix = INFLUENCER_ID_PREFIX

        LOG.debug(f"ID Prefix:{self.id_prefix}, Influencer ID Prefix:{self.influencer_id_prefix}, ID Last Value:{self.id_first_value}")

    @staticmethod
    def get_payment_method(payment_status):
        if payment_status == "PAID":
            return "Prepaid"
        elif payment_status == "AWAITING_PAYMENT":
            return "COD"

    @staticmethod
    def get_order_date(date_string):
        date, time, _ = date_string.split(" ")
        year, month, day = date.split("-")
        year = year[2:] # Hack to satisfy the Shiprocket bulk update
        hour, minute, _ = time.split(":")
        return f"{'-'.join([year, month, day])} {':'.join([hour, minute])}"

    def generate_id(self, ecwid_order_id, order):
        order_id = self.id_first_value + int(ecwid_order_id)

        if Settings.INFLUENCER_COUPON_PREFIX in order.get("discountCoupon", {}).get("code", "XXXX"): # Gracefully handling the discount coupon
            return f"{self.influencer_id_prefix}{order_id}"

        return f"{self.id_prefix}{order_id}"

    def generate_csv_order_file(self, created_from, created_to=int(time()), source_sample_file=Settings.SOURCE_FILE, 
        dest_file_format = Settings.DESTINATION_FILE):

        dest_file = dest_file_format.format(created_to)
        copyfile(source_sample_file, dest_file)

        for order in self.ecwid_api_obj.get_all_orders(created_from, created_to):
            order_id = self.generate_id(order['id'], order)
            order_date = self.get_order_date(order['createDate'])
            channel = Settings.CHANNEL
            payment_method = self.get_payment_method(order['paymentStatus'])
            cutomer_first_name = order['shippingPerson'].get('firstName') or order['shippingPerson'].get('name')
            cutomer_last_name = order['shippingPerson'].get('lastName')
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

if __name__ == '__main__':
    Tr = Transformer()
    if len(sys.argv) == 3:
        Tr.generate_csv_order_file(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        Tr.generate_csv_order_file(sys.argv[1])
