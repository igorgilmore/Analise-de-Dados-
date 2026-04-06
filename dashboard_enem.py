import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard ENEM 2024", layout="wide")

# Estilo para os Cards
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e1e4e8; }
    h1 { color: #1F4E79; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Dashboard Completo ENEM 2024")
st.markdown("Análise Geográfica e Estatística das Notas de Matemática")

# 2. Carregamento de Dados (SEM LIMIT)
@st.cache_data
def load_data():
    try:
        # CONEXÃO COM O BANCO DO IESB
        engine = create_engine("postgresql+psycopg2://data_iesb:iesb@bigdata.dataiesb.com:5432/iesb")
        
        # REMOVEMOS O LIMIT PARA PEGAR O BRASIL TODO
        query = "SELECT * FROM ed_enem_2024_resultados_amos_per WHERE nota_mt_matematica IS NOT NULL"
        
        df = pd.read_sql(query, engine)
        return df, "Banco de Dados (Brasil Completo)"
    except Exception as e:
        # SE O BANCO FALHAR, USA O SEU CSV
        df = pd.read_csv('ed_enem_2024_resultados_amos_per.csv')
        return df, "Base CSV Local"

df_raw, fonte = load_data()

if df_raw is not None:
    # 3. Sidebar com Filtros
    with st.sidebar:
        st.header("⚙️ Filtros da Análise")
        
        # Aqui pegamos TODOS os estados únicos
        lista_estados = sorted(df_raw["nome_uf_prova"].unique())
        
        # Selecionamos todos por padrão
        ufs_selecionadas = st.multiselect(
            "Selecione os Estados:", 
            options=lista_estados, 
            default=lista_estados
        )
        
        st.write(f"✅ **{len(ufs_selecionadas)}** estados selecionados.")
        st.divider()
        st.info(f"Conectado via: {fonte}")

    # Filtragem
    df = df_raw[df_raw["nome_uf_prova"].isin(ufs_selecionadas)]

    # 4. KPIs (Indicadores)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Alunos", f"{len(df):,}")
    c2.metric("Média MT", f"{df['nota_mt_matematica'].mean():.1f}")
    c3.metric("Maior Nota", f"{df['nota_mt_matematica'].max():.0f}")
    c4.metric("Qtd. Estados", f"{df['nome_uf_prova'].nunique()}")

    st.markdown("---")

    # 5. Visualizações
    col_esq, col_dir = st.columns([1.2, 0.8])

    with col_esq:
        # Média por UF (Gráfico de Barras)
        media_uf = df.groupby("nome_uf_prova")["nota_mt_matematica"].mean().reset_index().sort_values("nota_mt_matematica", ascending=False)
        fig_bar = px.bar(
            media_uf, x="nome_uf_prova", y="nota_mt_matematica",
            title="Média de Matemática por Estado (Ranking)",
            color="nota_mt_matematica", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_dir:
        # Histograma
        fig_hist = px.histogram(
            df, x="nota_mt_matematica", nbins=30,
            title="Distribuição das Notas",
            color_discrete_sequence=['#1F4E79']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # 6. Mapa (Brasil Inteiro)
    st.subheader("🌍 Mapa de Notas por Município")
    if 'latitude' in df.columns and 'longitude' in df.columns:
        fig_map = px.scatter_mapbox(
            df, lat="latitude", lon="longitude", 
            color="nota_mt_matematica", size="nota_mt_matematica",
            hover_name="no_municipio_prova", 
            mapbox_style="carto-positron", zoom=3, height=600,
            color_continuous_scale="RdYlGn" # Verde para notas altas, vermelho para baixas
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    
    st.caption("Igor Andrade - Análise Exploratória de Dados 2024")
else:
    st.error("Erro ao carregar dados.")
