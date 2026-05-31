import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from utils.header import show_logo
from utils.footer import show_footer
from utils.theme import init_theme

init_theme(page_title="Home - ENADE 2023", layout="wide")

# Estilo para alinhar tabelas à esquerda
st.markdown("""
    <style>
        [data-testid="stDataFrame"] {text-align: left !important;}
        [data-testid="stDataFrame"] > div {text-align: left !important;}
    </style>
""", unsafe_allow_html=True)

show_logo()



st.markdown("# 🎓 Mapeando o Desempenho do Estudante no ENADE: Uma Plataforma Interativa Para Comparações Interinstitucionais")
st.markdown("# Análise do ENADE 2023")

from utils.data_loader import load_conceito

df = load_conceito()

# Calculate average concept per IES per UF
ies_avg = df.groupby(['Sigla da UF** ', 'Sigla da IES*']).agg(
    conceito_medio_ies=('Conceito Enade (Contínuo)', 'mean')
).reset_index()

# Find top IES per UF
top_ies_per_uf = ies_avg.loc[ies_avg.groupby('Sigla da UF** ')['conceito_medio_ies'].idxmax()].rename(columns={'Sigla da UF** ': 'uf', 'Sigla da IES*': 'top_ies', 'conceito_medio_ies': 'top_ies_conceito'})

# Aggregate data by UF
aggregated_df = df.groupby('Sigla da UF** ').agg(
    conceito_medio=('Conceito Enade (Contínuo)', 'mean'),
    inscritos=('Nº de Concluintes Inscritos', 'sum'),
    participantes=('Nº  de Concluintes Participantes', 'sum'),
    qtd_ies=('Sigla da IES*', 'nunique'),
    nota_fg_media=('Nota Bruta - FG', 'mean'),
    nota_ce_media=('Nota Padronizada - CE', 'mean')
).reset_index().rename(columns={'Sigla da UF** ': 'uf'})

# Merge top IES data
aggregated_df = aggregated_df.merge(top_ies_per_uf[['uf', 'top_ies', 'top_ies_conceito']], on='uf', how='left')

num_cursos = df['Código do Curso'].nunique()
num_inscritos_raw = aggregated_df['inscritos'].sum()
num_participantes_raw = aggregated_df['participantes'].sum()
num_ies = df['Sigla da IES*'].nunique()
taxa_participacao = (num_participantes_raw / num_inscritos_raw * 100) if num_inscritos_raw > 0 else 0
conceito_medio_nacional = df['Conceito Enade (Contínuo)'].mean()

