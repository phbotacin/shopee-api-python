import requests
import hashlib
import time
import json
import csv
import re
import os
import urllib3
from datetime import datetime
from gerador import gerar_texto_oferta
from envio import enviar_whatsapp

INTERVALO_ENVIO = 900
INTERVALO_MINUTOS = 10
MAX_ENVIOS_POR_CICLO = 3
INTERVALO_BUSCA = 60
INTERVALO_ENVIO = 15 * 60
FILA_OFERTAS = []
MIN_SCORE_ENVIO = 180

GRUPOS = [
    "120363423990969726@g.us",
    "120363423599499160@g.us"
]

# ==========================================
# REMOVE AVISO SSL
# ==========================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CONFIG API
# ==========================================
APP_ID = '18364220581'
SECRET = 'GAHBWP5ADTSBNEYR7VUMWLVAA252EXGL'

URL = 'https://open-api.affiliate.shopee.com.br/graphql'

# ==========================================
# CONFIGURAÇÕES DO BOT
# ==========================================
INTERVALO_MINUTOS = 10

MIN_DESCONTO = 40
MIN_SALES = 30
MIN_COMISSAO = 0.03

LIMIT = 50
PAGINAS = 10

ARQUIVO_HISTORICO = 'data/historico_ids.json'
ARQUIVO_CSV = 'data/novas_promocoes.csv'

# ==========================================
# SEM FILTRO DE PALAVRA
# ==========================================
KEYWORDS = [""]

# ==========================================
# LIMPA COMISSION BUGADA
# ==========================================
def limpar_commission_rate(valor_str):

    if not valor_str:
        return 0

    valor_str = str(valor_str)

    match = re.search(r'0\.\d+', valor_str)

    if match:
        return float(match.group(0))

    return 0

# ==========================================
# HISTÓRICO IDS
# ==========================================
def carregar_historico():

    if not os.path.exists(ARQUIVO_HISTORICO):
        return set()

    with open(
        ARQUIVO_HISTORICO,
        'r',
        encoding='utf-8'
    ) as f:

        return set(json.load(f))

def salvar_historico(ids):

    with open(
        ARQUIVO_HISTORICO,
        'w',
        encoding='utf-8'
    ) as f:

        json.dump(list(ids), f)

# ==========================================
# ASSINATURA API
# ==========================================
def gerar_headers(payload):

    timestamp = str(int(time.time()))

    factor = APP_ID + timestamp + payload + SECRET

    signature = hashlib.sha256(
        factor.encode('utf-8')
    ).hexdigest()

    return {
        'Content-Type': 'application/json',
        'Authorization':
            f"SHA256 Credential={APP_ID},"
            f"Timestamp={timestamp},"
            f"Signature={signature}"
    }

# ==========================================
# CONSULTA API
# ==========================================
def buscar_produtos(keyword="", page=1):

    query = f'''
    {{
      productOfferV2(
        keyword: "{keyword}",
        sortType: 4,
        page: {page},
        limit: {LIMIT}
      ) {{

        nodes {{
          itemId
          productName
          offerLink
          priceMin
          price
          imageUrl
          priceDiscountRate
          commissionRate
          sales
          shopName
        }}

        pageInfo {{
          hasNextPage
        }}
      }}
    }}
    '''

    payload = json.dumps({
        'query': query
    }, separators=(',', ':'))

    headers = gerar_headers(payload)

    response = requests.post(
        URL,
        data=payload,
        headers=headers,
        verify=False
    )

    if response.status_code != 200:

        print(
            "❌ Erro HTTP:",
            response.status_code
        )

        return []

    resposta_json = response.json()

    if 'errors' in resposta_json:

        print("❌ Erro GraphQL:")

        print(json.dumps(
            resposta_json,
            indent=2,
            ensure_ascii=False
        ))

        return []

    data = resposta_json \
        .get('data', {}) \
        .get('productOfferV2', {})

    return data.get('nodes', [])

