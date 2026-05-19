# Trabalho de Análise de Dados — REDATA e B3

## Tema

Este trabalho investiga os efeitos do **PL 278/2026 (REDATA)** sobre o mercado acionário brasileiro. O REDATA é um **regime especial de tributação para data centers no Brasil**, criado para atrair investimentos em infraestrutura digital ao reduzir tributos federais sobre a importação de equipamentos, a aquisição de máquinas e a contratação de serviços ligados a centros de processamento de dados.

A discussão pública em torno do projeto tem implicações relevantes para setores intensivos em energia, insumos metálicos e infraestrutura física, dado o perfil de demanda associado à expansão de data centers no país.

## Pergunta de pesquisa

> **Eventos associados à tramitação do PL 278/2026 geraram retornos anormais nas ações de empresas brasileiras dos setores de energia, mineração e siderurgia listadas na B3?**

## Metodologia

O estudo adota a abordagem clássica de **estudo de evento** (event study), com as seguintes janelas de análise centradas em cada evento relevante da tramitação do PL:

- **-1 / +1 dia** (janela curta, reação imediata)
- **-3 / +3 dias** (janela intermediária)
- **-5 / +5 dias** (janela ampla, captura difusão da informação)

Para cada empresa analisada, os retornos diários observados durante essas janelas são comparados ao retorno do **Ibovespa (IBOV)** no mesmo período, com o objetivo de identificar **retornos anormais** que possam ser atribuídos à tramitação do PL e não ao comportamento geral do mercado.

## Setores e empresas analisadas

### Energia
- **ELET3 / ELET6** — Eletrobras
- **EGIE3** — Engie Brasil
- **TAEE11** — Taesa
- **CPLE6** — Copel
- **CMIG4** — Cemig
- **EQTL3** — Equatorial

### Siderurgia e metais
- **GGBR4** — Gerdau
- **CSNA3** — CSN
- **USIM5** — Usiminas
- **CBAV3** — CBA (Companhia Brasileira de Alumínio)

### Mineração
- **VALE3** — Vale
- **CMIN3** — CSN Mineração
- **AURA33** — Aura Minerals
