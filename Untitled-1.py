
# %%
# =============================================================================
#  AULA 1 — STACK DA DISCIPLINA
#  Conceito: bibliotecas previstas na ementa (Python + Pandas + requests)
# =============================================================================
import requests
import pandas as pd
import re   # AULA REGEX — módulo de expressões regulares


# %%
# =============================================================================
#  AULA 3 — VARIÁVEIS (strings)
#  Conceito: armazenar valores em variáveis
# =============================================================================
BASE_URL = "https://laboratoriodefinancas.com/api/v2"
TOKEN    = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgxNzQzNjUwLCJpYXQiOjE3NzkxNTE2NTAsImp0aSI6Ijg5NDM1MTEyZTU2ZjQ2ZGNhOTE4NzFiMDA3M2YzMGMyIiwidXNlcl9pZCI6IjEwMSJ9.0RvfbPUc3L1dwU04C7owFlZ1pObMs6bQobLcMx7lKnM"

DATA_INI = "2025-03-01"
DATA_FIM = "2026-05-15"


# %%
# =============================================================================
#  AULA 3 — DICIONÁRIO + LISTA
#  Conceito: dicionário {chave: valor}, onde o valor pode ser uma lista
#  Aplicação: agrupar as ações por setor
# =============================================================================
TICKERS = {
    "Energia":             ["AXIA3", "EGIE3", "TAEE11", "CPLE3", "CMIG4", "EQTL3", "ISAE4", "NEOE3"],
    "Siderurgia e metais": ["GGBR4", "CSNA3", "USIM5", "CBAV3"],
    "Mineração":           ["VALE3", "CMIN3", "AURA33"],
}

# Dicionário com os 8 eventos analisados (chave = código, valor = data)
EVENTOS = {
    "E1": "2025-07-18",  # MP 1.307 (ZPEs)
    "E2": "2025-09-17",  # MP 1.318 (REDATA) - edição
    "E3": "2025-09-18",  # MP 1.318 - publicação DOU
    "E4": "2026-02-04",  # Protocolo do PL 278/2026
    "E5": "2026-02-10",  # Urgência aprovada na Câmara
    "E6": "2026-02-25",  # PL aprovado na Câmara
    "E7": "2026-02-25",  # Senado não vota
    "E8": "2026-02-25",  # Caducidade da MP
}


# %%
# =============================================================================
#  AULA 3 — ESTRUTURA DE REPETIÇÃO (LOOP ANINHADO)
#  Conceito: usar dois loops "for" para percorrer o dicionário TICKERS
#            e construir uma lista única com todas as ações.
#
#  OBS: no código profissional isso foi feito com "list comprehension"
#  (recurso avançado). Aqui reescrevemos com loop normal, no estilo da aula.
# =============================================================================

todos_tickers = []   # lista vazia (AULA 3 — listas)

for nome_setor in TICKERS:                  # AULA 3 — loop em dicionário
    for ticker in TICKERS[nome_setor]:      # AULA 3 — loop aninhado em lista
        todos_tickers.append(ticker)        # AULA 3 — método append

print(f"Total de ações a coletar: {len(todos_tickers)}")
print(f"Tickers: {todos_tickers}")


# %%
# =============================================================================
#  AULA REGEX — VALIDAÇÃO DOS TICKERS
#  Conceito: usar expressão regular para verificar se o código segue
#            o padrão da B3 (4 letras maiúsculas + 1 ou 2 dígitos)
#
#  Padrão usado:
#     ^         → início da string (slide do Cifrão e Circunflexo)
#     [A-Z]{4}  → range A-Z + quantificador {n} (slides de Colchetes e Quantificadores)
#     \d{1,2}   → classe pré-definida \d (dígito) + quantificador
#     $         → fim da string
# =============================================================================

padrao_ticker_b3 = r"^[A-Z]{4}\d{1,2}$"

print("\nValidação dos tickers pelo padrão da B3:")
for ticker in todos_tickers:
    # AULA REGEX — função re.search
    if re.search(padrao_ticker_b3, ticker):
        print(f"  {ticker}: válido")
    else:
        print(f"  {ticker}: INVÁLIDO")


# %%
# =============================================================================
#  AULA 6 — API REST (método GET)
#  Conceitos:
#    - requests.get(url, headers, params) → faz uma chamada GET (CRUD: Read)
#    - headers com token Bearer → autenticação
#    - status_code → 200 significa sucesso (slide de Status Codes)
#    - resp.json() → resposta em formato JSON
#
#  AULA 5 — JSON → DataFrame
#    - pd.DataFrame(lista_de_dicionarios) transforma o JSON em DataFrame
#
#  AULA 3 — loop + condicional para repetir a chamada por cada ação
# =============================================================================

HEADERS = {"Authorization": f"Bearer {TOKEN}"}   # AULA 3 — dicionário

lista_dfs = []   # AULA 3 — lista vazia (vai acumular um DataFrame por ação)

