import requests
import os

from urllib.parse import urlparse
# ==========================================
# CONFIG EVOLUTION API
# ==========================================
URL = "http://localhost:8081"

INSTANCE = "WPP_TESTE"

TOKEN = "B0530B9FA045-43CC-88A0-EFCC49D4B84A"

# ==========================================
# ENVIO WHATSAPP
# ==========================================
def enviar_whatsapp(
    grupo_id,
    imagem_url,
    legenda
):

    url = (
        f"{URL}"
        f"/message/sendMedia/"
        f"{INSTANCE}"
    )

    headers = {
        "apikey": TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "number": grupo_id,
        "mediatype": "image",
        "media": imagem_url,
        "caption": legenda
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120
    )

    print(
        f"WhatsApp: {response.status_code}"
    )

    print(response.text)