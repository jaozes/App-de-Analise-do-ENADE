import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
from pathlib import Path
from utils.header import show_logo
from utils.footer import show_footer
from utils.header import inject_css

#inject_css()
show_logo()

st.set_page_config(layout="wide", page_title="Perfil Socioeconômico - ENADE 2023")

# Mapeamento das questões QE (texto para exibição)
QUESTION_METADATA = {
    "QE_I01": "Qual o seu estado civil?",
    "QE_I02": "Qual é a sua cor ou raça?",
    "QE_I03": "Qual a sua nacionalidade?",
    "QE_I04": "Até que etapa de escolarização seu pai concluiu?",
    "QE_I05": "Até que etapa de escolarização sua mãe concluiu?",
    "QE_I06": "Onde e com quem você mora atualmente?",
    "QE_I07": "Quantas pessoas da sua família moram com você?",
    "QE_I08": "Qual a renda total de sua família, incluindo seus rendimentos?",
    "QE_I09": "Qual alternativa melhor descreve sua situação financeira (incluindo bolsas)?",
    "QE_I10": "Qual alternativa melhor descreve sua situação de trabalho (exceto estágio ou bolsas)?",
    "QE_I11": "Que tipo de bolsa de estudos ou financiamento você recebeu?",
    "QE_I12": "Ao longo da sua trajetória acadêmica, você recebeu auxílio permanência?",
    "QE_I13": "Ao longo da sua trajetória acadêmica, você recebeu bolsa acadêmica?",
    "QE_I14": "Participou de programas/atividades curriculares no exterior?",
    "QE_I15": "Seu ingresso no curso se deu por ação afirmativa/inclusão social?",
    "QE_I16": "Em que unidade da Federação você concluiu o ensino médio?",
    "QE_I17": "Em que tipo de escola você cursou o ensino médio?",
    "QE_I18": "Qual modalidade de ensino médio você concluiu?",
    "QE_I19": "Quem lhe deu maior incentivo para cursar a graduação?",
    "QE_I20": "Algum grupo foi determinante para você enfrentar dificuldades e concluir o curso?",
    "QE_I21": "Alguém em sua família concluiu um curso superior?",
    "QE_I22": "Quantos livros você leu neste ano (excluindo bibliografia do curso)?",
    "QE_I23": "Quantas horas por semana você dedicou aos estudos (excluindo aulas)?",
    "QE_I24": "Você teve oportunidade de aprendizado de idioma estrangeiro na instituição?",
    "QE_I25": "Qual o principal motivo para você ter escolhido este curso?",
    "QE_I26": "Qual a principal razão para você ter escolhido sua instituição?",
}

# Variáveis adicionais (não são QE, mas estão em microdados)
EXTRA_VARS = {
    "TP_SEXO": "Sexo",
    "NU_IDADE": "Idade (anos)"
}

