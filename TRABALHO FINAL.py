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

# ----- AJUSTES PARA RODAR VIA TERMINAL (Windows) -----
# (1) Forçar stdout em UTF-8: o cmd/PowerShell do Windows usa cp1252
#     por padrão e quebra ao imprimir emojis (✅, 🏆, 📉, etc.)
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# (2) Aceitar conexão SSL mesmo com cert local desatualizado:
#     o cert raiz do laboratoriodefinancas.com pode não estar no bundle
#     do Python desta máquina, causando SSLCertVerificationError.
#     Patcheamos requests.get uma única vez para passar verify=False
#     em todas as chamadas sem precisar repetir o argumento.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Pode rodar a célula quantas vezes quiser: SEMPRE reseta requests.get
# pra função original do módulo (requests.api.get) antes de envolver.
# Assim NUNCA empilha wrappers — não dá RecursionError no Jupyter.
requests.get = requests.api.get
_orig_get = requests.get
def _get_sem_verify(*args, **kwargs):
    kwargs.setdefault("verify", False)
    kwargs.setdefault("timeout", 60)
    return _orig_get(*args, **kwargs)
requests.get = _get_sem_verify
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
# %%
# =============================================================
#  PARTE 5: CALCULAR RETORNOS ANORMAIS
#  Retorno anormal = Retorno da ação − Retorno do Ibovespa
# =============================================================

# ----- GARANTIR QUE A COLUNA DATA DO IBOV ESTÁ EM FORMATO DATETIME -----
df_ibov["data"] = pd.to_datetime(df_ibov["data"])

# ----- JUNTAR RETORNO DO IBOVESPA NO DF_PRECOS -----
df_ibov_renomeado = df_ibov[["data", "retorno"]].rename(
    columns={"retorno": "retorno_ibov"}
)

# Faz o merge (junção) pela coluna data
df_precos = df_precos.merge(df_ibov_renomeado, on="data", how="left")

# ----- CALCULAR O RETORNO ANORMAL -----
df_precos["retorno_anormal"] = df_precos["retorno"] - df_precos["retorno_ibov"]

# ----- RESUMO ESTATÍSTICO -----
print("=" * 90)
print("RESUMO DOS RETORNOS ANORMAIS POR AÇÃO")
print("=" * 90)

resumo_anormal = df_precos.groupby("ticker")["retorno_anormal"].agg(
    ["mean", "min", "max", "count"]
)
resumo_anormal.columns = ["RA Médio", "RA Mín", "RA Máx", "Qtd dias"]
resumo_anormal["RA Médio"] = resumo_anormal["RA Médio"] * 100
resumo_anormal["RA Mín"] = resumo_anormal["RA Mín"] * 100
resumo_anormal["RA Máx"] = resumo_anormal["RA Máx"] * 100

dias_acima = df_precos[df_precos["retorno_anormal"] > 0].groupby("ticker").size()
dias_abaixo = df_precos[df_precos["retorno_anormal"] < 0].groupby("ticker").size()
resumo_anormal["Dias > Ibov"] = dias_acima
resumo_anormal["Dias < Ibov"] = dias_abaixo

print(resumo_anormal)

print("\n" + "=" * 90)
print("MÉDIA DO RETORNO ANORMAL POR SETOR")
print("=" * 90)

def buscar_setor(ticker):
    for setor, tickers in TICKERS.items():
        if ticker in tickers:
            return setor
    return "Outro"

df_precos["setor"] = df_precos["ticker"].apply(buscar_setor)

resumo_setor = df_precos.groupby("setor")["retorno_anormal"].agg(["mean", "min", "max"])
resumo_setor.columns = ["RA Médio", "RA Mín", "RA Máx"]
resumo_setor = resumo_setor * 100

print(resumo_setor)

print("\n✅ Colunas 'retorno_ibov', 'retorno_anormal' e 'setor' adicionadas ao df_precos")
# %%
# =============================================================
#  PARTE 6: APLICAR JANELAS DOS EVENTOS
#  Calcula o CAR (Retorno Anormal Acumulado) para cada ação
#  em cada evento, nas 3 janelas (-1/+1, -3/+3, -5/+5)
# =============================================================

# Define as 3 janelas
JANELAS = {
    "-1/+1": 1,   # 1 dia antes até 1 dia depois
    "-3/+3": 3,   # 3 dias antes até 3 dias depois
    "-5/+5": 5,   # 5 dias antes até 5 dias depois
}

