import os

ECWID_PUBLIC_TOKEN = os.getenv("ECWID_PUBLIC_TOKEN")
ECWID_PRIVATE_TOKEN = os.getenv("ECWID_PRIVATE_TOKEN")
STORE_ID = os.getenv("STORE_ID")

if not ECWID_PRIVATE_TOKEN or not STORE_ID:
    raise Exception("Token or store id missing")
    