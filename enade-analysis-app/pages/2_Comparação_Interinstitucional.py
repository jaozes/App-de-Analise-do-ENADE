import streamlit as st
import pandas as pd
import plotly.express as px
from utils.header import show_logo
from utils.footer import show_footer
from utils.header import inject_css

inject_css()
show_logo()

st.set_page_config(layout="wide", page_title="Comparação Interinstitucional - ENADE 2023")

# Carregar os dados
from utils.data_loader import load_conceito

df = load_conceito()

# abreviações dos cursos para exibição nos eixos X
ABBR = {
    "AGRONOMIA": "AG",
    "ARQUITETURA E URBANISMO": "AR",
    "BIOMEDICINA": "BM",
    "ENFERMAGEM": "EN",
    "ENGENHARIA AMBIENTAL": "EA",
    "ENGENHARIA CIVIL": "CV",
    "ENGENHARIA DE ALIMENTOS": "AL",
    "ENGENHARIA DE COMPUTAÇÃO I": "CI",
    "ENGENHARIA DE CONTROLE E AUTOMAÇÃO": "CA",
    "ENGENHARIA DE PRODUÇÃO": "PR",
    "ENGENHARIA ELÉTRICA": "EL",
    "ENGENHARIA FLORESTAL": "FL",
    "ENGENHARIA MECÂNICA": "MC",
    "ENGENHARIA QUÍMICA": "EQ",
    "FARMÁCIA": "FA",
    "FISIOTERAPIA": "FI",
    "FONOAUDIOLOGIA": "FO",
    "MEDICINA": "ME",
    "MEDICINA VETERINÁRIA": "MV",
    "NUTRIÇÃO": "NU",
    "ODONTOLOGIA": "OD",
    "TECNOLOGIA EM AGRONEGÓCIOS": "AN",
    "TECNOLOGIA EM ESTÉTICA E COSMÉTICA": "EC",
    "TECNOLOGIA EM GESTÃO AMBIENTAL": "GA",
    "TECNOLOGIA EM GESTÃO HOSPITALAR": "GH",
    "TECNOLOGIA EM RADIOLOGIA": "RA",
    "TECNOLOGIA EM SEGURANÇA NO TRABALHO": "ST",
    "ZOOTECNIA": "ZO"
}

# coluna abreviada (mantém o nome original para outros usos)
df['Área_abrev'] = df['Área de Avaliação'].map(ABBR).fillna(df['Área de Avaliação'])

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
        selected_uf = st.multiselect('UF', uf_options1, key='uf1')
    with filter_cols1_row1[1]:
        municipio_options1 = sorted(get_filtered_df(st.session_state.uf1, None, st.session_state.ies1, st.session_state.curso1, st.session_state.mod1, st.session_state.cat1, st.session_state.grau1)['Município do Curso**'].dropna().unique())
        selected_municipio = st.multiselect('Município', municipio_options1, key='mun1')
    with filter_cols1_row1[2]:
        ies_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, None, st.session_state.curso1, st.session_state.mod1, st.session_state.cat1, st.session_state.grau1)['Nome da IES*'].dropna().unique())
        selected_ies = st.multiselect('IES', ies_options1, key='ies1')
    with filter_cols1_row1[3]:
        curso_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, st.session_state.ies1, None, st.session_state.mod1, st.session_state.cat1, st.session_state.grau1)['Área de Avaliação'].dropna().unique())
        selected_curso = st.multiselect('Curso', curso_options1, key='curso1')

    filter_cols1_row2 = st.columns(3)
    with filter_cols1_row2[0]:
        modalidade_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, st.session_state.ies1, st.session_state.curso1, None, st.session_state.cat1, st.session_state.grau1)['Modalidade de Ensino'].dropna().unique())
        selected_modalidade = st.multiselect('Modalidade', modalidade_options1, key='mod1')
    with filter_cols1_row2[1]:
        categoria_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, st.session_state.ies1, st.session_state.curso1, st.session_state.mod1, None, st.session_state.grau1)['Categoria Administrativa'].dropna().unique())
        selected_categoria = st.multiselect('Categoria', categoria_options1, key='cat1')
    with filter_cols1_row2[2]:
        grau_options1 = sorted(get_filtered_df(st.session_state.uf1, st.session_state.mun1, st.session_state.ies1, st.session_state.curso1, st.session_state.mod1, st.session_state.cat1, None)['Grau Acadêmico'].dropna().unique())
        selected_grau = st.multiselect('Grau', grau_options1, key='grau1')

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

