
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
from streamlit.components.v1 import html as st_html

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
    cor_sidebar = "#161b22"
    cor_tabela_borda = "#30363d"
    sidebar_text_color = texto
else:
    fundo = "#f3f4f6"
    texto = "#0a0a0a"
    destaque = "#0b4dd8"
    cor_botao = "#1d4ed8"
    cor_hover = "#0b3ea9"
    cor_sidebar = "#f9fafb"
    cor_tabela_borda = "#d1d5db"
    sidebar_text_color = "#000000"

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
        h1, h2, h3 {{
            color: {destaque} !important;
            font-weight: 700 !important;
        }}
        div.stButton > button {{
            background-color: {cor_botao} !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.5em 1.2em !important;
            font-weight: 600 !important;
        }}
        div.stButton > button:hover {{
            background-color: {cor_hover} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE ESTILO DAS TABELAS ---
def aplicar_estilo_tabela(df):
    """Retorna o DataFrame com estilo base conforme tema."""
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
                   ('border', f'1px solid {cor_borda}')]}])
    return estilo

# --- NOVA FUNÇÃO PARA RENDERIZAR TABELAS (DARK/LIGHT FUNCIONAL) ---
def render_styled_table(df, height=420, hide_index=True):
    """Renderiza DataFrame com tema respeitando fundo escuro ou claro."""
    styler = aplicar_estilo_tabela(df)
    if hide_index:
        try:
            styler = styler.hide_index()
        except Exception:
            pass

    html_table = styler.to_html()

    if st.session_state.tema == "escuro":
        _fundo = "#161b22"
        _header = "#0d1117"
        _texto = "#f0f0f0"
        _borda = "#30363d"
    else:
        _fundo = "#f9fafb"
        _header = "#e5e7eb"
        _texto = "#0a0a0a"
        _borda = "#d1d5db"

    wrapper = f"""
    <div style="background:{_fundo}; padding:8px; border-radius:10px; border:1px solid {_borda}; overflow:auto;">
      {html_table}
    </div>
    <style>
      .dataframe thead th {{
        background: {_header} !important;
        color: {_texto} !important;
        border: 1px solid {_borda} !important;
        font-weight: 700 !important;
      }}
      .dataframe tbody td {{
        background: {_fundo} !important;
        color: {_texto} !important;
        border: 1px solid {_borda} !important;
        padding: 8px !important;
      }}
      .dataframe {{ width:100% !important; border-collapse: collapse !important; }}
    </style>
    """
    st_html(wrapper, height=height, scrolling=True)


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