# Mapping de valores codificados para os QE_Ixx (dicionário íntegro fornecido pelo usuário)
# e também para algumas variáveis extras (TP_SEXO).
QE_VALUE_LABELS = {
    "TP_SEXO": {
        "M": "Masculino",
        "F": "Feminino",
        "9": "Indefinido",
    },
    "QE_I01": {
        "A": "Solteiro(a)",
        "B": "Casado(a)",
        "C": "Separado(a) judicialmente/divorciado(a)",
        "D": "Viúvo(a)",
        "E": "Outro(a)",
    },
    "QE_I02": {
        "A": "Branca",
        "B": "Preta",
        "C": "Amarela",
        "D": "Parda",
        "E": "Indígena",
        "F": "Não quero declarar",
    },
    "QE_I03": {
        "A": "Brasileira",
        "B": "Brasileira naturalizada",
        "C": "Estrangeira",
    },
    "QE_I04": {
        "A": "Nenhuma",
        "B": "Ensino Fundamental: 1ª a 5ª série",
        "C": "Ensino Fundamental: 6ª a 9ª série",
        "D": "Ensino Médio",
        "E": "Ensino Superior - Graduação",
        "F": "Pós-graduação",
    },
    "QE_I05": {
        "A": "Nenhuma",
        "B": "Ensino Fundamental: 1ª a 5ª ano",
        "C": "Ensino Fundamental: 6ª a 9ª ano",
        "D": "Ensino Médio",
        "E": "Ensino Superior - Graduação",
        "F": "Pós-graduação",
    },
    "QE_I06": {
        "A": "Em casa ou apartamento, sozinho",
        "B": "Em casa ou apartamento, com pais e/ou parentes",
        "C": "Em casa ou apartamento, com cônjuge e/ou filhos",
        "D": "Em casa ou apartamento, com outras pessoas (incluindo república)",
        "E": "Em alojamento universitário da própria instituição",
        "F": "Em outros tipos de habitação (hotel, hospedaria, pensão ou outro)",
    },
    "QE_I07": {
        "A": "Nenhuma pessoa.",
        "B": "Uma pessoa",
        "C": "Duas pessoas",
        "D": "Três pessoas",
        "E": "Quatro pessoas",
        "F": "Cinco pessoas",
        "G": "Seis pessoas",
        "H": "Sete ou mais pessoas",
    },
    "QE_I08": {
        "A": "Até 1,5 salário mínimo (até R$ 1.980,00)",
        "B": "De 1,5 a 3 salários mínimos (R$ 1.980,01 a R$ 3.960,00)",
        "C": "De 3,5 a 5 salários mínimos (R$ 3.960,01 a R$ 5.940,00)",
        "D": "De 5,5 a 6 salários mínimos (R$ 5.940,01 a R$ 7.920,00)",
        "E": "De 6 a 10 salários mínimos (R$ 7.920,01 a R$ 13.200,00)",
        "F": "De 10 a 30 salários mínimos (R$ 13.200,01 a R$ 39.600,00)",
        "G": "Acima de 30 salários mínimos (mais de R$ 39.600,00)",
    },
    "QE_I09": {
        "A": "Não tenho renda e meus gastos são financiados por programas governamentais",
        "B": "Não tenho renda e meus gastos são financiados pela família ou outras pessoas",
        "C": "Tenho renda, mas recebo ajuda de família/outros para financiar meus gastos",
        "D": "Tenho renda e não preciso de ajuda para financiar meus gastos",
        "E": "Tenho renda e contribuo com o sustento da família",
        "F": "Sou o principal responsável pelo sustento da família",
    },
    "QE_I10": {
        "A": "Não estou trabalhando",
        "B": "Trabalho eventual",
        "C": "Trabalho até 20 horas semanais",
        "D": "Trabalho de 21 a 39 horas semanais",
        "E": "Trabalho 40 horas semanais ou mais",
    },
    "QE_I11": {
        "A": "Nenhuma",
        "B": "ProUni integral",
        "C": "ProUni parcial",
        "D": "FIES apenas",
        "E": "ProUni parcial e FIES",
        "F": "FIES parcial",
        "G": "Bolsa oferecida por governo estadual/distrital/municipal",
        "H": "Bolsa oferecida pela própria instituição",
        "I": "Bolsa oferecida por outra entidade (empresa, ONG, outra)",
        "J": "Financiamento oferecido pela própria instituição",
        "K": "Financiamento bancário",
    },
    "QE_I12": {
        "A": "Nenhum",
        "B": "Auxílio moradia",
        "C": "Auxílio alimentação",
        "D": "Auxílio moradia e alimentação",
        "E": "Auxílio permanência",
        "F": "Outro tipo de auxílio",
    },
    "QE_I13": {
        "A": "Nenhum",
        "B": "Bolsa de iniciação científica",
        "C": "Bolsa de monitoria/tutoria",
        "D": "Bolsa PET",
        "E": "Outro tipo de bolsa acadêmica",
    },
    "QE_I14": {
        "A": "Não participei",
        "B": "Sim, Programa Ciência sem Fronteiras",
        "C": "Sim, programa de intercâmbio financiado pelo Governo Federal",
        "D": "Sim, programa de intercâmbio financiado pelo Governo Estadual",
        "E": "Sim, programa de intercâmbio da minha instituição",
        "F": "Sim, outro programa de intercâmbio",
    },
    "QE_I15": {
        "A": "Não",
        "B": "Sim, por critério étnico-racial",
        "C": "Sim, por critério de renda",
        "D": "Sim, por ter estudado em escola pública ou particular com bolsa",
        "E": "Sim, por sistema que combina dois ou mais critérios",
        "F": "Sim, por sistema diferente dos anteriores",
    },
    "QE_I16": {
        "11": "Rondônia (RO)",
        "12": "Acre (AC)",
        "13": "Amazonas (AM)",
        "14": "Roraima (RR)",
        "15": "Pará (PA)",
        "16": "Amapá (AP)",
        "17": "Tocantins (TO)",
        "21": "Maranhão (MA)",
        "22": "Piauí (PI)",
        "23": "Ceará (CE)",
        "24": "Rio Grande do Norte (RN)",
        "25": "Paraíba (PB)",
        "26": "Pernambuco (PE)",
        "27": "Alagoas (AL)",
        "28": "Sergipe (SE)",
        "29": "Bahia (BA)",
        "31": "Minas Gerais (MG)",
        "32": "Espírito Santo (ES)",
        "33": "Rio de Janeiro (RJ)",
        "35": "São Paulo (SP)",
        "41": "Paraná (PR)",
        "42": "Santa Catarina (SC)",
        "43": "Rio Grande do Sul (RS)",
        "50": "Mato Grosso do Sul (MS)",
        "51": "Mato Grosso (MT)",
        "52": "Goiás (GO)",
        "53": "Distrito Federal (DF)",
        "99": "Não se aplica",
    },
    "QE_I17": {
        "A": "Todo em escola pública",
        "B": "Todo em escola privada (particular)",
        "C": "Todo no exterior",
        "D": "Maioria em escola pública",
        "E": "Maioria em escola privada (particular)",
        "F": "Parte no Brasil e parte no exterior",
    },
    "QE_I18": {
        "A": "Ensino médio tradicional",
        "B": "Profissionalizante técnico (eletrônica, contabilidade, agrícola, outro)",
        "C": "Profissionalizante magistério (Curso Normal)",
        "D": "Educação de Jovens e Adultos (EJA) / Supletivo",
        "E": "Outra modalidade",
    },
    "QE_I19": {
        "A": "Ninguém",
        "B": "Pais",
        "C": "Outros membros da família (não pais)",
        "D": "Professores",
        "E": "Líder ou representante religioso",
        "F": "Colegas/Amigos",
        "G": "Outras pessoas",
    },
    "QE_I20": {
        "A": "Não tive dificuldade",
        "B": "Não recebi apoio",
        "C": "Pais",
        "D": "Avós",
        "E": "Irmãos/primos/tios",
        "F": "Líder ou representante religioso",
        "G": "Colegas de curso ou amigos",
        "H": "Professores do curso",
        "I": "Profissionais do serviço de apoio da IES",
        "J": "Colegas de trabalho",
        "K": "Outro grupo",
    },
    "QE_I21": {
        "A": "Sim",
        "B": "Não",
        "C": "Nenhum",
    },
    "QE_I22": {
        "A": "Nenhum",
        "B": "Um ou dois",
        "C": "De tres a cinco",
        "D": "De seis a oito",
        "E": "Mais de oito",
    },
    "QE_I23": {
        "A": "Nenhuma, apenas assisto às aulas",
        "B": "De uma a três horas",
        "C": "De quatro a sete horas",
        "D": "De oito a doze horas",
        "E": "De oito a doze horas",
    },
    "QE_I24": {
        "A": "Sim, somente presencial",
        "B": "Sim, somente semipresencial",
        "C": "Sim, parte presencial e parte semipresencial",
        "D": "Sim, modalidade a distância",
        "E": "Não",
    },
    "QE_I25": {
        "A": "Inserção no mercado de trabalho",
        "B": "Influência familiar",
        "C": "Valorização profissional",
        "D": "Prestígio social",
        "E": "Vocação",
        "F": "Oferecido na modalidade a distância",
        "G": "Baixa concorrência para ingresso",
        "H": "Outro motivo",
    },
    "QE_I26": {
        "A": "Gratuidade",
        "B": "Preço da mensalidade",
        "C": "Proximidade da minha residência",
        "D": "Proximidade do meu trabalho",
        "E": "Facilidade de acesso",
        "F": "Qualidade / reputação",
        "G": "Foi única onde tive aprovação",
        "H": "Possibilidade de ter bolsa de estudo",
        "I": "Outro motivo",
    },
}