# Seção do segundo gráfico
with col2:
    st.header('2ª Instituição - Filtros')

    # Filtros para Segundo Gráfico
    filter_cols2_row1 = st.columns(4)
    with filter_cols2_row1[0]:
        uf_options2 = sorted(get_filtered_df(None, st.session_state.mun2, st.session_state.ies2, st.session_state.curso2, st.session_state.mod2, st.session_state.cat2, st.session_state.grau2)['Sigla da UF** '].dropna().unique())
        selected_uf2 = st.multiselect('UF', uf_options2, key='uf2')
    with filter_cols2_row1[1]:
        municipio_options2 = sorted(get_filtered_df(st.session_state.uf2, None, st.session_state.ies2, st.session_state.curso2, st.session_state.mod2, st.session_state.cat2, st.session_state.grau2)['Município do Curso**'].dropna().unique())
        selected_municipio2 = st.multiselect('Município', municipio_options2, key='mun2')
    with filter_cols2_row1[2]:
        ies_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, None, st.session_state.curso2, st.session_state.mod2, st.session_state.cat2, st.session_state.grau2)['Nome da IES*'].dropna().unique())
        selected_ies2 = st.multiselect('IES', ies_options2, key='ies2')
    with filter_cols2_row1[3]:
        curso_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, st.session_state.ies2, None, st.session_state.mod2, st.session_state.cat2, st.session_state.grau2)['Área de Avaliação'].dropna().unique())
        selected_curso2 = st.multiselect('Curso', curso_options2, key='curso2')

    filter_cols2_row2 = st.columns(3)
    with filter_cols2_row2[0]:
        modalidade_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, st.session_state.ies2, st.session_state.curso2, None, st.session_state.cat2, st.session_state.grau2)['Modalidade de Ensino'].dropna().unique())
        selected_modalidade2 = st.multiselect('Modalidade', modalidade_options2, key='mod2')
    with filter_cols2_row2[1]:
        categoria_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, st.session_state.ies2, st.session_state.curso2, st.session_state.mod2, None, st.session_state.grau2)['Categoria Administrativa'].dropna().unique())
        selected_categoria2 = st.multiselect('Categoria', categoria_options2, key='cat2')
    with filter_cols2_row2[2]:
        grau_options2 = sorted(get_filtered_df(st.session_state.uf2, st.session_state.mun2, st.session_state.ies2, st.session_state.curso2, st.session_state.mod2, st.session_state.cat2, None)['Grau Acadêmico'].dropna().unique())
        selected_grau2 = st.multiselect('Grau', grau_options2, key='grau2')

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

# Seção do gráfico comparativo
st.markdown("---")
st.header('📊 Comparação Interinstitucional')

# Checkbox para mostrar apenas cursos em comum
apenas_comum = st.checkbox("Mostrar apenas cursos em comum", value=False)