def gerar_pdf_resumo(df):
    from reportlab.platypus import Image, KeepTogether
    from reportlab.lib.styles import ParagraphStyle
    import tempfile

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name='TituloGrafico',
        parent=estilos['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        spaceAfter=6,
        textColor=colors.black,
        italic=False
    ))

    elementos = []

    titulo = Paragraph("<b>Mente Digital - Relatório de Estatísticas</b>", estilos['Title'])
    # data_geracao = Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", estilos['Normal'])
    elementos.extend([titulo, Spacer(1, 20)])

    campos_mostrar = [
        "gênero", "genero", "raça", "raca",
        "grau de escolaridade", "estado civil",
        "situação atual de trabalho", "situacao atual de trabalho",
        "área de atuação", "area de atuação", "area de atuacao"
    ]

    coluna_idade = next((c for c in df.columns if c.lower() == "idade"), None)
    df_local = df.copy()

    def salvar_grafico(fig):
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.savefig(tmpfile.name, bbox_inches='tight', dpi=150)
        plt.close(fig)
        return tmpfile.name

    for col in df_local.columns:
        col_lower = col.lower()
        if col_lower.startswith("p"):
            continue
        if any(chave in col_lower for chave in campos_mostrar):
            titulo_coluna = Paragraph(f"<b>{col.capitalize()}</b>", estilos['Heading2'])
            elementos.append(titulo_coluna)
            elementos.append(Spacer(1, 10))

            contagem = df_local[col].value_counts()
            contagem = contagem[contagem.index.astype(str).str.strip() != '']

            if not contagem.empty:
                # 🔹 Gráfico de pizza
                if any(pie_field in col_lower for pie_field in ["gênero", "genero", "raça", "raca", "estado civil"]):
                    cores = plt.cm.Set3.colors[:len(contagem)]
                    fig, ax = plt.subplots(figsize=(7.5, 3.5))

                    if "estado civil" in col_lower:
                        # --- Gráfico de pizza especial com percentuais fora ---
                        wedges, texts = ax.pie(
                            contagem.values,
                            labels=None,
                            startangle=180,
                            radius=0.9,
                            wedgeprops={'edgecolor': 'white', 'linewidth': 2, 'antialiased': True},
                            colors=cores
                        )

                        total = contagem.values.sum()
                        percents = 100.0 * contagem.values / total

                        # Posiciona os percentuais fora com linhas
                        for i, p in enumerate(wedges):
                            ang = (p.theta2 + p.theta1) / 2.0
                            x = np.cos(np.deg2rad(ang))
                            y = np.sin(np.deg2rad(ang))

                            text_x = x * 1.3
                            text_y = y * 1.3
                            xy_x = x * 0.9
                            xy_y = y * 0.9
                            ha = "left" if x >= 0 else "right"

                            ax.annotate(
                                f"{percents[i]:.1f}%",
                                xy=(xy_x, xy_y),
                                xytext=(text_x, text_y),
                                ha=ha, va='center',
                                fontsize=10, fontweight='bold',
                                color='black',
                                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"),
                                arrowprops=dict(arrowstyle='-', connectionstyle="arc3,rad=0.2", color='black', linewidth=0.8)
                            )

                    else:
                        # --- Gráfico de pizza padrão ---
                        wedges, texts, autotexts = ax.pie(
                            contagem.values, autopct='%1.1f%%', colors=cores,
                            startangle=90, radius=0.8,
                            textprops={'fontsize': 10, 'color': 'black'},
                            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
                        )
                        for autotext in autotexts:
                            autotext.set_fontsize(10)
                            autotext.set_color('black')

                    ax.axis('equal')
                    # 🔸 Legenda com fonte maior
                    ax.legend(
                        wedges, contagem.index, loc="center left",
                        bbox_to_anchor=(1, 0, 0.5, 1),
                        fontsize=12  # Aumentado
                    )
                    img_path = salvar_grafico(fig)
                    elementos.append(Image(img_path, width=400, height=250))

                    # 🔹 Gráfico de Idade (mantido junto com gênero)
                    if any(p in col_lower for p in ["gênero", "genero"]) and coluna_idade in df_local.columns:
                        idades = df_local[coluna_idade].dropna()
                        if not idades.empty:
                            titulo_idade = Paragraph("Idade", estilos['TituloGrafico'])
                            espacador_idade = Spacer(1, 8)

                            fig, ax = plt.subplots(figsize=(5.5, 3.5))
                            bins = range(int(idades.min()), int(idades.max()) + 10, 10)
                            n, bins_edges, patches = ax.hist(
                                idades, bins=bins, color="#58a6ff",
                                edgecolor="white", linewidth=1.5, alpha=0.85
                            )
                            ax.bar_label(patches, fmt='%d', fontsize=9, color="black")
                            bin_labels = [f"{int(bins_edges[i])}-{int(bins_edges[i+1])-1}" for i in range(len(bins_edges)-1)]
                            ax.set_xticks([(bins_edges[i] + bins_edges[i+1]) / 2 for i in range(len(bins_edges)-1)])
                            ax.set_xticklabels(bin_labels, rotation=45, ha='right', fontsize=9)
                            ax.set_xlabel("Faixa Etária", fontsize=10, fontweight='bold')
                            ax.set_ylabel("Quantidade", fontsize=10, fontweight='bold')
                            ax.grid(axis='y', color="#cccccc", linestyle='--', linewidth=0.5)

                            img_path_idade = salvar_grafico(fig)
                            imagem_idade = Image(img_path_idade, width=400, height=250)
                            bloco_idade = KeepTogether([Spacer(1, 12), titulo_idade, espacador_idade, imagem_idade, Spacer(1, 12)])
                            elementos.append(bloco_idade)

                # 🔹 Gráfico de barras
                elif any(bar_field in col_lower for bar_field in [
                    "grau de escolaridade", "área de atuação", "area de atuação", "area de atuacao",
                    "situação atual de trabalho", "situacao atual de trabalho"
                ]):
                    fig, ax = plt.subplots(figsize=(12, 6))
                    cores = plt.cm.tab20.colors[:len(contagem)]
                    barras = ax.bar(range(len(contagem)), contagem.values, color=cores, edgecolor="white", linewidth=1.5)

                    # 🔹 Aumentar o tamanho dos números nas barras
                    ax.bar_label(barras, fmt='%d', fontsize=14, color="black", fontweight='bold')

                    ax.set_xticks([])
                    ax.set_ylabel("Quantidade", fontsize=14, fontweight='bold')
                    ax.set_title("Situação atual de trabalho", fontsize=18, fontweight='bold', pad=15)

                    # 🔹 Aumentar tamanho da legenda
                    ax.legend(
                        barras, contagem.index,
                        loc='upper center', bbox_to_anchor=(0.5, -0.25),
                        ncol=2, frameon=False, fontsize=14
                    )

                    # 🔹 Aumentar fonte dos eixos e rótulos
                    ax.tick_params(axis='y', labelsize=13)
                    ax.grid(axis='y', color="#cccccc", linestyle='--', linewidth=0.6)

                    img_path = salvar_grafico(fig)
                    elementos.append(Image(img_path, width=550, height=450))


            # 🔹 Adiciona a data de geração apenas no final do PDF
            elementos.append(PageBreak())

    data_geracao = Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
        estilos['Normal']
    )
    elementos.append(Spacer(1, 20))
    elementos.append(data_geracao)

    doc.build(elementos)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf



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



