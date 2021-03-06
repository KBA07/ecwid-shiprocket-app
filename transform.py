import sys
import os
import csv
from time import time
from shutil import copyfile

from fetch import EcwidAPI
from settings import Settings
from logger import LOG


class Transformer(object):
    _SKIP_ORDER_STATUS = ["REFUNDED", "CANCELLED"]
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
        
        LOG.info(f"unknown payment status recieved {payment_status}")

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
    
    def get_final_price(self, order_id, selling_price, discount):
        if "ISTY" in order_id:
            return selling_price
        return selling_price - discount

    def get_order_list(self, created_from, created_to):
        order_list = []
        order_count = 0
        total_price = 0
        for order in self.ecwid_api_obj.get_all_orders(created_from, created_to):
            if order['paymentStatus'] in self._SKIP_ORDER_STATUS:
                LOG.info("recieved order which is cancelled or refunded, hence skipping")
                continue

            order_count += 1
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
                tax = item['tax'] if item['tax'] else Settings.DEFAULT_TAX
                selling_price = item['price']
                discount = item.get('couponAmount', 0) if Settings.SHOW_DISCOUNT else None
                total_price += self.get_final_price(order_id, selling_price, discount)
                shipping_charges = item.get('shipping') if item.get('shipping') else None
                cod_charges = None
                gift_wrap_charges = None
                total_discount_per_order = order.get('couponDiscount') if Settings.SHOW_DISCOUNT else None

                dimensions = item.get('dimensions', {}) # gracefully handling this field
                length = dimensions.get('length') if dimensions.get('length') else Settings.DEFAULT_LENGTH # length, breath, height can also be 0
                breadth = dimensions.get('width') if dimensions.get('width') else Settings.DEFAULT_BREADTH
                height = dimensions.get('height') if dimensions.get('height') else Settings.DEFAULT_HEIGHT
                weight = item['weight'] if item['weight'] else Settings.DEFAULT_WEIGHT
                send_notification = Settings.SEND_NOTIFICATION
                comment = None
                hsn_code = None
                pickup_location_id = Settings.PICKUP_LOCATION_ID

                order_details = [master_sku, product_name, product_quantity, tax, selling_price, discount, shipping_charges, cod_charges,
                    gift_wrap_charges, total_discount_per_order, length, breadth, height, weight, send_notification, comment, hsn_code, 
                    pickup_location_id]

                order_list.append(base_details + order_details)

        return order_list, order_count, total_price


    def generate_csv_order_file(self, created_from, created_to=int(time()), source_sample_file=Settings.SOURCE_FILE, 
        dest_file_format = Settings.DESTINATION_FILE):

        for file in os.listdir(Settings.GENERATED_FILES_FOLDER):
            if "csv" in file:
                os.remove(Settings.GENERATED_FILES_FOLDER + file)

        dest_file = Settings.GENERATED_FILES_FOLDER + dest_file_format.format(created_to)
        copyfile(source_sample_file, dest_file)

        order_list, order_count, total_price = self.get_order_list(created_from, created_to)

        with open(dest_file, 'a', newline='') as file:
            for order in order_list:
                writer = csv.writer(file)
                writer.writerow(order)

        return dest_file, order_count, total_price, created_to    

if __name__ == '__main__':
    Tr = Transformer()
    if len(sys.argv) == 3:
        Tr.generate_csv_order_file(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        Tr.generate_csv_order_file(sys.argv[1])
    else:
        Tr.generate_csv_order_file(1)
