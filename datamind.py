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

# --- CONFIGURAÇÃO GERAL ---
st.set_page_config(
    page_title="Mente Digital - Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO DARK ---
st.markdown("""
    <style>
        /* Fundo geral */
        .stApp {
            background-color: #0d1117;
            color: #f0f0f0;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #161b22 !important;
            border-right: 1px solid #30363d;
        }

        /* Títulos */
        h1, h2, h3, h4 {
            color: #58a6ff !important;
        }

        /* Texto padrão */
        p, label, span, div {
            color: #f0f0f0 !important;
        }

        /* Tabelas */
        .dataframe {
            background-color: #161b22 !important;
            color: #f0f0f0 !important;
            border-radius: 10px;
        }

        /* Botões */
        div.stDownloadButton > button,
        div.stButton > button {
            background-color: #238636 !important;
            color: white !important;
            border-radius: 8px !important;
            border: 1px solid #2ea043 !important;
            padding: 0.6em 1.2em !important;
            font-weight: 600;
        }

        div.stDownloadButton > button:hover,
        div.stButton > button:hover {
            background-color: #2ea043 !important;
        }

        /* Radio e Selectbox */
        div[data-testid="stRadio"] label, 
        div[data-baseweb="select"] span {
            color: #e6edf3 !important;
        }

        /* Inputs e caixas */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea > div > div > textarea {
            background-color: #21262d !important;
            color: #f0f0f0 !important;
            border: 1px solid #30363d !important;
            border-radius: 5px !important;
        }

        /* Separadores */
        hr {
            border: 1px solid #30363d !important;
        }

        /* Métricas */
        div[data-testid="stMetricValue"] {
            color: #79c0ff !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0d1117;
        }
        ::-webkit-scrollbar-thumb {
            background-color: #30363d;
            border-radius: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO PARA CARREGAR DADOS ---
@st.cache_data(ttl=120)
def carregar_dados():
    url = 'https://docs.google.com/spreadsheets/d/1M0YOy5YtE7BgeD45BAzVBXZCIGtAfdkonv0rHlri9sg/export?format=csv&gid=898962914'
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        
        # REMOÇÃO DO ID E DA COLUNA DE DATA/HORA ADICIONADA:
        # Removendo a linha abaixo para não inserir mais o "id"
        # df.insert(0, "id", range(1, len(df) + 1))
        
        # AQUI VAMOS APENAS GARANTIR QUE SE HOUVER UMA COLUNA DE DATA/HORA, ELA SE CHAME data_hora_registro 
        # MAS NÃO VAMOS ADICIONAR UMA NOVA SE ELA JÁ EXISTIR (APENAS RENOMEAR A EXISTENTE SE NECESSÁRIO)
        data_hora_col = next((c for c in df.columns if "hora" in c or "timestamp" in c), None)
        if data_hora_col:
            df.rename(columns={data_hora_col: "data_hora_registro"}, inplace=True)
        # Se não houver, não faremos nada, focando apenas nos dados de resposta.

        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- FUNÇÃO AUXILIAR PARA OBTER COLUNAS DE PERFIL (EXCLUINDO ID E DATA/HORA) ---
def get_colunas_de_analise(df):
    """Retorna as colunas que devem ser usadas para filtro e estatísticas, 
    excluindo aquelas que são identificadores ou de controle."""
    # Lista de termos a serem ignorados para filtro/estatísticas
    termos_ignorar = ("em", "qual", "que", "você", "voce", "hora", "timestamp", "data_hora_registro", "id")
    
    colunas_de_analise = [
        col for col in df.columns
        if len(col.split()) <= 5 # Critério de nome curto
        and not col.startswith(termos_ignorar)
    ]
    return colunas_de_analise

# --- FUNÇÃO PARA GERAR PDF (AJUSTADA) ---
def gerar_pdf_por_campo(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    estilos = getSampleStyleSheet()
    elementos = []

    # Título do PDF alterado para refletir a ausência de ID
    titulo = Paragraph("<b>🧠 Mente Digital - Relatório de Respostas (por campo - Sem Identificadores)</b>", estilos['Title'])
    data_geracao = Paragraph(f"Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", estilos['Normal'])
    elementos.extend([titulo, data_geracao, Spacer(1, 12)])

    # Usando a nova função auxiliar para obter as colunas sem ID/Data
    colunas_perfil = get_colunas_de_analise(df)

    for i, col in enumerate(colunas_perfil):
        elementos.append(Paragraph(f"<b>{col.capitalize()}</b>", estilos['Heading2']))
        elementos.append(Spacer(1, 8))
        
        # AQUI É O AJUSTE PRINCIPAL: a lista 'campos' agora só contém a coluna de interesse.
        campos = [col] 
        dados_coluna = df[campos].copy()
        dados = [dados_coluna.columns.tolist()] + dados_coluna.values.tolist()
        tabela = Table(dados, repeatRows=1)
        
        estilo_tabela = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ])
        tabela.setStyle(estilo_tabela)
        elementos.append(tabela)
        if i < len(colunas_perfil) - 1:
            elementos.extend([Spacer(1, 20), PageBreak()])

    doc.build(elementos)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# --- SIDEBAR ---
st.sidebar.title("🧭 Navegação")
menu = st.sidebar.radio(
    "Escolha uma seção:",
    ["📊 Visão Geral", "🔍 Filtrar Dados", "📈 Estatísticas", "🧾 Ver Dados Brutos"]
)
st.sidebar.markdown("---")
st.sidebar.caption("🔄 Atualiza automaticamente a cada 2 minutos.")

# --- CONTEÚDO PRINCIPAL ---
st.title("🧠 Mente Digital - Dashboard de Respostas")
st.markdown("Explore os dados do Forms com uma interface moderna e escura 🌙")
st.divider()

df = carregar_dados()

# Colunas que NÃO são identificadores (para uso no selectbox de filtro)
colunas_analise_filtro = [col for col in df.columns if col not in ("data_hora_registro", "id")]

if df.empty:
    st.warning("⚠️ Nenhum dado disponível no momento.")
else:
    if menu == "📊 Visão Geral":
        st.subheader("📋 Resumo dos Dados")
        with st.container():
            st.metric(label="Total de Respostas", value=len(df))
            st.dataframe(df.head(), use_container_width=True)

    elif menu == "🔍 Filtrar Dados":
        st.subheader("🎯 Filtrar Dados Interativamente")
        st.markdown("Escolha uma coluna e um valor específico para visualizar apenas os registros correspondentes.")
        st.divider()

        # AJUSTE: Usando as colunas filtradas, sem ID e data_hora_registro.
        if not colunas_analise_filtro:
            st.warning("Nenhuma coluna disponível para filtro após a remoção dos identificadores.")
        else:
            coluna = st.selectbox("📌 Escolha a coluna:", colunas_analise_filtro)
            valores_unicos = df[coluna].dropna().unique().tolist()
            valor = st.selectbox("🎯 Escolha o valor:", valores_unicos)

            filtrado = df[df[coluna] == valor]
            st.success(f"{len(filtrado)} registros encontrados.")
            st.dataframe(filtrado, use_container_width=True)

    elif menu == "📈 Estatísticas":
        st.subheader("📊 Estatísticas Automáticas (dados pessoais)")
        
        # AJUSTE: Usando a nova função auxiliar para obter as colunas de perfil
        colunas_perfil = get_colunas_de_analise(df)
        
        if not colunas_perfil:
            st.warning("Nenhum campo de perfil encontrado.")
        else:
            for col in colunas_perfil:
                contagem = df[col].value_counts(dropna=True)
                st.markdown(f"#### 📍 {col.capitalize()}")
                col1, col2 = st.columns(2)
                with col1:
                    st.bar_chart(contagem)
                with col2:
                    st.write(contagem)
                st.divider()

    elif menu == "🧾 Ver Dados Brutos":
        st.subheader("📑 Todos os Dados Coletados")
        
        # AJUSTE: Exibindo o DataFrame sem as colunas de controle (se existirem)
        df_display = df.copy()
        if "data_hora_registro" in df_display.columns:
            df_display.drop(columns=["data_hora_registro"], inplace=True)
            
        st.dataframe(df_display, use_container_width=True)
        st.divider()
        
        pdf = gerar_pdf_por_campo(df)
        st.download_button(
            # Rótulo do botão alterado
            label="📄 Baixar Relatório PDF (Sem Identificadores)",
            data=pdf,
            file_name='respostas_anonimas.pdf',
            mime='application/pdf'
        )