#----CARREGAR DADOS----#
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

# 🔹 LIMPEZA E TRATAMENTO DE DADOS
df_limpo = df.copy()
coluna_idade = next((c for c in df_limpo.columns if c.lower() == "idade"), None)

for col in df_limpo.columns:
    if df_limpo[col].dtype == "object":
        df_limpo[col] = df_limpo[col].astype(str).apply(limpar_texto)

if coluna_idade:
    df_limpo[coluna_idade] = df_limpo[coluna_idade].apply(tentar_converter_para_int)



# --- VISÃO GERAL (ALTERADO CONFORME SOLICITADO) ---
if menu == "Home":
    st.subheader("Bem-vindo(a) ao Projeto Mente Digital")
    texto_apresentacao = """
    <main style="font-size: 20px; line-height: 1.5; text-align: justify; font-weight: bold;">
    O Mente Digital é um projeto voltado à análise de dados coletados em pesquisas relacionadas ao comportamento, bem-estar e hábitos digitais dos participantes.  
    <br><br>
    Este painel interativo permite visualizar estatísticas, filtrar informações e exportar relatório em PDF, oferecendo uma visão clara e organizada das respostas obtidas.  
    <br><br>
    Este painel é atualizado automaticamente a cada 2 minutos para refletir as respostas mais recentes.
    </main>
    """
    st.markdown(texto_apresentacao, unsafe_allow_html=True)

# --- FILTRAR DADOS ---
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
        st.dataframe(filtrado, use_container_width=True)
    else:
        st.info("Esta coluna não possui valores para filtragem após a limpeza.")

    st.markdown("---")

    st.subheader("Dados Gerais")

    df_display = df_limpo.drop(columns=["data_hora_registro"], errors="ignore").copy()
    st.dataframe(df_display, use_container_width=True)

    st.markdown("---")
    st.subheader("Relatório PDF")
    st.write("Gerar PDF com  resumo de todos os dados em forma de gráfico .")

    pdf = gerar_pdf_resumo(df)
    st.download_button(
        "Baixar (PDF)", 
        pdf, 
        f"resumo_em_grafico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", 
        "application/pdf", 
        key='download_pdf_brutos'
    )


