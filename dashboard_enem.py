import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
import numpy as np

# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="ENEM 2024 · Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    "Faixa de Nota — Matemática",
    int(df_raw["nota_mt_matematica"].min()),
    int(df_raw["nota_mt_matematica"].max()),
    (300, 800)
)

df = df_raw[
    (df_raw["nome_uf_prova"].isin(ufs)) &
    (df_raw["nota_mt_matematica"].between(faixa[0], faixa[1]))
]

# ==============================
# HEADER
# ==============================
st.title("ENEM 2024 Analytics")

# ==============================
# KPIs
# ==============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Candidatos", len(df))
col2.metric("Média Matemática", round(df["nota_mt_matematica"].mean(), 1))
col3.metric("Estados", df["nome_uf_prova"].nunique())
col4.metric("Municípios", df["no_municipio_prova"].nunique())

# ==============================
# ESTATÍSTICA
# ==============================
st.subheader("Estatística Descritiva")
st.dataframe(df["nota_mt_matematica"].describe())

# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4 = st.tabs([
    "Geral",
    "Distribuição",
    "Inteligência",
    "Machine Learning"
])

# ------------------------------
# TAB 1
# ------------------------------
with tab1:
    media = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().sort_values()

    fig_bar = px.bar(media, orientation="h", title="Média por Estado")
    st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------
# TAB 2
# ------------------------------
with tab2:
    fig_hist = px.histogram(df, x="nota_mt_matematica", marginal="box")
    st.plotly_chart(fig_hist, use_container_width=True)

# ------------------------------
# TAB 3 (AQUI FOI ALTERADO)
# ------------------------------
with tab3:
    st.subheader("Mapa de Correlação")

    # 🔥 AQUI está a correção
    numeric_df = df.select_dtypes(include=np.number).drop(
        columns=["latitude", "longitude"], errors="ignore"
    )

    if len(numeric_df.columns) > 2:
        corr = numeric_df.corr()

        fig_corr = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu",
            zmin=-1,
            zmax=1
        )

        st.plotly_chart(fig_corr, use_container_width=True)

    # Regressão
    if "nota_lc_linguagens_e_codigos" in df.columns:
        fig_reg = px.scatter(
            df.sample(min(2000, len(df))),
            x="nota_lc_linguagens_e_codigos",
            y="nota_mt_matematica",
            trendline="ols"
        )
        st.plotly_chart(fig_reg, use_container_width=True)

# ------------------------------
# TAB 4
# ------------------------------
with tab4:
    if "nota_lc_linguagens_e_codigos" in df.columns:
        features = df[["nota_mt_matematica", "nota_lc_linguagens_e_codigos"]].dropna()

        kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
        features["Cluster"] = kmeans.fit_predict(features)

        fig_cluster = px.scatter(
            features,
            x="nota_lc_linguagens_e_codigos",
            y="nota_mt_matematica",
            color=features["Cluster"].astype(str)
        )

        st.plotly_chart(fig_cluster, use_container_width=True)

# ==============================
# INSIGHTS
# ==============================
st.subheader("Insights")

melhor = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().idxmax()
pior = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().idxmin()

st.write(f"🏆 Melhor estado: {melhor}")
st.write(f"⚠️ Pior estado: {pior}")

# ==============================
# DOWNLOAD
# ==============================
st.download_button(
    "Baixar CSV",
    df.to_csv(index=False),
    "dados_enem.csv"
)
