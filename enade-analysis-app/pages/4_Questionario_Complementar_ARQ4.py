import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
from pathlib import Path

from utils.header import show_logo
from utils.footer import show_footer
from utils.formatting import format_br_number, format_br_percentage
from utils.data_loader import load_conceito

st.set_page_config(layout="wide", page_title="Questionário Complementar ARQ4 - ENADE 2023")

# Estilo para alinhar tabelas à esquerda
st.markdown(
    """
    <style>
        [data-testid=\"stDataFrame\"] {text-align: left !important;}
        [data-testid=\"stDataFrame\"] > div {text-align: left !important;}
    </style>
""",
    unsafe_allow_html=True,
)

show_logo()

# -------------------------
# Configuração do Questionário Complementar (arq4)
# -------------------------

# Escala de resposta (contexto do usuário)
# 1..6: discordância/concordância (grau de concordância)
# 7: não ter elementos para avaliar (Não sei responder)
# 8: não pertinente ao curso (Não se aplica)

QE4_VARIABLES = [f"QE_I{i}" for i in range(27, 69)]  # QE_I27..QE_I68

# Texto para exibição por agrupamento (contexto do usuário)
EIXO_TEXTO = {
    "Organização Didático-Pedagógica": "Organização Didático-Pedagógica",
    "Infraestrutura": "Infraestrutura",
    "Oportunidades": "Oportunidades de ampliação da formação acadêmica e profissional",
}

# Mapeamento de rótulos para a escala 1..6, 7 e 8 (mesmo para todas as QE_Ixx do arq4)
QE4_SCALE_LABELS = {
    "1": "1 (Discordância total)",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6 (Concordância total)",
    "7": "7 (Não sei responder)",
    "8": "8 (Não se aplica)",
}

QE4_SCALE_ABBREV = {
    "1": "1-Discordo",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6-Concordo",
    "7": "7-Não sei",
    "8": "8-N/A",
}

# Como a página 3 usa dicionários por variável para ordenação,
# aqui criamos um dicionário por QE_Ixx para permitir ordenação consistente.
QE_VALUE_LABELS = {v: QE4_SCALE_LABELS for v in QE4_VARIABLES}
QE_ABBREVIATIONS = {v: QE4_SCALE_ABBREV for v in QE4_VARIABLES}


def abbreviate_response(var_name: str, full_text: str | None) -> str:
    if var_name not in QE_ABBREVIATIONS:
        return full_text
    if full_text is None or pd.isna(full_text):
        return full_text

    abbr_dict = QE_ABBREVIATIONS[var_name]

    # Reverte o mapeamento labels (texto -> chave numérica)
    labels_dict = QE_VALUE_LABELS.get(var_name, {})
    text_to_letter = {v: k for k, v in labels_dict.items()}
    key = text_to_letter.get(str(full_text).strip())
    if key is not None and str(key) in abbr_dict:
        return abbr_dict[str(key)]

    return full_text


def sort_responses(df: pd.DataFrame, column: str, var_name: str | None) -> pd.DataFrame:
    """Ordena respostas pela ordem da escala 1..8."""
    try:
        if var_name and var_name in QE_VALUE_LABELS:
            labels_dict = QE_VALUE_LABELS[var_name]
            text_to_letter = {v: k for k, v in labels_dict.items()}
            df = df.copy()
            df["_letter_order"] = df[column].map(text_to_letter)
            df = df.dropna(subset=["_letter_order"])
            if not df.empty:
                # letra_order é na prática o código ("1".."8"); ordena numericamente
                df["_letter_order"] = pd.to_numeric(df["_letter_order"], errors="coerce")
                df = df.sort_values("_letter_order").reset_index(drop=True)
                df = df.drop(columns=["_letter_order"])
                return df
    except Exception:
        pass
    return df.sort_values("count", ascending=False).reset_index(drop=True)