def normalize_col(name: str) -> str:
    """Normaliza nomes de colunas para facilitar uso (remove acentos e espaços extras)."""
    return unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii").strip()


def format_br_number(value: float, decimal_places: int = 0) -> str:
    """Formata número para o padrão brasileiro (ponto para milhares, vírgula para decimal)."""
    if pd.isna(value):
        return ""
    if decimal_places == 0:
        return f"{int(value):,}".replace(",", ".")
    else:
        return f"{value:,.{decimal_places}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_br_percentage(value: float) -> str:
    """Formata percentual para o padrão brasileiro."""
    if pd.isna(value):
        return ""
    return f"{value:.2f}%".replace(".", ",")


from utils.data_loader import load_conceito


@st.cache_data(ttl=300)
def build_question_file_index() -> dict[str, Path]:
    """Indexa quais arquivos de microdados contêm cada variável (QE_Ixx / TP_SEXO / NU_IDADE)."""
    base = Path("enade-analysis-app/data")
    files = sorted(base.glob("microdados2023_arq*.txt"))
    index = {}
    for f in files:
        df0 = pd.read_csv(f, sep=";", encoding="latin1", nrows=0)
        for col in df0.columns:
            if col in QUESTION_METADATA or col in EXTRA_VARS:
                index[col] = f
    return index


