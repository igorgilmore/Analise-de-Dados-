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
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0a0d14;
    color: #e8eaf0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f1320 !important;
    border-right: 1px solid #1e2438;
}

[data-testid="stSidebar"] * {
    color: #c8ccd8 !important;
}

[data-testid="stSidebar"] .stMultiSelect > div,
[data-testid="stSidebar"] .stSlider > div {
    background: #161b2e !important;
    border-radius: 8px;
    border: 1px solid #252d45;
}

/* ── Header ── */
.dash-header {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid #1e2438;
    margin-bottom: 2rem;
}

.dash-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #e8eaf0 30%, #5c7cfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}

.dash-caption {
    font-size: 0.82rem;
    color: #5a6080;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.5rem;
    font-weight: 500;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.kpi-card {
    background: linear-gradient(145deg, #131829, #0f1320);
    border: 1px solid #1e2438;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}

.kpi-card:hover {
    border-color: #2e3a5e;
    transform: translateY(-2px);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
    border-radius: 14px 14px 0 0;
}

.kpi-icon {
    font-size: 1.1rem;
    margin-bottom: 0.7rem;
    opacity: 0.7;
}

.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #e8eaf0;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.kpi-label {
    font-size: 0.75rem;
    color: #5a6080;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── Section headings ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #9aa3c0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e2438;
    margin-left: 0.5rem;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #0f1320;
    border: 1px solid #1e2438;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
}

[data-testid="stTabs"] button[role="tab"] {
    border-radius: 7px !important;
    color: #5a6080 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.15s !important;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: #1e2a4a !important;
    color: #7ba7ff !important;
}

/* ── Insights box ── */
.insight-box {
    background: linear-gradient(135deg, #111a30, #0d1525);
    border: 1px solid #1e3a6e;
    border-left: 3px solid #5c7cfa;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-top: 0.5rem;
}

.insight-box p {
    margin: 0.2rem 0;
    color: #b0bcd8;
    font-size: 0.9rem;
    line-height: 1.6;
}

.insight-box strong {
    color: #7ba7ff;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #1e2a4a !important;
    border: 1px solid #2e3f6e !important;
    color: #7ba7ff !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.15s !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: #253561 !important;
    border-color: #5c7cfa !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e2438;
    border-radius: 10px;
    overflow: hidden;
}

/* ── Metrics (native) ── */
[data-testid="metric-container"] {
    background: #0f1320;
    border: 1px solid #1e2438;
    border-radius: 12px;
    padding: 1rem 1.2rem;
}

[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    color: #e8eaf0 !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# PLOTLY THEME
# ==============================
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#9aa3c0", size=12),
    title_font=dict(family="Syne, sans-serif", color="#c8ccd8", size=15),
    xaxis=dict(gridcolor="#1e2438", linecolor="#1e2438", tickfont=dict(color="#5a6080")),
    yaxis=dict(gridcolor="#1e2438", linecolor="#1e2438", tickfont=dict(color="#5a6080")),
    margin=dict(l=20, r=20, t=50, b=20),
    colorway=["#5c7cfa", "#34d399", "#f59e0b", "#f87171", "#a78bfa", "#38bdf8"],
)

ACCENT_COLORS = ["#5c7cfa", "#34d399", "#f59e0b", "#f87171"]

def apply_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

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
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem; border-bottom:1px solid #1e2438; margin-bottom:1.5rem;">
        <p style="font-family:'Syne',sans-serif; font-weight:700; font-size:1rem;
                  color:#5c7cfa; letter-spacing:0.05em; margin:0;">⚙ FILTROS</p>
    </div>
    """, unsafe_allow_html=True)

    ufs = st.multiselect(
        "Estados",
        sorted(df_raw["nome_uf_prova"].unique()),
        default=sorted(df_raw["nome_uf_prova"].unique())
    )

    faixa = st.slider(
        "Faixa de Nota — Matemática",
        int(df_raw["nota_mt_matematica"].min()),
        int(df_raw["nota_mt_matematica"].max()),
        (300, 800)
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.7rem; color:#2e3a5e; text-align:center; letter-spacing:0.05em;">
    ENEM 2024 · Analytics Pro · v5.0<br>Igor Andrade · Data Science
    </p>
    """, unsafe_allow_html=True)

df = df_raw[
    (df_raw["nome_uf_prova"].isin(ufs)) &
    (df_raw["nota_mt_matematica"].between(faixa[0], faixa[1]))
]

# ==============================
# HEADER
# ==============================
st.markdown("""
<div class="dash-header">
    <h1 class="dash-title">ENEM 2024<br>Analytics</h1>
    <p class="dash-caption">Igor Andrade · Data Science · v5.0</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# KPI CARDS
# ==============================
kpis = [
    ("👤", len(df), "Candidatos", "#5c7cfa"),
    ("📐", round(df["nota_mt_matematica"].mean(), 1), "Média Matemática", "#34d399"),
    ("🗺", df["nome_uf_prova"].nunique(), "Estados", "#f59e0b"),
    ("📍", df["no_municipio_prova"].nunique(), "Municípios", "#a78bfa"),
]

cols = st.columns(4)
for col, (icon, value, label, color) in zip(cols, kpis):
    col.markdown(f"""
    <div class="kpi-card" style="--accent:{color};">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value:,}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# ESTATÍSTICA
# ==============================
st.markdown('<p class="section-title">📊 Estatística Descritiva</p>', unsafe_allow_html=True)
desc = df["nota_mt_matematica"].describe().reset_index()
desc.columns = ["Métrica", "Valor"]
desc["Valor"] = desc["Valor"].round(2)
st.dataframe(desc, use_container_width=True, hide_index=True)

# ==============================
# TABS
# ==============================
st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs([
    "  📈 Geral  ",
    "  📊 Distribuição  ",
    "  🧠 Inteligência  ",
    "  🤖 Machine Learning  "
])

# ── TAB 1 ──────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([1.2, 1])

    media = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().sort_values()

    fig_bar = px.bar(
        media,
        orientation="h",
        title="Ranking por Estado — Média Matemática",
        color=media.values,
        color_continuous_scale=[[0, "#1e2a4a"], [0.5, "#5c7cfa"], [1, "#34d399"]],
    )
    fig_bar.update_coloraxes(showscale=False)
    fig_bar.update_traces(marker_line_width=0)
    apply_theme(fig_bar)
    col1.plotly_chart(fig_bar, use_container_width=True)

    fig_tree = px.treemap(
        df,
        path=["nome_uf_prova"],
        title="Participação por Estado",
        color_discrete_sequence=["#5c7cfa", "#34d399", "#f59e0b", "#f87171", "#a78bfa", "#38bdf8"]
    )
    fig_tree.update_traces(marker=dict(line=dict(width=2, color="#0a0d14")))
    apply_theme(fig_tree)
    col2.plotly_chart(fig_tree, use_container_width=True)

# ── TAB 2 ──────────────────────────────────────────────────────────
with tab2:
    col3, col4 = st.columns(2)

    fig_hist = px.histogram(
        df,
        x="nota_mt_matematica",
        marginal="box",
        title="Distribuição de Notas — Matemática",
        color_discrete_sequence=["#5c7cfa"]
    )
    fig_hist.update_traces(marker_line_width=0, opacity=0.85)
    apply_theme(fig_hist)
    col3.plotly_chart(fig_hist, use_container_width=True)

    fig_box = px.box(
        df,
        x="nome_uf_prova",
        y="nota_mt_matematica",
        title="Dispersão por Estado",
        color="nome_uf_prova",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_box.update_layout(showlegend=False)
    apply_theme(fig_box)
    col4.plotly_chart(fig_box, use_container_width=True)

# ── TAB 3 ──────────────────────────────────────────────────────────
with tab3:
    st.markdown('<p class="section-title">🔗 Mapa de Correlação</p>', unsafe_allow_html=True)

    numeric_df = df.select_dtypes(include=np.number)

    if len(numeric_df.columns) > 2:
        corr = numeric_df.corr()
        fig_corr = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale=[[0, "#f87171"], [0.5, "#0f1320"], [1, "#5c7cfa"]],
            title="Correlação entre Variáveis Numéricas",
            zmin=-1, zmax=1
        )
        fig_corr.update_traces(textfont_size=10)
        apply_theme(fig_corr)
        st.plotly_chart(fig_corr, use_container_width=True)

    col_lc = "nota_lc_linguagens_e_codigos"
    if col_lc in df.columns:
        st.markdown('<p class="section-title">📉 Regressão Linear</p>', unsafe_allow_html=True)
        fig_reg = px.scatter(
            df.sample(min(2000, len(df))),
            x=col_lc,
            y="nota_mt_matematica",
            trendline="ols",
            title="Matemática × Linguagens & Códigos",
            color_discrete_sequence=["#5c7cfa"],
            opacity=0.5
        )
        fig_reg.update_traces(marker=dict(size=5))
        apply_theme(fig_reg)
        st.plotly_chart(fig_reg, use_container_width=True)

# ── TAB 4 ──────────────────────────────────────────────────────────
with tab4:
    st.markdown('<p class="section-title">🤖 Clusterização K-Means</p>', unsafe_allow_html=True)

    col_lc = "nota_lc_linguagens_e_codigos"
    if col_lc in df.columns:
        features = df[["nota_mt_matematica", col_lc]].dropna()
        kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
        features = features.copy()
        features["Cluster"] = kmeans.fit_predict(features).astype(str)
        features["Cluster"] = features["Cluster"].map({"0": "Grupo A", "1": "Grupo B", "2": "Grupo C"})

        fig_cluster = px.scatter(
            features,
            x=col_lc,
            y="nota_mt_matematica",
            color="Cluster",
            title="Segmentação de Candidatos",
            color_discrete_map={"Grupo A": "#5c7cfa", "Grupo B": "#34d399", "Grupo C": "#f59e0b"},
            opacity=0.65
        )
        fig_cluster.update_traces(marker=dict(size=5, line=dict(width=0)))
        apply_theme(fig_cluster)
        st.plotly_chart(fig_cluster, use_container_width=True)

        # Sumário dos clusters
        summary = features.groupby("Cluster").agg(
            Candidatos=("nota_mt_matematica", "count"),
            Média_MT=("nota_mt_matematica", "mean"),
            Média_LC=(col_lc, "mean")
        ).round(1).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        st.info("Coluna de Linguagens não encontrada nos dados carregados.")

# ==============================
# INSIGHTS
# ==============================
st.markdown('<p class="section-title">🧠 Insights Automáticos</p>', unsafe_allow_html=True)

melhor = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().idxmax()
pior = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().idxmin()
diff = (
    df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().max()
    - df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().min()
)

st.markdown(f"""
<div class="insight-box">
    <p>🏆 <strong>Melhor estado:</strong> {melhor}</p>
    <p>⚠️ <strong>Pior estado:</strong> {pior}</p>
    <p>📏 <strong>Diferença entre extremos:</strong> {diff:.1f} pontos — indica desigualdade educacional regional relevante.</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# DOWNLOAD
# ==============================
st.markdown("<br>", unsafe_allow_html=True)
st.download_button(
    "📥 Baixar dados filtrados (.csv)",
    df.to_csv(index=False),
    "dados_enem_filtrados.csv",
    mime="text/csv"
)