def build_question_file_index_arq4() -> dict[str, Path]:
    """Indexa quais arquivos de microdados contêm cada variável arq4 (QE_I27..QE_I68)."""
    base = Path("enade-analysis-app/data")
    files = sorted(base.glob("microdados2023_arq*.txt"))
    index = {}

    wanted = set(QE4_VARIABLES)
    for f in files:
        df0 = pd.read_csv(f, sep=";", encoding="latin1", nrows=0)
        for col in df0.columns:
            if col in wanted:
                index[col] = f

    return index


@st.cache_data(ttl=600)
def load_question_df_arq4(col: str) -> pd.DataFrame:
    index = build_question_file_index_arq4()
    if col not in index:
        raise KeyError(f"Coluna {col} não encontrada nos arquivos de microdados")

    df = pd.read_csv(index[col], sep=";", encoding="latin1", usecols=["NU_ANO", "CO_CURSO", col])

    # Mapeia códigos numéricos (1..8) para labels
    mapping = QE4_SCALE_LABELS

    def _map(v):
        if pd.isna(v):
            return v
        if isinstance(v, float) and v.is_integer():
            key = str(int(v))
        else:
            key = str(v).strip()
        return mapping.get(key, key)

    df[col] = df[col].apply(_map)
    return df


def get_filtered_df(conceito_df: pd.DataFrame, uf=None, municipio=None, ies=None, curso=None, modalidade=None, categoria=None, grau=None):
    def safe_tuple(val):
        if val is None or val == []:
            return tuple()
        return tuple(val) if hasattr(val, "__iter__") else (val,)

    uf = safe_tuple(uf)
    municipio = safe_tuple(municipio)
    ies = safe_tuple(ies)
    curso = safe_tuple(curso)
    modalidade = safe_tuple(modalidade)
    categoria = safe_tuple(categoria)
    grau = safe_tuple(grau)

    filtered = conceito_df.copy()
    if len(uf) > 0:
        filtered = filtered[filtered['Sigla da UF** '].isin(uf)]
    if len(municipio) > 0:
        filtered = filtered[filtered['Município do Curso**'].isin(municipio)]
    if len(ies) > 0:
        filtered = filtered[filtered['Nome da IES*'].isin(ies)]
    if len(curso) > 0:
        filtered = filtered[filtered['Área de Avaliação'].isin(curso)]
    if len(modalidade) > 0:
        filtered = filtered[filtered['Modalidade de Ensino'].isin(modalidade)]
    if len(categoria) > 0:
        filtered = filtered[filtered['Categoria Administrativa'].isin(categoria)]
    if len(grau) > 0:
        filtered = filtered[filtered['Grau Acadêmico'].isin(grau)]
    return filtered


# -------------------------
# UI
# -------------------------

st.markdown("# 📘 Questionário Complementar (arq4) - Avaliação do Processo Formativo")
st.markdown(
    """
Este painel compila respostas do **questionário complementar do ENADE 2023 (arq4)**, especificamente as assertivas **QE_I27 a QE_I68**, que avaliam o **processo formativo**.

**Legenda (escala de concordância):**
- 1..6: grau de concordância (1 = discordância total, 6 = concordância total)
- 7: não ter elementos para avaliar (**Não sei responder**)
- 8: não pertinente ao curso (**Não se aplica**)

A análise permite filtrar por curso/IES e relacionar a distribuição das respostas com o **Conceito Enade (Contínuo)**.
"""
)

conceito_df = load_conceito()

index = build_question_file_index_arq4()
available_vars = [v for v in QE4_VARIABLES if v in index]
if not available_vars:
    st.warning("Nenhuma variável QE_I27..QE_I68 encontrada nos arquivos de microdados. Verifique os nomes das colunas nos microdados.")
    st.stop()