@st.cache_data
def load_question_df(col: str) -> pd.DataFrame:
    """Carrega o arquivo de microdados que contém a coluna solicitada."""
    index = build_question_file_index()
    if col not in index:
        raise KeyError(f"Coluna {col} não encontrada nos arquivos de microdados")
    df = pd.read_csv(index[col], sep=";", encoding="latin1", usecols=["NU_ANO", "CO_CURSO", col])

    # Traduzir códigos para labels (quando houver dicionário disponível)
    if col in QE_VALUE_LABELS:
        mapping = QE_VALUE_LABELS[col]

        def _map(v):
            if pd.isna(v):
                return v
            # Normalizar para string (tratando floats que são inteiros)
            if isinstance(v, float) and v.is_integer():
                key = str(int(v))
            else:
                key = str(v).strip()
            return mapping.get(key, key)

        df[col] = df[col].apply(_map)

    return df


def summarize_question(df_q: pd.DataFrame, col: str) -> pd.DataFrame:
    """Agrega respostas por (Ano, Curso) retornando contagens e proporções."""
    df_q = df_q.dropna(subset=[col])
    # Se for numérico (como idade), calcular média
    if pd.api.types.is_numeric_dtype(df_q[col]):
        summary = df_q.groupby(["NU_ANO", "CO_CURSO"]).agg(
            total_respostas=(col, "count"),
            valor_medio=(col, "mean"),
            valor_mediana=(col, "median"),
        ).reset_index()
        return summary

    # Categórico: proporção por categoria
    counts = (
        df_q.groupby(["NU_ANO", "CO_CURSO", col])
        .size()
        .reset_index(name="count")
    )
    totals = (
        df_q.groupby(["NU_ANO", "CO_CURSO"]).size().reset_index(name="total")
    )
    merged = counts.merge(totals, on=["NU_ANO", "CO_CURSO"], how="left")
    merged["prop"] = merged["count"] / merged["total"]
    return merged


# --- Interface ---

st.markdown("# 📋 Perfil Socioeconômico dos Participantes")
st.markdown(
    """Esta página explora as respostas do questionário socioeconômico (microdados do ENADE 2023) e
    permite relacioná-las com o desempenho médio (Conceito Enade) por curso."""
)

# Carregar dados
conceito_df = load_conceito()

# Selecionar pergunta / variável
index = build_question_file_index()
available_vars = [var for var in list(QUESTION_METADATA.keys()) + list(EXTRA_VARS.keys()) if var in index]
if not available_vars:
    st.warning("Nenhuma coluna de perfil socioeconômico encontrada nos arquivos de microdados. Adicione os arquivos corretos ou verifique os nomes das colunas.")
    st.stop()
available_labels = {
    **{k: f"{k} — {QUESTION_METADATA[k]}" for k in QUESTION_METADATA},
    **{k: f"{k} — {EXTRA_VARS[k]}" for k in EXTRA_VARS},
}

pass

selected_var = st.selectbox(
    "Selecione a questão a ser veríficada:",
    options=available_vars,
    format_func=lambda v: available_labels.get(v, v),
)

# Carregar dados de microdados para a variável
micro_q = load_question_df(selected_var)

# Filtros baseados na planilha de conceito
col_uf = "Sigla da UF** "
col_area = "Área de Avaliação"
col_modalidade = "Modalidade de Ensino"
col_categoria = "Categoria Administrativa"
col_grau = "Grau Acadêmico"
col_municipio = "Município do Curso**"
col_ies_nome = "Nome da IES*"

# Função auxiliar para atualizar opções de filtro dinamicamente
def get_filtered_options(df, column, filters_dict=None):
    """Retorna opções disponíveis para um filtro baseado em outros filtros aplicados (exclui coluna atual)."""
    filtered_df = df.copy()
    
    if filters_dict:
        for filter_col, filter_values in filters_dict.items():
            if filter_col != column and filter_values:
                filtered_df = filtered_df[filtered_df[filter_col].isin(filter_values)]
    
    return sorted(filtered_df[column].dropna().unique())

# Inicializar estado dos filtros na sessão
if 'selected_ufs' not in st.session_state:
    st.session_state.selected_ufs = []
if 'selected_areas' not in st.session_state:
    st.session_state.selected_areas = []
if 'selected_modalidades' not in st.session_state:
    st.session_state.selected_modalidades = []
if 'selected_categorias' not in st.session_state:
    st.session_state.selected_categorias = []
if 'selected_graus' not in st.session_state:
    st.session_state.selected_graus = []
if 'selected_municipios' not in st.session_state:
    st.session_state.selected_municipios = []
if 'selected_ies' not in st.session_state:
    st.session_state.selected_ies = []

# Second institution session state
if 'selected_ufs2' not in st.session_state:
    st.session_state.selected_ufs2 = []
if 'selected_areas2' not in st.session_state:
    st.session_state.selected_areas2 = []
if 'selected_modalidades2' not in st.session_state:
    st.session_state.selected_modalidades2 = []
if 'selected_categorias2' not in st.session_state:
    st.session_state.selected_categorias2 = []
if 'selected_graus2' not in st.session_state:
    st.session_state.selected_graus2 = []
