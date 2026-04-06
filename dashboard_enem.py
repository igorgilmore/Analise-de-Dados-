# Feito por Igor Andrade - Análise Exploratória de Dados
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Dashboard ENEM 2024", layout="wide")
st.title("📊 Dashboard ENEM 2024 - BigData IESB")

# === 1. Criar conexão segura com o BigData-IESB usando SQLAlchemy ===
try:
    engine = create_engine(
        "postgresql+psycopg2://data_iesb:iesb@bigdata.dataiesb.com:5432/iesb"
    )
    conn = engine.connect()
except Exception as e:
    st.error(f"Não foi possível conectar ao banco de dados: {e}")
    st.stop()  # Para o app se não conseguir conectar

# === 2. Buscar os dados da tabela ed_enem_2024_resultados ===
# Tenta conectar no banco, se falhar, usa o CSV que está no GitHub
try:
    engine = create_engine("postgresql+psycopg2://data_iesb:iesb@bigdata.dataiesb.com:5432/iesb")
    df = pd.read_sql("SELECT * FROM ed_enem_2024_resultados LIMIT 5000", engine) # LIMIT ajuda a não travar
except Exception:
    st.warning("Conexão com o banco falhou. Carregando dados do arquivo local...")
    df = pd.read_csv('ed_enem_2024_resultados_amos_per.csv')
    st.stop()

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