# Labels textuais das assertivas (substitui o placeholder “QE_Ixx ...”) 
QE4_ASSERTIVE_TEXT = {
    "QE_I27": "As disciplinas cursadas contribuíram para sua formação integral, como cidadão e profissional.",
    "QE_I28": "Os conteúdos abordados nas disciplinas do curso favoreceram sua atuação em estágios ou em atividades de iniciação profissional.",
    "QE_I29": "As metodologias de ensino utilizadas no curso desafiaram você a aprofundar conhecimentos e desenvolver competências reflexivas e críticas.",
    "QE_I30": "O curso propiciou experiências de aprendizagem inovadoras.",
    "QE_I31": "O curso contribuiu para o desenvolvimento da sua consciência ética para o exercício profissional.",
    "QE_I32": "No curso você teve oportunidade de aprender a trabalhar em equipe.",
    "QE_I33": "O curso possibilitou aumentar sua capacidade de reflexão e argumentação.",
    "QE_I34": "O curso promoveu o desenvolvimento da sua capacidade de pensar criticamente, analisar e refletir sobre soluções para problemas da sociedade.",
    "QE_I35": "O curso contribuiu para você ampliar sua capacidade de comunicação nas formas oral e escrita.",
    "QE_I36": "O curso contribuiu para o desenvolvimento da sua capacidade de aprender e atualizar-se permanentemente.",
    "QE_I37": "As relações professor-aluno ao longo do curso estimularam você a estudar e aprender.",
    "QE_I38": "Os planos de ensino apresentados pelos professores contribuíram para o desenvolvimento das atividades acadêmicas e para seus estudos.",
    "QE_I39": "As referências bibliográficas indicadas pelos professores nos planos de ensino contribuíram para seus estudos e aprendizagens.",
    "QE_I40": "Foram oferecidas oportunidades para os estudantes superarem dificuldades relacionadas ao processo de formação.",
    "QE_I41": "A coordenação do curso esteve disponível para orientação acadêmica dos estudantes.",
    "QE_I42": "O curso exigiu de você organização e dedicação frequente aos estudos.",
    "QE_I43": "Foram oferecidas oportunidades para os estudantes participarem de programas, projetos ou atividades de extensão universitária.",
    "QE_I44": "Foram oferecidas oportunidades para os estudantes participarem de projetos de iniciação científica e de atividades que estimularam a investigação acadêmica.",
    "QE_I45": "O curso ofereceu condições para os estudantes participarem de eventos internos e/ou externos à instituição.",
    "QE_I46": "A instituição ofereceu oportunidades para os estudantes atuarem como representantes em órgãos colegiados.",
    "QE_I47": "O curso favoreceu a articulação do conhecimento teórico com atividades práticas.",
    "QE_I48": "As atividades práticas foram suficientes para relacionar os conteúdos do curso com a prática, contribuindo para sua formação profissional.",
    "QE_I49": "O curso propiciou acesso a conhecimentos atualizados e/ou contemporâneos em sua área de formação.",
    "QE_I50": "O estágio supervisionado proporcionou experiências diversificadas para a sua formação.",
    "QE_I51": "As atividades realizadas durante seu trabalho de conclusão de curso contribuíram para qualificar sua formação profissional.",
    "QE_I52": "Foram oferecidas oportunidades para os estudantes realizarem intercâmbios e/ou estágios no país.",
    "QE_I53": "Foram oferecidas oportunidades para os estudantes realizarem intercâmbios e/ou estágios fora do país.",
    "QE_I54": "Os estudantes participaram de avaliações periódicas do curso (disciplinas, atuação dos professores, infraestrutura).",
    "QE_I55": "As avaliações de aprendizagem realizadas durante o curso foram compatíveis com os conteúdos ou temas trabalhados pelos professores.",
    "QE_I56": "Os professores apresentaram disponibilidade para atender os estudantes fora do horário das aulas.",
    "QE_I57": "Os professores demonstraram domínio dos conteúdos abordados nas disciplinas.",
    "QE_I58": "Os professores utilizaram tecnologias da informação e comunicação (TIC's) como estratégia de ensino (projetor, multimídia, laboratório de informática, ambiente virtual de aprendizagem).",
    "QE_I59": "A instituição dispôs de quantidade suficiente de funcionários para o apoio administrativo e acadêmico.",
    "QE_I60": "O curso disponibilizou monitores ou tutores para auxiliar os estudantes.",
    "QE_I61": "As condições de infraestrutura das salas de aula foram adequadas.",
    "QE_I62": "Os equipamentos e materiais disponíveis para as aulas práticas foram adequados para a quantidade de estudantes.",
    "QE_I63": "Os ambientes e equipamentos destinados às aulas práticas foram adequados ao curso.",
    "QE_I64": "A biblioteca dispôs das referências bibliográficas que os estudantes necessitaram.",
    "QE_I65": "A instituição contou com biblioteca virtual ou conferiu acesso a obras disponíveis em acervos virtuais.",
    "QE_I66": "As atividades acadêmicas desenvolvidas dentro e fora da sala de aula possibilitaram reflexão, convivência e respeito à diversidade.",
    "QE_I67": "A instituição promoveu atividades de cultura, de lazer e de interação social.",
    "QE_I68": "A instituição dispôs de refeitório, cantina e banheiros em condições adequadas que atenderam as necessidades dos seus usuários.",
}

