import os
import requests

from PIL import (
    Image,
    ImageDraw,
    ImageFont
)

# ==========================================
# PASTAS
# ==========================================
os.makedirs(
    'imagens/ofertas',
    exist_ok=True
)

os.makedirs(
    'imagens/produtos',
    exist_ok=True
)

# ==========================================
# GERA TEXTO DA OFERTA
# ==========================================
def gerar_texto_oferta(item):

    nome = item.get(
        'productName',
        'Produto'
    )

    preco_original = float(
        item.get('price', 0)
    )

    preco_promocao = float(
        item.get('priceMin', 0)
    )

    desconto = float(
        item.get(
            'priceDiscountRate',
            0
        )
    )

    link = item.get(
        'offerLink',
        ''
    )

    # ======================================
    # CALCULA PREÇO ORIGINAL
    # ======================================
    if (
        preco_original <= preco_promocao
        and desconto > 0
    ):

        preco_original = (
            preco_promocao /
            (1 - (desconto / 100))
        )

    # ======================================
    # FORMATA PREÇOS
    # ======================================
    preco_original_txt = (
        f"R$ {preco_original:.2f}"
        .replace('.', ',')
    )

    preco_promocao_txt = (
        f"R$ {preco_promocao:.2f}"
        .replace('.', ',')
    )

    # ======================================
    # TEXTO
    # ======================================
    texto = f"🔥 {nome} 🔥\n\n"

    texto += (
        f"❌ De {preco_original_txt}\n"
    )

    texto += (
        f"✅ Por {preco_promocao_txt}\n\n"
        f"({desconto:.0f}% OFF)\n\n"
    )

    texto += (
        f"⭐⭐⭐⭐⭐ \n\n"
    )

    texto += (
        "Faça seu pedido no Link 👇\n"
    )

    texto += f"➡️ {link}"

    return texto.strip()

# ==========================================
# GERA IMAGEM OFERTA
# ==========================================
def gerar_imagem_oferta(item):

    nome = item.get(
        'productName',
        'Produto'
    )

    preco = float(
        item.get('priceMin', 0)
    )

    desconto = int(
        float(
            item.get(
                'priceDiscountRate',
                0
            )
        )
    )

    image_url = item.get(
        'imageUrl',
        ''
    )

    item_id = item.get(
        'itemId'
    )

    # ======================================
    # BAIXA IMAGEM PRODUTO
    # ======================================
    caminho_produto = (
        f'imagens/produtos/{item_id}.jpg'
    )

    if image_url:

        response = requests.get(image_url)

        with open(
            caminho_produto,
            'wb'
        ) as f:

            f.write(response.content)

    # ======================================
    # CRIA FUNDO
    # ======================================
    largura = 800
    altura = 800

    imagem = Image.new(
        'RGB',
        (largura, altura),
        color=(20, 20, 20)
    )

    draw = ImageDraw.Draw(imagem)

    # ======================================
    # FONTES
    # ======================================
    fonte = ImageFont.load_default()

    # ======================================
    # INSERE IMAGEM PRODUTO
    # ======================================
    try:

        produto = Image.open(
            caminho_produto
        )

        produto = produto.resize(
            (400, 400)
        )

        imagem.paste(
            produto,
            (200, 50)
        )

    except:
        pass

    # ======================================
    # NOME
    # ======================================
    nome = nome[:45]

    draw.text(
        (50, 500),
        f"🔥 {nome}",
        fill=(255, 255, 255),
        font=fonte
    )

    # ======================================
    # PREÇO
    # ======================================
    preco_txt = (
        f"R$ {preco:.2f}"
        .replace('.', ',')
    )

    draw.text(
        (50, 580),
        f"✅ {preco_txt}",
        fill=(0, 255, 120),
        font=fonte
    )

    # ======================================
    # DESCONTO
    # ======================================
    draw.text(
        (50, 650),
        f"🏷️ {desconto}% OFF",
        fill=(255, 180, 0),
        font=fonte
    )

    # ======================================
    # SALVA
    # ======================================
    caminho_final = (
        f'imagens/ofertas/{item_id}.png'
    )

    imagem.save(caminho_final)

    return caminho_final