import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
import numpy as np

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="ENEM 2024 - Analytics Pro", layout="wide")

st.title("📊 Dashboard Avançado ENEM 2024")
st.caption("Igor Andrade • Data Science • Versão 4.0")

# ==============================
# DATA
# ==============================
@st.cache_data
def load_data():
    try:
        engine = create_engine("postgresql+psycopg2://data_iesb:iesb@bigdata.dataiesb.com:5432/iesb")
        df = pd.read_sql("SELECT * FROM ed_enem_2024_resultados_amos_per WHERE nota_mt_matematica IS NOT NULL", engine)
        return df
    except:
        return pd.read_csv("ed_enem_2024_resultados_amos_per.csv")

df_raw = load_data()

# ==============================
# SIDEBAR
# ==============================
ufs = st.sidebar.multiselect(
    "Estados",
    sorted(df_raw["nome_uf_prova"].unique()),
    default=sorted(df_raw["nome_uf_prova"].unique())
)

faixa = st.sidebar.slider(
    "Nota",
    int(df_raw["nota_mt_matematica"].min()),
    int(df_raw["nota_mt_matematica"].max()),
    (300, 800)
)

df = df_raw[
    (df_raw["nome_uf_prova"].isin(ufs)) &
    (df_raw["nota_mt_matematica"].between(faixa[0], faixa[1]))
]

# ==============================
# KPIs
# ==============================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Alunos", len(df))
c2.metric("Média", round(df["nota_mt_matematica"].mean(),1))
c3.metric("Estados", df["nome_uf_prova"].nunique())
c4.metric("Municípios", df["no_municipio_prova"].nunique())

# ==============================
# ESTATÍSTICA
# ==============================
st.subheader("📊 Estatística Descritiva")
st.dataframe(df["nota_mt_matematica"].describe())

# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Geral",
    "📊 Distribuição",
    "🧠 Inteligência",
    "🤖 Machine Learning"
])

# ==============================
# TAB 1
# ==============================
with tab1:
    col1, col2 = st.columns(2)

    media = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().sort_values()

    col1.plotly_chart(px.bar(media, orientation="h", title="Ranking por Estado"))

    col2.plotly_chart(px.treemap(df, path=["nome_uf_prova"]))

# ==============================
# TAB 2
# ==============================
with tab2:
    col3, col4 = st.columns(2)

    col3.plotly_chart(px.histogram(df, x="nota_mt_matematica", marginal="box"))

    col4.plotly_chart(px.box(df, x="nome_uf_prova", y="nota_mt_matematica"))

# ==============================
# TAB 3 (INTELIGÊNCIA)
# ==============================
with tab3:
    st.subheader("🔗 Correlação")

    numeric_df = df.select_dtypes(include=np.number)

    if len(numeric_df.columns) > 2:
        corr = numeric_df.corr()

        fig_corr = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu",
            title="Mapa de Correlação"
        )

        st.plotly_chart(fig_corr, use_container_width=True)

    # Regressão
    col_lc = "nota_lc_linguagens_e_codigos"

    if col_lc in df.columns:
        fig_reg = px.scatter(
            df.sample(min(2000, len(df))),
            x=col_lc,
            y="nota_mt_matematica",
            trendline="ols",
            title="Regressão Matemática vs Linguagens"
        )

        st.plotly_chart(fig_reg)

# ==============================
# TAB 4 (ML)
# ==============================
with tab4:
    st.subheader("🤖 Clusterização de Alunos")

    if "nota_lc_linguagens_e_codigos" in df.columns:
        features = df[["nota_mt_matematica", "nota_lc_linguagens_e_codigos"]].dropna()

        kmeans = KMeans(n_clusters=3, random_state=42)
        features["cluster"] = kmeans.fit_predict(features)

        fig_cluster = px.scatter(
            features,
            x="nota_lc_linguagens_e_codigos",
            y="nota_mt_matematica",
            color="cluster",
            title="Segmentação de Alunos"
        )

        st.plotly_chart(fig_cluster)

# ==============================
# INSIGHTS
# ==============================
st.subheader("🧠 Insights Automáticos")

melhor = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().idxmax()
pior = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().idxmin()

st.success(f"""
Melhor estado: {melhor}  
Pior estado: {pior}  
Diferença relevante entre regiões indica desigualdade educacional.
""")

# ==============================
# DOWNLOAD
# ==============================
st.download_button(
    "📥 Baixar dados filtrados",
    df.to_csv(index=False),
    "dados_enem_filtrados.csv"
)