selected_var = st.selectbox(
    "Selecione a assertiva (QE):",
    options=available_vars,
    format_func=lambda v: f"{v} - {QE4_ASSERTIVE_TEXT.get(v, '')}".strip(),
)


micro_q = load_question_df_arq4(selected_var)

# Toggle filtros comparativos
col_insts, _ = st.columns([1, 3])
with col_insts:
    enable_comparison = st.toggle("**Comparação Interinstitucional**", key="toggle_comparison_arq4")
    chart_type = st.radio(
        "Tipo de gráfico",
        options=["Linha", "Barras"],
        index=0,
        horizontal=True,
        key="toggle_chart_type_arq4",
    )

col1, col2 = st.columns(2)

with col1:
    st.markdown("### **1ª Instituição**")

    col1a, col1b, col1c, col1d = st.columns(4)
    with col1a:
        ufs_options1 = sorted(
            get_filtered_df(
                conceito_df,
                None,
                st.session_state.get('selected_municipios', []),
                st.session_state.get('selected_ies', []),
                st.session_state.get('selected_areas', []),
                st.session_state.get('selected_modalidades', []),
                st.session_state.get('selected_categorias', []),
                st.session_state.get('selected_graus', []),
            )["Sigla da UF** "].dropna().unique()
        )
        selected_uf = st.multiselect("UF", options=ufs_options1, key='uf1_arq4')

    with col1b:
        municipios_options1 = sorted(
            get_filtered_df(
                conceito_df,
                selected_uf,
                None,
                st.session_state.get('selected_ies', []),
                st.session_state.get('selected_areas', []),
                st.session_state.get('selected_modalidades', []),
                st.session_state.get('selected_categorias', []),
                st.session_state.get('selected_graus', []),
            )["Município do Curso**"].dropna().unique()
        )
        selected_municipio = st.multiselect("Município", options=municipios_options1, key='mun1_arq4')

    with col1c:
        ies_options1 = sorted(
            get_filtered_df(
                conceito_df,
                selected_uf,
                selected_municipio,
                None,
                st.session_state.get('selected_areas', []),
                st.session_state.get('selected_modalidades', []),
                st.session_state.get('selected_categorias', []),
                st.session_state.get('selected_graus', []),
            )["Nome da IES*"].dropna().unique()
        )
        selected_ies = st.multiselect("IES", options=ies_options1, key='ies1_arq4')

    with col1d:
        areas_options1 = sorted(
            get_filtered_df(
                conceito_df,
                selected_uf,
                selected_municipio,
                selected_ies,
                None,
                st.session_state.get('selected_modalidades', []),
                st.session_state.get('selected_categorias', []),
                st.session_state.get('selected_graus', []),
            )["Área de Avaliação"].dropna().unique()
        )
        selected_curso = st.multiselect("Curso", options=areas_options1, key='area1_arq4')

    col1e, col1f, col1g = st.columns(3)
    with col1e:
        modalidades_options1 = sorted(
            get_filtered_df(conceito_df, selected_uf, selected_municipio, selected_ies, selected_curso)["Modalidade de Ensino"].dropna().unique()
        )
        selected_modalidade = st.multiselect("Modalidade", options=modalidades_options1, key='mod1_arq4')

    with col1f:
        categorias_options1 = sorted(
            get_filtered_df(conceito_df, selected_uf, selected_municipio, selected_ies, selected_curso, selected_modalidade)["Categoria Administrativa"].dropna().unique()
        )
        selected_categoria = st.multiselect("Categoria", options=categorias_options1, key='cat1_arq4')

    with col1g:
        graus_options1 = sorted(
            get_filtered_df(conceito_df, selected_uf, selected_municipio, selected_ies, selected_curso, selected_modalidade, selected_categoria)["Grau Acadêmico"].dropna().unique()
        )
        selected_grau = st.multiselect("Grau", options=graus_options1, key='grau1_arq4')

