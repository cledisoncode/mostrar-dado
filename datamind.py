import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, PageBreak
)
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO GERAL ---
st.set_page_config(
    page_title="Mente Digital - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GERENCIAMENTO DE TEMA ---
if 'tema' not in st.session_state:
    st.session_state.tema = "escuro"

def alternar_tema():
    st.session_state.tema = "claro" if st.session_state.tema == "escuro" else "escuro"

# --- DEFINIÇÃO DE CORES E ESTILOS ---
if st.session_state.tema == "escuro":
    fundo = "#0d1117"
    texto = "#f0f0f0"
    destaque = "#58a6ff"
    cor_botao = "#238636"
    cor_hover = "#2ea043"
    cor_tabela_fundo = "#161b22"
    cor_tabela_borda = "#30363d"
    cor_sidebar = "#161b22"
    cor_scroll = "#30363d"
    cor_divisoria = "#ffffff"
    sidebar_text_color = texto
    metric_label_color = texto
else:
    fundo = "#f3f4f6"
    texto = "#0a0a0a"
    destaque = "#0b4dd8"
    cor_botao = "#1d4ed8"
    cor_hover = "#0b3ea9"
    cor_tabela_fundo = "#f9fafb"
    cor_tabela_borda = "#000000C3"
    cor_sidebar = "#f3f4f6"
    cor_scroll = "#475569"
    cor_divisoria = "#1e293b"
    sidebar_text_color = "#000000"
    metric_label_color = "#000000"

# --- CSS GLOBAL ---
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {fundo};
            color: {texto};
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {cor_sidebar} !important;
            color: {sidebar_text_color} !important;
            border-right: 2px solid {cor_tabela_borda} !important;
        }}
        section[data-testid="stSidebar"] * {{
            font-size: 21.5px !important;
            font-weight: 700 !important;
        }}
        h1, h2, h3, h4 {{
            color: {destaque} !important;
            font-weight: 700 !important;
        }}
        div.stButton > button {{
            background-color: {cor_botao} !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.5em 1.2em !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }}
        div.stButton > button:hover {{
            background-color: {cor_hover} !important;
            transform: translateY(-1px) !important;
        }}
        div.stDownloadButton > button {{
            background-color: #16a34a !important;
            color: white !important;
            border: 2px solid #16a34a !important;
            border-radius: 10px !important;
            font-size: 18px !important;
            font-weight: 700 !important;
        }}
        div.stDownloadButton > button:hover {{
            background-color: #22c55e!important;
            transform: translateY(-2px) !important;
        }}
        ::-webkit-scrollbar-thumb {{
            background-color: {cor_scroll} !important;
            border-radius: 6px !important;
        }}
        hr {{
            border: 2px solid {cor_divisoria} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO PARA ESTILIZAR TABELAS CONFORME O TEMA ---
def aplicar_estilo_tabela(df):
    """Retorna o DataFrame com estilo adaptado ao tema atual."""
    if st.session_state.tema == "escuro":
        cor_fundo = "#161b22"
        cor_texto = "#f0f0f0"
        cor_header = "#0d1117"
        cor_borda = "#30363d"
    else:
        cor_fundo = "#f9fafb"
        cor_texto = "#0a0a0a"
        cor_header = "#e5e7eb"
        cor_borda = "#d1d5db"

    estilo = df.style.set_table_styles([
        {'selector': 'thead th',
         'props': [('background-color', cor_header),
                   ('color', cor_texto),
                   ('font-weight', 'bold'),
                   ('border', f'1px solid {cor_borda}')]},
        {'selector': 'tbody td',
         'props': [('background-color', cor_fundo),
                   ('color', cor_texto),
                   ('border', f'1px solid {cor_borda}')]}
    ]).set_properties(**{
        'text-align': 'center',
        'border-color': cor_borda
    })

    return estilo

# --- FUNÇÕES AUXILIARES ---
def limpar_texto(texto):
    if isinstance(texto, str):
        texto = texto.lower().strip()
        texto = texto.replace("anos", "").replace("ano", "").replace("( )", "").replace("()", "")
        texto = texto.strip().strip('()').strip()
        if texto.count("(") > texto.count(")"):
            texto = texto + ")"
        texto = " ".join(texto.split())
    return texto

def tentar_converter_para_int(valor):
    try:
        if pd.isna(valor) or valor == '':
            return np.nan
        return int(float(valor)) 
    except (ValueError, TypeError):
        return np.nan

@st.cache_data(ttl=120)
def carregar_dados():
    url = 'https://docs.google.com/spreadsheets/d/1M0YOy5YtE7BgeD45BAzVBXZCIGtAfdkonv0rHlri9sg/export?format=csv&gid=898962914'
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        data_hora_col = next((c for c in df.columns if "hora" in c or "timestamp" in c), None)
        if data_hora_col:
            df.rename(columns={data_hora_col: "data_hora_registro"}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    menu = st.radio("Escolha uma seção:", ["Home", "Consultar Dados", "Estatísticas"])

# --- ÍCONE DE TROCA DE TEMA ---
icone_tema = "☀️" if st.session_state.tema == "escuro" else "🌙"
col1, col2 = st.columns([0.9, 0.1])
with col2:
    if st.button(icone_tema, key="botao_tema", help="Alternar tema"):
        alternar_tema()
        st.rerun()

# --- CONTEÚDO PRINCIPAL ---
st.title("Mente Digital - Dashboard de Respostas")
st.divider()

# ---- CARREGAR DADOS ---- #
df = carregar_dados()
if df.empty:
    st.warning("Nenhum dado disponível no momento.")
    st.stop()

df.columns = (
    df.columns.str.replace(r"\(.*?\)", "", regex=True)
              .str.replace("anos", "", case=False, regex=True)
              .str.replace(r"\s+", " ", regex=True)
              .str.strip()
)

df_limpo = df.copy()
coluna_idade = next((c for c in df_limpo.columns if c.lower() == "idade"), None)

for col in df_limpo.columns:
    if df_limpo[col].dtype == "object":
        df_limpo[col] = df_limpo[col].astype(str).apply(limpar_texto)
if coluna_idade:
    df_limpo[coluna_idade] = df_limpo[coluna_idade].apply(tentar_converter_para_int)

# --- HOME ---
if menu == "Home":
    st.subheader("Bem-vindo(a) ao Projeto Mente Digital")
    st.markdown("""
    <main style="font-size: 20px; line-height: 1.5; text-align: justify; font-weight: bold;">
    O Mente Digital é um projeto voltado à análise de dados coletados em pesquisas relacionadas ao comportamento, bem-estar e hábitos digitais dos participantes.  
    <br><br>
    Este painel interativo permite visualizar estatísticas, filtrar informações e exportar relatórios em PDF, oferecendo uma visão clara e organizada das respostas obtidas.  
    <br><br>
    Este painel é atualizado automaticamente a cada 2 minutos para refletir as respostas mais recentes.
    </main>
    """, unsafe_allow_html=True)

# --- CONSULTAR DADOS ---
elif menu == "Consultar Dados":
    st.subheader("Consultar Dados")
    st.markdown("Selecione um campo e um valor específico para análise.")
    colunas_filtrar = [c for c in df_limpo.columns if c not in ["data_hora_registro", "id"]]
    coluna = st.selectbox("Escolha a coluna:", colunas_filtrar)

    valores = df_limpo[coluna].dropna().unique().tolist()
    valores = [v for v in valores if str(v).strip() != '']

    if len(valores) > 0:
        valor_selecionado = st.selectbox("Escolha o valor:", sorted(valores, key=str))
        filtrado = df_limpo[df_limpo[coluna].astype(str) == str(valor_selecionado)]
        st.success(f"{len(filtrado)} registros encontrados onde '{coluna.capitalize()}' é '{valor_selecionado}'.")
        st.dataframe(aplicar_estilo_tabela(filtrado), use_container_width=True)
    else:
        st.info("Esta coluna não possui valores para filtragem após a limpeza.")

    st.markdown("---")
    st.subheader("Dados Gerais")
    df_display = df_limpo.drop(columns=["data_hora_registro"], errors="ignore").copy()
    st.dataframe(aplicar_estilo_tabela(df_display), use_container_width=True)
