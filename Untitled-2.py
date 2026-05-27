# %%
# =============================================================
#  COLETA DE DADOS — TRABALHO REDATA E B3
#  Fonte: Laboratório de Finanças
#  Objetivo: coletar preços diários das ações dos setores de
#  energia, mineração e siderurgia + Ibovespa
# =============================================================
import requests
import pandas as pd
from datetime import date, timedelta

# ----- CONFIGURAÇÃO -----
BASE_URL = "https://laboratoriodefinancas.com/api/v2"
TOKEN   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgxNzQzNjUwLCJpYXQiOjE3NzkxNTE2NTAsImp0aSI6Ijg5NDM1MTEyZTU2ZjQ2ZGNhOTE4NzFiMDA3M2YzMGMyIiwidXNlcl9pZCI6IjEwMSJ9.0RvfbPUc3L1dwU04C7owFlZ1pObMs6bQobLcMx7lKnM"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# %%
# =============================================================
#  COLETA COMPLETA — 13 AÇÕES DA AMOSTRA
#  Período: outubro/2025 a maio/2026
# =============================================================

# Lista de ações por setor
TICKERS = {
    "Energia":             ["AXIA3", "EGIE3", "TAEE11", "CPLE3", "CMIG4", "EQTL3", "ISAE4", "NEOE3"],
    "Siderurgia e metais": ["GGBR4", "CSNA3", "USIM5", "CBAV3"],
    "Mineração":           ["VALE3", "CMIN3", "AURA33"],
}

# Período de coleta
DATA_INI = "2025-03-01"
DATA_FIM = "2026-05-15"

# Lista plana de todos os tickers (junta tudo em uma lista só)
todos_tickers = [t for setor in TICKERS.values() for t in setor]
print(f"Total de ações a coletar: {len(todos_tickers)}")
print(f"Tickers: {todos_tickers}")

# %%
# ----- BUSCAR PREÇOS DE TODAS AS AÇÕES -----
lista_dfs = []  # vai guardar um DataFrame por ação

for ticker in todos_tickers:
    params = {
        "ticker":   ticker,
        "data_ini": DATA_INI,
        "data_fim": DATA_FIM,
    }

    resp = requests.get(
        f"{BASE_URL}/preco/corrigido",
        headers=HEADERS,
        params=params,
    )

    if resp.status_code == 200:
        dados = resp.json()
        if len(dados) > 0:
            df_temp = pd.DataFrame(dados)
            lista_dfs.append(df_temp)
            print(f"✅ {ticker}: {len(dados)} registros")
        else:
            print(f"⚠️  {ticker}: sem dados no período")
    else:
        print(f"❌ {ticker}: erro {resp.status_code}")

# %%
# =============================================================
#  COLETA DO IBOVESPA (BENCHMARK)
#  Endpoint diferente: /preco/diversos (índices e outros)
# =============================================================
params_ibov = {
    "ticker":   "IBOV",
    "data_ini": DATA_INI,
    "data_fim": DATA_FIM,
}

resp = requests.get(
    f"{BASE_URL}/preco/diversos",
    headers=HEADERS,
    params=params_ibov,
)

df_ibov = pd.DataFrame(resp.json())

print(f"Total de registros do Ibovespa: {len(df_ibov)}")
print(f"Primeira data: {df_ibov['data'].min()}")
print(f"Última data:   {df_ibov['data'].max()}")
print()
df_ibov.head()

# %%
# =============================================================
#  JUNTAR TODAS AS AÇÕES NUM ÚNICO DATAFRAME
# =============================================================
df_precos = pd.concat(lista_dfs, ignore_index=True)

print(f"DataFrame único criado: df_precos")
print(f"Total de linhas: {len(df_precos)}")
print(f"Ações distintas: {df_precos['ticker'].nunique()}")
print(f"Colunas: {list(df_precos.columns)}")
df_precos.head()


# %%
# =============================================================
#  PARTE 1: PREPARAÇÃO PARA ANÁLISE POR EVENTO
#  Define os 8 eventos do REDATA e prepara o DataFrame de preços
# =============================================================

