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
    "Energia":             ["EGIE3", "TAEE11", "CPLE3", "CMIG4", "EQTL3", "ISAE4", "NEOE3"],
    "Siderurgia e metais": ["GGBR4", "CSNA3", "USIM5", "CBAV3"],
    "Mineração":           ["VALE3", "CMIN3", "AURA33"],
}

# Período de coleta
DATA_INI = "2025-10-01"
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

# Juntar tudo num único DataFrame
df_precos = pd.concat(lista_dfs, ignore_index=True)
print(f"\n{'='*50}")
print(f"Total de linhas coletadas: {len(df_precos)}")
print(f"{'='*50}")
df_precos.head()