# Verificar se ambos os dataframes têm dados
if not filtered_df.empty and not filtered_df2.empty:
    # Determinar nome da instituição 1
    if selected_ies and len(selected_ies) == 1:
        nome_inst1 = selected_ies[0]
    else:
        nome_inst1 = "Instituição 1"
    
    # Determinar nome da instituição 2
    if selected_ies2 and len(selected_ies2) == 1:
        nome_inst2 = selected_ies2[0]
    else:
        nome_inst2 = "Instituição 2"
    
    # Recalcular os dataframes sem o sort para manter a ordem original
    # agrupa pelo nome original para manter coluna completa, depois adiciona abreviatura
    avg_df = filtered_df.groupby('Área de Avaliação')['Conceito Enade (Contínuo)'].mean().reset_index()
    avg_df['Área_abrev'] = avg_df['Área de Avaliação'].map(ABBR).fillna(avg_df['Área de Avaliação'])
    avg_df['Média'] = avg_df['Conceito Enade (Contínuo)'].round(2)
    avg_df["Instituicao"] = nome_inst1
    avg_df = avg_df.rename(columns={'Área_abrev': 'Sigla Área'})
    
    avg_df2 = filtered_df2.groupby('Área de Avaliação')['Conceito Enade (Contínuo)'].mean().reset_index()
    avg_df2['Área_abrev'] = avg_df2['Área de Avaliação'].map(ABBR).fillna(avg_df2['Área de Avaliação'])
    avg_df2['Média'] = avg_df2['Conceito Enade (Contínuo)'].round(2)
    avg_df2["Instituicao"] = nome_inst2
    avg_df2 = avg_df2.rename(columns={'Área_abrev': 'Sigla Área'})
    
    # Unir os dois dataframes
    df_comparacao = pd.concat([avg_df, avg_df2], ignore_index=True)
    
    # Se checkbox marcado, filtrar apenas cursos em comum
    if apenas_comum:
        # Encontrar cursos presentes em ambas as instituições
        cursos_inst1 = set(avg_df['Área de Avaliação'].unique())
        cursos_inst2 = set(avg_df2['Área de Avaliação'].unique())
        cursos_comum = cursos_inst1.intersection(cursos_inst2)
        
        # Filtrar para manter apenas cursos em comum
        df_comparacao = df_comparacao[df_comparacao['Área de Avaliação'].isin(cursos_comum)]
        avg_df = avg_df[avg_df['Área de Avaliação'].isin(cursos_comum)]
        avg_df2 = avg_df2[avg_df2['Área de Avaliação'].isin(cursos_comum)]
    
    # Obter lista de cursos ordenada (ordem decrescente pela média combinada)
    # ordenar com base na abreviatura para manter eixo X curto
    cursos_ordenados = df_comparacao.groupby('Sigla Área')['Média'].mean().sort_values(ascending=False).index.tolist()
    
    # Converter colunas para categoria ordenada usando abreviação
    df_comparacao['Sigla Área'] = pd.Categorical(df_comparacao['Sigla Área'], categories=cursos_ordenados, ordered=True)
    df_comparacao = df_comparacao.sort_values(['Sigla Área', 'Instituicao'])
    
    # Criar gráfico de linha comparativo
    fig_comparativo = px.line(
        df_comparacao, 
        x='Sigla Área', 
        y='Média', 
        color='Instituicao',
        markers=True,
        line_shape='linear',
        title="",
        custom_data=['Área de Avaliação','Instituicao']
    )
    fig_comparativo.update_layout(
        title="",
        xaxis_tickangle=0,
        template="plotly_white",
        xaxis_title='Curso',
        yaxis_title='Média do Conceito ENADE',
        height=600
    )
    fig_comparativo.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Instituição: %{customdata[1]}<br>Média: %{y:.2f}<extra></extra>', hoverlabel=dict(font=dict(size=14)), line=dict(width=4), marker=dict(size=8))
    # Forçar a ordem dos cursos no eixo X (já são abreviados)
    fig_comparativo.update_xaxes(categoryorder='array', categoryarray=cursos_ordenados)
    st.plotly_chart(fig_comparativo, width='stretch')
    
    # Exibir tabelas de médias por curso de cada instituição
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        st.subheader(f'{nome_inst1} - Médias por Curso')
        # mostramos também a abreviatura para facilitar visualização
        st.dataframe(avg_df[['Sigla Área','Área de Avaliação', 'Média']], height=400, width='stretch')
    with col_tab2:
        st.subheader(f'{nome_inst2} - Médias por Curso')
        st.dataframe(avg_df2[['Sigla Área','Área de Avaliação', 'Média']], height=400, width='stretch')
    
elif filtered_df.empty and filtered_df2.empty:
    st.write('Nenhum dado encontrado com os filtros selecionados para ambas as instituições.')
elif filtered_df.empty:
    st.write('Nenhum dado encontrado com os filtros selecionados para a primeira instituição.')
elif filtered_df2.empty:
    st.write('Nenhum dado encontrado com os filtros selecionados para a segunda instituição.')

show_footer(
    advisor_text="Orientador: Prof. Dr. César Candido Xavier • Email: cesarcx@gmail.com",
    text="Pesquisador: João Octavio Venâncio Borba • UNISO - Universidade de Sorocaba • Email: joaooctaviov.borba@gmail.com",
    links=[("Github", "https://github.com/jaozes"), ("LinkedIn", "https://www.linkedin.com/in/jo%C3%A3o-octavio-vb/"), ("Currículo Lattes", "http://lattes.cnpq.br/0821075410761662")],
    bg_color="#ffffff",
    text_color="#000000",
    height_px=56
)