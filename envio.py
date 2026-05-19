import requests
import os

from urllib.parse import urlparse
from datetime import datetime
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

    agora = datetime.now().strftime("%H:%M:%S")

    print("\n📤 Enviando oferta...")
    print(f"🕒 Horário : {agora}")
    print(f"🛍️ Produto : {titulo}")

    print(f"\n👥 Grupo   : {grupo_nome}")
    print(f"📱 Status  : {response.status_code}")

    if response.status_code == 201:
        print("✅ Sucesso")
        print(f"🆔 Msg ID  : {resp.get('key', {}).get('id')}")
    else:
        print("❌ Erro ao enviar")
        print(resp)

    print("-" * 50)