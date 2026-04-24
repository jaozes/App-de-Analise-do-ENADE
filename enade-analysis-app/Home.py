import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from utils.header import show_logo
from utils.header import inject_css
from utils.footer import show_footer

st.set_page_config(layout="wide")

# Estilo para alinhar tabelas à esquerda
st.markdown("""
    <style>
        [data-testid="stDataFrame"] {text-align: left !important;}
        [data-testid="stDataFrame"] > div {text-align: left !important;}
    </style>
""", unsafe_allow_html=True)

#inject_css()
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
num_inscritos = aggregated_df['inscritos'].sum()
num_participantes = aggregated_df['participantes'].sum()
num_ies = df['Sigla da IES*'].nunique()

# Formatar números no padrão brasileiro para o mapa
aggregated_df['inscritos'] = aggregated_df['inscritos'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
aggregated_df['participantes'] = aggregated_df['participantes'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
aggregated_df['qtd_ies'] = aggregated_df['qtd_ies'].apply(lambda x: f"{x:,}".replace(",", "."))

# Formatar números no padrão brasileiro (ponto como separador de milhares)
num_inscritos = f"{num_inscritos:,.0f}".replace(",", ".")
num_participantes = f"{num_participantes:,.0f}".replace(",", ".")
num_cursos = f"{num_cursos:,}".replace(",", ".")
num_ies = f"{num_ies:,}".replace(",", ".")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Número de Inscritos", num_inscritos)
with col2:
    st.metric("Número de Participantes", num_participantes)
with col3:
    st.metric("Total de Cursos", num_cursos)
with col4:
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

Este projeto analisa os conceitos do **Exame Nacional de Desempenho de Estudantes (ENADE)** de 2023.

### Objetivos

- Comparar desempenho entre cursos, instituições e regiões.
- Analisar tendências de qualidade no ensino superior.
- Identificar variações por modalidade e categoria administrativa.
- Fornecer insights estatísticos para analises educacionais.
- Checar resultados do questionario socioeconômico.

### Navegação

Use o menu lateral para acessar:
- **Análise Brasil**: Visão geral dos dados de todo o país
- **Comparação**: Compare dois grupos diferentes de filtros
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
    citation="Como citar: BORBA, J. O. V. ; XAVIER, C. C. Mapeando o desempenho e o perfil do estudante no Enade: uma plataforma interativa para comparações interinstitucionais. Sorocaba, SP, 2026."
)