if 'selected_municipios2' not in st.session_state:
    st.session_state.selected_municipios2 = []
if 'selected_ies2' not in st.session_state:
    st.session_state.selected_ies2 = []

# Filtros em colunas com lógica em cascata
col_insts, _ = st.columns([1, 3])
with col_insts:
    enable_comparison = st.toggle("**Comparação Interinstitucional**", key="toggle_comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### **1ª Instituição**")
    # Filters dict for inst1 cascade
    filters_dict1 = {
        col_uf: st.session_state.selected_ufs,
        col_area: st.session_state.selected_areas,
        col_modalidade: st.session_state.selected_modalidades,
        col_categoria: st.session_state.selected_categorias,
        col_grau: st.session_state.selected_graus,
        col_municipio: st.session_state.selected_municipios,
        col_ies_nome: st.session_state.selected_ies,
    }

    col1a, col1b, col1c = st.columns(3)
    with col1a:
        ufs_options1 = get_filtered_options(conceito_df, col_uf, filters_dict1)
        st.session_state.selected_ufs = st.multiselect(
            "UF", 
            options=ufs_options1, 
            default=st.session_state.selected_ufs
        )
    with col1b:
        areas_options1 = get_filtered_options(conceito_df, col_area, filters_dict1)
        st.session_state.selected_areas = st.multiselect(
            "Área", 
            options=areas_options1, 
            default=st.session_state.selected_areas
        )
    with col1c:
        modalidades_options1 = get_filtered_options(conceito_df, col_modalidade, filters_dict1)
        st.session_state.selected_modalidades = st.multiselect(
            "Modalidade", 
            options=modalidades_options1, 
            default=st.session_state.selected_modalidades
        )

    col1d, col1e, col1f, col1g = st.columns([1,1,1,1.5])
    with col1d:
        categorias_options1 = get_filtered_options(conceito_df, col_categoria, filters_dict1)
        st.session_state.selected_categorias = st.multiselect(
            "Categoria Adm.", 
            options=categorias_options1, 
            default=st.session_state.selected_categorias
        )
    with col1e:
        graus_options1 = get_filtered_options(conceito_df, col_grau, filters_dict1)
        st.session_state.selected_graus = st.multiselect(
            "Grau", 
            options=graus_options1, 
            default=st.session_state.selected_graus
        )
    with col1f:
        municipios_options1 = get_filtered_options(conceito_df, col_municipio, filters_dict1)
        st.session_state.selected_municipios = st.multiselect(
            "Município", 
            options=municipios_options1, 
            default=st.session_state.selected_municipios
        )
    with col1g:
        ies_options1 = get_filtered_options(conceito_df, col_ies_nome, filters_dict1)
        st.session_state.selected_ies = st.multiselect(
            "IES", 
            options=ies_options1, 
            default=st.session_state.selected_ies
        )

if enable_comparison:
    with col2:
        st.markdown("### **2ª Instituição**")
        # Filters dict for inst2 cascade
        filters_dict2 = {
            col_uf: st.session_state.selected_ufs2,
            col_area: st.session_state.selected_areas2,
            col_modalidade: st.session_state.selected_modalidades2,
            col_categoria: st.session_state.selected_categorias2,
            col_grau: st.session_state.selected_graus2,
            col_municipio: st.session_state.selected_municipios2,
            col_ies_nome: st.session_state.selected_ies2,
        }
        
        col2a, col2b, col2c = st.columns(3)
        with col2a:
            ufs_options2 = get_filtered_options(conceito_df, col_uf, filters_dict2)
            st.session_state.selected_ufs2 = st.multiselect(
                "UF", key="uf2",
                options=ufs_options2, 
                default=st.session_state.selected_ufs2
            )
        with col2b:
            areas_options2 = get_filtered_options(conceito_df, col_area, filters_dict2)
            st.session_state.selected_areas2 = st.multiselect(
                "Área", key="area2",
                options=areas_options2, 
                default=st.session_state.selected_areas2
            )
        with col2c:
            modalidades_options2 = get_filtered_options(conceito_df, col_modalidade, filters_dict2)
            st.session_state.selected_modalidades2 = st.multiselect(
                "Modalidade", key="modal2",
                options=modalidades_options2, 
                default=st.session_state.selected_modalidades2
            )
        
        col2d, col2e, col2f, col2g = st.columns([1,1,1,1.5])
        with col2d:
            categorias_options2 = get_filtered_options(conceito_df, col_categoria, filters_dict2)
            st.session_state.selected_categorias2 = st.multiselect(
                "Categoria Adm.", key="cat2",
                options=categorias_options2, 
                default=st.session_state.selected_categorias2
            )
        with col2e:
            graus_options2 = get_filtered_options(conceito_df, col_grau, filters_dict2)
            st.session_state.selected_graus2 = st.multiselect(
                "Grau", key="grau2",
                options=graus_options2, 
                default=st.session_state.selected_graus2
            )
        with col2f:
            municipios_options2 = get_filtered_options(conceito_df, col_municipio, filters_dict2)
            st.session_state.selected_municipios2 = st.multiselect(
                "Município", key="mun2",
                options=municipios_options2, 
                default=st.session_state.selected_municipios2
            )
        with col2g:
            ies_options2 = get_filtered_options(conceito_df, col_ies_nome, filters_dict2)
            st.session_state.selected_ies2 = st.multiselect(
                "IES", key="ies2",
                options=ies_options2, 
                default=st.session_state.selected_ies2
            )