# ==========================================
# SCORE INTELIGENTE
# ==========================================
def calcular_score(item):

    desconto = float(
        item.get('priceDiscountRate', 0)
    )

    sales = int(
        item.get('sales', 0)
    )

    comissao = float(
        item.get('commissionRate_clean', 0)
    )

    preco = float(
        item.get('priceMin', 0)
    )

    # ======================================
    # BONUS PREÇO
    # ======================================
    bonus_preco = 0

    if preco <= 50:
        bonus_preco = 25

    elif preco <= 100:
        bonus_preco = 15

    elif preco <= 200:
        bonus_preco = 5

    # ======================================
    # BONUS SALES
    # ======================================
    bonus_sales = 0

    if sales >= 1000:
        bonus_sales = 50

    elif sales >= 500:
        bonus_sales = 30

    elif sales >= 100:
        bonus_sales = 10

    # ======================================
    # BONUS COMISSÃO
    # ======================================
    bonus_comissao = 0

    if comissao >= 0.10:
        bonus_comissao = 40

    elif comissao >= 0.07:
        bonus_comissao = 25

    elif comissao >= 0.05:
        bonus_comissao = 10

    # ======================================
    # SCORE FINAL
    # ======================================
    score = (
        desconto * 2 +
        sales * 0.3 +
        (comissao * 100) +
        bonus_preco +
        bonus_sales +
        bonus_comissao
    )

    return round(score, 2)

# ==========================================
# SALVA CSV
# ==========================================
def salvar_csv(produtos):

    arquivo_existe = os.path.exists(
        ARQUIVO_CSV
    )

    with open(
        ARQUIVO_CSV,
        'a',
        newline='',
        encoding='utf-8-sig'
    ) as csvfile:

        writer = csv.writer(csvfile)

        # CABEÇALHO
        if not arquivo_existe:

            writer.writerow([
                'Data',
                'Score',
                'Item Id',
                'Produto',
                'Preço',
                'Desconto',
                'Sales',
                'Comissão',
                'Loja',
                'Link'
            ])

        # PRODUTOS
        for item in produtos:

            preco = float(
                item.get('priceMin', 0)
            )

            writer.writerow([
                datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                item.get('score'),
                item.get('itemId'),
                item.get('productName'),
                f'R${preco:.2f}'.replace('.', ','),
                f"{item.get('priceDiscountRate')}%",
                item.get('sales'),
                f"{item.get('commissionRate_clean') * 100:.0f}%",
                item.get('shopName'),
                item.get('offerLink')
            ])

# ==========================================
# FILTRO OFERTAS
# ==========================================
def filtrar_ofertas(nodes, historico):

    novas = []

    for item in nodes:

        try:

            item_id = str(
                item.get('itemId')
            )

            # IGNORA REPETIDOS
            if item_id in historico:
                continue

            desconto = float(
                item.get('priceDiscountRate', 0)
            )

            sales = int(
                item.get('sales', 0)
            )

            comissao = limpar_commission_rate(
                item.get('commissionRate', '0')
            )

            preco = float(
                item.get('priceMin', 0)
            )

            # ==================================
            # FILTROS
            # ==================================
            if desconto < MIN_DESCONTO:
                continue

            if sales < MIN_SALES:
                continue

            if comissao < MIN_COMISSAO:
                continue

            # IGNORA PREÇOS MUITO ALTOS
            if preco > 3000:
                continue

            # SALVA COMISSÃO LIMPA
            item['commissionRate_clean'] = comissao

            # CALCULA SCORE
            item['score'] = calcular_score(item)

            novas.append(item)

            historico.add(item_id)

        except:
            continue

    return novas

