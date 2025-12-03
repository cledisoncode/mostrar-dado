
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
        section[data-testid="stSidebar"] label p,
        section[data-testid="stSidebar"] div[role="radiogroup"] label span {{
            color: {sidebar_text_color} !important;
        }}
        h1, h2, h3, h4 {{
            color: {destaque} !important;
            font-weight: 700 !important;
        }}
        h2 {{
            font-size: 2.4em !important;  /* Aumenta o subheader */
            font-family: 'Segoe UI', sans-serif !important;  /* Mantém estilo profissional */
            letter-spacing: 0.5px !important;  /* Pequeno espaçamento entre letras */
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
        div[data-testid="stMetricValue"] {{
            font-size: 1.5em !important;
            font-weight: 800 !important;
            color: {destaque} !important;
        }}
        div[data-testid="stMetricLabel"] p {{
            font-size: 1.1em !important; 
            font-weight: 600 !important;
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
        div.stDownloadButton > button {{
            background-color: #16a34a !important;
            color: white !important;
            border: 2px solid #16a34a !important;
            border-radius: 10px !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            padding: 0.6em 1.4em !important;
            transition: all 0.2s ease-in-out !important;
        }}
        div.stDownloadButton > button:hover {{
            background-color: #22c55e!important;
            border-color: #22c55e !important;
            transform: translateY(-2px) !important;
        }}
        /* --- Ícone de alternância de tema --- */
        .theme-toggle {{
            position: absolute;
            top: 25px;
            right: 35px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 30px;
            transition: transform 0.2s ease, filter 0.2s ease;
        }}
        .theme-toggle:hover {{
            transform: scale(1.2);
            filter: brightness(1.3);
        }}
        
    </style>
""", unsafe_allow_html=True)

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

#-----------------------------------------------------------
def gerar_pdf_resumo(df):
    """
    Gera um PDF com: capa, explicações e todas as figuras da aba 'Estatísticas'
    (pirâmide etária, gráficos pizza, gráficos de barras e gráficos Likert).
    Retorna bytes do PDF.
    """
    from io import BytesIO
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from datetime import datetime
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    def fig_to_bytes(fig, dpi=150):
        """Salva figura Matplotlib em BytesIO e retorna o buffer pronto (cursor em 0)."""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', transparent=False)
        buf.seek(0)
        plt.close(fig)
        return buf

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name='TituloCapa', parent=estilos['Title'], alignment=1, fontSize=18, spaceAfter=12))
    estilos.add(ParagraphStyle(name='Subtitulo', parent=estilos['Heading2'], spaceAfter=8, fontSize=14))
    estilos.add(ParagraphStyle(name='Texto', parent=estilos['Normal'], fontSize=11, leading=14, spaceAfter=8))

    elementos = []

    # CAPA
    elementos.append(Paragraph("Mente Digital: Tecnoestresse e Bem-Estar no Uso de Tecnologias", estilos['TituloCapa']))
    elementos.append(Paragraph(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", estilos['Texto']))
    elementos.append(Spacer(1, 12))
    
     # ---- 1. INTRODUÇÃO ----
    elementos.append(Paragraph("1. Introdução", estilos['Subtitulo']))
    elementos.append(Paragraph(
        "O avanço das tecnologias digitais transformou profundamente as relações sociais, profissionais e educacionais. "
        "Embora essas ferramentas ampliem o acesso à informação e à comunicação, também geram novas formas de sobrecarga cognitiva e emocional. "
        "Nesse contexto, surge o conceito de tecnoestresse, definido como o conjunto de reações psicológicas negativas decorrentes do uso excessivo ou inadequado de dispositivos tecnológicos.", estilos['Texto']
    ))
    elementos.append(Paragraph(
        "O projeto Mente Digital: Tecnoestresse e Bem-Estar no Uso de Tecnologias tem como objetivo analisar como estudantes e trabalhadores estão reagindo ao ambiente digital contemporâneo, "
        "observando padrões de comportamento, percepções de estresse e hábitos de uso de tecnologia. "
        "A partir da coleta de dados e da análise estatística, busca-se compreender a relação entre variáveis demográficas e fatores de sobrecarga digital.", estilos['Texto']
    ))

    # ---- 2. FUNDAMENTAÇÃO TEÓRICA ----
    elementos.append(Paragraph("2. Fundamentação Teórica", estilos['Subtitulo']))
    elementos.append(Paragraph(
        "De acordo com estudos sobre saúde mental e tecnologias, o tecnoestresse manifesta-se em sintomas como ansiedade, irritabilidade, fadiga mental e dificuldade de concentração. "
        "Esses efeitos tendem a ser mais intensos em contextos de hiperconectividade, onde o indivíduo sente-se constantemente pressionado a responder, interagir e produzir conteúdo.", estilos['Texto']
    ))
    elementos.append(Paragraph(
        "A literatura aponta que a origem do tecnoestresse pode estar ligada a quatro dimensões principais:", estilos['Texto']
    ))
    elementos.append(Paragraph("<b>Sobrecarga de informação</b> — o excesso de dados e estímulos digitais;", estilos['Texto']))
    elementos.append(Paragraph("<b>Invasão tecnológica</b> — a dificuldade de desconectar-se;", estilos['Texto']))
    elementos.append(Paragraph("<b>Complexidade tecnológica</b> — a exigência de adaptação constante;", estilos['Texto']))
    elementos.append(Paragraph("<b>Insegurança tecnológica</b> — o medo de substituição ou inadequação profissional.", estilos['Texto']))
    elementos.append(Paragraph(
        "Com base nessas dimensões, o projeto Mente Digital propõe um estudo empírico sobre como esses fatores se manifestam em diferentes perfis de usuários.", estilos['Texto']
    ))

    # ---- 3. ANÁLISE DOS RESULTADOS ----
    elementos.append(Paragraph("3. Análise dos Resultados", estilos['Subtitulo']))
    elementos.append(Paragraph(
        "A seguir, são apresentados os gráficos e tabelas extraídos da base de dados do projeto. "
        "Eles permitem observar a distribuição das respostas por variáveis demográficas (gênero, idade, escolaridade, entre outras) "
        "e ajudam a identificar como grupos distintos percebem o impacto da tecnologia em seu bem-estar.", estilos['Texto']
    ))
    elementos.append(Paragraph(
        "Cada visualização é acompanhada de um breve comentário analítico, interpretando tendências relevantes. "
        "Essas interpretações contribuem para relacionar os dados quantitativos com a discussão teórica apresentada anteriormente.", estilos['Texto']
    ))


    # --- 1) PIRÂMIDE ETÁRIA ---
    try:
        df_limpo = df.copy()
        # Tentativa de detectar colunas de idade/gênero (mesma lógica do streamlit)
        coluna_idade = next((c for c in df_limpo.columns if c.lower() == "idade"), None)
        coluna_genero = None
        for g in ["gênero", "genero"]:
            if g in df_limpo.columns:
                coluna_genero = g
                break

        if coluna_idade and coluna_genero:
            df_valid = df_limpo[[coluna_genero, coluna_idade]].dropna()
            df_valid = df_valid[df_valid[coluna_idade].apply(lambda x: str(x).isdigit())]
            df_valid[coluna_idade] = df_valid[coluna_idade].astype(int)

            # Criar bins de 10 em 10 anos (garantindo pelo menos um bin)
            min_age = df_valid[coluna_idade].min()
            max_age = df_valid[coluna_idade].max()
            start = 10 * (min_age // 10)
            end = 10 * ((max_age // 10) + 1)
            bins = list(range(start, end + 1, 10))
            if len(bins) < 2:
                bins = [start, start + 10]
            df_valid["faixa_etaria"] = pd.cut(df_valid[coluna_idade], bins=bins, right=False).astype(str)
            tabela = df_valid.groupby(["faixa_etaria", coluna_genero]).size().unstack(fill_value=0)
            tabela = tabela[~tabela.index.str.contains("nan", case=False, na=False)]

            if not tabela.empty and tabela.shape[1] >= 2:
                tabela_perc = tabela.div(tabela.sum(axis=1), axis=0) * 100
                tabela_perc = tabela_perc.iloc[::-1]
                generos = tabela_perc.columns.tolist()
                genero1, genero2 = generos[:2]
                lado_esq = tabela_perc[genero1] * -1
                lado_dir = tabela_perc[genero2]

                # Plot
                fig, ax = plt.subplots(figsize=(8, 6))
                y = np.arange(len(tabela_perc))
                ax.barh(y, lado_esq, color="#6baed6", label=str(genero1))
                ax.barh(y, lado_dir, color="#fd8d3c", label=str(genero2))
                ax.set_yticks(y)
                ax.set_yticklabels(tabela_perc.index)
                ax.set_xlabel("Porcentagem (%)")
                ax.set_title("Pirâmide Etária por Gênero")
                ax.axvline(0, color="gray", linewidth=0.8)
                # limitar de acordo com máximo real (mas manter simetria até 100)
                max_val = max(lado_esq.abs().max(), lado_dir.max())
                lim = max(100, np.ceil(max_val / 10) * 10)
                ax.set_xlim(-lim, lim)
                ax.legend(loc="lower right")
                plt.tight_layout()

                # Inserir no PDF
                elementos.append(Paragraph("Pirâmide Etária (Gênero × Idade)", estilos['Subtitulo']))
                img_buf = fig_to_bytes(fig, dpi=150)
                img = Image(img_buf, width=6.5*inch, height=4.5*inch)
                elementos.append(img)
                elementos.append(Spacer(1, 12))
            else:
                elementos.append(Paragraph("Pirâmide Etária: dados insuficientes para gerar o gráfico.", estilos['Texto']))
    except Exception as e:
        elementos.append(Paragraph(f"Erro ao gerar pirâmide etária: {e}", estilos['Texto']))

    elementos.append(PageBreak())

    # --- 2) GRÁFICOS AUTOMÁTICOS: PIZZA E BARRAS ---
    try:

        campos_mostrar = [
            "raça", "raca",
            "grau de escolaridade", "estado civil",
            "situação atual de trabalho", "situacao atual de trabalho",
            "área de atuação", "area de atuação", "area de atuacao"
        ]

        # Varre colunas e gera figuras compatíveis
        for col in df_limpo.columns:
            col_lower = col.lower()
            if col_lower.startswith("p"):
                continue
            if any(chave in col_lower for chave in campos_mostrar):
                contagem = df_limpo[col].value_counts()
                contagem = contagem[contagem.index.astype(str).str.strip() != '']

                titulo = col.capitalize().strip()
                if contagem.empty:
                    # pula ou coloca aviso
                    elementos.append(Paragraph(f"{titulo}: nenhum dado válido.", estilos['Texto']))
                    elementos.append(Spacer(1, 8))
                    continue

                # Pizza para raça / estado civil
                if any(pie_field in col_lower for pie_field in ["estado civil", "raça", "raca"]):
                    fig, ax = plt.subplots(figsize=(7, 4))
                    cores = plt.cm.Set3.colors[:len(contagem)]

                    # --- Calcula porcentagens ---
                    percentages = (contagem.values / contagem.values.sum()) * 100

                    wedges, texts, autotexts = ax.pie(
                        contagem.values,
                        autopct='%1.1f%%',
                        colors=cores,
                        startangle=90,
                        radius=0.9,
                        pctdistance=0.75,
                        labeldistance=1.05,
                        textprops={'fontsize': 9},
                        wedgeprops={'edgecolor': 'white', 'linewidth': 1}
                    )

                    ax.axis('equal')

                    # --- Monta legenda com porcentagem ---
                    legend_labels = [
                        f"{str(label).capitalize()} – {percentages[i]:.1f}%"
                        for i, label in enumerate(contagem.index)
                    ]

                    ax.legend(
                        wedges,
                        legend_labels,
                        loc="center left",
                        bbox_to_anchor=(1, 0, 0.4, 1),
                        fontsize=8
                    )

                    plt.tight_layout()
                    elementos.append(Paragraph(titulo, estilos['Subtitulo']))
                    img_buf = fig_to_bytes(fig, dpi=150)
                    img = Image(img_buf, width=6.5*inch, height=3.8*inch)
                    elementos.append(img)
                    elementos.append(Spacer(1, 10))


                # Barras para escolaridade / área / situação de trabalho
                elif any(bar_field in col_lower for bar_field in [
                    "grau de escolaridade", "área de atuação", "area de atuação", "area de atuacao",
                    "situação atual de trabalho", "situacao atual de trabalho"
                ]):
                    fig, ax = plt.subplots(figsize=(8, 4.5))
                    cores = plt.cm.tab20.colors[:len(contagem)]
                    barras = ax.bar(range(len(contagem)), contagem.values, color=cores, edgecolor='white', linewidth=1)
                    ax.bar_label(barras, fmt='%d', fontsize=9)
                    ax.set_xticks([])
                    ax.set_ylabel('Quantidade')
                    ax.legend(barras, [str(x) for x in contagem.index], loc='upper center',
                              bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=10, frameon=False)
                    ax.grid(axis='y', linestyle='--', alpha=0.5)
                    plt.tight_layout()
                    elementos.append(Paragraph(titulo, estilos['Subtitulo']))
                    img_buf = fig_to_bytes(fig, dpi=150)
                    img = Image(img_buf, width=6.5*inch, height=3.8*inch)
                    elementos.append(img)
                    elementos.append(Spacer(1, 10))

                else:
                    # fallback: tabela simples com counts
                    data = [["Categoria", "Quantidade"]]
                    for idx, val in contagem.items():
                        data.append([str(idx), int(val)])
                    t = Table(data, hAlign='LEFT')
                    elementos.append(Paragraph(titulo, estilos['Subtitulo']))
                    elementos.append(t)
                    elementos.append(Spacer(1, 8))

        elementos.append(PageBreak())
    except Exception as e:
        elementos.append(Paragraph(f"Erro ao gerar gráficos automáticos: {e}", estilos['Texto']))
        elementos.append(PageBreak())

    # --- 3) ESCALAS LIKERT (todas as dimensões) ---
    try:
        elementos.append(Paragraph("Escalas Likert — Todas as Dimensões", estilos['Subtitulo']))
        elementos.append(Spacer(1, 8))

        dimensoes = {
            "DIMENSÃO I — DESCRIÇÃO": ["P1", "P2", "P3", "P4"],
            "DIMENSÃO II — FADIGA": ["P5", "P6", "P7", "P8"],
            "DIMENSÃO III — ANSIEDADE": ["P9", "P10", "P11", "P12"],
            "DIMENSÃO IV — INEFICÁCIA": ["P13", "P14", "P15", "P16"]
        }

        categorias = [
            "Nada", "Quase nada", "Raramente",
            "Algumas vezes", "Bastante",
            "Com frequência", "Sempre"
        ]

        cores = [
            "#d73027", "#fc8d59", "#fee08b",
            "#ffffbf", "#d9ef8b", "#91cf60", "#1a9850"
        ]

        def grafico_likert_dimensao_para_fig(df_local, perguntas, titulo_dim):
            # localiza colunas por pergunta (mesma lógica)
            colunas_encontradas = []
            nomes_legiveis = []
            for pergunta in perguntas:
                for col in df_local.columns:
                    if pergunta.lower() in col.lower():
                        colunas_encontradas.append(col)
                        nomes_legiveis.append(pergunta)
                        break
            if not colunas_encontradas:
                return None, f"Nenhuma pergunta encontrada para {titulo_dim}"

            df_dim = df_local[colunas_encontradas].copy()
            # normaliza/resgata valores
            for col in colunas_encontradas:
                df_dim[col] = df_dim[col].astype(str).str.strip().str.capitalize()
                df_dim[col] = df_dim[col].replace({
                    'Quase nada': 'Quase nada',
                    'Algumas vezes': 'Algumas vezes',
                    'Com frequencia': 'Com frequência',
                    'Com frequência': 'Com frequência',
                    '1': 'Nada',
                    '2': 'Quase nada',
                    '3': 'Raramente',
                    '4': 'Algumas vezes',
                    '5': 'Bastante',
                    '6': 'Com frequência',
                    '7': 'Sempre'
                })
            resumo_data = {}
            for i, col in enumerate(colunas_encontradas):
                contagem = df_dim[col].value_counts()
                for cat in categorias:
                    if cat not in contagem:
                        contagem[cat] = 0
                resumo_data[nomes_legiveis[i]] = contagem.reindex(categorias, fill_value=0)
            resumo_df = pd.DataFrame(resumo_data).fillna(0)
            if resumo_df.empty:
                return None, f"Nenhum dado válido para {titulo_dim}"

            totais_por_pergunta = resumo_df.sum(axis=0)
            max_respostas = max(totais_por_pergunta) if len(totais_por_pergunta) > 0 else 0
            limite_x = max(max_respostas * 1.2, 80)

            # desenha figura
            fig, ax = plt.subplots(figsize=(10, 6))
            left = np.zeros(len(resumo_df.columns))
            for i, categoria in enumerate(categorias):
                if categoria in resumo_df.index:
                    valores = resumo_df.loc[categoria].values
                    ax.barh(resumo_df.columns, valores, left=left, color=cores[i], label=categoria, height=0.6)
                    # labels
                    for j, valor in enumerate(valores):
                        if valor > 0:
                            ax.text(left[j] + valor/2, j, f'{int(valor)}', ha='center', va='center', fontsize=10, fontweight='bold')
                    left += valores
            ax.set_xlabel("Número de Respostas")
            ax.set_ylabel("Perguntas")
            ax.set_title(titulo_dim)
            ax.set_xlim(0, limite_x)
            ax.grid(axis='x', linestyle='--', alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
            plt.tight_layout()
            return fig, None

        # itera dimensões e insere a figura
        for nome_dim, perguntas in dimensoes.items():
            fig, erro = grafico_likert_dimensao_para_fig(df_limpo, perguntas, nome_dim)
            if erro:
                elementos.append(Paragraph(erro, estilos['Texto']))
                elementos.append(Spacer(1, 6))
            else:
                elementos.append(Paragraph(nome_dim, estilos['Subtitulo']))
                img_buf = fig_to_bytes(fig, dpi=150)
                img = Image(img_buf, width=6.5*inch, height=3.8*inch)
                elementos.append(img)
                elementos.append(Spacer(1, 8))

        elementos.append(PageBreak())
    except Exception as e:
        elementos.append(Paragraph(f"Erro ao gerar gráficos Likert: {e}", estilos['Texto']))
        elementos.append(PageBreak())

 # ---- 4. DISCUSSÃO ----
    elementos.append(Paragraph("4. Discussão", estilos['Subtitulo']))
    elementos.append(Paragraph(
        "Com base nos dados coletados, observa-se que o tecnoestresse não se limita a uma faixa etária específica, "
        "mas tende a ser mais percebido entre indivíduos com rotinas digitais intensas e menor domínio técnico sobre as ferramentas. "
        "A presença de sentimentos de exaustão digital e dificuldade de concentração foi recorrente em diferentes grupos.", estilos['Texto']
    ))
    elementos.append(Paragraph(
        "Esses resultados confirmam a hipótese de que o uso contínuo e pouco reflexivo de tecnologias pode impactar a saúde mental, "
        "reforçando a importância de programas educativos sobre o uso consciente e equilibrado das mídias digitais.", estilos['Texto']
    ))

    # ---- 5. CONCLUSÃO ----
    elementos.append(Paragraph("5. Conclusão", estilos['Subtitulo']))
    elementos.append(Paragraph(
        "O projeto Mente Digital reforça a relevância de se discutir o papel das tecnologias na qualidade de vida e na saúde emocional. "
        "O fenômeno do tecnoestresse emerge como uma consequência direta da hiperconectividade contemporânea, "
        "exigindo abordagens interdisciplinares que envolvam tecnologia, psicologia e educação digital.", estilos['Texto']
    ))
    elementos.append(Paragraph(
        "As análises aqui apresentadas demonstram a necessidade de promover ações de conscientização, oficinas de bem-estar digital e estratégias de regulação do uso tecnológico. "
        "Recomenda-se a continuidade da pesquisa com amostras maiores e aplicação de instrumentos psicométricos para aprofundar a compreensão das dimensões do tecnoestresse.", estilos['Texto']
    ))

    # Constrói o PDF
    doc.build(elementos)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


#----------------------------------------------------------

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

#  LIMPEZA DE NOMES DAS COLUNAS
df.columns = (
    df.columns.str.replace(r"\(.*?\)", "", regex=True)
            .str.replace("anos", "", case=False, regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
)

#  LIMPEZA E TRATAMENTO DE DADOS
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

elif menu == "Estatísticas":
    st.subheader("Estatísticas por Campo de Perfil")
    st.markdown("### Visualização Automática de Todas as Variáveis")
    st.info("Os gráficos abaixo são gerados automaticamente com base nos tipos de dados do conjunto.")

    # 🔹 PIRÂMIDE ETÁRIA (GÊNERO × IDADE) — COM PORCENTAGEM

    if "idade" in df_limpo.columns and any(col in df_limpo.columns for col in ["gênero", "genero"]):
        st.markdown("## Pirâmide Etária (Gênero × Idade)")

        coluna_genero = "gênero" if "gênero" in df_limpo.columns else "genero"
        coluna_idade = "idade"

        df_valid = df_limpo[[coluna_genero, coluna_idade]].dropna()
        df_valid = df_valid[df_valid[coluna_idade].apply(lambda x: str(x).isdigit())]
        df_valid[coluna_idade] = df_valid[coluna_idade].astype(int)

        # Criar faixas etárias padronizadas de 10 em 10 anos
        bins = list(range(10 * (df_valid[coluna_idade].min() // 10),
                          10 * ((df_valid[coluna_idade].max() // 10 + 1)), 10))
        df_valid["faixa_etaria"] = pd.cut(df_valid[coluna_idade], bins=bins, right=False)
        df_valid["faixa_etaria"] = df_valid["faixa_etaria"].astype(str)

        tabela = df_valid.groupby(["faixa_etaria", coluna_genero]).size().unstack(fill_value=0)

        # Remover faixas vazias ou 'nan'
        tabela = tabela[~tabela.index.str.contains("nan", case=False, na=False)]

        # Converter em porcentagem
        tabela_perc = tabela.div(tabela.sum(axis=1), axis=0) * 100

        # Ordenar da faixa etária mais velha (topo) para a mais nova (baixo)
        tabela_perc = tabela_perc.iloc[::-1]

        generos = tabela_perc.columns.tolist()

        if len(generos) < 2:
            st.info("Não há dados suficientes de ambos os gêneros para gerar a pirâmide etária.")
        else:
            genero1, genero2 = generos[:2]
            lado_esq = tabela_perc[genero1] * -1  # Negativo para espelhar
            lado_dir = tabela_perc[genero2]

            # Tema claro/escuro
            if st.session_state.tema == "escuro":
                fundo = "#0E1117"
                texto_cor = "white"
            else:
                fundo = "white"
                texto_cor = "black"

            # Plotar pirâmide percentual
            fig, ax = plt.subplots(figsize=(8, 6))
            y = np.arange(len(tabela_perc))
            ax.barh(y, lado_esq, color="#6baed6", label=genero1)
            ax.barh(y, lado_dir, color="#fd8d3c", label=genero2)

            ax.set_yticks(y)
            ax.set_yticklabels(tabela_perc.index, color=texto_cor)
            ax.set_xlabel("Porcentagem (%)", color=texto_cor)
            ax.set_title("Pirâmide Etária por Gênero", color=texto_cor, fontsize=13, fontweight="bold")

            # Linhas de referência e estilo
            ax.axvline(0, color="gray", linewidth=0.8)
            ax.set_xlim(-100, 100)  # Escala simétrica
            ax.legend(loc="lower right", labelcolor=texto_cor)
            ax.set_facecolor(fundo)
            fig.patch.set_facecolor(fundo)
            ax.tick_params(colors=texto_cor)
            plt.tight_layout()

            st.pyplot(fig)
        st.divider()

    #  OUTROS GRÁFICOS (AUTOMÁTICOS)
    campos_mostrar = [
        "raça", "raca",
        "grau de escolaridade", "estado civil",
        "situação atual de trabalho", "situacao atual de trabalho",
        "área de atuação", "area de atuação", "area de atuacao"
    ]

    for col in df_limpo.columns:
        col_lower = col.lower()
        if col_lower.startswith("p"): 
            continue
        if any(chave in col_lower for chave in campos_mostrar):
            titulo = col.capitalize().strip()
            st.markdown(f"#### {titulo}")
            
            contagem = df_limpo[col].value_counts()
            contagem = contagem[contagem.index.astype(str).str.strip() != '']

            if not contagem.empty:
                # --- GRÁFICO DE PIZZA PARA ESTADO CIVIL E RAÇA ---
                if any(pie_field in col_lower for pie_field in ["estado civil", "raça", "raca"]):
                    cores = plt.cm.Set3.colors[:len(contagem)]
                    legend_labels = [str(idx).capitalize() for idx in contagem.index]
                    fig, ax = plt.subplots(figsize=(7, 4))

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

                    if st.session_state.tema == "escuro":
                        fig.patch.set_facecolor("#0E1117")
                        ax.set_facecolor("#0E1117")
                        legend_color = "white"
                    else:
                        fig.patch.set_facecolor("white")
                        ax.set_facecolor("white")
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

                # --- GRÁFICO DE BARRAS PARA ESCOLARIDADE, ÁREA DE ATUAÇÃO, TRABALHO ---
                elif any(bar_field in col_lower for bar_field in [
                    "grau de escolaridade", "área de atuação", "area de atuação", "area de atuacao",
                    "situação atual de trabalho", "situacao atual de trabalho"
                ]):
                    fig, ax = plt.subplots(figsize=(8, 5))
                    cores = plt.cm.tab20.colors[:len(contagem)]

                    if st.session_state.tema == "escuro":
                        fig.patch.set_facecolor("#0E1117")
                        ax.set_facecolor("#0E1117")
                        texto_cor = "white"
                        grid_color = "#555555"
                    else:
                        fig.patch.set_facecolor("white")
                        ax.set_facecolor("white")
                        texto_cor = "black"
                        grid_color = "#cccccc"

                    barras = ax.bar(range(len(contagem)), contagem.values, color=cores, edgecolor='white', linewidth=1.5)
                    ax.bar_label(barras, fmt='%d', color=texto_cor, fontsize=10, fontweight='bold')
                    ax.set_xticks([])
                    ax.set_ylabel('Quantidade', color=texto_cor, fontsize=12, fontweight='bold')
                    ax.tick_params(axis='y', labelcolor=texto_cor, labelsize=10)
                    ax.grid(axis='y', color=grid_color, linestyle='--', linewidth=0.5, alpha=0.7)
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
         
    # GRÁFICO DE ESCALA LIKERT — TODAS AS DIMENSÕES
    st.markdown("## Escalas Likert — Todas as Dimensões")

    # Mapeamento das perguntas por dimensão
    dimensoes = {
        "DIMENSÃO I — DESCRIÇÃO": ["P1", "P2", "P3", "P4"],
        "DIMENSÃO II — FADIGA": ["P5", "P6", "P7", "P8"],
        "DIMENSÃO III — ANSIEDADE": ["P9", "P10", "P11", "P12"],
        "DIMENSÃO IV — INEFICÁCIA": ["P13", "P14", "P15", "P16"]
    }

    # Categorias da escala Likert (ordem lógica)
    categorias = [
        "Nada", "Quase nada", "Raramente",
        "Algumas vezes", "Bastante",
        "Com frequência", "Sempre"
    ]

    # Cores de gradiente suave
    cores = [
        "#d73027", "#fc8d59", "#fee08b",
        "#ffffbf", "#d9ef8b", "#91cf60", "#1a9850"
    ]

    # Função para gerar gráfico por dimensão
    def grafico_likert_dimensao(df, perguntas, titulo):
        # Encontrar colunas que correspondem às perguntas
        colunas_encontradas = []
        nomes_legiveis = []
        
        for pergunta in perguntas:
            # Procura por colunas que contenham o código da pergunta
            for col in df.columns:
                if pergunta.lower() in col.lower():
                    colunas_encontradas.append(col)
                    # Cria um nome mais legível para o gráfico
                    nome_legivel = f"{pergunta}"
                    nomes_legiveis.append(nome_legivel)
                    break
        
        if len(colunas_encontradas) == 0:
            st.warning(f"Nenhuma pergunta encontrada para {titulo}.")
            return

        st.write(f"**{titulo}**")
        
        df_dim = df[colunas_encontradas].copy()

        # Normaliza respostas
        for col in colunas_encontradas:
            df_dim[col] = df_dim[col].astype(str).str.strip().str.capitalize()
            # Corrige variações comuns
            df_dim[col] = df_dim[col].replace({
                'Quase nada': 'Quase nada',
                'Algumas vezes': 'Algumas vezes', 
                'Com frequencia': 'Com frequência',
                'Com frequência': 'Com frequência',
                '1': 'Nada',
                '2': 'Quase nada', 
                '3': 'Raramente',
                '4': 'Algumas vezes',
                '5': 'Bastante',
                '6': 'Com frequência',
                '7': 'Sempre'
            })

        # Conta respostas por pergunta
        resumo_data = {}
        for i, col in enumerate(colunas_encontradas):
            contagem = df_dim[col].value_counts()
            # Garante que todas as categorias existam, mesmo com valor 0
            for cat in categorias:
                if cat not in contagem:
                    contagem[cat] = 0
            # Reordena conforme a escala Likert
            resumo_data[nomes_legiveis[i]] = contagem.reindex(categorias, fill_value=0)

        resumo_df = pd.DataFrame(resumo_data).fillna(0)
        
        if resumo_df.empty:
            st.info(f"Nenhum dado válido para {titulo}.")
            return

        # Calcula o máximo total para definir o limite do eixo X
        totais_por_pergunta = resumo_df.sum(axis=0)
        max_respostas = max(totais_por_pergunta) if len(totais_por_pergunta) > 0 else 0
        # Aumenta o limite em 20% para dar margem
        limite_x = max(max_respostas * 1.2, 80)  # Mínimo de 80 para garantir espaço

        # Cria gráfico de barras horizontais empilhadas
        fig, ax = plt.subplots(figsize=(12, 6))  # Aumentei o tamanho do gráfico
        left = np.zeros(len(resumo_df.columns))

        for i, categoria in enumerate(categorias):
            if categoria in resumo_df.index:
                valores = resumo_df.loc[categoria].values
                ax.barh(resumo_df.columns, valores, left=left, color=cores[i], label=categoria, height=0.7)
                
                # Adiciona labels nos valores (apenas se forem significativos)
                for j, valor in enumerate(valores):
                    if valor > 0:  # Só mostra label se tiver valor
                        ax.text(left[j] + valor/2, j, f'{int(valor)}', 
                            ha='center', va='center', fontweight='bold', fontsize=9)
                
                left += valores

        # Configurações do gráfico
        ax.set_xlabel("Número de Respostas", fontweight='bold', fontsize=12)
        ax.set_ylabel("Perguntas", fontweight='bold', fontsize=12)
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        
        # Define o limite do eixo X para garantir consistência entre dimensões
        ax.set_xlim(0, limite_x)
        
        # Grid para melhor leitura
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Tema escuro/claro
        tema_escuro = st.session_state.tema == "escuro"
        if tema_escuro:
            ax.set_facecolor("#0E1117")
            fig.patch.set_facecolor("#0E1117")
            ax.title.set_color("white")
            ax.tick_params(colors="white")
            ax.xaxis.label.set_color("white")
            ax.yaxis.label.set_color("white")
            ax.legend(facecolor="#0E1117", edgecolor="none", labelcolor="white", 
                    bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            # Cor do grid para tema escuro
            ax.grid(axis='x', alpha=0.2, linestyle='--', color='white')
        else:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            ax.grid(axis='x', alpha=0.3, linestyle='--', color='gray')

        plt.tight_layout()
        st.pyplot(fig)
        
        # Mostra estatísticas resumidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de respostas", int(totais_por_pergunta.sum()))
        with col2:
            st.metric("Média por pergunta", f"{totais_por_pergunta.mean():.1f}")
        with col3:
            st.metric("Pergunta com mais respostas", int(totais_por_pergunta.max()))

    # Gera um gráfico para cada dimensão
    for nome_dim, perguntas in dimensoes.items():
        grafico_likert_dimensao(df_limpo, perguntas, nome_dim)
        st.divider()
