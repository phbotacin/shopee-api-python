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
# BAIXA IMAGEM
# ==========================================
def baixar_imagem(url_imagem):

    pasta = "temp"

    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = os.path.basename(
        urlparse(url_imagem).path
    )

    caminho = os.path.join(
        pasta,
        nome_arquivo
    )

    response = requests.get(
        url_imagem,
        timeout=30
    )

    with open(caminho, 'wb') as f:
        f.write(response.content)

    return caminho

# ==========================================
# ENVIO WHATSAPP
# ==========================================
def enviar_whatsapp(
    grupo_id,
    imagem_url,
    legenda
):

    # ======================================
    # BAIXA IMAGEM
    # ======================================
    caminho_imagem = baixar_imagem(
        imagem_url
    )

    url = (
        f"{EVOLUTION_URL}"
        f"/message/sendMedia/"
        f"{INSTANCE}"
    )

    headers = {
        "apikey": API_KEY
    }

    files = {
        "file": open(caminho_imagem, "rb")
    }

    data = {
        "number": grupo_id,
        "mediatype": "image",
        "caption": legenda
    }

    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=data,
        timeout=120
    )

    print(
        f"WhatsApp: {response.status_code}"
    )

    print(response.text)

    # ======================================
    # REMOVE IMAGEM TEMP
    # ======================================
    try:
        os.remove(caminho_imagem)
    except:
        pass