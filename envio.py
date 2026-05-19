import requests
import os

from urllib.parse import urlparse
# ==========================================
# CONFIG EVOLUTION API
# ==========================================
URL = "https://evolution.casteloautomotivo.com.br/"

INSTANCE = "evolution_vps"

TOKEN = "959FC4B19C56-4635-9097-94070E58B24A"

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

    resp = response.json()

    print({
        "status": response.status_code,
        "id": resp.get("key", {}).get("id"),
        "grupo": resp.get("key", {}).get("remoteJid"),
    })