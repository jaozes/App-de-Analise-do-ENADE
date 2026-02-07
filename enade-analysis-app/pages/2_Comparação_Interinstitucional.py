import streamlit as st
import pandas as pd
import plotly.express as px
from utils.header import show_logo
from utils.footer import show_footer

show_logo()

st.set_page_config(layout="wide", page_title="Comparação Interinstitucional - ENADE 2023")

# Carregar os dados
@st.cache_data
def load_data():
    df = pd.read_excel('enade-analysis-app/data/conceito_enade_2023.xlsx', engine='openpyxl')
    # Remover linhas onde 'Conceito Enade (Contínuo)' é NaN
    df = df.dropna(subset=['Conceito Enade (Contínuo)'])
    return df

df = load_data()

# Função para filtrar dataframe com base nas seleções
def get_filtered_df(uf, municipio, ies, curso, modalidade, categoria, grau):
    filtered = df.copy()
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

# Inicializar session state para filtros
for key in ['uf1', 'mun1', 'ies1', 'curso1', 'mod1', 'cat1', 'grau1', 'uf2', 'mun2', 'ies2', 'curso2', 'mod2', 'cat2', 'grau2']:
    if key not in st.session_state:
        st.session_state[key] = []

# Título
st.title('Médias do Conceito Enade por Curso')

st.markdown("""- Por padrão os gráficos exibem os dados de todo o país.""")

# Opções compartilhadas
uf_options = sorted(df['Sigla da UF** '].dropna().unique())

# Criar duas colunas para exibição lado a lado
col1, col2 = st.columns(2)

# Seção do primeiro gráfico
with col1:
    st.header('1ª Instituição - Filtros')

    # Filtros para Primeiro Gráfico
    filter_cols1_row1 = st.columns(4)
    with filter_cols1_row1[0]:
        uf_options1 = sorted(df['Sigla da UF** '].dropna().unique())
        selected_uf = st.multiselect('UF', uf_options1, default=st.session_state.uf1, key='uf1')
    with filter_cols1_row1[1]:
        municipio_options1 = sorted(get_filtered_df(st.session_state.uf1, None, st.session_state.ies1, st.session_state.curso1, st.session_state.mod1, st.session_state.cat1, st.session_state.grau1)['Município do Curso**'].dropna().unique())
        selected_municipio = st.multiselect('Município', municipio_options1, default=st.session_state.mun1, key='mun1')
    with filter_cols1_row1[2]:
        ies_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, None, st.session_state.curso1, st.session_state.mod1, st.session_state.cat1, st.session_state.grau1)['Nome da IES*'].dropna().unique())
        selected_ies = st.multiselect('IES', ies_options1, default=st.session_state.ies1, key='ies1')
    with filter_cols1_row1[3]:
        curso_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, st.session_state.ies1, None, st.session_state.mod1, st.session_state.cat1, st.session_state.grau1)['Área de Avaliação'].dropna().unique())
        selected_curso = st.multiselect('Curso', curso_options1, default=st.session_state.curso1, key='curso1')

    filter_cols1_row2 = st.columns(3)
    with filter_cols1_row2[0]:
        modalidade_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, st.session_state.ies1, st.session_state.curso1, None, st.session_state.cat1, st.session_state.grau1)['Modalidade de Ensino'].dropna().unique())
        selected_modalidade = st.multiselect('Modalidade', modalidade_options1, default=st.session_state.mod1, key='mod1')
    with filter_cols1_row2[1]:
        categoria_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, st.session_state.ies1, st.session_state.curso1, st.session_state.mod1, None, st.session_state.grau1)['Categoria Administrativa'].dropna().unique())
        selected_categoria = st.multiselect('Categoria', categoria_options1, default=st.session_state.cat1, key='cat1')
    with filter_cols1_row2[2]:
        grau_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, st.session_state.ies1, st.session_state.curso1, st.session_state.mod1, st.session_state.cat1, None)['Grau Acadêmico'].dropna().unique())
        selected_grau = st.multiselect('Grau', grau_options1, default=st.session_state.grau1, key='grau1')

    # Filtrar o dataframe para o primeiro gráfico
    filtered_df = df.copy()
    if selected_uf:
        filtered_df = filtered_df[filtered_df['Sigla da UF** '].isin(selected_uf)]
    if selected_municipio:
        filtered_df = filtered_df[filtered_df['Município do Curso**'].isin(selected_municipio)]
    if selected_ies:
        filtered_df = filtered_df[filtered_df['Nome da IES*'].isin(selected_ies)]
    if selected_curso:
        filtered_df = filtered_df[filtered_df['Área de Avaliação'].isin(selected_curso)]
    if selected_modalidade:
        filtered_df = filtered_df[filtered_df['Modalidade de Ensino'].isin(selected_modalidade)]
    if selected_categoria:
        filtered_df = filtered_df[filtered_df['Categoria Administrativa'].isin(selected_categoria)]
    if selected_grau:
        filtered_df = filtered_df[filtered_df['Grau Acadêmico'].isin(selected_grau)]

    if not filtered_df.empty:
        avg_df = filtered_df.groupby('Área de Avaliação')['Conceito Enade (Contínuo)'].mean().reset_index()
        avg_df['Média'] = avg_df['Conceito Enade (Contínuo)'].round(2)
        avg_df = avg_df.sort_values('Média', ascending=False)

        # Gráfico Plotly
        st.subheader('1º Gráfico das Médias por Curso')
        fig = px.bar(avg_df, x='Área de Avaliação', y='Média', color='Área de Avaliação', color_discrete_sequence=px.colors.qualitative.Dark24)
        fig.update_layout(xaxis_title='Curso', yaxis_title='Média do Conceito Enade (Contínuo)', xaxis_tickangle=-45, height=600, width=1200, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, width='stretch')

        # Exibir tabela
        st.subheader('Médias por Curso')
        st.dataframe(avg_df[['Área de Avaliação', 'Média']], height=400, width='stretch')
    else:
        st.write('Nenhum dado encontrado com os filtros selecionados para o primeiro gráfico.')