# --- ESTATÍSTICAS ---
elif menu == "Estatísticas":
    st.subheader("Estatísticas por Campo de Perfil")
    campos_mostrar = [
        "gênero", "genero", "raça", "raca",
        "grau de escolaridade", "estado civil",
        "situação atual de trabalho", "situacao atual de trabalho",
        "área de atuação", "area de atuação", "area de atuacao"
    ]

    campos_mostrar_filtrados = [c for c in campos_mostrar if c not in ["idade"]] 

    for col in df_limpo.columns:
        col_lower = col.lower()
        if col_lower.startswith("p"): 
            continue
        if any(chave in col_lower for chave in campos_mostrar_filtrados):
            titulo = col.capitalize().strip()
            st.markdown(f"#### {titulo}")

            contagem = df_limpo[col].value_counts()
            contagem = contagem[contagem.index.astype(str).str.strip() != '']  # Remove vazios

            if not contagem.empty:
                # --- GRÁFICO DE PIZZA PARA GÊNERO, RAÇA, ESTADO CIVIL ---
                    # --- GRÁFICOS DE PIZZA ---
                if any(pie_field in col_lower for pie_field in ["gênero", "genero", "estado civil", "raça", "raca"]):
                    cores = plt.cm.Set3.colors[:len(contagem)]
                    legend_labels = [limpar_texto(str(idx)).capitalize() for idx in contagem.index]
                    fig, ax = plt.subplots(figsize=(7, 4))

                    # 🔸 Gráfico especial apenas para "Estado civil"
                    if "estado civil" in col_lower:
                        # --- GRÁFICO DE PIZZA COM LEADER LINES ---
                        wedges, texts = ax.pie(
                            contagem.values,
                            labels=None,
                            startangle=180,
                            radius=0.9,
                            wedgeprops={'edgecolor': 'white', 'linewidth': 2, 'antialiased': True},
                            colors=cores
                        )

                        total = contagem.values.sum()
                        percents = 100.0 * contagem.values / total

                        # Cores do texto e fundo conforme tema
                        if st.session_state.tema == "escuro":
                            text_color = "white"
                            bbox_fc = fundo
                        else:
                            text_color = "black"
                            bbox_fc = "white"

                        # Posiciona percentuais fora com linhas
                        for i, p in enumerate(wedges):
                            ang = (p.theta2 + p.theta1) / 2.0
                            x = np.cos(np.deg2rad(ang))
                            y = np.sin(np.deg2rad(ang))

                            text_x = x * 1.35
                            text_y = y * 1.35
                            xy_x = x * 0.95
                            xy_y = y * 0.95
                            ha = "left" if x >= 0 else "right"

                            ax.annotate(
                                f"{percents[i]:.1f}%",
                                xy=(xy_x, xy_y),
                                xytext=(text_x, text_y),
                                ha=ha, va='center',
                                fontsize=10, fontweight='bold',
                                color=text_color,
                                bbox=dict(boxstyle="round,pad=0.2", fc=bbox_fc, ec="none"),
                                arrowprops=dict(arrowstyle='-', connectionstyle="arc3,rad=0.2", color=text_color, linewidth=0.8)
                            )

                    else:
                        # --- GRÁFICO DE PIZZA PADRÃO (demais colunas) ---
                        wedges, texts, autotexts = ax.pie(
                            contagem.values,
                            autopct='%1.1f%%',
                            colors=cores,
                            startangle=90,
                            radius=0.9,
                            pctdistance=0.75,
                            labeldistance=1.05,
                            textprops={'color': 'black', 'fontsize': 10, 'weight': 'bold'},
                            wedgeprops={'edgecolor': 'white', 'linewidth': 2, 'antialiased': True}
                        )

                        for autotext in autotexts:
                            autotext.set_horizontalalignment('center')
                            autotext.set_verticalalignment('center')

                    # 🔹 Fundo conforme tema
                    if st.session_state.tema == "escuro":
                        fig.patch.set_facecolor(fundo)
                        ax.set_facecolor(fundo)
                        legend_color = "white"
                    else:
                        fig.patch.set_facecolor('white')
                        ax.set_facecolor('white')
                        legend_color = "black"

                    ax.axis('equal')
                    ax.legend(
                        wedges,
                        legend_labels,
                        loc="center left",
                        bbox_to_anchor=(1, 0, 0.5, 1),
                        labelcolor=legend_color,
                        fontsize=10
                    )

                    plt.tight_layout(pad=2.5)
                    st.pyplot(fig)

                    # Separar gênero do gráfico de idade
                    if any(pie_field in col_lower for pie_field in ["gênero", "genero"]):
                        st.divider()

                    # --- GRÁFICO PARA IDADE (APÓS GÊNERO) ---
                    if any(pie_field in col_lower for pie_field in ["gênero", "genero"]):
                        if coluna_idade and coluna_idade in df_limpo.columns:
                            st.markdown("#### Idade")
                            idades = df_limpo[coluna_idade].dropna()
                            if not idades.empty:
                                fig, ax = plt.subplots(figsize=(8, 5))

                                # Fundo dinâmico conforme o tema
                                if st.session_state.tema == "escuro":
                                    fig.patch.set_facecolor(fundo)
                                    ax.set_facecolor(fundo)
                                    texto_cor = "white"
                                    grid_color = "#555555"
                                else:
                                    fig.patch.set_facecolor('white')
                                    ax.set_facecolor('white')
                                    texto_cor = "black"
                                    grid_color = "#cccccc"

                                # Histograma com bins apropriados (ex: de 10 em 10 anos)
                                bins = range(int(idades.min()), int(idades.max()) + 10, 10)
                                n, bins_edges, patches = ax.hist(idades, bins=bins, color='#58a6ff', edgecolor='white', linewidth=1.5, alpha=0.8)

                                # Adicionar valores no topo das barras (patches)
                                ax.bar_label(patches, fmt='%d', color=texto_cor, fontsize=10, fontweight='bold')

                                # Criar labels para faixas etárias (ex: "20-29", "30-39", etc.)
                                bin_labels = [f"{int(bins_edges[i])}-{int(bins_edges[i+1])-1}" for i in range(len(bins_edges)-1)]
                                ax.set_xticks([(bins_edges[i] + bins_edges[i+1]) / 2 for i in range(len(bins_edges)-1)])  # Centralizar ticks
                                ax.set_xticklabels(bin_labels, rotation=45, ha='right', color=texto_cor, fontsize=10)

                                # Títulos e layout
                                ax.set_xlabel('Faixa Etária', color=texto_cor, fontsize=12, fontweight='bold')
                                ax.set_ylabel('Quantidade', color=texto_cor, fontsize=12, fontweight='bold')
                                ax.tick_params(axis='y', labelcolor=texto_cor, labelsize=10)
                                ax.grid(axis='y', color=grid_color, linestyle='--', linewidth=0.5, alpha=0.7)

                                st.pyplot(fig)
                            else:
                                st.info("Nenhum dado válido para idade.")
                            # Não adicionar divider aqui para não separar idade de raça

                # --- GRÁFICO DE COLUNAS COLORIDAS PARA GRAU DE ESCOLARIDADE, ÁREA DE ATUAÇÃO, SITUAÇÃO ATUAL DE TRABALHO ---
                elif any(bar_field in col_lower for bar_field in [
                    "grau de escolaridade", "área de atuação", "area de atuação", "area de atuacao",
                    "situação atual de trabalho", "situacao atual de trabalho"
                ]):
                    fig, ax = plt.subplots(figsize=(8, 5))  # Tamanho maior para melhor visibilidade
                    # Paleta colorida moderna
                    cores = plt.cm.tab20.colors[:len(contagem)]  

                    # Fundo dinâmico conforme o tema
                    if st.session_state.tema == "escuro":
                        fig.patch.set_facecolor(fundo)
                        ax.set_facecolor(fundo)
                        texto_cor = "white"
                        grid_color = "#555555"
                    else:
                        fig.patch.set_facecolor('white')
                        ax.set_facecolor('white')
                        texto_cor = "black"
                        grid_color = "#cccccc"

                    # Gráfico de barras com cores distintas
                    barras = ax.bar(range(len(contagem)), contagem.values, color=cores, edgecolor='white', linewidth=1.5)

                    # Adicionar valores no topo das barras para melhor visibilidade
                    ax.bar_label(barras, fmt='%d', color=texto_cor, fontsize=10, fontweight='bold')

                    # Remove os rótulos do eixo X (mantém legenda)
                    ax.set_xticks([])

                    # Títulos e layout moderno
                    ax.set_ylabel('Quantidade', color=texto_cor, fontsize=12, fontweight='bold')
                    ax.tick_params(axis='y', labelcolor=texto_cor, labelsize=10)
                    ax.grid(axis='y', color=grid_color, linestyle='--', linewidth=0.5, alpha=0.7)  # Grade sutil

                    # Legenda abaixo do gráfico, moderna
                    ax.legend(
                        barras, contagem.index,
                        loc='upper center', bbox_to_anchor=(0.5, -0.15),
                        ncol=2, frameon=False, labelcolor=texto_cor, fontsize=10
                    )

                    st.pyplot(fig)
                else:
                    st.bar_chart(contagem)
            else:
                st.info("Nenhum dado válido para esta coluna.")
            st.divider()