if enable_comparison:
    with col2:
        st.markdown("### **2ª Instituição**")

        col2a, col2b, col2c, col2d = st.columns(4)
        with col2a:
            ufs_options2 = sorted(conceito_df["Sigla da UF** "].dropna().unique())
            selected_uf2 = st.multiselect("UF", options=ufs_options2, key='uf2_arq4')

        with col2b:
            municipios_options2 = sorted(conceito_df["Município do Curso**"].dropna().unique())
            selected_municipio2 = st.multiselect("Município", options=municipios_options2, key='mun2_arq4')

        with col2c:
            ies_options2 = sorted(conceito_df["Nome da IES*"].dropna().unique())
            selected_ies2 = st.multiselect("IES", options=ies_options2, key='ies2_arq4')

        with col2d:
            areas_options2 = sorted(conceito_df["Área de Avaliação"].dropna().unique())
            selected_curso2 = st.multiselect("Curso", options=areas_options2, key='area2_arq4')

        col2e, col2f, col2g = st.columns(3)
        with col2e:
            modalidades_options2 = sorted(conceito_df["Modalidade de Ensino"].dropna().unique())
            selected_modalidade2 = st.multiselect("Modalidade", options=modalidades_options2, key='mod2_arq4')

        with col2f:
            categorias_options2 = sorted(conceito_df["Categoria Administrativa"].dropna().unique())
            selected_categoria2 = st.multiselect("Categoria", options=categorias_options2, key='cat2_arq4')

        with col2g:
            graus_options2 = sorted(conceito_df["Grau Acadêmico"].dropna().unique())
            selected_grau2 = st.multiselect("Grau", options=graus_options2, key='grau2_arq4')

# -------------------------
# Aplicar filtros e fazer merge com micro_q
# -------------------------

st.markdown("---")

conceito_filtrado1 = conceito_df.copy()
if selected_uf:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1['Sigla da UF** '].isin(selected_uf)]
if selected_curso:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1['Área de Avaliação'].isin(selected_curso)]
if selected_modalidade:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1['Modalidade de Ensino'].isin(selected_modalidade)]
if selected_categoria:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1['Categoria Administrativa'].isin(selected_categoria)]
if selected_grau:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1['Grau Acadêmico'].isin(selected_grau)]
if selected_municipio:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1['Município do Curso**'].isin(selected_municipio)]
if selected_ies:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1['Nome da IES*'].isin(selected_ies)]

if conceito_filtrado1.empty:
    st.warning("Não há dados para os filtros selecionados na 1ª instituição.")
    st.stop()

merge_cols = ["NU_ANO", "CO_CURSO"]
left1 = conceito_filtrado1.rename(columns={"Ano": "NU_ANO", "Código do Curso": "CO_CURSO"})
merged1 = pd.merge(micro_q, left1, on=merge_cols, how="inner")