# Apply filters to both institutions
conceito_filtrado1 = conceito_df.copy()
if st.session_state.selected_ufs:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1[col_uf].isin(st.session_state.selected_ufs)]
if st.session_state.selected_areas:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1[col_area].isin(st.session_state.selected_areas)]
if st.session_state.selected_modalidades:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1[col_modalidade].isin(st.session_state.selected_modalidades)]
if st.session_state.selected_categorias:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1[col_categoria].isin(st.session_state.selected_categorias)]
if st.session_state.selected_graus:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1[col_grau].isin(st.session_state.selected_graus)]
if st.session_state.selected_municipios:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1[col_municipio].isin(st.session_state.selected_municipios)]
if st.session_state.selected_ies:
    conceito_filtrado1 = conceito_filtrado1[conceito_filtrado1[col_ies_nome].isin(st.session_state.selected_ies)]

# Second institution filters
conceito_filtrado2 = conceito_df.copy()
if st.session_state.selected_ufs2:
    conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2[col_uf].isin(st.session_state.selected_ufs2)]
if st.session_state.selected_areas2:
    conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2[col_area].isin(st.session_state.selected_areas2)]
if st.session_state.selected_modalidades2:
    conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2[col_modalidade].isin(st.session_state.selected_modalidades2)]
if st.session_state.selected_categorias2:
    conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2[col_categoria].isin(st.session_state.selected_categorias2)]
if st.session_state.selected_graus2:
    conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2[col_grau].isin(st.session_state.selected_graus2)]
if st.session_state.selected_municipios2:
    conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2[col_municipio].isin(st.session_state.selected_municipios2)]
if st.session_state.selected_ies2:
    conceito_filtrado2 = conceito_filtrado2[conceito_filtrado2[col_ies_nome].isin(st.session_state.selected_ies2)]

# Define institution names for both modes
nome_inst1 = st.session_state.selected_ies[0] if st.session_state.selected_ies and len(st.session_state.selected_ies) == 1 else "Instituição 1"
nome_inst2 = st.session_state.selected_ies2[0] if st.session_state.selected_ies2 and len(st.session_state.selected_ies2) == 1 else "Instituição 2"

st.markdown("---")

merge_cols = ["NU_ANO", "CO_CURSO"]
left1 = conceito_filtrado1.rename(columns={"Ano": "NU_ANO", "Código do Curso": "CO_CURSO"})
merged1 = pd.merge(micro_q, left1, on=merge_cols, how="inner")

left2 = None
merged2 = pd.DataFrame()
if enable_comparison and st.session_state.selected_ies2:
    left2 = conceito_filtrado2.rename(columns={"Ano": "NU_ANO", "Código do Curso": "CO_CURSO"})
    merged2 = pd.merge(micro_q, left2, on=merge_cols, how="inner")

# Montar tabela de frequência (e gráfico de barras) -----------------------------------
if merged1.empty:
    st.warning("Não há dados para os filtros selecionados na 1ª instituição.")
    st.stop()
