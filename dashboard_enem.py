/meu_dashboard
│
├─ dashboard_enem.py
├─ dados/
│   └─ ed_enem_2024_resultados_amos_per.csv
├─ requirements.txt
└─ README.md


  # Feito por Igor Andrade - Análise Exploratória de Dados

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard ENEM 2024", layout="wide")

st.title("📊 Dashboard ENEM 2024")

# Carregando os dados
df = pd.read_csv("dados/ed_enem_2024_resultados_amos_per.csv")

# Filtros
estado = st.selectbox("Selecione o estado:", df['estado'].unique())
df_filtrado = df[df['estado'] == estado]

cidade = st.selectbox("Selecione a cidade:", df_filtrado['cidade'].unique())
df_filtrado = df_filtrado[df_filtrado['cidade'] == cidade]

# Gráficos
st.subheader("Distribuição de Notas")
fig = px.histogram(df_filtrado, x='nota_lc_linguagens_e_codigos', nbins=20, title="Notas em Linguagens e Códigos")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Média por Idade")
df_idade = df_filtrado.groupby('idade_vitima')['nota_lc_linguagens_e_codigos'].mean().reset_index()
fig2 = px.bar(df_idade, x='idade_vitima', y='nota_lc_linguagens_e_codigos', title="Média de Notas por Idade")
st.plotly_chart(fig2, use_container_width=True)
