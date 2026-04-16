import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
from pathlib import Path
from utils.header import show_logo
from utils.footer import show_footer
from utils.header import inject_css

#streamlit run enade-analysis-app/Home.py
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

# Dicionário de abreviações para exibição nas tabelas
QE_ABBREVIATIONS = {
    "TP_SEXO": {
        "M": "Masc.",
        "F": "Fem.",
        "9": "Indef.",
    },
    "QE_I01": {
        "A": "Solteiro",
        "B": "Casado",
        "C": "Divorc.",
        "D": "Viúvo",
        "E": "Outro",
    },
    "QE_I02": {
        "A": "Branca",
        "B": "Preta",
        "C": "Amarela",
        "D": "Parda",
        "E": "Indígena",
        "F": "N/ decl.",
    },
    "QE_I03": {
        "A": "Bras.",
        "B": "Bras. nat.",
        "C": "Estrang.",
    },
    "QE_I04": {
        "A": "Nenhuma",
        "B": "Fund. I",
        "C": "Fund. II",
        "D": "Ens. Médio",
        "E": "Graduação",
        "F": "Pós-grad.",
    },
    "QE_I05": {
        "A": "Nenhuma",
        "B": "Fund. I",
        "C": "Fund. II",
        "D": "Ens. Médio",
        "E": "Graduação",
        "F": "Pós-grad.",
    },
    "QE_I06": {
        "A": "Sozinho",
        "B": "C/ pais",
        "C": "C/ cônjuge",
        "D": "C/ outros",
        "E": "Aloj. univ.",
        "F": "Outros",
    },
    "QE_I07": {
        "A": "0",
        "B": "1",
        "C": "2",
        "D": "3",
        "E": "4",
        "F": "5",
        "G": "6",
        "H": "7+",
    },
    "QE_I08": {
        "A": "Até 1.5 SM",
        "B": "1.5–3 SM",
        "C": "3.5–5 SM",
        "D": "5.5–6 SM",
        "E": "6–10 SM",
        "F": "10–30 SM",
        "G": "30+ SM",
    },
    "QE_I09": {
        "A": "Sem renda (Gov.)",
        "B": "Sem renda (Fam.)",
        "C": "Renda + ajuda",
        "D": "Renda própria",
        "E": "Ajuda família",
        "F": "Resp. família",
    },
    "QE_I10": {
        "A": "Desemp.",
        "B": "Trab. event.",
        "C": "Até 20h",
        "D": "21–39h",
        "E": "40h+",
    },
    "QE_I11": {
        "A": "Nenhuma",
        "B": "ProUni int.",
        "C": "ProUni parc.",
        "D": "FIES",
        "E": "ProUni+FIES",
        "F": "FIES parc.",
        "G": "Bolsa gov.",
        "H": "Bolsa inst.",
        "I": "Bolsa outro",
        "J": "Financ. inst.",
        "K": "Financ. banc.",
    },
    "QE_I12": {
        "A": "Nenhum",
        "B": "Aux. moradia",
        "C": "Aux. alim.",
        "D": "Moradia+alim.",
        "E": "Perm. geral",
        "F": "Outro",
    },
    "QE_I13": {
        "A": "Nenhum",
        "B": "IC",
        "C": "Monitoria",
        "D": "PET",
        "E": "Outro",
    },
    "QE_I14": {
        "A": "Não",
        "B": "CsF",
        "C": "Interc. Fed.",
        "D": "Interc. Est.",
        "E": "Interc. IES",
        "F": "Outro",
    },
    "QE_I15": {
        "A": "Não",
        "B": "Étnico",
        "C": "Renda",
        "D": "Esc. púb.",
        "E": "Misto",
        "F": "Outro",
    },
    "QE_I16": {
        "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA",
        "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
        "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE",
        "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
        "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT",
        "52": "GO", "53": "DF", "99": "N/A",
    },
    "QE_I17": {
        "A": "Pública",
        "B": "Privada",
        "C": "Exterior",
        "D": "Maior pub.",
        "E": "Maior priv.",
        "F": "Misto/ext.",
    },
    "QE_I18": {
        "A": "Tradicional",
        "B": "Técnico",
        "C": "Magistério",
        "D": "EJA",
        "E": "Outro",
    },
    "QE_I19": {
        "A": "Ninguém",
        "B": "Pais",
        "C": "Família",
        "D": "Prof.",
        "E": "Relig.",
        "F": "Amigos",
        "G": "Outro",
    },
    "QE_I20": {
        "A": "Sem dif.",
        "B": "Sem apoio",
        "C": "Pais",
        "D": "Avós",
        "E": "Família",
        "F": "Relig.",
        "G": "Amigos",
        "H": "Prof.",
        "I": "Apoio IES",
        "J": "Trabalho",
        "K": "Outro",
    },
    "QE_I21": {
        "A": "Sim",
        "B": "Não",
        "C": "Nenhum",
    },
    "QE_I22": {
        "A": "0",
        "B": "1–2",
        "C": "3–5",
        "D": "6–8",
        "E": "8+",
    },
    "QE_I23": {
        "A": "0h",
        "B": "1–3h",
        "C": "4–7h",
        "D": "8–12h",
        "E": "8–12h",
    },
    "QE_I24": {
        "A": "Pres.",
        "B": "Semi",
        "C": "Misto",
        "D": "EAD",
        "E": "Não",
    },
    "QE_I25": {
        "A": "Mercado",
        "B": "Família",
        "C": "Valoriz.",
        "D": "Prestígio",
        "E": "Vocação",
        "F": "EAD",
        "G": "Conc. baixa",
        "H": "Outro",
    },
    "QE_I26": {
        "A": "Gratuito",
        "B": "Preço",
        "C": "Próx. casa",
        "D": "Próx. trab.",
        "E": "Acesso",
        "F": "Qualidade",
        "G": "Única op.",
        "H": "Bolsa",
        "I": "Outro",
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


def sort_responses(df: pd.DataFrame, column: str, var_name: str = None) -> pd.DataFrame:
    """Ordena respostas pela sequência de alternativas (A,B,C...) ou por contagem."""
    try:
        # Se temos um var_name e ele existe em QE_VALUE_LABELS, usar a ordem das alternativas
        if var_name and var_name in QE_VALUE_LABELS:
            labels_dict = QE_VALUE_LABELS[var_name]
            # Criar mapeamento reverso: texto -> letra (ordem das alternativas)
            text_to_letter = {v: k for k, v in labels_dict.items()}
            
            # Adicionar coluna com a letra da alternativa
            df['_letter_order'] = df[column].map(text_to_letter)
            
            # Filtrar apenas respostas que têm mapeamento
            df = df.dropna(subset=['_letter_order'])
            
            if not df.empty:
                # Ordenar por letra (que preserva a ordem A, B, C, D...)
                df = df.sort_values('_letter_order').reset_index(drop=True)
                df = df.drop('_letter_order', axis=1)
                return df
    except Exception:
        pass
    
    # Se não conseguir ordenar por letras, ordena por contagem
    return df.sort_values("count", ascending=False).reset_index(drop=True)


def abbreviate_response(var_name: str, full_text: str) -> str:
    """Converte resposta completa para abreviação usando QE_ABBREVIATIONS."""
    if var_name not in QE_ABBREVIATIONS:
        return full_text
    
    abbr_dict = QE_ABBREVIATIONS[var_name]
    
    # Tentar encontrar a abreviação pelo mapeamento reverso (texto -> letra)
    if var_name in QE_VALUE_LABELS:
        labels_dict = QE_VALUE_LABELS[var_name]
        text_to_letter = {v: k for k, v in labels_dict.items()}
        letter = text_to_letter.get(full_text)
        if letter and letter in abbr_dict:
            return abbr_dict[letter]
    
    return full_text


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
    **{k: f"{QUESTION_METADATA[k]}" for k in QUESTION_METADATA},
    **{k: f"{EXTRA_VARS[k]}" for k in EXTRA_VARS},
}

pass

selected_var = st.selectbox(
    "Selecione a questão a ser veríficada:",
    options=available_vars,
    format_func=lambda v: available_labels.get(v, v),
)

# Carregar dados de microdados para a variável
micro_q = load_question_df(selected_var)

# Função auxiliar para atualizar opções de filtro dinamicamente (igual à página 2)
def get_filtered_df(uf, municipio, ies, curso, modalidade, categoria, grau):
    """Filtra dataframe com base nas seleções (baseado na página 2)."""
    filtered = conceito_df.copy()
    if uf:
        filtered = filtered[filtered['Sigla da UF** '].isin(uf)]
    if municipio:
        filtered = filtered[filtered['Município do Curso**'].isin(municipio)]
    if ies:
        filtered = filtered[filtered['Nome da IES*'].isin(ies)]
    if curso:
        filtered = filtered[filtered['Área de Avaliação'].isin(curso)]
    if modalidade:
        filtered = filtered[filtered['Modalidade de Ensino'].isin(modalidade)]
    if categoria:
        filtered = filtered[filtered['Categoria Administrativa'].isin(categoria)]
    if grau:
        filtered = filtered[filtered['Grau Acadêmico'].isin(grau)]
    return filtered

# Filtros em colunas com lógica em cascata
col_insts, _ = st.columns([1, 3])
with col_insts:
    enable_comparison = st.toggle("**Comparação Interinstitucional**", key="toggle_comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### **1ª Instituição**")

    col1a, col1b, col1c, col1d = st.columns(4)
    with col1a:
        ufs_options1 = sorted(get_filtered_df(None, st.session_state.get('selected_municipios', []), st.session_state.get('selected_ies', []), st.session_state.get('selected_areas', []), st.session_state.get('selected_modalidades', []), st.session_state.get('selected_categorias', []), st.session_state.get('selected_graus', []))['Sigla da UF** '].dropna().unique())
        selected_uf = st.multiselect(
            "UF", 
            options=ufs_options1, 
            key='uf1'
        )
    with col1b:
        municipios_options1 = sorted(get_filtered_df(selected_uf, None, st.session_state.get('selected_ies', []), st.session_state.get('selected_areas', []), st.session_state.get('selected_modalidades', []), st.session_state.get('selected_categorias', []), st.session_state.get('selected_graus', []))['Município do Curso**'].dropna().unique())
        selected_municipio = st.multiselect(
            "Município", 
            options=municipios_options1, 
            key='mun1'
        )
    with col1c:
        ies_options1 = sorted(get_filtered_df(selected_uf, selected_municipio, None, st.session_state.get('selected_areas', []), st.session_state.get('selected_modalidades', []), st.session_state.get('selected_categorias', []), st.session_state.get('selected_graus', []))['Nome da IES*'].dropna().unique())
        selected_ies = st.multiselect(
            "IES", 
            options=ies_options1, 
            key='ies1'
        )
    with col1d:
        areas_options1 = sorted(get_filtered_df(selected_uf, selected_municipio, selected_ies, None, st.session_state.get('selected_modalidades', []), st.session_state.get('selected_categorias', []), st.session_state.get('selected_graus', []))['Área de Avaliação'].dropna().unique())
        selected_curso = st.multiselect(
            "Curso", 
            options=areas_options1, 
            key='area1'
        )

    col1e, col1f, col1g = st.columns(3)
    with col1e:
        modalidades_options1 = sorted(get_filtered_df(selected_uf, selected_municipio, selected_ies, selected_curso, None, st.session_state.get('selected_categorias', []), st.session_state.get('selected_graus', []))['Modalidade de Ensino'].dropna().unique())
        selected_modalidade = st.multiselect(
            "Modalidade", 
            options=modalidades_options1, 
            key='mod1'
        )
    with col1f:
        categorias_options1 = sorted(get_filtered_df(selected_uf, selected_municipio, selected_ies, selected_curso, selected_modalidade, None, st.session_state.get('selected_graus', []))['Categoria Administrativa'].dropna().unique())
        selected_categoria = st.multiselect(
            "Categoria", 
            options=categorias_options1, 
            key='cat1'
        )
    with col1g:
        graus_options1 = sorted(get_filtered_df(selected_uf, selected_municipio, selected_ies, selected_curso, selected_modalidade, selected_categoria, None)['Grau Acadêmico'].dropna().unique())
        selected_grau = st.multiselect(
            "Grau", 
            options=graus_options1, 
            key='grau1'
        )

if enable_comparison:
    with col2:
        st.markdown("### **2ª Instituição**")
        
        col2a, col2b, col2c, col2d = st.columns(4)
        with col2a:
            ufs_options2 = sorted(get_filtered_df(None, st.session_state.get('selected_municipios2', []), st.session_state.get('selected_ies2', []), st.session_state.get('selected_areas2', []), st.session_state.get('selected_modalidades2', []), st.session_state.get('selected_categorias2', []), st.session_state.get('selected_graus2', []))['Sigla da UF** '].dropna().unique())
            selected_uf2 = st.multiselect(
                "UF", key="uf2",
                options=ufs_options2
            )
        with col2b:
            municipios_options2 = sorted(get_filtered_df(selected_uf2, None, st.session_state.get('selected_ies2', []), st.session_state.get('selected_areas2', []), st.session_state.get('selected_modalidades2', []), st.session_state.get('selected_categorias2', []), st.session_state.get('selected_graus2', []))['Município do Curso**'].dropna().unique())
            selected_municipio2 = st.multiselect(
                "Município", key="mun2",
                options=municipios_options2
            )
        with col2c:
            ies_options2 = sorted(get_filtered_df(selected_uf2, selected_municipio2, None, st.session_state.get('selected_areas2', []), st.session_state.get('selected_modalidades2', []), st.session_state.get('selected_categorias2', []), st.session_state.get('selected_graus2', []))['Nome da IES*'].dropna().unique())
            selected_ies2 = st.multiselect(
                "IES", key="ies2",
                options=ies_options2
            )
        with col2d:
            areas_options2 = sorted(get_filtered_df(selected_uf2, selected_municipio2, selected_ies2, None, st.session_state.get('selected_modalidades2', []), st.session_state.get('selected_categorias2', []), st.session_state.get('selected_graus2', []))['Área de Avaliação'].dropna().unique())
            selected_curso2 = st.multiselect(
                "Curso", key="area2",
                options=areas_options2
            )
        
        col2e, col2f, col2g = st.columns(3)
        with col2e:
            modalidades_options2 = sorted(get_filtered_df(selected_uf2, selected_municipio2, selected_ies2, selected_curso2, None, st.session_state.get('selected_categorias2', []), st.session_state.get('selected_graus2', []))['Modalidade de Ensino'].dropna().unique())
            selected_modalidade2 = st.multiselect(
                "Modalidade", key="mod2",
                options=modalidades_options2
            )
        with col2f:
            categorias_options2 = sorted(get_filtered_df(selected_uf2, selected_municipio2, selected_ies2, selected_curso2, selected_modalidade2, None, st.session_state.get('selected_graus2', []))['Categoria Administrativa'].dropna().unique())
            selected_categoria2 = st.multiselect(
                "Categoria", key="cat2",
                options=categorias_options2
            )
        with col2g:
            graus_options2 = sorted(get_filtered_df(selected_uf2, selected_municipio2, selected_ies2, selected_curso2, selected_modalidade2, selected_categoria2, None)['Grau Acadêmico'].dropna().unique())
            selected_grau2 = st.multiselect(
                "Grau", key="grau2",
                options=graus_options2
            )
        with col2f:
            municipios_options2 = sorted(get_filtered_df(selected_uf2, None, st.session_state.get('selected_ies2', []), selected_curso2, selected_modalidade2, selected_categoria2, selected_grau2)['Município do Curso**'].dropna().unique())
            selected_municipio2 = st.multiselect(
                "Município", key="mun2",
                options=municipios_options2
            )
        with col2g:
            ies_options2 = sorted(get_filtered_df(selected_uf2, selected_municipio2, None, selected_curso2, selected_modalidade2, selected_categoria2, selected_grau2)['Nome da IES*'].dropna().unique())
            selected_ies2 = st.multiselect(
                "IES", key="ies2",
                options=ies_options2
            )

# Apply filters to both institutions
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

# Second institution filters
conceito_filtrado2 = conceito_df.copy()
if enable_comparison:
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

# Define institution names for both modes
has_filters1 = bool(selected_uf or selected_curso or selected_modalidade or selected_categoria or selected_grau or selected_ies or selected_municipio)
if selected_ies and len(selected_ies) == 1:
    nome_inst1 = selected_ies[0]
elif has_filters1:
    nome_inst1 = "Instituição 1"
else:
    nome_inst1 = "Contagem Nacional"

nome_inst2 = "Instituição 2"
if enable_comparison:
    has_filters2 = bool(selected_uf2 or selected_curso2 or selected_modalidade2 or selected_categoria2 or selected_grau2 or selected_ies2 or selected_municipio2)
    if selected_ies2 and len(selected_ies2) == 1:
        nome_inst2 = selected_ies2[0]
    elif has_filters2:
        nome_inst2 = "Instituição 2"
    else:
        nome_inst2 = "Contagem Nacional"

st.markdown("---")

# Validar se há dados antes de fazer merge (como na página 2)
if conceito_filtrado1.empty:
    st.warning("Não há dados para os filtros selecionados na 1ª instituição.")
    st.stop()

merge_cols = ["NU_ANO", "CO_CURSO"]
left1 = conceito_filtrado1.rename(columns={"Ano": "NU_ANO", "Código do Curso": "CO_CURSO"})
merged1 = pd.merge(micro_q, left1, on=merge_cols, how="inner")

left2 = None
merged2 = pd.DataFrame()
if enable_comparison:
    if conceito_filtrado2.empty:
        st.warning("Não há dados para os filtros selecionados na 2ª instituição.")
        enable_comparison = False
    else:
        left2 = conceito_filtrado2.rename(columns={"Ano": "NU_ANO", "Código do Curso": "CO_CURSO"})
        merged2 = pd.merge(micro_q, left2, on=merge_cols, how="inner")

# Montar tabela de frequência (e gráfico de barras) -----------------------------------
if merged1.empty:
    st.warning("Não há dados microeconômicos para os filtros selecionados na 1ª instituição.")
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

    # Ordenação: para NU_IDADE, ordena por idade; para respostas com QE_VALUE_LABELS, ordena por alternativa (A,B,C...); caso contrário, ordena por contagem.
    if selected_var == "NU_IDADE":
        # manter tipo numérico se possível
        try:
            freq["Resposta"] = pd.to_numeric(freq["Resposta"], errors="coerce")
        except Exception:
            pass
        freq = freq.sort_values("Resposta", ascending=True).reset_index(drop=True)
    else:
        freq = sort_responses(freq, "Resposta", selected_var)

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
        
        # Aplicar mesma ordenação de freq
        if selected_var == "NU_IDADE":
            try:
                freq2["Resposta"] = pd.to_numeric(freq2["Resposta"], errors="coerce")
            except Exception:
                pass
            freq2 = freq2.sort_values("Resposta", ascending=True).reset_index(drop=True)
        else:
            freq2 = sort_responses(freq2, "Resposta", selected_var)

        # Determine institution names
# Removed duplicate definitions - now defined at top-level

        # Prepare freq1 like page2
        freq1_prep = freq.reset_index()
        freq1_prep["Contagem"] = freq1_prep["count"].round(0)
        freq1_prep["Percentual"] = (freq1_prep["count"] / freq1_prep["count"].sum() * 100).round(2)
        freq1_prep["Instituicao"] = nome_inst1
        freq1_prep = freq1_prep.rename(columns={'Resposta': 'Resposta_Completa', 'count': 'Sigla Resposta'})
        
        freq2_prep = freq2.reset_index()
        freq2_prep["Contagem"] = freq2_prep["count"].round(0)
        freq2_prep["Percentual"] = (freq2_prep["count"] / freq2_prep["count"].sum() * 100).round(2)
        freq2_prep["Instituicao"] = nome_inst2
        freq2_prep = freq2_prep.rename(columns={'Resposta': 'Resposta_Completa', 'count': 'Sigla Resposta'})

        # Create abbreviations for display
        def create_abbreviations(df_prep):
            df_prep['Abreviacao'] = df_prep['Resposta_Completa'].apply(lambda x: abbreviate_response(selected_var, x))
            return df_prep

        freq1_prep = create_abbreviations(freq1_prep)
        freq2_prep = create_abbreviations(freq2_prep)

        df_comparacao = pd.concat([
            freq1_prep[['Abreviacao', 'Contagem', 'Percentual', 'Instituicao', 'Resposta_Completa']], 
            freq2_prep[['Abreviacao', 'Contagem', 'Percentual', 'Instituicao', 'Resposta_Completa']]
        ], ignore_index=True)

        # Ordenar por ordem das alternativas (A, B, C, D...) usando QE_VALUE_LABELS
        respostas_unicas = df_comparacao['Resposta_Completa'].drop_duplicates().tolist()
        
        # Se a variável está em QE_VALUE_LABELS, usar a ordem das alternativas
        if selected_var in QE_VALUE_LABELS:
            labels_dict = QE_VALUE_LABELS[selected_var]
            text_to_letter = {v: k for k, v in labels_dict.items()}
            
            # Filtrar respostas que têm mapeamento e criar lista ordenada por letra
            respostas_com_letra = [(resp, text_to_letter.get(resp, 'Z')) for resp in respostas_unicas if resp in text_to_letter]
            respostas_com_letra.sort(key=lambda x: x[1])  # Ordena por letra (A < B < C < D...)
            respostas_unicas_sorted = [resp for resp, _ in respostas_com_letra]
        else:
            # Se não estiver em QE_VALUE_LABELS, ordenar alfabeticamente
            respostas_unicas_sorted = sorted(respostas_unicas)
        
        # Criar mapeamento de Abreviacao mantendo a ordem correta
        abrev_resposta_map = df_comparacao[['Abreviacao', 'Resposta_Completa']].drop_duplicates().set_index('Resposta_Completa')['Abreviacao'].to_dict()
        abrev_ordenadas = [abrev_resposta_map[resp] for resp in respostas_unicas_sorted if resp in abrev_resposta_map]
        
        df_comparacao['Abreviacao'] = pd.Categorical(df_comparacao['Abreviacao'], categories=abrev_ordenadas, ordered=True)
        df_comparacao = df_comparacao.sort_values(['Abreviacao', 'Instituicao'])
        
        # Adicionar coluna formatada para hover
        df_comparacao['Contagem_fmt'] = df_comparacao['Contagem'].apply(lambda x: format_br_number(x, 0))
        df_comparacao['Percentual_fmt'] = df_comparacao['Percentual'].apply(lambda x: format_br_percentage(x))

        fig_comparativo = px.line(
            df_comparacao, 
            x='Abreviacao', 
            y='Percentual', 
            color='Instituicao',
            markers=True,
            line_shape='linear',
            title="",
            custom_data=['Resposta_Completa','Instituicao', 'Percentual_fmt', 'Contagem_fmt']
        )
        fig_comparativo.update_layout(
            title="",
            xaxis_tickangle=0,
            template="plotly_white",
            xaxis_title='Resposta',
            yaxis_title='Percentual (%)',
            height=600
        )
        fig_comparativo.update_yaxes(ticksuffix='%')
        fig_comparativo.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Instituição: %{customdata[1]}<br>Percentual: %{customdata[2]}<br>Contagem: %{customdata[3]}<extra></extra>', hoverlabel=dict(font=dict(size=14)), line=dict(width=4), marker=dict(size=8))
        fig_comparativo.update_xaxes(categoryorder='array', categoryarray=abrev_ordenadas)
        st.plotly_chart(fig_comparativo, width="stretch")

        col_tab1, col_tab2 = st.columns(2)
        with col_tab1:
            st.markdown(f"**{nome_inst1}**")
            if selected_var == "NU_IDADE":
                display_df1 = freq1_prep[['Resposta_Completa', 'Contagem']].copy()
                perc1 = (display_df1['Contagem'] / display_df1['Contagem'].sum() * 100).round(1)
                display_df1['Resposta_Completa'] = display_df1['Resposta_Completa'].apply(lambda x: format_br_number(int(x), 0))
                display_df1['Contagem'] = display_df1['Contagem'].apply(lambda x: format_br_number(x, 0))
                display_df1['%'] = [format_br_percentage(p) for p in perc1]
                display_df1.columns = ['Idade', 'Contagem', '%']
            else:
                display_df1 = freq1_prep[['Resposta_Completa', 'Abreviacao', 'Contagem']].copy()
                perc1 = (display_df1['Contagem'] / display_df1['Contagem'].sum() * 100).round(1)
                display_df1['Contagem'] = display_df1['Contagem'].apply(lambda x: format_br_number(x, 0))
                display_df1['%'] = [format_br_percentage(p) for p in perc1]
                display_df1.columns = ['Resposta', 'Abreviação', 'Contagem', '%']
            st.dataframe(display_df1, width='stretch', hide_index=True)
        with col_tab2:
            st.markdown(f"**{nome_inst2}**")
            if selected_var == "NU_IDADE":
                display_df2 = freq2_prep[['Resposta_Completa', 'Contagem']].copy()
                perc2 = (display_df2['Contagem'] / display_df2['Contagem'].sum() * 100).round(1)
                display_df2['Resposta_Completa'] = display_df2['Resposta_Completa'].apply(lambda x: format_br_number(int(x), 0))
                display_df2['Contagem'] = display_df2['Contagem'].apply(lambda x: format_br_number(x, 0))
                display_df2['%'] = [format_br_percentage(p) for p in perc2]
                display_df2.columns = ['Idade', 'Contagem', '%']
            else:
                display_df2 = freq2_prep[['Resposta_Completa', 'Abreviacao', 'Contagem']].copy()
                perc2 = (display_df2['Contagem'] / display_df2['Contagem'].sum() * 100).round(1)
                display_df2['Contagem'] = display_df2['Contagem'].apply(lambda x: format_br_number(x, 0))
                display_df2['%'] = [format_br_percentage(p) for p in perc2]
                display_df2.columns = ['Resposta', 'Abreviação', 'Contagem', '%']
            st.dataframe(display_df2, width='stretch', hide_index=True)
    else:
        st.subheader(f"📊 Contagem de respostas: {available_labels[selected_var]}")
        # Single institution line chart (existing)
        freq_line = freq.reset_index()
        freq_line['percent'] = (freq_line['count'] / freq_line['count'].sum()) * 100
        
        # Adicionar coluna de abreviações
        freq_line['Abreviacao'] = freq_line['Resposta'].apply(lambda x: abbreviate_response(selected_var, x))
        
        if selected_var == "NU_IDADE":
            freq_line['Abreviacao'] = freq_line['Resposta'].astype(str)
        
        freq_line['Abreviacao'] = pd.Categorical(freq_line['Abreviacao'], categories=freq_line['Abreviacao'], ordered=True)
        
        # Adicionar colunas formatadas para hover
        freq_line['count_fmt'] = freq_line['count'].apply(lambda x: format_br_number(x, 0))
        freq_line['percent_fmt'] = freq_line['percent'].apply(lambda x: format_br_percentage(x))
        
        fig = px.line(
            freq_line,
            x='Abreviacao',
            y='percent',
            markers=True,
            line_shape='linear',
            title="",
            custom_data=['Resposta', 'count_fmt', 'percent_fmt']
        )
        fig.update_layout(
            title="",
            template="plotly_white",
            xaxis_title='Resposta',
            yaxis_title='Percentual (%)',
            xaxis_tickangle=0,
            height=600
        )
        fig.update_yaxes(ticksuffix='%')
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>Contagem: %{customdata[1]}<br>Percentual: %{customdata[2]}<extra></extra>',
            hoverlabel=dict(font=dict(size=14)),
            line=dict(width=4),
            marker=dict(size=8)
        )

        fig.update_xaxes(categoryorder='array', categoryarray=freq_line['Abreviacao'].cat.categories.tolist())
        st.plotly_chart(fig, width="stretch")

        st.subheader("**Distribuição**")
        if selected_var == "NU_IDADE":
            freq_display = freq_line[["Resposta", "count_fmt", "percent_fmt"]].copy()
            freq_display['Resposta'] = freq_display['Resposta'].apply(lambda x: format_br_number(int(x), 0) if pd.notna(x) else x)
            freq_display.columns = ["Idade", "Contagem", "%"]
        else:
            freq_display = freq_line[["Resposta", "Abreviacao", "count_fmt", "percent_fmt"]].copy()
            freq_display.columns = ["Resposta", "Abreviação", "Contagem", "%"]
        st.dataframe(freq_display, width='stretch', hide_index=True)

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