# Dicionário com os 8 eventos: código -> data
EVENTOS = {
    "E1": "2025-07-18",  # MP 1.307 (ZPEs)
    "E2": "2025-09-17",  # MP 1.318 (REDATA) - edição
    "E3": "2025-09-18",  # MP 1.318 - publicação DOU
    "E4": "2026-02-04",  # Protocolo do PL 278/2026
    "E5": "2026-02-10",  # Urgência aprovada na Câmara
    "E6": "2026-02-25",  # PL aprovado na Câmara (madrugada 24-25)
    "E7": "2026-02-25",  # Senado não vota
    "E8": "2026-02-25",  # Caducidade da MP
}

# Converte a coluna 'data' do DataFrame pra tipo datetime do pandas
df_precos["data"] = pd.to_datetime(df_precos["data"])

# Mostra o que ficou
print(f"Eventos definidos: {len(EVENTOS)}")
for cod, data in EVENTOS.items():
    print(f"  {cod}: {data}")
print(f"\nDataFrame de preços: {len(df_precos)} linhas")
print(f"Colunas: {list(df_precos.columns)}")

# %%
# =============================================================
#  PARTE 2: FUNÇÃO QUE GERA A TABELA DE UM SETOR NUM EVENTO
#  Recebe: nome do setor + código do evento
#  Retorna: tabela com 11 linhas (dias -5 a +5)
#           e colunas Abertura/Fechamento de cada ação
# =============================================================

def gerar_tabela_setor_evento(nome_setor, codigo_evento):
    # PASSO 1: pegar a data do evento e a lista de ações do setor
    data_evento = pd.to_datetime(EVENTOS[codigo_evento])
    tickers_setor = TICKERS[nome_setor]

    # PASSO 2: pegar todas as datas distintas do df_precos (só dias de pregão)
    datas_pregao = sorted(df_precos["data"].unique())

    # PASSO 3: achar o índice do dia do evento na lista de pregões
    # (se o evento caiu num dia sem pregão, pega o próximo dia útil)
    idx_evento = None
    for i in range(len(datas_pregao)):
        if datas_pregao[i] >= data_evento:
            idx_evento = i
            break

    # PASSO 4: pegar os 11 dias da janela (-5 a +5)
    idx_inicio = idx_evento - 5
    idx_fim = idx_evento + 5
    datas_janela = datas_pregao[idx_inicio : idx_fim + 1]

    # PASSO 5: filtrar o df_precos pra ter só essas datas e essas ações
    df_filtrado = df_precos[
        (df_precos["data"].isin(datas_janela)) &
        (df_precos["ticker"].isin(tickers_setor))
    ]

    # PASSO 6: reorganizar com pivot (uma linha por data, colunas por ação)
    tabela = df_filtrado.pivot(
        index="data",
        columns="ticker",
        values=["abertura", "fechamento"]
    )

    # PASSO 7: simplificar nomes das colunas (juntar os 2 níveis em 1)
    # Ex: ("abertura", "AXIA3") vira "AXIA3_abertura"
    tabela.columns = [f"{ticker}_{valor}" for valor, ticker in tabela.columns]

    # PASSO 8: ordenar colunas: cada ação aparece junto (abertura + fechamento)
    tickers_ordenados = sorted(tickers_setor)
    colunas_ordenadas = []
    for t in tickers_ordenados:
        colunas_ordenadas.append(f"{t}_abertura")
        colunas_ordenadas.append(f"{t}_fechamento")
    tabela = tabela[colunas_ordenadas]

    # PASSO 9: adicionar coluna "Dia" no início (-5 a +5)
    tabela.insert(0, "Dia", range(-5, 6))

    # IMPRESSÃO COM DESTAQUE NO DIA 0
    print("=" * 100)
    print(f"SETOR: {nome_setor.upper()}    |    EVENTO: {codigo_evento} ({EVENTOS[codigo_evento]})")
    print("=" * 100)
    print(tabela)
    print("=" * 100)
    print(f"⭐ Linha em destaque: dia 0 = data do evento ({data_evento.strftime('%d/%m/%Y')})")
    print()

    return tabela


