import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Dashboard ENEM 2024",
    layout="wide",
    page_icon="📊"
)

# ==============================
# ESTILO AVANÇADO (UI PROFISSIONAL)
# ==============================
st.markdown("""
<style>
    .main { background-color: #F7F9FC; }
    
    .block-container {
        padding-top: 2rem;
    }

    h1, h2, h3 {
        color: #1F4E79;
        font-weight: 700;
    }

    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #1F4E79;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.title("📊 Dashboard Estratégico ENEM 2024")
st.markdown("### Análise de Performance Educacional")
st.caption("Autor: Igor Andrade • Versão 3.0 • Data Science & Analytics")

# ==============================
# FUNÇÃO DE DADOS
# ==============================
@st.cache_data(show_spinner="Carregando dados...")
def load_data():
    try:
        engine = create_engine("postgresql+psycopg2://data_iesb:iesb@bigdata.dataiesb.com:5432/iesb")
        query = """
        SELECT *
        FROM ed_enem_2024_resultados_amos_per
        WHERE nota_mt_matematica IS NOT NULL
        """
        df = pd.read_sql(query, engine)
        return df, "Banco de Dados"
    except Exception:
        df = pd.read_csv('ed_enem_2024_resultados_amos_per.csv')
        return df, "CSV Local"

df_raw, fonte = load_data()

# ==============================
# SIDEBAR PROFISSIONAL
# ==============================
with st.sidebar:
    st.title("🎛️ Painel de Controle")

    st.subheader("📍 Filtros Geográficos")
    ufs = sorted(df_raw["nome_uf_prova"].dropna().unique())
    ufs_sel = st.multiselect("Estados", ufs, default=ufs)

    st.subheader("📊 Filtro de Nota")
    min_nota = int(df_raw["nota_mt_matematica"].min())
    max_nota = int(df_raw["nota_mt_matematica"].max())

    faixa = st.slider("Intervalo de Nota", min_nota, max_nota, (min_nota, max_nota))

    st.divider()
    st.info(f"📌 Fonte: {fonte}")
    st.caption(f"{len(df_raw):,} registros carregados")

# ==============================
# FILTRO DE DADOS
# ==============================
df = df_raw[
    (df_raw["nome_uf_prova"].isin(ufs_sel)) &
    (df_raw["nota_mt_matematica"].between(faixa[0], faixa[1]))
]

# ==============================
# KPIs (VISUAL MELHORADO)
# ==============================
st.markdown("## 📌 Indicadores Gerais")

c1, c2, c3, c4 = st.columns(4)

c1.metric("👨‍🎓 Alunos", f"{len(df):,}")
c2.metric("📊 Média Matemática", f"{df['nota_mt_matematica'].mean():.1f}")
c3.metric("🏙️ Municípios", df['no_municipio_prova'].nunique())
c4.metric("🗺️ Estados", df['nome_uf_prova'].nunique())

# ==============================
# TABS (PROFISSIONAL)
# ==============================
tab1, tab2, tab3 = st.tabs(["📈 Análise Geral", "📊 Distribuições", "🌍 Geoespacial"])

# ==============================
# TAB 1
# ==============================
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        media_uf = (
            df.groupby("nome_uf_prova")["nota_mt_matematica"]
            .mean()
            .reset_index()
            .sort_values("nota_mt_matematica")
        )

        fig1 = px.bar(
            media_uf,
            x="nota_mt_matematica",
            y="nome_uf_prova",
            orientation="h",
            color="nota_mt_matematica",
            color_continuous_scale="Blues",
            title="Ranking de Performance por Estado"
        )

        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.treemap(
            df,
            path=["nome_uf_prova"],
            title="Distribuição de Participação",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        st.plotly_chart(fig2, use_container_width=True)

# ==============================
# TAB 2
# ==============================
with tab2:
    col3, col4 = st.columns(2)

    with col3:
        col_lc = 'nota_lc_linguagens_e_codigos'

        if col_lc in df.columns:
            fig3 = px.scatter(
                df.sample(min(len(df), 2000)),
                x=col_lc,
                y="nota_mt_matematica",
                color="nome_uf_prova",
                opacity=0.6,
                title="Correlação: Matemática vs Linguagens"
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.histogram(
            df,
            x="nota_mt_matematica",
            nbins=50,
            marginal="box",
            color_discrete_sequence=["#1F4E79"],
            title="Distribuição das Notas"
        )
        st.plotly_chart(fig4, use_container_width=True)

# ==============================
# TAB 3 (MAPA)
# ==============================
with tab3:
    st.subheader("Distribuição Geográfica")

    if "latitude" in df.columns and "longitude" in df.columns:
        fig_map = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            color="nota_mt_matematica",
            size="nota_mt_matematica",
            hover_name="no_municipio_prova",
            zoom=3,
            height=600,
            mapbox_style="carto-positron"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Dados geográficos não disponíveis.")