for ticker in todos_tickers:                     # AULA 3 — loop
    params = {                                   # AULA 3 — dicionário
        "ticker":   ticker,
        "data_ini": DATA_INI,
        "data_fim": DATA_FIM,
    }

    # AULA 6 — chamada GET com headers e params
    resp = requests.get(
        f"{BASE_URL}/preco/corrigido",
        headers=HEADERS,
        params=params,
    )

    # AULA 6 — verificar status_code
    # AULA 3 — estrutura condicional if/else
    if resp.status_code == 200:
        dados = resp.json()                      # AULA 6 — converter resposta em JSON
        if len(dados) > 0:
            df_temp = pd.DataFrame(dados)        # AULA 5 — JSON (lista de dicts) → DataFrame
            lista_dfs.append(df_temp)
            print(f"OK {ticker}: {len(dados)} registros")
        else:
            print(f"-- {ticker}: sem dados no periodo")
    else:
        print(f"XX {ticker}: erro {resp.status_code}")


# %%
# =============================================================================
#  AULA 6 — COLETA DO IBOVESPA (mesma lógica anterior)
#  AULA 5 — JSON → DataFrame
# =============================================================================

params_ibov = {                                  # AULA 3 — dicionário
    "ticker":   "IBOV",
    "data_ini": DATA_INI,
    "data_fim": DATA_FIM,
}

# AULA 6 — chamada GET
resp = requests.get(
    f"{BASE_URL}/preco/diversos",
    headers=HEADERS,
    params=params_ibov,
)

# AULA 5 — JSON → DataFrame
df_ibov = pd.DataFrame(resp.json())

print(f"\nTotal de registros do Ibovespa: {len(df_ibov)}")
print(f"Primeira data: {df_ibov['data'].min()}")
print(f"Última data:   {df_ibov['data'].max()}")


# %%
# =============================================================================
#  AULA 4 — JUNTAR DATAFRAMES
#  Conceito: pd.concat() empilha vários DataFrames em um único
#            (mesmo conceito de "append" mostrado no slide da A4)
# =============================================================================

df_precos = pd.concat(lista_dfs, ignore_index=True)

print(f"\nDataFrame único criado: df_precos")
print(f"Total de linhas: {len(df_precos)}")
print(f"Ações distintas: {df_precos['ticker'].nunique()}")
print(f"Colunas: {list(df_precos.columns)}")


# %%
# =============================================================================
#  AULA 4 — EXPLORAÇÃO DO DATAFRAME
#  Conceitos: .head(), .shape, .columns, .isna()
# =============================================================================

print("\nShape (linhas, colunas):", df_precos.shape)
print("\nPrimeiras 5 linhas:")
print(df_precos.head())
print("\nQuantidade de valores ausentes (NaN) por coluna:")
print(df_precos.isna().sum())


# %%
# =============================================================================
#  PRÉ-PROCESSAMENTO — conversão da coluna data
#
#  Observação: pd.to_datetime() não foi mostrado explicitamente em aula,
#  mas é o equivalente direto, no Pandas, ao conceito de "tipo de dado"
#  da AULA 3. Aqui ele é necessário para podermos comparar datas mais à frente.
# =============================================================================

df_precos["data"] = pd.to_datetime(df_precos["data"])


# %%
# =============================================================================
#  PARTE 2 — GERAR TABELA DE UM SETOR EM UM EVENTO
#
#  Esta parte usa exclusivamente:
#    - AULA 3: variáveis, listas, dicionários, loops, condicional
#    - AULA 4: filtrar DataFrame, acessar colunas
#    - AULA 5: dicionário → DataFrame
#
#  No código profissional, esta parte usou df.pivot() (não visto em aula).
#  Aqui reescrevemos com loop manual + dicionário → DataFrame, gerando
#  exatamente o mesmo resultado.
# =============================================================================