# TESTE: gerar uma tabela pra ver se funciona
tabela_teste = gerar_tabela_setor_evento("Energia", "E5")

# %%
# =============================================================
#  PARTE 3: GERAR AS 24 TABELAS (3 SETORES × 8 EVENTOS)
#  Loop que chama a função gerar_tabela_setor_evento()
#  pra cada combinação setor + evento
# =============================================================

# Dicionário pra guardar todas as tabelas geradas
# Chave: "E1_Energia", "E1_Siderurgia", ..., "E8_Mineração"
# Valor: o DataFrame da tabela
todas_tabelas = {}

# Loop pelos 8 eventos
for codigo_evento in EVENTOS.keys():
    # Loop pelos 3 setores
    for nome_setor in TICKERS.keys():
        # Chama a função e guarda a tabela no dicionário
        chave = f"{codigo_evento}_{nome_setor}"
        tabela = gerar_tabela_setor_evento(nome_setor, codigo_evento)
        todas_tabelas[chave] = tabela

# Resumo final
print(f"\n{'=' * 100}")
print(f"✅ TOTAL DE TABELAS GERADAS: {len(todas_tabelas)}")
print(f"{'=' * 100}")
print(f"\nTabelas disponíveis em 'todas_tabelas' (dicionário):")
for chave in todas_tabelas.keys():
    print(f"  - {chave}")


# %%
# =============================================================
#  PARTE 4: CALCULAR RETORNOS DIÁRIOS
#  Calcula a variação % de um dia pro outro
#  - Para cada ação (agrupando por ticker)
#  - Para o Ibovespa
# =============================================================

# ----- CONVERTER COLUNAS DE PREÇO PARA NÚMERO -----
# A API retorna como texto (string), precisa converter pra calcular
colunas_preco = ["abertura", "maximo", "minimo", "medio", "fechamento"]
for col in colunas_preco:
    df_precos[col] = pd.to_numeric(df_precos[col], errors="coerce")
    df_ibov[col] = pd.to_numeric(df_ibov[col], errors="coerce")

# ----- RETORNOS DAS AÇÕES -----
# Garante que o DataFrame está ordenado por ticker e data
df_precos = df_precos.sort_values(["ticker", "data"]).reset_index(drop=True)

# Calcula o retorno diário de cada ação separadamente (groupby por ticker)
df_precos["retorno"] = df_precos.groupby("ticker")["fechamento"].pct_change()

# ----- RETORNO DO IBOVESPA -----
df_ibov = df_ibov.sort_values("data").reset_index(drop=True)
df_ibov["retorno"] = df_ibov["fechamento"].pct_change()

# ----- RESUMO ESTATÍSTICO -----
print("=" * 80)
print("RESUMO DOS RETORNOS DIÁRIOS POR AÇÃO")
print("=" * 80)

resumo = df_precos.groupby("ticker")["retorno"].agg(["mean", "min", "max", "count"])
resumo.columns = ["Retorno Médio", "Retorno Mín", "Retorno Máx", "Qtd dias"]
resumo["Retorno Médio"] = resumo["Retorno Médio"] * 100
resumo["Retorno Mín"] = resumo["Retorno Mín"] * 100
resumo["Retorno Máx"] = resumo["Retorno Máx"] * 100

print(resumo)

print("\n" + "=" * 80)
print("RESUMO DO RETORNO DIÁRIO DO IBOVESPA")
print("=" * 80)
print(f"  Retorno Médio: {df_ibov['retorno'].mean() * 100:.4f}%")
print(f"  Retorno Mín:   {df_ibov['retorno'].min() * 100:.4f}%")
print(f"  Retorno Máx:   {df_ibov['retorno'].max() * 100:.4f}%")
print(f"  Qtd dias:      {df_ibov['retorno'].count()}")

print("\n✅ Coluna 'retorno' adicionada ao df_precos e ao df_ibov")