else:
    # Calcular contagem por resposta
    # - Para NU_IDADE, tratamos como categórico (idade por ano) para evitar bins erráticos.
    # - Para outros numéricos (caso existam), agrupamos em bins quando há muitas categorias.
    if pd.api.types.is_numeric_dtype(merged1[selected_var]):
        if selected_var == "NU_IDADE":
            freq = (
                merged1[selected_var].value_counts(dropna=True)
                .reset_index(name="count")
            )
        else:
            unique_values = merged1[selected_var].dropna().unique()
            if len(unique_values) <= 30:
                freq = (
                    merged1[selected_var].value_counts(dropna=True)
                    .reset_index(name="count")
                )
            else:
                merged1["_bin"] = pd.cut(merged1[selected_var], bins=10)
                freq = (
                    merged1["_bin"].value_counts(dropna=True)
                    .reset_index(name="count")
                )
        # Renomeia a coluna de resposta para 'Resposta'
        resposta_col = [c for c in freq.columns if c != "count"][0]
        freq = freq.rename(columns={resposta_col: "Resposta"})
        # manter o tipo original para idade, mas garantir string no gráfico
        if selected_var != "NU_IDADE":
            freq["Resposta"] = freq["Resposta"].astype(str)
    else:
        freq = (
            merged1[selected_var].value_counts(dropna=True)
            .reset_index(name="count")
        )
        resposta_col = [c for c in freq.columns if c != "count"][0]
        freq = freq.rename(columns={resposta_col: "Resposta"})
        freq["Resposta"] = freq["Resposta"].astype(str)

    if freq.empty or freq["count"].sum() == 0:
        st.warning("Nenhuma resposta encontrada para os filtros aplicados.")
        st.stop()

    freq["percent"] = (freq["count"] / freq["count"].sum()) * 100

    # Ordenação: para NU_IDADE, ordena por idade; caso contrário, ordena por contagem.
    if selected_var == "NU_IDADE":
        # manter tipo numérico se possível
        try:
            freq["Resposta"] = pd.to_numeric(freq["Resposta"], errors="coerce")
        except Exception:
            pass
        freq = freq.sort_values("Resposta", ascending=True).reset_index(drop=True)
    else:
        freq = freq.sort_values("count", ascending=False).reset_index(drop=True)

    freq["percent_fmt"] = freq["percent"].map(format_br_percentage)
    freq["count_fmt"] = freq["count"].map(format_br_number)

    # Set index to Resposta for proper plotting
    freq = freq.set_index("Resposta")



    if enable_comparison and not merged2.empty:
        st.subheader(f"📊 Comparação Interinstitucional: {available_labels[selected_var]}")


        
        # Calculate freq2 for Inst2
        if pd.api.types.is_numeric_dtype(merged2[selected_var]):
            if selected_var == "NU_IDADE":
                freq2 = merged2[selected_var].value_counts(dropna=True).reset_index(name="count")
            else:
                unique_values2 = merged2[selected_var].dropna().unique()
                if len(unique_values2) <= 30:
                    freq2 = merged2[selected_var].value_counts(dropna=True).reset_index(name="count")
                else:
                    merged2["_bin"] = pd.cut(merged2[selected_var], bins=10)
                    freq2 = merged2["_bin"].value_counts(dropna=True).reset_index(name="count")
            resposta_col2 = [c for c in freq2.columns if c != "count"][0]
            freq2 = freq2.rename(columns={resposta_col2: "Resposta"})
            if selected_var != "NU_IDADE":
                freq2["Resposta"] = freq2["Resposta"].astype(str)
        else:
            freq2 = merged2[selected_var].value_counts(dropna=True).reset_index(name="count")
            resposta_col2 = [c for c in freq2.columns if c != "count"][0]
            freq2 = freq2.rename(columns={resposta_col2: "Resposta"})
            freq2["Resposta"] = freq2["Resposta"].astype(str)

        # Determine institution names