# Seção do segundo gráfico
with col2:
    st.header('2ª Instituição - Filtros')

    # Filtros para Segundo Gráfico
    filter_cols2_row1 = st.columns(4)
    with filter_cols2_row1[0]:
        uf_options2 = sorted(get_filtered_df(None, st.session_state.mun2, st.session_state.ies2, st.session_state.curso2, st.session_state.mod2, st.session_state.cat2, st.session_state.grau2)['Sigla da UF** '].dropna().unique())
        selected_uf2 = st.multiselect('UF', uf_options2, default=st.session_state.uf2, key='uf2')
    with filter_cols2_row1[1]:
        municipio_options2 = sorted(get_filtered_df(st.session_state.uf2, None, st.session_state.ies2, st.session_state.curso2, st.session_state.mod2, st.session_state.cat2, st.session_state.grau2)['Município do Curso**'].dropna().unique())
        selected_municipio2 = st.multiselect('Município', municipio_options2, default=st.session_state.mun2, key='mun2')
    with filter_cols2_row1[2]:
        ies_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, None, st.session_state.curso2, st.session_state.mod2, st.session_state.cat2, st.session_state.grau2)['Nome da IES*'].dropna().unique())
        selected_ies2 = st.multiselect('IES', ies_options2, default=st.session_state.ies2, key='ies2')
    with filter_cols2_row1[3]:
        curso_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, st.session_state.ies2, None, st.session_state.mod2, st.session_state.cat2, st.session_state.grau2)['Área de Avaliação'].dropna().unique())
        selected_curso2 = st.multiselect('Curso', curso_options2, default=st.session_state.curso2, key='curso2')

    filter_cols2_row2 = st.columns(3)
    with filter_cols2_row2[0]:
        modalidade_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, st.session_state.ies2, st.session_state.curso2, None, st.session_state.cat2, st.session_state.grau2)['Modalidade de Ensino'].dropna().unique())
        selected_modalidade2 = st.multiselect('Modalidade', modalidade_options2, default=st.session_state.mod2, key='mod2')
    with filter_cols2_row2[1]:
        categoria_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, st.session_state.ies2, st.session_state.curso2, st.session_state.mod2, None, st.session_state.grau2)['Categoria Administrativa'].dropna().unique())
        selected_categoria2 = st.multiselect('Categoria', categoria_options2, default=st.session_state.cat2, key='cat2')
    with filter_cols2_row2[2]:
        grau_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, st.session_state.ies2, st.session_state.curso2, st.session_state.mod2, st.session_state.cat2, None)['Grau Acadêmico'].dropna().unique())
        selected_grau2 = st.multiselect('Grau', grau_options2, default=st.session_state.grau2, key='grau2')

    # Filtrar o dataframe para o segundo gráfico
    filtered_df2 = df.copy()
    if selected_uf2:
        filtered_df2 = filtered_df2[filtered_df2['Sigla da UF** '].isin(selected_uf2)]
    if selected_municipio2:
        filtered_df2 = filtered_df2[filtered_df2['Município do Curso**'].isin(selected_municipio2)]
    if selected_ies2:
        filtered_df2 = filtered_df2[filtered_df2['Nome da IES*'].isin(selected_ies2)]
    if selected_curso2:
        filtered_df2 = filtered_df2[filtered_df2['Área de Avaliação'].isin(selected_curso2)]
    if selected_modalidade2:
        filtered_df2 = filtered_df2[filtered_df2['Modalidade de Ensino'].isin(selected_modalidade2)]
    if selected_categoria2:
        filtered_df2 = filtered_df2[filtered_df2['Categoria Administrativa'].isin(selected_categoria2)]
    if selected_grau2:
        filtered_df2 = filtered_df2[filtered_df2['Grau Acadêmico'].isin(selected_grau2)]

    if not filtered_df2.empty:
        avg_df2 = filtered_df2.groupby('Área de Avaliação')['Conceito Enade (Contínuo)'].mean().reset_index()
        avg_df2['Média'] = avg_df2['Conceito Enade (Contínuo)'].round(2)
        avg_df2 = avg_df2.sort_values('Média', ascending=False)

        # Segundo gráfico: Gráfico de barras vertical
        st.subheader('2º Gráfico das Médias por Curso')
        fig2 = px.bar(avg_df2, x='Área de Avaliação', y='Média', color='Área de Avaliação', color_discrete_sequence=px.colors.qualitative.Light24)
        fig2.update_layout(xaxis_title='Curso', yaxis_title='Média do Conceito Enade (Contínuo)', xaxis_tickangle=-45, height=600, width=1200, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig2, width='stretch')

        # Exibir tabela
        st.subheader('Médias por Curso')
        st.dataframe(avg_df2[['Área de Avaliação', 'Média']], height=400, width='stretch')
    else:
        st.write('Nenhum dado encontrado com os filtros selecionados para o segundo gráfico.')

show_footer(
    advisor_text="Orientador: Prof. Dr. César Cândido Xavier • Email: cesarcx@gmail.com",
    text="Pesquisador: João Octavio Venâncio Borba • UNISO - Universidade de Sorocaba • Email: joaooctaviov.borba@gmail.com",
    links=[("Github", "https://github.com/jaozes"), ("LinkedIn", "https://www.linkedin.com/in/jo%C3%A3o-octavio-vb/"), ("Currículo Lattes", "http://lattes.cnpq.br/0821075410761662")],
    bg_color="#ffffff",
    text_color="#000000",
    height_px=56
)