import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard ENEM 2024 - Pro", layout="wide")

# Estilo CSS para melhorar o visual
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #1F4E79; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1F4E79; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Análise Avançada ENEM 2024")
st.markdown("**Analista:** Igor Andrade | Dashboard Interativo v2.0")

# 2. Carregamento de Dados (Banco ou CSV)
@st.cache_data
def load_data():
    try:
        engine = create_engine("postgresql+psycopg2://data_iesb:iesb@bigdata.dataiesb.com:5432/iesb")
        # Sem LIMIT para pegar todos os estados
        query = "SELECT * FROM ed_enem_2024_resultados_amos_per WHERE nota_mt_matematica IS NOT NULL"
        df = pd.read_sql(query, engine)
        return df, "Banco de Dados"
    except Exception:
        df = pd.read_csv('ed_enem_2024_resultados_amos_per.csv')
        return df, "Base CSV Local"

df_raw, fonte = load_data()

if df_raw is not None:
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("🎯 Filtros")
        lista_ufs = sorted(df_raw["nome_uf_prova"].unique())
        ufs_selecionadas = st.multiselect("Estados:", options=lista_ufs, default=lista_ufs)
        
        # Filtro de Nota
        n_min, n_max = int(df_raw["nota_mt_matematica"].min()), int(df_raw["nota_mt_matematica"].max())
        faixa = st.slider("Nota de Matemática:", n_min, n_max, (n_min, n_max))
        
        st.divider()
        st.info(f"Dados: {fonte} | {len(df_raw)} registros")

    # Aplicando Filtros
    df = df_raw[df_raw["nome_uf_prova"].isin(ufs_selecionadas)]
    df = df[(df["nota_mt_matematica"] >= faixa[0]) & (df["nota_mt_matematica"] <= faixa[1])]

    # --- MÉTRICAS (KPIs) ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Alunos Selecionados", f"{len(df):,}")
    m2.metric("Média MT", f"{df['nota_mt_matematica'].mean():.1f}")
    m3.metric("Qtd Municípios", f"{df['no_municipio_prova'].nunique()}")
    m4.metric("Estados no Gráfico", f"{df['nome_uf_prova'].nunique()}")

    st.divider()

    # --- LINHA 1 DE GRÁFICOS ---
    c1, c2 = st.columns(2)

    with c1:
        # 1. Ranking de Médias (Barras)
        media_uf = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().reset_index().sort_values("nota_mt_matematica")
        fig1 = px.bar(media_uf, y="nome_uf_prova", x="nota_mt_matematica", orientation='h',
                      title="🏆 Ranking de Médias por Estado", color="nota_mt_matematica",
                      color_continuous_scale="Viridis")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        # 2. Distribuição de Participação (Treemap)
        fig2 = px.treemap(df, path=['nome_uf_prova'], title="📦 Proporção de Alunos por Estado",
                          color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # --- LINHA 2 DE GRÁFICOS ---
    c3, c4 = st.columns(2)

    with c3:
        # 3. Correlação Matemática vs Linguagens (se existir a coluna no seu banco)
        col_lc = 'nota_lc_linguagens_e_codigos'
        if col_lc in df.columns:
            fig3 = px.scatter(df.sample(min(2000, len(df))), x=col_lc, y="nota_mt_matematica",
                              color="nome_uf_prova", title="📈 Matemática vs Linguagens (Amostra)",
                              opacity=0.5, template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Coluna de Linguagens não encontrada para o Scatter.")

    with c4:
        # 4. Distribuição das Notas (Histograma)
        fig4 = px.histogram(df, x="nota_mt_matematica", nbins=40, marginal="box",
                           title="📊 Curva de Distribuição das Notas", color_discrete_sequence=['#1F4E79'])
        st.plotly_chart(fig4, use_container_width=True)

    # --- MAPA ---
    st.subheader("🌍 Localização Geográfica dos Candidatos")
    if 'latitude' in df.columns and 'longitude' in df.columns:
        fig_map = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="nota_mt_matematica",
                                   hover_name="no_municipio_prova", mapbox_style="carto-positron", 
                                   zoom=3, height=600)
        st.plotly_chart(fig_map, use_container_width=True)

else:
    st.error("Erro ao carregar os dados. Verifique o banco ou o arquivo CSV.")