merged2 = pd.DataFrame()
if enable_comparison:
    conceito_filtrado2 = conceito_df.copy()
    if selected_uf2:
        conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2['Sigla da UF** '].isin(selected_uf2)]
    if selected_curso2:
        conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2['Área de Avaliação'].isin(selected_curso2)]
    if selected_modalidade2:
        conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2['Modalidade de Ensino'].isin(selected_modalidade2)]
    if selected_categoria2:
        conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2['Categoria Administrativa'].isin(selected_categoria2)]
    if selected_grau2:
        conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2['Grau Acadêmico'].isin(selected_grau2)]
    if selected_municipio2:
        conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2['Município do Curso**'].isin(selected_municipio2)]
    if selected_ies2:
        conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2['Nome da IES*'].isin(selected_ies2)]

    if conceito_filtrado2.empty:
        st.warning("Não há dados para os filtros selecionados na 2ª instituição.")
        enable_comparison = False
    else:
        left2 = conceito_filtrado2.rename(columns={"Ano": "NU_ANO", "Código do Curso": "CO_CURSO"})
        merged2 = pd.merge(micro_q, left2, on=merge_cols, how="inner")

# -------------------------
# Frequência e gráficos
# -------------------------

def compute_freq(df: pd.DataFrame, var: str):
    if df.empty:
        return None

    freq = df[var].value_counts(dropna=True).reset_index(name="count")
    freq = freq.rename(columns={freq.columns[0]: "Resposta"})
    freq["Resposta"] = freq["Resposta"].astype(str)
    freq["percent"] = (freq["count"] / freq["count"].sum()) * 100

    freq = sort_responses(freq, "Resposta", var)

    freq["percent_fmt"] = freq["percent"].map(format_br_percentage)
    freq["count_fmt"] = freq["count"].map(format_br_number)
    freq = freq.set_index("Resposta")
    return freq


if merged1.empty:
    st.warning("Não há dados microeconômicos para os filtros selecionados na 1ª instituição.")
    st.stop()

freq1 = compute_freq(merged1, selected_var)
if freq1 is None or freq1["count"].sum() == 0:
    st.warning("Nenhuma resposta encontrada para os filtros aplicados.")
    st.stop()

if enable_comparison and not merged2.empty:
    freq2 = compute_freq(merged2, selected_var)

    st.subheader(f"📊 Comparação Interinstitucional: {selected_var} (Processo formativo)")

    freq1_prep = freq1.reset_index()
    freq1_prep["Contagem"] = freq1_prep["count"].round(0)
    freq1_prep["Percentual"] = (freq1_prep["count"] / freq1_prep["count"].sum() * 100).round(2)
    freq1_prep["Instituicao"] = "Instituição 1"
    freq1_prep = freq1_prep.rename(columns={"Resposta": "Resposta_Completa"})

    freq2_prep = freq2.reset_index()
    freq2_prep["Contagem"] = freq2_prep["count"].round(0)
    freq2_prep["Percentual"] = (freq2_prep["count"] / freq2_prep["count"].sum() * 100).round(2)
    freq2_prep["Instituicao"] = "Instituição 2"
    freq2_prep = freq2_prep.rename(columns={"Resposta": "Resposta_Completa"})

    freq1_prep["Abreviacao"] = freq1_prep["Resposta_Completa"].apply(lambda x: abbreviate_response(selected_var, x))
    freq2_prep["Abreviacao"] = freq2_prep["Resposta_Completa"].apply(lambda x: abbreviate_response(selected_var, x))

    df_comparacao = pd.concat(
        [
            freq1_prep[["Abreviacao", "Contagem", "Percentual", "Instituicao", "Resposta_Completa"]],
            freq2_prep[["Abreviacao", "Contagem", "Percentual", "Instituicao", "Resposta_Completa"]],
        ],
        ignore_index=True,
    )

    # Ordenação do eixo X
    ordem = [QE4_SCALE_ABBREV[str(i)] for i in range(1, 9)]
    df_comparacao["Abreviacao"] = pd.Categorical(df_comparacao["Abreviacao"], categories=ordem, ordered=True)
    df_comparacao = df_comparacao.sort_values(["Abreviacao", "Instituicao"])

    if chart_type == "Barras":
        fig = px.bar(
            df_comparacao,
            x="Abreviacao",
            y="Percentual",
            color="Instituicao",
            barmode="group",
            custom_data=["Resposta_Completa", "Instituicao", "Percentual", "Contagem"],
        )
    else:
        fig = px.line(
            df_comparacao,
            x="Abreviacao",
            y="Percentual",
            color="Instituicao",
            markers=True,
            line_shape="linear",
            custom_data=["Resposta_Completa", "Instituicao", "Percentual", "Contagem"],
        )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Resposta (escala)",
        yaxis_title="Percentual (%)",
        height=600,
        legend=dict(orientation="h", x=0.99, xanchor="right", y=0.99, yanchor="top"),
    )

    fig.update_yaxes(ticksuffix="%")

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Instituição: %{customdata[1]}<br>Percentual: %{customdata[2]:.2f}%<br>Contagem: %{customdata[3]}<extra></extra>"
    )

    st.plotly_chart(fig, width="stretch")

    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        st.markdown("**Instituição 1**")
        st.dataframe(
            freq1.reset_index()[["Resposta", "count"]].rename(columns={"Resposta": "Resposta", "count": "Contagem"}),
            hide_index=True,
            width="stretch",
        )
    with col_tab2:
        st.markdown("**Instituição 2**")
        st.dataframe(
            freq2.reset_index()[["Resposta", "count"]].rename(columns={"Resposta": "Resposta", "count": "Contagem"}),
            hide_index=True,
            width="stretch",
        )

