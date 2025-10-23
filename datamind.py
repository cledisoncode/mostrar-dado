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
    metric_label_color = texto  # mantém texto claro no modo escuro

else:
    # --- MODO CLARO MELHORADO ---
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
    sidebar_text_color = "#000000"  # texto preto na sidebar
    metric_label_color = "#000000"  # “Total de Respostas” preto no modo claro

# --- ESTILO GLOBAL ---
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
            overflow-y: hidden !important;
            border-right: 2px solid {cor_tabela_borda} !important;
        }}
        section[data-testid="stSidebar"] * {{
            font-size: 21.5px !important;
            font-weight: 700 !important;
        }}
        /* Texto do menu “Escolha uma seção” e opções */
        section[data-testid="stSidebar"] label p,
        section[data-testid="stSidebar"] div[role="radiogroup"] label span {{
            color: {sidebar_text_color} !important;
        }}
        h1, h2, h3, h4 {{
            color: {destaque} !important;
            font-weight: 700 !important;
        }}
        div.stButton > button {{
            background-color: {cor_botao} !important;
            color: white !important;
            border-radius: 10px !important;
            border: 2px solid {cor_botao} !important;
            padding: 0.5em 1.2em !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }}
        div.stButton > button:hover {{
            background-color: {cor_hover} !important;
            border-color: {cor_hover} !important;
            transform: translateY(-1px) !important;
        }}
        .stDataFrame {{
            font-size: 17px !important;
            color: {texto} !important;
            background-color: {cor_tabela_fundo} !important;
            border: 2px solid {cor_tabela_borda} !important;
            border-radius: 8px !important;
        }}
        /* --- Ajuste total de respostas --- */
        div[data-testid="stMetricValue"] {{
            font-size: 1.5em !important;
            font-weight: 800 !important;
            color: {destaque} !important;
        }}
        div[data-testid="stMetricLabel"] > div > p {{
            font-size: 6em !important;
            font-weight: 900 !important;
            color: {metric_label_color} !important;
        }}
        div[data-testid="stMetricLabel"] p {{
            color: {metric_label_color} !important;
        }}
        /* Reforço extra para forçar cor preta no modo claro */
        .stMetric label, .stMetric div p {{
            color: {metric_label_color} !important;
        }}
        [data-testid="stSelectbox"] label p {{
            font-size: 1.2em !important;
            font-weight: 600 !important;
            color: {texto} !important;
        }}
        h1 {{ font-size: 2.8em !important; }}
        h2 {{ font-size: 2.2em !important; }}
        h3 {{ font-size: 1.5em !important; }}
        ::-webkit-scrollbar {{
            width: 10px !important;
        }}
        ::-webkit-scrollbar-thumb {{
            background-color: {cor_scroll} !important;
            border-radius: 6px !important;
            border: 2px solid {fundo} !important;
        }}
        ::-webkit-scrollbar-track {{
            background-color: {cor_sidebar} !important;
        }}
        hr {{
            border: 2px solid {cor_divisoria} !important;
            opacity: 1 !important;
            margin: 1.5rem 0 !important;
        }}

        /* --- Botão de download PDF --- */
        div.stDownloadButton > button {{
            background-color: #16a34a  !important;  /* verde equilibrado */
            color: white !important;
            border: 2px solid #16a34a !important;
            border-radius: 10px !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            padding: 0.6em 1.4em !important;
            transition: all 0.2s ease-in-out !important;
        }}
        div.stDownloadButton > button:hover {{
            background-color: #22c55e!important;  /* tom mais escuro no hover */
            border-color: #22c55e !important;
            transform: translateY(-2px) !important;
        }}
    </style>
