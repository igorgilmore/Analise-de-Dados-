import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# 1. Configuração de Estilo da Página
st.set_page_config(
    page_title="Dashboard ENEM 2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para deixar o visual ainda mais "premium"
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1 { color: #1f4e79; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. Cabeçalho Principal
st.title("📊 Dashboard ENEM 2024 - Análise BigData")
st.markdown(f"**Desenvolvido por:** Igor Andrade | **Disciplina:** Análise Exploratória de Dados")
st.divider()

# 3. Função de Carregamento Robusta
@st.cache_data(ttl=3600) # Cache de 1 hora para performance
def load_data():
    try:
        # Tenta conexão com o banco do IESB (Nomes de colunas do seu código original)
        engine = create_engine("postgresql+psycopg2://data_iesb:iesb@bigdata.dataiesb.com:5432/iesb")
        query = "SELECT * FROM ed_enem_2024_resultados_amos_per WHERE nota_mt_matematica IS NOT NULL LIMIT 10000"
        df = pd.read_sql(query, engine)
        return df, "Conexão Direta (Banco IESB)"
    except Exception:
        # Plano B: Carrega o CSV que você já tem no repositório
        try:
            df = pd.read_csv('ed_enem_2024_resultados_amos_per.csv')
            return df, "Modo Offline (Base Local CSV)"
        except:
            return None, None

df_raw, fonte_dados = load_data()

if df_raw is not None:
    # --- BARRA LATERAL (FILTROS) ---
    with st.sidebar:
        st.image("https://www.iesb.br/wp-content/uploads/2023/07/logo-iesb-azul.png", width=150)
        st.header("⚙️ Painel de Filtros")
        
        # Filtro de Estados (Todos selecionados por padrão como você pediu!)
        lista_ufs = sorted(df_raw["nome_uf_prova"].unique())
        ufs_selecionadas = st.multiselect(
            "Selecione os Estados:", 
            options=lista_ufs, 
            default=lista_ufs
        )

        # Filtro de Notas
        n_min, n_max = int(df_raw["nota_mt_matematica"].min()), int(df_raw["nota_mt_matematica"].max())
        faixa_nota = st.slider("Filtrar por Nota (MT):", n_min, n_max, (n_min, n_max))
        
        st.info(f"📍 Fonte: {fonte_dados}")

    # Aplicando filtros
    df = df_raw[df_raw["nome_uf_prova"].isin(ufs_selecionadas)]
    df = df[(df["nota_mt_matematica"] >= faixa_nota[0]) & (df["nota_mt_matematica"] <= faixa_nota[1])]

    # --- INDICADORES (KPIs) ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📌 Alunos Analisados", f"{len(df):,}")
    k2.metric("📐 Média Matemática", f"{df['nota_mt_matematica'].mean():.1f}")
    k3.metric("🔝 Maior Nota", f"{df['nota_mt_matematica'].max():.0f}")
    k4.metric("📉 Menor Nota", f"{df['nota_mt_matematica'].min():.0f}")

    st.markdown("---")

    # --- GRÁFICOS (Layout Lado a Lado) ---
    col_1, col_2 = st.columns([1.2, 0.8])

    with col_1:
        # Gráfico de Barras - Média por Estado
        media_uf = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().reset_index().sort_values("nota_mt_matematica", ascending=False)
        fig_bar = px.bar(
            media_uf, x="nome_uf_prova", y="nota_mt_matematica",
            title="🏆 Média de Matemática por Estado",
            color="nota_mt_matematica", color_continuous_scale="Viridis",
            labels={'nome_uf_prova': 'Estado', 'nota_mt_matematica': 'Média'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_2:
        # Histograma - Distribuição
        fig_hist = px.histogram(
            df, x="nota_mt_matematica", nbins=25,
            title="🎯 Distribuição Geral das Notas",
            color_discrete_sequence=['#1f4e79'],
            labels={'nota_mt_matematica': 'Nota Matemática'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- MAPA (Área debaixo) ---
    st.subheader("🗺️ Distribuição Geográfica das Notas")
    if 'latitude' in df.columns and 'longitude' in df.columns:
        fig_map = px.scatter_mapbox(
            df, lat="latitude", lon="longitude", 
            color="nota_mt_matematica", size="nota_mt_matematica",
            hover_name="no_municipio_prova", 
            mapbox_style="carto-positron", zoom=3.5, height=600,
            color_continuous_scale="Portland"
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    # --- TABELA DETALHADA ---
    with st.expander("📂 Clique aqui para ver os dados brutos filtrados"):
        st.dataframe(df, use_container_width=True)

else:
    st.error("❌ Erro fatal: Não conseguimos carregar os dados. Verifique o arquivo CSV no seu GitHub.")