# Lista pra guardar os resultados (vamos transformar em DataFrame depois)
resultados = []

# Pegar todas as datas distintas (só dias de pregão)
datas_pregao = sorted(df_precos["data"].unique())

# Loop pelos 8 eventos
for codigo_evento, data_evento_str in EVENTOS.items():
    data_evento = pd.to_datetime(data_evento_str)

    # Achar o índice do dia do evento na lista de pregões
    # (se cair em dia sem pregão, pega o próximo dia útil)
    idx_evento = None
    for i in range(len(datas_pregao)):
        if datas_pregao[i] >= data_evento:
            idx_evento = i
            break

    # Loop pelas 3 janelas
    for nome_janela, tamanho in JANELAS.items():
        idx_inicio = idx_evento - tamanho
        idx_fim = idx_evento + tamanho
        datas_janela = datas_pregao[idx_inicio : idx_fim + 1]

        # Loop por cada ação
        for ticker in df_precos["ticker"].unique():
            # Filtrar: só essa ação e só os dias da janela
            df_filtro = df_precos[
                (df_precos["ticker"] == ticker) &
                (df_precos["data"].isin(datas_janela))
            ]

            # Calcular o CAR (soma dos retornos anormais da janela)
            car = df_filtro["retorno_anormal"].sum()

            # Pegar o setor dessa ação
            setor = buscar_setor(ticker)

            # Guardar resultado
            resultados.append({
                "Evento": codigo_evento,
                "Data": data_evento_str,
                "Ticker": ticker,
                "Setor": setor,
                "Janela": nome_janela,
                "CAR": car * 100,  # em %
            })

# Transformar em DataFrame
df_resultados = pd.DataFrame(resultados)

# ----- RESUMO 1: CAR POR AÇÃO E EVENTO (-5/+5 só, pra não ficar gigante) -----
print("=" * 100)
print("CAR (RETORNO ANORMAL ACUMULADO) POR AÇÃO E EVENTO — JANELA -5/+5")
print("=" * 100)
print()

# Pivotar pra ficar: linhas=ação, colunas=evento, valores=CAR
tabela_acao_evento = df_resultados[df_resultados["Janela"] == "-5/+5"].pivot(
    index="Ticker",
    columns="Evento",
    values="CAR"
)
print(tabela_acao_evento.round(2))

# ----- RESUMO 2: CAR MÉDIO POR SETOR E EVENTO -----
print("\n" + "=" * 100)
print("CAR MÉDIO POR SETOR E EVENTO (todas as janelas)")
print("=" * 100)

# Agrupar por evento + setor + janela, calcular média do CAR
resumo_setor_evento = df_resultados.groupby(
    ["Evento", "Setor", "Janela"]
)["CAR"].mean().reset_index()

# Pivotar: linhas=evento+setor, colunas=janela, valores=CAR médio
tabela_setor = resumo_setor_evento.pivot_table(
    index=["Evento", "Setor"],
    columns="Janela",
    values="CAR"
)
print(tabela_setor.round(2))

# ----- RESUMO 3: TABELA RESUMO PRA RESPONDER AS HIPÓTESES -----
print("\n" + "=" * 100)
print("RESUMO PRA AS HIPÓTESES: CAR MÉDIO POR SETOR (média de todos os eventos)")
print("=" * 100)

resumo_hipoteses = df_resultados.groupby(["Setor", "Janela"])["CAR"].mean().reset_index()
tabela_hipoteses = resumo_hipoteses.pivot(
    index="Setor",
    columns="Janela",
    values="CAR"
)
print(tabela_hipoteses.round(2))

print("\n✅ DataFrame 'df_resultados' criado com todos os CARs calculados")
print(f"   Total de linhas: {len(df_resultados)}")
print(f"   (15 ações × 8 eventos × 3 janelas = 360 cálculos esperados)")
# %%
# =============================================================
#  PARTE 7: GRÁFICO DO EVENTO E5 (Aprovação da Urgência)
#  Linhas: retorno acumulado bruto de cada setor + Ibovespa
#  Janela: -5/+5 dias úteis ao redor do evento
# =============================================================
import matplotlib.pyplot as plt

# Evento que vamos plotar
CODIGO_EVENTO = "E5"
data_evento = pd.to_datetime(EVENTOS[CODIGO_EVENTO])

# ----- IDENTIFICAR OS DIAS DA JANELA -5/+5 -----
datas_pregao = sorted(df_precos["data"].unique())