""", unsafe_allow_html=True)


# --- FUNÇÃO PARA CARREGAR DADOS ---
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

# --- FUNÇÃO PARA LIMPAR TEXTO ---
def limpar_texto(texto):
    if isinstance(texto, str):
        texto = texto.replace("anos", "").replace("(anos)", "").replace("(anos", "").replace("anos)", "")
        texto = texto.replace("( )", "").replace("()", "")
        texto = texto.strip().strip('()').strip()
    return texto

# --- GERAR PDF APENAS COM RESUMO ---
def gerar_pdf_resumo(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    estilos = getSampleStyleSheet()
    elementos = []

    titulo = Paragraph("<b>Mente Digital - Relatório de Resumo das Respostas</b>", estilos['Title'])
    data_geracao = Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", estilos['Normal'])
    elementos.extend([titulo, data_geracao, Spacer(1, 12)])

    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(limpar_texto)

    colunas_perfil = [c for c in df.columns if not c.startswith("p") and "data_hora" not in c]
    for i, col in enumerate(colunas_perfil):
        titulo_coluna = col.capitalize().replace("(anos)", "").replace("anos", "").strip()
        elementos.append(Paragraph(f"<b>{titulo_coluna}</b>", estilos['Heading2']))
        elementos.append(Spacer(1, 6))
        contagem = df[col].value_counts().reset_index()
        contagem.columns = ["Resposta", "Quantidade"]
        contagem["Resposta"] = contagem["Resposta"].apply(limpar_texto)
        dados = [contagem.columns.tolist()] + contagem.values.tolist()
        tabela = Table(dados, repeatRows=1, colWidths=[350, 100])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elementos.append(tabela)
        if i < len(colunas_perfil) - 1:
            elementos.append(PageBreak())

    doc.build(elementos)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# --- SIDEBAR ---
with st.sidebar:
    menu = st.radio("Escolha uma seção:", ["Visão Geral", "Filtrar Dados", "Estatísticas", "Ver Dados Brutos"])
    st.markdown("---")
    st.caption("Atualiza automaticamente a cada 2 minutos.")
    nome_tema = "Modo Claro" if st.session_state.tema == "escuro" else "Modo Escuro"
    if st.button(f"{nome_tema}"):
        alternar_tema()
        st.rerun()

# --- CONTEÚDO PRINCIPAL ---
st.title("Mente Digital - Dashboard de Respostas")
st.divider()

df = carregar_dados()
if df.empty:
    st.warning("Nenhum dado disponível no momento.")
    st.stop()

# 🔹 LIMPEZA DE NOMES DAS COLUNAS
df.columns = (
    df.columns.str.replace(r"\(.*?\)", "", regex=True)
              .str.replace("anos", "", case=False, regex=True)
              .str.replace(r"\s+", " ", regex=True)
              .str.strip()
)

# --- VISÃO GERAL ---
if menu == "Visão Geral":
    st.subheader("Resumo dos Dados")
    st.metric("Total de Respostas", len(df))
    st.dataframe(df.head(), use_container_width=True)

# --- FILTRAR DADOS ---
elif menu == "Filtrar Dados":
    st.subheader("Filtrar Dados")
    colunas = [c for c in df.columns if c not in ["data_hora_registro", "id"]]
    coluna = st.selectbox("Escolha a coluna:", colunas)
    valores = df[coluna].dropna().unique().tolist()
    valores_limpos = [limpar_texto(str(v)) for v in valores]
    valor = st.selectbox("Escolha o valor:", valores_limpos)
    valor_original = next((v for v in valores if limpar_texto(str(v)) == valor), valor)
    filtrado = df[df[coluna].astype(str).apply(limpar_texto) == valor]
    st.success(f"{len(filtrado)} registros encontrados.")
    st.dataframe(filtrado, use_container_width=True)

# --- ESTATÍSTICAS ---
elif menu == "Estatísticas":
    st.subheader("Estatísticas por Campo")
    campos_mostrar = [
        "gênero", "genero", "idade", "raça", "raca",
        "grau de escolaridade", "estado civil",
        "situação atual de trabalho", "situacao atual de trabalho",
        "área de atuação", "area de atuação", "area de atuacao"
    ]

    for col in df.columns:
        col_lower = col.lower()
        if col_lower.startswith("p"):
            continue
        if any(chave in col_lower for chave in campos_mostrar):
            titulo = limpar_texto(col.capitalize())
            st.markdown(f"#### {titulo}")
            coluna_limpa = df[col].apply(limpar_texto)
            contagem = coluna_limpa.value_counts()
            st.bar_chart(contagem)
            st.dataframe(contagem.rename("Quantidade"), use_container_width=True)
            st.divider()

# --- VER DADOS BRUTOS ---
elif menu == "Ver Dados Brutos":
    st.subheader("Resumo das Respostas por Campo")
    df_display = df.drop(columns=["data_hora_registro"], errors="ignore").copy()
    for col in df_display.columns:
        if df_display[col].dtype == "object":
            df_display[col] = df_display[col].apply(limpar_texto)
    st.dataframe(df_display, use_container_width=True)
    pdf = gerar_pdf_resumo(df)
    st.download_button("📄 Baixar Relatório de Resumo (PDF)", pdf, "resumo_respostas.pdf", "application/pdf")