# Removed duplicate definitions - now defined at top-level

        # Prepare freq1 like page2
        freq1_prep = freq.reset_index()
        freq1_prep["Contagem"] = freq1_prep["count"].round(0)
        freq1_prep["Instituicao"] = nome_inst1
        freq1_prep = freq1_prep.rename(columns={'Resposta': 'Resposta_Completa', 'count': 'Sigla Resposta'})
        
        freq2_prep = freq2.reset_index()
        freq2_prep["Contagem"] = freq2_prep["count"].round(0)
        freq2_prep["Instituicao"] = nome_inst2
        freq2_prep = freq2_prep.rename(columns={'Resposta': 'Resposta_Completa', 'count': 'Sigla Resposta'})

        # Create sigla for x-axis (reuse logic)
        def create_siglas(df_prep):
            unique_respostas = df_prep['Resposta_Completa'].tolist()
            sigla_mapping = {resp: resp[:3].upper() for resp in unique_respostas}
            sigla_used = {}
            final_siglas = []
            for resp in unique_respostas:
                sigla = sigla_mapping[resp]
                count = sigla_used.get(sigla, 0)
                final_sigla = sigla if count == 0 else f"{sigla}{count}"
                sigla_used[sigla] = count + 1
                final_siglas.append(final_sigla)
            df_prep['Sigla Resposta'] = final_siglas
            return df_prep

        freq1_prep = create_siglas(freq1_prep)
        freq2_prep = create_siglas(freq2_prep)

        df_comparacao = pd.concat([
            freq1_prep[['Sigla Resposta', 'Contagem', 'Instituicao', 'Resposta_Completa']], 
            freq2_prep[['Sigla Resposta', 'Contagem', 'Instituicao', 'Resposta_Completa']]
        ], ignore_index=True)



        # Order by combined average count
        cursos_ordenados = df_comparacao.groupby('Sigla Resposta')['Contagem'].mean().sort_values(ascending=False).index.tolist()
        df_comparacao['Sigla Resposta'] = pd.Categorical(df_comparacao['Sigla Resposta'], categories=cursos_ordenados, ordered=True)
        df_comparacao = df_comparacao.sort_values(['Sigla Resposta', 'Instituicao'])

        fig_comparativo = px.line(
            df_comparacao, 
            x='Sigla Resposta', 
            y='Contagem', 
            color='Instituicao',
            markers=True,
            line_shape='linear',
            title="",
            custom_data=['Resposta_Completa','Instituicao']
        )
        fig_comparativo.update_layout(
            title="",
            xaxis_tickangle=0,
            template="plotly_white",
            xaxis_title='Resposta',
            yaxis_title='Contagem',
            height=600
        )
        fig_comparativo.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Instituição: %{customdata[1]}<br>Contagem: %{y:.0f}<extra></extra>', hoverlabel=dict(font=dict(size=14)), line=dict(width=4), marker=dict(size=8))
        fig_comparativo.update_xaxes(categoryorder='array', categoryarray=cursos_ordenados)
        st.plotly_chart(fig_comparativo, width="stretch")

        col_tab1, col_tab2 = st.columns(2)
        with col_tab1:
            st.markdown(f"**{nome_inst1}**")
            display_df1 = freq1_prep[['Resposta_Completa', 'Contagem']].copy()
            perc1 = (display_df1['Contagem'] / display_df1['Contagem'].sum() * 100).round(1)
            display_df1['%'] = [f"{p:.1f}%" for p in perc1]
            display_df1.columns = ['Resposta', 'Contagem', '%']
            st.dataframe(display_df1, width="stretch", hide_index=True)
        with col_tab2:
            st.markdown(f"**{nome_inst2}**")
            display_df2 = freq2_prep[['Resposta_Completa', 'Contagem']].copy()
            perc2 = (display_df2['Contagem'] / display_df2['Contagem'].sum() * 100).round(1)
            display_df2['%'] = [f"{p:.1f}%" for p in perc2]
            display_df2.columns = ['Resposta', 'Contagem', '%']
            st.dataframe(display_df2, width="stretch", hide_index=True)
    else:
        st.subheader(f"📊 Contagem de respostas: {available_labels[selected_var]}")
        # Single institution line chart (existing)
        freq_line = freq.reset_index()
        freq_line['percent'] = (freq_line['count'] / freq_line['count'].sum()) * 100
        
        if selected_var == "NU_IDADE":
            freq_line['Sigla Resposta'] = freq_line['Resposta'].astype(str)
        else:
            unique_respostas = freq_line['Resposta'].tolist()
            sigla_mapping = {resp: resp[:3].upper() for resp in unique_respostas}
            sigla_used = {}
            final_siglas = []
            for resp in unique_respostas:
                sigla = sigla_mapping[resp]
                count = sigla_used.get(sigla, 0)
                final_sigla = sigla if count == 0 else f"{sigla}{count}"
                sigla_used[sigla] = count + 1
                final_siglas.append(final_sigla)
            freq_line['Sigla Resposta'] = final_siglas
        
        freq_line['Sigla Resposta'] = pd.Categorical(freq_line['Sigla Resposta'], categories=freq_line['Sigla Resposta'], ordered=True)
        
        fig = px.line(
            freq_line,
            x='Sigla Resposta',
            y='count',
            markers=True,
            line_shape='linear',
            title="",
            custom_data=['Resposta', 'percent']
        )
        fig.update_layout(
            title="",
            template="plotly_white",
            xaxis_title='Resposta',
            yaxis_title='Contagem',
            xaxis_tickangle=0,
            height=600
        )
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>Contagem: %{y}<br>Percentual: %{customdata[1]:.1f}%<extra></extra>',
            hoverlabel=dict(font=dict(size=14)),
            line=dict(width=4),
            marker=dict(size=8)
        )

        fig.update_xaxes(categoryorder='array', categoryarray=freq_line['Sigla Resposta'].cat.categories.tolist())
        st.plotly_chart(fig, width="stretch")

        st.subheader("**Distribuição**")
        freq_display = freq.reset_index()[["Resposta", "count_fmt", "percent_fmt"]]
        freq_display.columns = ["Resposta", "Contagem", "%"]
        st.dataframe(freq_display, width="stretch", hide_index=True)

show_footer(

    advisor_text="Orientador: Prof. Dr. César Candido Xavier • Email: cesarcx@gmail.com",
    text="Pesquisador: João Octavio Venâncio Borba • UNISO - Universidade de Sorocaba • Email: joaooctaviov.borba@gmail.com",
    links=[
        ("Github", "https://github.com/jaozes"),
        ("LinkedIn", "https://www.linkedin.com/in/jo%C3%A3o-octavio-vb/"),
        ("Currículo Lattes", "http://lattes.cnpq.br/0821075410761662"),
    ],
    bg_color="#ffffff",
    text_color="#000000",
    height_px=56,
)