# Achar o índice do dia do evento
idx_evento = None
for i in range(len(datas_pregao)):
    if datas_pregao[i] >= data_evento:
        idx_evento = i
        break

# Pegar os 11 dias da janela (-5 a +5)
datas_janela = datas_pregao[idx_evento - 5 : idx_evento + 6]
dias = list(range(-5, 6))  # [-5, -4, ..., 0, ..., +5]

# ----- CALCULAR RETORNO ACUMULADO POR SETOR -----
# Pra cada setor, tira a média dos retornos das ações em cada dia
# e acumula (vai somando dia a dia)

retornos_por_setor = {}  # vai guardar a lista de retornos acumulados por setor

for nome_setor, tickers_setor in TICKERS.items():
    retornos_dia = []  # retorno médio do setor em cada dia da janela
    for data_dia in datas_janela:
        # Filtra ações do setor nesse dia
        df_dia = df_precos[
            (df_precos["data"] == data_dia) &
            (df_precos["ticker"].isin(tickers_setor))
        ]
        # Tira a média dos retornos das ações desse setor nesse dia
        retorno_medio = df_dia["retorno"].mean()
        retornos_dia.append(retorno_medio)

    # Calcula o ACUMULADO (soma cumulativa dia a dia)
    # Ex: [0.01, 0.02, -0.01] → [0.01, 0.03, 0.02]
    acumulado = []
    soma = 0
    for r in retornos_dia:
        soma += r
        acumulado.append(soma * 100)  # em %

    retornos_por_setor[nome_setor] = acumulado

# ----- CALCULAR RETORNO ACUMULADO DO IBOVESPA -----
retornos_ibov_dia = []
for data_dia in datas_janela:
    df_dia_ibov = df_ibov[df_ibov["data"] == data_dia]
    if len(df_dia_ibov) > 0:
        retornos_ibov_dia.append(df_dia_ibov["retorno"].iloc[0])
    else:
        retornos_ibov_dia.append(0)

acumulado_ibov = []
soma = 0
for r in retornos_ibov_dia:
    soma += r
    acumulado_ibov.append(soma * 100)

# ----- CRIAR O GRÁFICO -----
plt.figure(figsize=(12, 7))

# Linhas dos setores (cores diferentes)
cores = {
    "Energia": "#2E74B5",          # azul
    "Siderurgia e metais": "#E97132",  # laranja
    "Mineração": "#70AD47",        # verde
}

for nome_setor, valores in retornos_por_setor.items():
    plt.plot(
        dias, valores,
        marker="o", linewidth=2.5,
        label=nome_setor, color=cores[nome_setor]
    )

# Linha do Ibovespa (referência, mais discreta)
plt.plot(
    dias, acumulado_ibov,
    marker="s", linewidth=2, linestyle="--",
    label="Ibovespa", color="gray"
)

# Linha vertical no dia do evento (dia 0)
plt.axvline(x=0, color="red", linestyle=":", linewidth=1.5, alpha=0.7)

# Linha horizontal no zero (referência)
plt.axhline(y=0, color="black", linestyle="-", linewidth=0.5)

# Anotação do evento
plt.text(
    0.1, plt.ylim()[1] * 0.9,
    f"Evento {CODIGO_EVENTO}\n{data_evento.strftime('%d/%m/%Y')}",
    fontsize=10, color="red"
)

# Títulos e labels
plt.title(
    f"Retorno Acumulado por Setor — Evento {CODIGO_EVENTO} "
    f"(Aprovação da Urgência do PL 278/2026)",
    fontsize=13, fontweight="bold"
)
plt.xlabel("Dias em relação ao evento", fontsize=11)
plt.ylabel("Retorno acumulado (%)", fontsize=11)
plt.xticks(dias)
plt.legend(loc="best", fontsize=10, framealpha=0.9)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.show()

print(f"\n✅ Gráfico do evento {CODIGO_EVENTO} gerado")
print(f"   Setores comparados: {list(retornos_por_setor.keys())}")
print(f"   Referência: Ibovespa")
# %%
# =============================================================
#  PARTE 8: VARIAÇÃO DE PREÇO NA JANELA DO EVENTO (-5 vs +5)
#  Calcula, para cada ação em cada evento, a variação percentual
#  do preço de fechamento entre o dia -5 e o dia +5.
#  É a medida descritiva principal usada na conclusão do trabalho.
# =============================================================

variacoes = []  # vai acumular dicionários, depois vira DataFrame

