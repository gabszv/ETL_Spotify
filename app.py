import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Spotify Dashboard",
    layout="wide"
)

# Conexão MongoDB
@st.cache_resource
def init_connection():
    try:
        client = MongoClient('mongodb+srv://admin:admin@marioteste.ncplnpm.mongodb.net/spotify_db')
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f'Erro ao conectar ao MongoDB: {str(e)}')
        return None

@st.cache_data(ttl=600)
def get_data():
    client = init_connection()
    if client is None:
        return None
    
    try:
        db = client.spotify_db
        items = list(db.teste_spotify.find())
        if not items:
            st.warning('Nenhum dado encontrado no MongoDB.')
            return None
        return pd.DataFrame(items)
    except Exception as e:
        st.error(f'Erro ao buscar dados: {str(e)}')
        return None

# Título
st.markdown("<h1 style='text-align: center;'>Dashboard Spotify</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Carregar dados
df = get_data()

if df is None:
    st.error("Não foi possível obter os dados do MongoDB.")
    st.stop()

# Limpar ID
if '_id' in df.columns:
    df = df.drop('_id', axis=1)

# Tabela - movida para o topo
st.subheader("Lista de Músicas")
st.dataframe(
    df[['nome', 'artistas', 'popularidade', 'duracao_min']].sort_values('popularidade', ascending=False),
    column_config={
        'nome': 'Música',
        'artistas': 'Artistas',
        'popularidade': st.column_config.ProgressColumn('Popularidade', min_value=0, max_value=100),
        'duracao_min': st.column_config.NumberColumn('Duração (min)', format="%.2f")
    },
    hide_index=True
)

# Gráficos
st.markdown("<hr>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Músicas por Popularidade")
    top_10_popular = df.nlargest(10, 'popularidade')[['nome', 'artistas', 'popularidade']]
    fig_popular = px.bar(
        top_10_popular,
        x='popularidade',
        y='nome',
        orientation='h',
        text='popularidade',
        color='popularidade',
        color_continuous_scale='gray'
    )
    fig_popular.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_popular, use_container_width=True)

with col2:
    st.subheader("Distribuição de Duração das Músicas")
    fig_duration = px.histogram(
        df,
        x='duracao_min',
        nbins=20,
        title='Duração (minutos)',
        color_discrete_sequence=['gray']
    )
    st.plotly_chart(fig_duration, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Resumo Geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div style="background-color:#4CAF50;padding:20px;border-radius:10px;text-align:center;color:white;">
            <h4>Total de Músicas</h4>
            <h2>{len(df)}</h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="background-color:#2196F3;padding:20px;border-radius:10px;text-align:center;color:white;">
            <h4>Popularidade Média</h4>
            <h2>{df['popularidade'].mean():.1f}</h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style="background-color:#FF9800;padding:20px;border-radius:10px;text-align:center;color:white;">
            <h4>Duração Média</h4>
            <h2>{df['duracao_min'].mean():.1f} min</h2>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div style="background-color:#9C27B0;padding:20px;border-radius:10px;text-align:center;color:white;">
            <h4>Artistas Únicos</h4>
            <h2>{len(df['artistas'].unique())}</h2>
        </div>
    """, unsafe_allow_html=True)