# ==========================================
# MOSTRA OFERTAS
# ==========================================
def mostrar_ofertas(ofertas):

    if not ofertas:

        print(
            "Nenhuma nova oferta encontrada."
        )

        return

    print(
        f"\n🔥 NOVAS OFERTAS: "
        f"{len(ofertas)}\n"
    )

    for item in ofertas:

        preco = float(
            item.get('priceMin', 0)
        )

        print("=" * 80)

        print(
            "🛒",
            item.get('productName')
        )

        print(
            f"⭐ SCORE: "
            f"{item.get('score')}"
        )

        print(
            f"💰 R${preco:.2f}"
            .replace('.', ',')
        )

        print(
            f"🏷️ "
            f"{item.get('priceDiscountRate')}% OFF"
        )

        print(
            f"💵 Comissão: "
            f"{item['commissionRate_clean'] * 100:.0f}%"
        )

        print(
            f"📦 Sales: "
            f"{item.get('sales')}"
        )

        print(
            f"🏪 Loja: "
            f"{item.get('shopName')}"
        )

        print(
            f"🔗 "
            f"{item.get('offerLink')}"
        )

# ==========================================
# LOOP PRINCIPAL
# ==========================================
def scanner():

    historico = carregar_historico()

    fila_ofertas = []

    ultima_busca = 0

    print(
        "\n🚀 Scanner Shopee iniciado...\n"
    )

    while True:

        try:

            agora = time.time()

            # ==================================
            # FAZ NOVA BUSCA
            # ==================================
            if (
                agora - ultima_busca
                >= INTERVALO_BUSCA * 60
            ):

                print(
                    f"\n🔎 Nova busca "
                    f"{datetime.now().strftime('%H:%M:%S')}"
                )

                todas_ofertas = []

                for page in range(
                    1,
                    PAGINAS + 1
                ):

                    print(
                        f"📄 Página {page}"
                    )

                    produtos = buscar_produtos(
                        keyword="",
                        page=page
                    )

                    ofertas = filtrar_ofertas(
                        produtos,
                        historico
                    )

                    todas_ofertas.extend(
                        ofertas
                    )

                    time.sleep(1)

                # ==============================
                # ORDENA SCORE
                # ==============================
                todas_ofertas.sort(
                    key=lambda x: float(
                        x.get('score', 0)
                    ),
                    reverse=True
                )

                # ==============================
                # ADICIONA NA FILA
                # ==============================
                for item in todas_ofertas:

                    if (
                        item.get('score', 0)
                        >= 180
                    ):

                        fila_ofertas.append(
                            item
                        )

                # REMOVE DUPLICADOS
                ids = set()

                fila_unica = []

                for item in fila_ofertas:

                    item_id = item.get(
                        'itemId'
                    )

                    if item_id not in ids:

                        ids.add(item_id)

                        fila_unica.append(
                            item
                        )

                fila_ofertas = fila_unica

                salvar_historico(
                    historico
                )

                ultima_busca = agora

                print(
                    f"\n📦 "
                    f"{len(fila_ofertas)} "
                    f"ofertas na fila"
                )

            # ==================================
            # ENVIA 1 OFERTA
            # ==================================
            if fila_ofertas:

                item = fila_ofertas.pop(0)

                texto = gerar_texto_oferta(
                    item
                )

                imagem = item.get(
                    'imageUrl'
                )

                print(
                    f"\n📤 Enviando:"
                )

                print(
                    item.get('productName')
                )

                for grupo in GRUPOS:

                    enviar_whatsapp(
                        grupo_id=grupo,
                        imagem_url=item.get('imageUrl'),
                        legenda=texto
                    )

                    time.sleep(3)

                salvar_csv([item])

                print(
                    f"\n⏳ "
                    f"Próximo envio em "
                    f"15 minutos..."
                )

                time.sleep(
                    INTERVALO_ENVIO
                )

            else:

                print(
                    "\n📭 "
                    "Fila vazia..."
                )

                time.sleep(60)

        except Exception as e:

            print("\n❌ ERRO:")

            print(str(e))

            time.sleep(30)