# Pega todas as datas distintas (só dias de pregão) — já ordenadas
datas_pregao = sorted(df_precos["data"].unique())

# Loop pelos 8 eventos
for codigo_evento, data_evento_str in EVENTOS.items():
    data_evento = pd.to_datetime(data_evento_str)

    # Acha o índice do dia do evento na lista de pregões
    idx_evento = None
    for i in range(len(datas_pregao)):
        if datas_pregao[i] >= data_evento:
            idx_evento = i
            break

    # Pega o dia -5 e o dia +5 (em pregões)
    dia_m5 = datas_pregao[idx_evento - 5]
    dia_p5 = datas_pregao[idx_evento + 5]

    # Para cada ação, calcula a variação
    for ticker in df_precos["ticker"].unique():
        # Preço no dia -5
        df_m5 = df_precos[
            (df_precos["ticker"] == ticker) & (df_precos["data"] == dia_m5)
        ]
        # Preço no dia +5
        df_p5 = df_precos[
            (df_precos["ticker"] == ticker) & (df_precos["data"] == dia_p5)
        ]

        if len(df_m5) > 0 and len(df_p5) > 0:
            preco_m5 = df_m5["fechamento"].iloc[0]
            preco_p5 = df_p5["fechamento"].iloc[0]
            variacao = (preco_p5 / preco_m5 - 1) * 100

            variacoes.append({
                "Evento": codigo_evento,
                "Data": data_evento_str,
                "Ticker": ticker,
                "Setor": buscar_setor(ticker),
                "Preço -5": round(preco_m5, 2),
                "Preço +5": round(preco_p5, 2),
                "Variação (%)": round(variacao, 2),
            })

# Transforma a lista em DataFrame
df_variacoes = pd.DataFrame(variacoes)

print("=" * 90)
print("VARIAÇÃO DE PREÇO NA JANELA (-5 vs +5) — TODAS AS COMBINAÇÕES")
print("=" * 90)
print(f"Total de combinações: {len(df_variacoes)} (15 ações × 8 eventos)")
print()
print(df_variacoes.head(15))

print("\n✅ DataFrame 'df_variacoes' criado")
# %%
# =============================================================
#  PARTE 9: TABELA POR AÇÃO — MAIOR ALTA, MAIOR QUEDA,
#           MAIOR PREÇO E MENOR PREÇO DA AMOSTRA INTEIRA
#  Para cada uma das 15 ações, mostra:
#    - A maior alta na janela (-5 vs +5) e em qual evento foi
#    - A maior queda na janela (-5 vs +5) e em qual evento foi
#    - O maior preço de fechamento observado em qualquer janela
#      e em qual evento esse pico aconteceu
#    - O menor preço de fechamento observado em qualquer janela
#      e em qual evento esse fundo aconteceu
#
#  Para os preços máximo e mínimo, varremos as 24 tabelas de
#  janela (todas as combinações setor × evento) geradas na PARTE 3.
# =============================================================

# Lista que vai virar o DataFrame final (uma linha por ação)
linhas_resumo = []

# Loop por cada uma das 15 ações
for ticker in sorted(df_variacoes["Ticker"].unique()):

    # -----------------------------------------------------------
    # PARTE A: maior alta e maior queda (-5 vs +5) por evento
    # -----------------------------------------------------------
    variacoes_ticker = df_variacoes[df_variacoes["Ticker"] == ticker]

    idx_alta = variacoes_ticker["Variação (%)"].idxmax()
    idx_queda = variacoes_ticker["Variação (%)"].idxmin()

    linha_alta = df_variacoes.loc[idx_alta]
    linha_queda = df_variacoes.loc[idx_queda]

    maior_alta_pct = linha_alta["Variação (%)"]
    evento_alta = linha_alta["Evento"]

    maior_queda_pct = linha_queda["Variação (%)"]
    evento_queda = linha_queda["Evento"]

    # -----------------------------------------------------------
    # PARTE B: maior e menor preço observado em QUALQUER janela
    # -----------------------------------------------------------
    maior_preco = None
    menor_preco = None
    evento_maior_preco = None
    evento_menor_preco = None

    for chave, tabela in todas_tabelas.items():
        codigo_evento = chave.split("_")[0]

        col_fechamento = f"{ticker}_fechamento"
        if col_fechamento not in tabela.columns:
            continue

        # Converte pra numerico — as 24 tabelas de todas_tabelas foram geradas
        # na PARTE 3, ANTES da conversao numerica que so acontece na PARTE 4.
        precos = pd.to_numeric(tabela[col_fechamento], errors="coerce").dropna()
        if len(precos) == 0:
            continue

        max_local = precos.max()
        min_local = precos.min()

        if maior_preco is None or max_local > maior_preco:
            maior_preco = max_local
            evento_maior_preco = codigo_evento

        if menor_preco is None or min_local < menor_preco:
            menor_preco = min_local
            evento_menor_preco = codigo_evento

    # -----------------------------------------------------------
    # Monta a linha final dessa ação
    # -----------------------------------------------------------
    linhas_resumo.append({
        "Ação": ticker,
        "Setor": buscar_setor(ticker),
        "Maior alta (%)": round(maior_alta_pct, 2),
        "Evento da alta": evento_alta,
        "Maior queda (%)": round(maior_queda_pct, 2),
        "Evento da queda": evento_queda,
        "Preço máximo (R$)": round(maior_preco, 2) if maior_preco is not None else None,
        "Evento do máximo": evento_maior_preco,
        "Preço mínimo (R$)": round(menor_preco, 2) if menor_preco is not None else None,
        "Evento do mínimo": evento_menor_preco,
    })

