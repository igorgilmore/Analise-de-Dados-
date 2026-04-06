import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from sqlalchemy import create_engine

# Configuração da página
st.set_page_config(page_title="Dashboard ENEM 2024", layout="wide")

# Cabeçalho formatado
st.markdown("""
<h2 style='text-align:center; color:#1F4E79;'>📊 Dashboard ENEM 2024</h2>
<p style='text-align:center; color:gray; font-size:16px;'>
Desenvolvido por <b>Igor Andrade</b> 📝 | Disciplina: Análise Exploratória de Dados
</p>
""", unsafe_allow_html=True)

# === FUNÇÃO DE CARREGAMENTO (BANCO OU CSV) ===
@st.cache_data
def load_data():
    try:
        # Tenta conexão com o banco do IESB
        engine = create_engine("postgresql+psycopg2://data_iesb:iesb@bigdata.dataiesb.com:5432/iesb")
        query = """
        SELECT * FROM ed_enem_2024_resultados_amos_per 
        WHERE nota_mt_matematica IS NOT NULL 
        LIMIT 5000
        """
        df = pd.read_sql(query, engine)
        return df, "Banco de Dados (Real-time)"
    except Exception as e:
        # Se falhar, tenta o CSV que está no seu GitHub
        try:
            df = pd.read_csv('ed_enem_2024_resultados_amos_per.csv')
            return df, "Arquivo CSV (Backup)"
        except:
            st.error("Não foi possível carregar o Banco nem o CSV.")
            return None, None

df, fonte = load_data()

if df is not None:
    st.info(f"Conectado via: {fonte}")

    # === SIDEBAR / FILTROS ===
    with st.sidebar:
        st.header("Filtros 🎯")
        
        # Filtro de Estados (usando o nome correto do seu código)
        lista_ufs = sorted(df["nome_uf_prova"].unique())
        ufs_selecionadas = st.multiselect("Selecione os Estados:", options=lista_ufs, default=lista_ufs[:5])

        # Filtro de Notas
        nota_min = int(df["nota_mt_matematica"].min())
        nota_max = int(df["nota_mt_matematica"].max())
        faixa_nota = st.slider("Faixa de Nota (Matemática):", nota_min, nota_max, (nota_min, nota_max))

    # Aplicando Filtros
    df_filtrado = df[df["nome_uf_prova"].isin(ufs_selecionadas)]
    df_filtrado = df_filtrado[(df_filtrado["nota_mt_matematica"] >= faixa_nota[0]) & 
                             (df_filtrado["nota_mt_matematica"] <= faixa_nota[1])]

    # === INDICADORES (KPIs) ===
    c1, c2, c3 = st.columns(3)
    c1.metric("Média Matemática", f"{df_filtrado['nota_mt_matematica'].mean():.1f}")
    c2.metric("Total de Alunos", f"{len(df_filtrado)}")
    c3.metric("Maior Nota", f"{df_filtrado['nota_mt_matematica'].max():.0f}")

    # === GRÁFICOS ===
    col_esq, col_dir = st.columns(2)

    with col_esq:
        media_estado = df_filtrado.groupby("nome_uf_prova")["nota_mt_matematica"].mean().reset_index().sort_values(by="nota_mt_matematica", ascending=False)
        fig_bar = px.bar(media_estado, x="nome_uf_prova", y="nota_mt_matematica", 
                         title="Média de Matemática por Estado", color="nota_mt_matematica")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_dir:
        fig_hist = px.histogram(df_filtrado, x="nota_mt_matematica", nbins=30, 
                                title="Distribuição das Notas", color_discrete_sequence=['#FF7F0E'])
        st.plotly_chart(fig_hist, use_container_width=True)

    # === MAPA ===
    st.subheader("🌍 Localização dos Centros de Prova")
    if 'latitude' in df_filtrado.columns and 'longitude' in df_filtrado.columns:
        fig_map = px.scatter_mapbox(df_filtrado, lat="latitude", lon="longitude", 
                                   color="nota_mt_matematica", size="nota_mt_matematica",
                                   hover_name="no_municipio_prova", mapbox_style="open-street-map", 
                                   zoom=3, height=500)
        st.plotly_chart(fig_map, use_container_width=True)
    
    # Tabela Resumo
    st.write("### 📋 Dados Detalhados", df_filtrado.head(10))

else:
    st.warning("Aguardando carregamento de dados...")