else:
    st.subheader(f"📊 Contagem de respostas: {selected_var} (Processo formativo)")

    freq_line = freq1.reset_index()

    freq_line["Abreviacao"] = freq_line["Resposta"].apply(lambda x: abbreviate_response(selected_var, x))
    ordem = [QE4_SCALE_ABBREV[str(i)] for i in range(1, 9)]
    freq_line["Abreviacao"] = pd.Categorical(freq_line["Abreviacao"], categories=ordem, ordered=True)

    freq_line["count_fmt"] = freq_line["count"].apply(lambda x: format_br_number(x, 0))
    freq_line["percent_fmt"] = freq_line["percent"].apply(lambda x: format_br_percentage(x))

    if chart_type == "Barras":
        fig = px.bar(
            freq_line,
            x="Abreviacao",
            y="percent",
            custom_data=["Resposta", "count_fmt", "percent_fmt"],
        )
    else:
        fig = px.line(
            freq_line,
            x="Abreviacao",
            y="percent",
            markers=True,
            line_shape="linear",
            custom_data=["Resposta", "count_fmt", "percent_fmt"],
        )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Resposta (escala)",
        yaxis_title="Percentual (%)",
        xaxis_tickangle=0,
        height=600,
    )

    fig.update_yaxes(ticksuffix="%")

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Contagem: %{customdata[1]}<br>Percentual: %{customdata[2]}<extra></extra>"
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("**Distribuição**")
    st.dataframe(
        freq_line[["Resposta", "Abreviacao", "count", "percent_fmt"]].rename(
            columns={"count": "Contagem", "percent_fmt": "%"}
        ),
        hide_index=True,
        width="stretch",
    )


show_footer(
    advisor_text="Orientador: Prof. Dr. César Candido Xavier • Email: cesarcx@gmail.com",
    advisor_link=("Currículo Lattes", "http://lattes.cnpq.br/2281060219061831"),
    text="Pesquisador: João Octavio Venâncio Borba • UNISO - Universidade de Sorocaba • Email: joaooctaviov.borba@gmail.com",
    links=[
        ("Github", "https://github.com/jaozes"),
        ("LinkedIn", "https://www.linkedin.com/in/jo%C3%A3o-octavio-vb/"),
        ("Currículo Lattes", "http://lattes.cnpq.br/0821075410761662"),
    ],
    bg_color="#ffffff",
    text_color="#000000",
    height_px=56,
    citation=(
        "Como citar: BORBA, J. O. V. ; XAVIER, C. C. Mapeando o desempenho e o perfil do estudante no Enade: "
        "uma plataforma interativa para comparações interinstitucionais. Sorocaba, SP, 2026. "
        "Disponível em: https://app-exploracao-enade2023.streamlit.app. Acesso em: [data de acesso]."
    ),
)