# Vira DataFrame
df_resumo_acao = pd.DataFrame(linhas_resumo)
df_resumo_acao = df_resumo_acao.sort_values(["Setor", "Ação"]).reset_index(drop=True)

print("=" * 120)
print("RESUMO POR AÇÃO — MAIOR/MENOR VARIAÇÃO E MAIOR/MENOR PREÇO EM QUALQUER EVENTO")
print("=" * 120)
print(df_resumo_acao.to_string(index=False))

# -----------------------------------------------------------
# DESTAQUES finais (linhas-resumo do trabalho)
# -----------------------------------------------------------
print("\n" + "=" * 120)
print("CAMPEÕES ABSOLUTOS DA AMOSTRA INTEIRA")
print("=" * 120)

idx_max_geral = df_resumo_acao["Maior alta (%)"].idxmax()
linha_max = df_resumo_acao.loc[idx_max_geral]
print(f"\n🏆 MAIOR ALTA: {linha_max['Ação']} ({linha_max['Setor']}) "
      f"com {linha_max['Maior alta (%)']:+.2f}% no evento {linha_max['Evento da alta']}")

idx_min_geral = df_resumo_acao["Maior queda (%)"].idxmin()
linha_min = df_resumo_acao.loc[idx_min_geral]
print(f"📉 MAIOR QUEDA: {linha_min['Ação']} ({linha_min['Setor']}) "
      f"com {linha_min['Maior queda (%)']:+.2f}% no evento {linha_min['Evento da queda']}")

idx_preco_max = df_resumo_acao["Preço máximo (R$)"].idxmax()
linha_pmax = df_resumo_acao.loc[idx_preco_max]
print(f"💰 MAIOR PREÇO: {linha_pmax['Ação']} ({linha_pmax['Setor']}) "
      f"a R$ {linha_pmax['Preço máximo (R$)']:.2f} na janela do evento {linha_pmax['Evento do máximo']}")

idx_preco_min = df_resumo_acao["Preço mínimo (R$)"].idxmin()
linha_pmin = df_resumo_acao.loc[idx_preco_min]
print(f"🪙 MENOR PREÇO: {linha_pmin['Ação']} ({linha_pmin['Setor']}) "
      f"a R$ {linha_pmin['Preço mínimo (R$)']:.2f} na janela do evento {linha_pmin['Evento do mínimo']}")

print("\n✅ DataFrame 'df_resumo_acao' criado")
# %%
# =============================================================
#  PARTE 10: VARIAÇÃO MÉDIA POR SETOR EM CADA EVENTO
#  Reproduz a tabela do item 2.1 da conclusão do trabalho.
#  Linhas = setores; colunas = eventos E1...E8.
#  Os valores são a média das variações (-5 vs +5) das ações
#  daquele setor em cada evento.
#  Usa: groupby (Aula 4) + unstack pra organizar em tabela.
# =============================================================

# Agrupa por setor + evento, tira a média da variação
media_setor_evento = df_variacoes.groupby(["Setor", "Evento"])["Variação (%)"].mean()

# Reorganiza pra ficar em formato de tabela (linhas = setor, colunas = evento)
tabela_media = media_setor_evento.unstack("Evento")

# Ordena as colunas na ordem cronológica E1, E2, ... E8
ordem_eventos = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
tabela_media = tabela_media[ordem_eventos]

