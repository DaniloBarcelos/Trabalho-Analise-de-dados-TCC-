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
# ----- TESTE: BUSCAR PREÇOS DA VALE3 -----
params = {
    "ticker": "VALE3",
    "data_ini": "2026-01-01",
    "data_fim": "2026-05-15",
}

resp = requests.get(
    f"{BASE_URL}/preco/corrigido",SS
    headers=HEADERS,
    params=params,
)

print(f"Status: {resp.status_code}")
print(f"Total de registros: {len(resp.json())}")

# Transformar em DataFrame
df_vale = pd.DataFrame(resp.json())
df_vale.head(10)