# Formatar números no padrão brasileiro para o mapa
aggregated_df['inscritos'] = aggregated_df['inscritos'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
aggregated_df['participantes'] = aggregated_df['participantes'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
aggregated_df['qtd_ies'] = aggregated_df['qtd_ies'].apply(lambda x: f"{x:,}".replace(",", "."))

# Formatar números no padrão brasileiro (ponto como separador de milhares)
num_inscritos = f"{num_inscritos_raw:,.0f}".replace(",", ".")
num_participantes = f"{num_participantes_raw:,.0f}".replace(",", ".")
num_cursos = f"{num_cursos:,}".replace(",", ".")
num_ies = f"{num_ies:,}".replace(",", ".")

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Concluintes Inscritos", num_inscritos)
with col2:
    st.metric("Concluintes Participantes", num_participantes)
with col3:
    st.metric("Taxa de Participação", f"{taxa_participacao:.1f}%".replace(".", ","),
              help="Percentual de inscritos que efetivamente participaram do ENADE 2023")
with col4:
    st.metric("Conceito Médio Nacional", f"{conceito_medio_nacional:.2f}".replace(".", ","),
              help="Média do Conceito ENADE Contínuo (escala 0–5) de todos os cursos avaliados")
with col5:
    st.metric("Total de Cursos", num_cursos)
with col6:
    st.metric("Total de IES", num_ies)


# Load GeoJSON
geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
response = requests.get(geojson_url)
brazil_states = response.json()

# Create the choropleth map
# Escala customizada: tons mais escuros a partir de 3
custom_colorscale = [
    [0, "#ffffff"],      # 0 - muito claro
    [0.2, "#e2eaf0"],    # 1
    [0.4, "#c2d6ff"],    # 2
    [0.5, '#598eff'],    # 2.5
    [0.6, "#0d2883"],    # 3 - transição
    [0.7, "#161675"],    # 3.5 - mais escuro
    [0.8, "#070747"],    # 4
    [1, '#000000']       # 5 - mais escuro possível
]

fig = go.Figure(go.Choropleth(
    geojson=brazil_states,
    locations=aggregated_df['uf'],
    z=aggregated_df['conceito_medio'],
    featureidkey="properties.sigla",
    colorscale=custom_colorscale,
    zmin=0,
    zmax=5,
    hovertemplate='<b>%{location}</b><br>' +
                  'Conceito Médio: %{z:.2f}<br>' +
                  'Inscritos: %{customdata[0]}<br>' +
                  'Participantes: %{customdata[1]}<br>' +
                  'Qtd. IES: %{customdata[2]}<br>' +
                  'Top IES: %{customdata[5]} - Conceito: %{customdata[6]:.2f}<extra></extra>',
    customdata=aggregated_df[['inscritos', 'participantes', 'qtd_ies', 'nota_fg_media', 'nota_ce_media', 'top_ies', 'top_ies_conceito']].values
))

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    title_font=dict(size=26, family="Arial Black", color="#1f1f1f"),
    margin=dict(r=0, t=0, l=0, b=0), 
    height=750, 
    width=None
)
fig.update_traces(hoverlabel=dict(font=dict(size=14)))

#col1, col2 = st.columns(2)

#with col1:
st.markdown("""
## Sobre o Projeto

Este projeto analisa os conceitos do **Exame Nacional de Desempenho de Estudantes (ENADE)** de 2023,
desenvolvido na **UNISO – Universidade de Sorocaba** como parte de uma pesquisa acadêmica orientada
pelo Prof. Dr. César Candido Xavier.

### Objetivos

- Comparar desempenho entre cursos, instituições e regiões.
- Analisar tendências de qualidade no ensino superior.
- Identificar variações por modalidade e categoria administrativa.
- Fornecer insights estatísticos para análises educacionais.
- Investigar o perfil socioeconômico e a avaliação do processo formativo pelos estudantes.
""")

st.markdown("---")

# Descrição detalhada das páginas
st.markdown("### 📂 Módulos Disponíveis")

desc_col1, desc_col2 = st.columns(2)

with desc_col1:
    st.markdown("""
    **📊 Comparação de Médias**

    Compara o Conceito ENADE Contínuo (escala 0–5) entre dois grupos de filtros simultâneos —
    por UF, município, IES, curso, modalidade, categoria administrativa e grau acadêmico.
    Exibe gráficos de linha interativos, boxplots por aluno (quando disponíveis nos microdados)
    e tabelas com estatísticas descritivas por curso.

    **👤 Perfil Socioeconômico**

    Analisa as respostas do Questionário Socioeconômico do ENADE 2023 (QE_I01 a QE_I26),
    cobrindo variáveis como cor/raça, renda familiar, situação de trabalho, tipo de escola
    do ensino médio, bolsas recebidas e motivação para escolha do curso. Permite comparação
    interinstitucional em gráficos de barras ou linha.
    """)

with desc_col2:
    st.markdown("""
    **📘 Questionário Complementar**

    Apresenta as respostas às assertivas QE_I27 a QE_I68 do questionário complementar,
    que avaliam o processo formativo em três eixos: Organização Didático-Pedagógica,
    Infraestrutura e Oportunidades de ampliação acadêmica. As respostas seguem escala
    Likert de 1 (Discordo totalmente) a 6 (Concordo totalmente), com opções adicionais
    "Não sei responder" e "Não se aplica".

    **🗺️ Esta Página (Home)**

    Visão geral do conjunto de dados: métricas nacionais, mapa coroplético do Conceito
    Médio ENADE por estado e apresentação dos módulos da plataforma. Nenhum filtro é
    aplicado aqui — os dados exibidos representam o Brasil inteiro.
    """)

st.markdown("---")

# Metodologia e Stack
method_col1, method_col2, method_col3 = st.columns(3)

with method_col1:
    st.markdown("""
    **🔬 Nota Metodológica**

    Os resultados desta plataforma são observacionais e não estabelecem relações de causalidade.
    O **Conceito ENADE Contínuo** varia de 0 a 5 e é calculado pelo INEP com base nas notas
    brutas de Formação Geral e Componente Específico, ponderadas pela proporção de participantes.

    Nas páginas de Comparação de Médias, a unidade de análise é o **curso por IES**. Nas páginas
    de Perfil Socioeconômico e Questionário Complementar, a unidade é o **aluno** (microdados).
    Os dados são oficiais do INEP e respeitam integralmente as políticas de anonimização e uso ético.
    """)

with method_col2:
    st.markdown("""
    **💻 Stack Tecnológico**

    **Interface:** Streamlit  
    **Processamento:** Pandas + NumPy  
    **Visualização:** Plotly  
    **Dados:** Microdados ENADE 2023 (INEP)  
    **Linguagem:** Python 3  
    **Cache:** `@st.cache_data` para performance  
    **Hospedagem:** Streamlit Community Cloud
    """)

with method_col3:
    st.markdown("""
    **🚀 Guia de Navegação**

    1. Acesse uma página pelo **menu lateral**
    2. Configure os **filtros em cascata** — UF → Município → IES → Curso → Modalidade
    3. Ative a **Comparação Interinstitucional** para confrontar dois grupos lado a lado
    4. Interaja com os **gráficos Plotly** (zoom, hover, clique na legenda para ocultar séries)
    5. Consulte as **tabelas de estatísticas** abaixo de cada gráfico para os valores exatos
    6. Use os tooltips (ícone **?**) nas métricas para entender cada indicador
    """)

#with col2:
st.plotly_chart(fig, use_container_width=True)
    
    # Legenda do Mapa - Explicação para Acessibilidade e Clareza
with st.expander("📊 Legenda do Mapa", expanded=True):
        st.markdown("**O que este mapa representa:**")
        st.markdown("""
        - **Conceito Médio ENADE por Estado:** Cada estado é colorido de acordo com a média dos conceitos ENADE contínuos de todas as IES (Instituições de Ensino Superior) naquele estado.
        """)
        
        st.markdown("**Escala de Cores (Azul):**")
        
        # Barra de gradiente visual usando HTML - escala customizada com transição mais rápida para escuro a partir de 3
        st.markdown("""
        <div style="background: linear-gradient(to right, #f7fbff, #deebf7, #c6dbef, #9ecae1, #6baed6, #3182bd, #08519c, #08306b); 
                    height: 25px; 
                    border-radius: 4px; 
                    margin: 10px 0;
                    border: 1px solid #ccc;"></div>
        """, unsafe_allow_html=True)
        
        # Labels abaixo da barra
        col_scale1, col_scale2, col_scale3 = st.columns([1, 2, 1])
        with col_scale1:
            st.caption("Baixo (0 - 2)")
        with col_scale2:
            st.caption("→ Médio (2 - 3) →")
        with col_scale3:
            st.caption("Alto (4 - 5)")
        
        # Explicação das cores
        st.markdown("""
         **Branco e Azul claro** = Conceito médio mais baixo (0 - 2)  
         **Azul médio** = Conceito médio intermediário (2 - 3)   
         **Azul escuro** = Conceito médio mais alto (4 - 5)
        """)

        
        st.markdown("---")
        
        st.markdown("**Como interagir:**")
        st.markdown("""
        - 🖱️ **Passe o mouse** sobre qualquer estado para ver detalhes completos
        - 📋 Informações exibidas: Conceito médio, número de inscritos, participantes, quantidade de IES e a melhor IES do estado
        """)


show_footer(
    advisor_text="Orientador: Prof. Dr. César Candido Xavier • Email: cesarcx@gmail.com",
    advisor_link=("Currículo Lattes", "http://lattes.cnpq.br/2281060219061831"),
    text="Pesquisador: João Octavio Venâncio Borba • UNISO - Universidade de Sorocaba • Email: joaooctaviov.borba@gmail.com",
    links=[("Github", "https://github.com/jaozes"), ("LinkedIn", "https://www.linkedin.com/in/jo%C3%A3o-octavio-vb/"), ("Currículo Lattes", "http://lattes.cnpq.br/0821075410761662")],
    bg_color="#ffffff",
    text_color="#000000",
    height_px=56,
    citation="Como citar: BORBA, J. O. V. ; XAVIER, C. C. Mapeando o desempenho e o perfil do estudante no Enade: uma plataforma interativa para comparações interinstitucionais. Sorocaba, SP, 2026. Disponível em: https://app-exploracao-enade2023.streamlit.app. Acesso em: [data de acesso]"
)