# Ordena as linhas na ordem que aparece no trabalho
ordem_setores = ["Energia", "Siderurgia e metais", "Mineração"]
tabela_media = tabela_media.reindex(ordem_setores)

# ----- Impressão formatada (com sinais + / − e alinhamento) -----
print("=" * 95)
print("TABELA 2.1 — VARIAÇÃO MÉDIA POR SETOR EM CADA EVENTO (em %)")
print("=" * 95)
print("Linhas = setores | Colunas = eventos | Valores = média das variações (-5 vs +5)")
print("-" * 95)

# Cabeçalho
header = f"{'Setor':<22} | " + " | ".join(f"{e:>7}" for e in ordem_eventos)
print(header)
print("-" * 95)

# Linhas dos setores
for setor in ordem_setores:
    valores = tabela_media.loc[setor]
    linha_str = f"{setor:<22} | " + " | ".join(f"{v:+7.2f}" for v in valores)
    print(linha_str)

print("-" * 95)
print("Observação: as colunas E6, E7 e E8 mostram o mesmo valor porque os três")
print("eventos caem na mesma data (25/02/2026) — compartilham a mesma janela.")

# ----- Melhor e pior evento por setor -----
print("\n" + "=" * 95)
print("MELHOR E PIOR EVENTO POR SETOR")
print("=" * 95)

for setor in ordem_setores:
    linha = tabela_media.loc[setor]
    melhor_evento = linha.idxmax()
    pior_evento = linha.idxmin()
    print(f"\n{setor}:")
    print(f"  ⬆️  Melhor evento: {melhor_evento} ({linha[melhor_evento]:+.2f}%)")
    print(f"  ⬇️  Pior evento:   {pior_evento} ({linha[pior_evento]:+.2f}%)")

print("\n✅ DataFrame 'tabela_media' criado (3 setores × 8 eventos)")
# %%
# =============================================================
#  PARTE 11: PADRÃO CONSOLIDADO POR SETOR (item 2.2 da conclusão)
#  Tira a média de TODOS os eventos para cada setor.
#  Responde: na média geral, qual setor subiu/caiu mais?
#  Também faz a validação visual da hipótese H0.
# =============================================================

# Média consolidada por setor (média de todas as 120 combinações)
media_por_setor = df_variacoes.groupby("Setor")["Variação (%)"].mean()

# Ordena: maior média primeiro
media_por_setor = media_por_setor.sort_values(ascending=False)

# ----- Tabela formatada (item 2.2) -----
print("=" * 60)
print("TABELA 2.2 — PADRÃO CONSOLIDADO POR SETOR")
print("=" * 60)
print("Média das variações (-5 vs +5) de todas as 120 combinações")
print("ação × evento, agrupadas por setor.")
print("-" * 60)

# Cabeçalho
print(f"{'Setor':<22} | {'Variação média':>15}")
print("-" * 60)

# Imprime cada setor com sua média (já ordenado do maior pro menor)
for setor, valor in media_por_setor.items():
    print(f"{setor:<22} | {valor:>+14.2f}%")

print("-" * 60)

# ----- Validação da hipótese H0 -----
print("\n" + "=" * 85)
print("VALIDAÇÃO DA HIPÓTESE H0 ('o mercado não reagiu')")
print("=" * 85)

total = len(df_variacoes)
positivas = len(df_variacoes[df_variacoes["Variação (%)"] > 0])
negativas = len(df_variacoes[df_variacoes["Variação (%)"] < 0])
neutras = len(df_variacoes[df_variacoes["Variação (%)"] == 0])

print(f"\n  Total de combinações ação × evento: {total}")
print(f"  Variações positivas: {positivas} ({positivas/total*100:.1f}%)")
print(f"  Variações negativas: {negativas} ({negativas/total*100:.1f}%)")
print(f"  Variações nulas:     {neutras} ({neutras/total*100:.1f}%)")

magnitude = df_variacoes["Variação (%)"].abs().mean()
print(f"\n  Magnitude média absoluta: {magnitude:.2f}%")
print(f"  → Em média, cada combinação variou {magnitude:.2f}% (em qualquer direção).")

if magnitude > 1.5:
    print(f"  → REJEITA H0: o mercado claramente reagiu — variações muito acima do esperado pra ruído.")
else:
    print(f"  → NÃO REJEITA H0: variações compatíveis com flutuação normal de mercado.")

print("\n✅ DataFrame 'media_por_setor' criado (3 setores × média geral)")