def gerar_tabela_setor_evento(nome_setor, codigo_evento):

    # ---------------------------------------------------------------------
    # AULA 3 — acessar valores de dicionário
    # ---------------------------------------------------------------------
    data_evento   = pd.to_datetime(EVENTOS[codigo_evento])
    tickers_setor = TICKERS[nome_setor]

    # ---------------------------------------------------------------------
    # AULA 4 — acessar coluna do DataFrame e pegar valores únicos
    # ---------------------------------------------------------------------
    datas_pregao = sorted(df_precos["data"].unique())

    # ---------------------------------------------------------------------
    # AULA 3 — loop com condicional para encontrar o dia do evento
    # (se o evento caiu num dia sem pregão, pega o próximo dia útil)
    # ---------------------------------------------------------------------
    idx_evento = None
    for i in range(len(datas_pregao)):
        if datas_pregao[i] >= data_evento:
            idx_evento = i
            break

    # ---------------------------------------------------------------------
    # AULA 3 — operações simples com variáveis numéricas (índices)
    # ---------------------------------------------------------------------
    idx_inicio   = idx_evento - 5
    idx_fim      = idx_evento + 5
    datas_janela = datas_pregao[idx_inicio : idx_fim + 1]

    # ---------------------------------------------------------------------
    # AULA 4 — filtragem de DataFrame com condições booleanas e .isin()
    # ---------------------------------------------------------------------
    df_filtrado = df_precos[
        (df_precos["data"].isin(datas_janela)) &
        (df_precos["ticker"].isin(tickers_setor))
    ]

    # ---------------------------------------------------------------------
    # AULA 5 — montar um dicionário onde cada chave será uma coluna do
    # DataFrame final. Depois transformamos esse dicionário em DataFrame.
    # AULA 3 — loops aninhados para preencher o dicionário.
    # ---------------------------------------------------------------------
    dados_tabela = {}

    # Coluna "Dia" com a numeração -5 a +5 (lista construída com range, AULA 3)
    dados_tabela["Dia"] = list(range(-5, 6))

    # Para cada ticker do setor, montamos duas colunas (abertura e fechamento)
    for ticker in sorted(tickers_setor):           # AULA 3 — loop
        lista_abertura   = []                      # AULA 3 — lista vazia
        lista_fechamento = []

        # Para cada dia da janela, buscamos o valor desse ticker
        for data_dia in datas_janela:              # AULA 3 — loop aninhado
            # AULA 4 — filtragem do DataFrame
            df_dia = df_filtrado[
                (df_filtrado["ticker"] == ticker) &
                (df_filtrado["data"]   == data_dia)
            ]
            # AULA 3 — estrutura condicional
            if len(df_dia) > 0:
                # AULA 4 — acessar valor de uma coluna do DataFrame
                lista_abertura.append(df_dia["abertura"].iloc[0])
                lista_fechamento.append(df_dia["fechamento"].iloc[0])
            else:
                lista_abertura.append(None)
                lista_fechamento.append(None)

        # AULA 3 — atribuir nova entrada no dicionário
        dados_tabela[f"{ticker}_abertura"]   = lista_abertura
        dados_tabela[f"{ticker}_fechamento"] = lista_fechamento

    # ---------------------------------------------------------------------
    # AULA 5 — transformar o dicionário (de listas) em DataFrame
    # ---------------------------------------------------------------------
    tabela = pd.DataFrame(dados_tabela)

    # ---------------------------------------------------------------------
    # IMPRESSÃO DA TABELA (uso de f-strings e print, AULA 3)
    # ---------------------------------------------------------------------
    print("=" * 100)
    print(f"SETOR: {nome_setor.upper()}    |    EVENTO: {codigo_evento} ({EVENTOS[codigo_evento]})")
    print("=" * 100)
    print(tabela)
    print("=" * 100)
    print(f"Linha em destaque: dia 0 = data do evento ({data_evento.strftime('%d/%m/%Y')})")
    print()

    return tabela


# ---------- TESTE: gerar UMA tabela para conferir ----------
tabela_teste = gerar_tabela_setor_evento("Energia", "E5")


# %%
# =============================================================================
#  PARTE 3 — GERAR AS 24 TABELAS (3 SETORES × 8 EVENTOS)
#
#  Conceitos usados:
#    - AULA 3: loop aninhado (loop dentro de loop) + dicionário
#    - Toda a lógica de geração da tabela está na função da PARTE 2
# =============================================================================

# AULA 3 — dicionário vazio para guardar todas as tabelas geradas
todas_tabelas = {}

# AULA 3 — loop pelos 8 eventos do dicionário EVENTOS
for codigo_evento in EVENTOS:
    # AULA 3 — loop aninhado pelos 3 setores do dicionário TICKERS
    for nome_setor in TICKERS:
        # AULA 3 — montar string com f-string
        chave  = f"{codigo_evento}_{nome_setor}"
        # Chama a função criada na PARTE 2
        tabela = gerar_tabela_setor_evento(nome_setor, codigo_evento)
        # AULA 3 — guardar resultado no dicionário
        todas_tabelas[chave] = tabela


# %%
# =============================================================================
#  RESUMO FINAL
# =============================================================================

print("\n" + "=" * 100)
print(f"TOTAL DE TABELAS GERADAS: {len(todas_tabelas)}")
print("=" * 100)
print("\nTabelas disponíveis no dicionário 'todas_tabelas':")

# AULA 3 — loop pelas chaves do dicionário
for chave in todas_tabelas:
    print(f"  - {chave}")

print()
print("=" * 100)
print("FIM DA VERSÃO DIDÁTICA")
print("=" * 100)
print()
print("Este arquivo cobriu, usando apenas o conteúdo das aulas:")
print("  - A1: stack de ferramentas")
print("  - A2: passos 1, 2, 3 e 4 do processo de análise de dados")
print("  - A3: variáveis, listas, dicionários, loops, condicionais")
print("  - A4: DataFrame, filtragem, exploração, concat")
print("  - A5: JSON/dicionário -> DataFrame")
print("  - A6: API REST com método GET, status_code, JSON")
print("  - Regex: validação dos códigos das ações da B3")
print()
print("O cálculo de retornos, retorno anormal, CAR e gráficos estão no")
print("arquivo principal (trabalho_completo.py), pois exigem conceitos")
print("além do escopo das aulas (groupby, pct_change, merge, matplotlib).")