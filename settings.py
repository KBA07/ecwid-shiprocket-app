import os

from logger import LOG

class Settings(object):
    TEST_MODE = False
    ECWID_HOST = os.getenv("ECWID_HOST", "https://app.ecwid.com/")
    ECWID_PUBLIC_TOKEN = os.getenv("ECWID_PUBLIC_TOKEN") # Optional for now
    ECWID_PRIVATE_TOKEN = os.getenv("ECWID_PRIVATE_TOKEN") # Mandatory
    ECWID_STORE_ID = os.getenv("STORE_ID") # Mandatory

    PICKUP_LOCATION_ID = int(os.getenv("PICKUP_LOCATION_ID")) # Mandatory
    ID_FIRST_VALUE = int(os.getenv("ID_FIRST_VALUE")) # Mandatory

    LOG.debug(f"ECWID_PRIVATE_TOKEN {ECWID_PRIVATE_TOKEN}, ECWID_STORE_ID {ECWID_STORE_ID},"
        f"PICKUP_LOCATION_ID {PICKUP_LOCATION_ID}, ID_FIRST_VALUE {ID_FIRST_VALUE}")

    if not ECWID_PRIVATE_TOKEN or not ECWID_STORE_ID or not PICKUP_LOCATION_ID or not ID_FIRST_VALUE:
        raise Exception("Some of the required fields are missing")

    SHOW_DISCOUNT = bool(os.getenv("SHOW_DISCOUNT", False)) # Toggle to write discount related data to csv
    SEND_NOTIFICATION = bool(os.getenv("SEND_NOTIFICATION", True)) # Todo Looks Buggy, Toggle to write send notification to CSV

    CHANNEL = os.getenv("CHANNEL", "CUSTOM")
    ID_PREFIX =  os.getenv("ID_PREFIX", "STY")
    
    INFLUENCER_ID_PREFIX = os.getenv("INFLUENCER_ID_PREFIX", "ISTY")
    INFLUENCER_COUPON_PREFIX = os.getenv("INFLUENCER_COUPON_PREFIX", "INFC")

    DEFAULT_LENGTH = int(os.getenv("DEFAULT_LENGTH", 14))
    DEFAULT_BREADTH = int(os.getenv("DEFAULT_BREADTH", 12))
    DEFAULT_HEIGHT = float(os.getenv("DEFAULT_HEIGHT", 0.5))
    DEFAULT_WEIGHT = float(os.getenv("DEFAULT_WEIGHT", 0.5))

    LOG.debug(f"DEFAULT_LENGTH: {DEFAULT_LENGTH}, DEFAULT_BREADTH: {DEFAULT_BREADTH}, DEFAULT_HEIGHT:{DEFAULT_HEIGHT}, DEFAULT_WEIGHT: {DEFAULT_WEIGHT} ")

    SOURCE_FILE = os.getenv("SOURCE_FILE", "order.csv")
    DESTINATION_FILE_PREFIX = os.getenv("DESTINATION_FILE_PREFIX", "orders")
    DESTINATION_FILE = DESTINATION_FILE_PREFIX + '{}.csv'
