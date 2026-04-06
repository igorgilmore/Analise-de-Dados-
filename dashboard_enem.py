/meu_dashboard
│
├─ dashboard_enem.py
├─ dados/
│   └─ ed_enem_2024_resultados_amos_per.csv
├─ requirements.txt
└─ README.md
# Feito por Igor Andrade - Análise Exploratória de Dados

# Feito por Igor Andrade - Análise Exploratória de Dados

import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2

st.set_page_config(page_title="Dashboard ENEM 2024", layout="wide")
st.title("📊 Dashboard ENEM 2024 - BigData IESB")

# === 1. Conexão com o banco BigData-IESB ===
conn = psycopg2.connect(
    host="bigdata.dataiesb.com",
    database="iesb",
    user="data_iesb",
    password="iesb",
    port=5432
)

# === 2. Buscar os dados da tabela ed_enem_2024_resultados ===
query = "SELECT * FROM ed_enem_2024_resultados;"
df = pd.read_sql(query, conn)

# Fechar conexão
conn.close()

# === 3. Filtros interativos ===
estado = st.selectbox("Selecione o estado:", df['estado'].unique())
df_filtrado = df[df['estado'] == estado]

cidade = st.selectbox("Selecione a cidade:", df_filtrado['cidade'].unique())
df_filtrado = df_filtrado[df_filtrado['cidade'] == cidade]

# === 4. Gráficos interativos ===
st.subheader("Distribuição de Notas")
fig = px.histogram(
    df_filtrado, 
    x='nota_lc_linguagens_e_codigos', 
    nbins=20,
    title="Notas em Linguagens e Códigos"
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Média de Notas por Idade")
df_idade = df_filtrado.groupby('idade_vitima')['nota_lc_linguagens_e_codigos'].mean().reset_index()
fig2 = px.bar(df_idade, x='idade_vitima', y='nota_lc_linguagens_e_codigos', title="Média de Notas por Idade")
st.plotly_chart(fig2, use_container_width=True)
