import streamlit as st
import pandas as pd
import plotly.express as px
from utils.header import show_logo
from utils.footer import show_footer
from utils.data_loader import load_conceito
from utils.header import inject_css

inject_css()
show_logo()

st.set_page_config(layout="centered", page_title="Análise Geral do Brasil - ENADE 2023")

df = load_conceito()

# ABBR dict and df['Área_abrev'] = ... remain unchanged below

# abreviações dos cursos utilizados nos gráficos de eixo X
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

# adicionar coluna abreviada para facilitar o uso nos gráficos
df['Área_abrev'] = df['Área de Avaliação'].map(ABBR).fillna(df['Área de Avaliação'])

st.title("📊 Análise Geral do Brasil")

# Seleção de gráfico
opcoes_graficos = [
    "Média de Conceitos por Área de Avaliação",
    "Média por Estado",
    "Média por Modalidade de Ensino",
    "Quantidade de Alunos por Curso ou Estado",
    "Densidade de Cursos no Brasil",
    "Densidade Relativa de Percentual de Cursos"
]
grafico_selecionado = st.selectbox("Selecione o gráfico a exibir:", opcoes_graficos)

# Análise por Área
if grafico_selecionado == "Média de Conceitos por Área de Avaliação":
    col1, col2, col3 = st.columns(3)

    with col1:
        # Filtro por UF
        ufs_disponiveis = sorted(df['Sigla da UF** '].unique())
        ufs_selecionadas = st.multiselect(
            "Selecione as UFs:",
            options=ufs_disponiveis,
            default=[],
            help="Selecione uma ou mais UFs para filtrar os dados."
        )

    with col2:
        # Filtro por Modalidade de Ensino
        modalidades_disponiveis = sorted(df['Modalidade de Ensino'].unique())
        modalidades_selecionadas = st.multiselect(
            "Selecione as Modalidades:",
            options=modalidades_disponiveis,
            default=[],
            help="Selecione uma ou mais modalidades para filtrar os dados."
        )

    with col3:
        # Filtro por Categoria Administrativa
        categorias_disponiveis = sorted(df['Categoria Administrativa'].unique())
        categorias_selecionadas = st.multiselect(
            "Selecione as Categorias:",
            options=categorias_disponiveis,
            default=[],
            help="Selecione uma ou mais categorias para filtrar os dados."
        )

    # Filtro por Grau Acadêmico
    graus_disponiveis = sorted(df['Grau Acadêmico'].unique())
    graus_selecionados = st.multiselect(
        "Selecione os Graus:",
        options=graus_disponiveis,
        default=[],
        help="Selecione um ou mais graus para filtrar os dados."
    )

    # Aplicar filtro
    df_filtrado = df
    if ufs_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Sigla da UF** '].isin(ufs_selecionadas)]
    if modalidades_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Modalidade de Ensino'].isin(modalidades_selecionadas)]
    if categorias_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Categoria Administrativa'].isin(categorias_selecionadas)]
    if graus_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Grau Acadêmico'].isin(graus_selecionados)]

    st.subheader("📊 Média de Conceitos por Área de Avaliação")
    avg_area = df_filtrado.groupby('Área de Avaliação')['Conceito Enade (Contínuo)'].mean().reset_index().round(2)
    avg_area['Área_abrev'] = avg_area['Área de Avaliação'].map(ABBR).fillna(avg_area['Área de Avaliação'])
    avg_area.columns = ['Área de Avaliação', 'Média', 'Sigla Área']
    avg_area = avg_area.sort_values('Média', ascending=False)

    fig1 = px.bar(
        avg_area,
        x='Sigla Área',
        y='Média',
        color='Média',
        color_continuous_scale='Viridis',
        custom_data=['Área de Avaliação']
    )
    fig1.update_layout(
        title="",
        title_font=dict(size=26, family="Arial Black", color="#1f1f1f"),
        xaxis_tickangle=0, 
        xaxis_title='Curso',
        height=500,
        coloraxis=dict(
            colorbar=dict(
                len=1,
                yanchor='middle',
                y=0.5,
                thickness=15
            )
        )
    )
    fig1.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Média: %{y:.2f}<extra></extra>', hoverlabel=dict(font=dict(size=14)))
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📋 Dados da Análise")
    st.dataframe(avg_area, width='stretch')

# Análise por UF
elif grafico_selecionado == "Média por Estado":
    col1, col2 = st.columns(2)

    with col1:
        # Filtro por UF
        ufs_disponiveis = sorted(df['Sigla da UF** '].unique())
        ufs_selecionadas = st.multiselect(
            "Selecione as UFs:",
            options=ufs_disponiveis,
            default=[],
            help="Selecione uma ou mais UFs para filtrar os dados."
        )

    with col2:
        # Filtro por Área de Avaliação
        areas_disponiveis = sorted(df['Área de Avaliação'].unique())
        areas_selecionadas = st.multiselect(
            "Selecione as Áreas de Avaliação:",
            options=areas_disponiveis,
            default=[],
            help="Selecione uma ou mais áreas para filtrar os dados."
        )

    col3, col4, col5 = st.columns(3)

    with col3:
        # Filtro por Modalidade de Ensino
        modalidades_disponiveis = sorted(df['Modalidade de Ensino'].unique())
        modalidades_selecionadas = st.multiselect(
            "Selecione as Modalidades:",
            options=modalidades_disponiveis,
            default=[],
            help="Selecione uma ou mais modalidades para filtrar os dados."
        )

    with col4:
        # Filtro por Categoria Administrativa
        categorias_disponiveis = sorted(df['Categoria Administrativa'].unique())
        categorias_selecionadas = st.multiselect(
            "Selecione as Categorias:",
            options=categorias_disponiveis,
            default=[],
            help="Selecione uma ou mais categorias para filtrar os dados."
        )

    with col5:
        # Filtro por Grau Acadêmico
        graus_disponiveis = sorted(df['Grau Acadêmico'].unique())
        graus_selecionados = st.multiselect(
            "Selecione os Graus:",
            options=graus_disponiveis,
            default=[],
            help="Selecione um ou mais graus para filtrar os dados."
        )

    # Aplicar filtros
    df_filtrado = df
    if ufs_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Sigla da UF** '].isin(ufs_selecionadas)]
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Área de Avaliação'].isin(areas_selecionadas)]
    if modalidades_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Modalidade de Ensino'].isin(modalidades_selecionadas)]
    if categorias_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Categoria Administrativa'].isin(categorias_selecionadas)]
    if graus_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Grau Acadêmico'].isin(graus_selecionados)]


    avg_uf = df_filtrado.groupby('Sigla da UF** ')['Conceito Enade (Contínuo)'].mean().reset_index().round(2)
    avg_uf.columns = ['Estado', 'Média']
    avg_uf = avg_uf.sort_values('Média', ascending=False)

    st.subheader("🗺️ Média por Estado")
    fig2 = px.bar(avg_uf, x='Estado', y='Média', color='Média', color_continuous_scale='Blues')
    fig2.update_layout(
        title="",  # Remove title from inside chart
        title_font=dict(size=26, family="Arial Black", color="#1f1f1f"),
        coloraxis=dict(
            colorbar=dict(
                len=1,
                yanchor='middle',
                y=0.5,
                thickness=15
            )
        )
    )
    fig2.update_traces(hoverlabel=dict(font=dict(size=14)))
    st.plotly_chart(fig2, width='stretch')

    st.subheader("Dados da Análise")
    st.dataframe(avg_uf, width='stretch')

# Análise por Modalidade
elif grafico_selecionado == "Média por Modalidade de Ensino":
    col1, col2 = st.columns(2)

    with col1:
        # Filtro por UF
        ufs_disponiveis = sorted(df['Sigla da UF** '].unique())
        ufs_selecionadas = st.multiselect(
            "Selecione as UFs:",
            options=ufs_disponiveis,
            default=[],
            help="Selecione uma ou mais UFs para filtrar os dados."
        )

    with col2:
        # Filtro por Área de Avaliação
        areas_disponiveis = sorted(df['Área de Avaliação'].unique())
        areas_selecionadas = st.multiselect(
            "Selecione as Áreas de Avaliação:",
            options=areas_disponiveis,
            default=[],
            help="Selecione uma ou mais áreas para filtrar os dados."
        )

    col3, col4 = st.columns(2)

    with col3:
        # Filtro por Categoria Administrativa
        categorias_disponiveis = sorted(df['Categoria Administrativa'].unique())
        categorias_selecionadas = st.multiselect(
            "Selecione as Categorias:",
            options=categorias_disponiveis,
            default=[],
            help="Selecione uma ou mais categorias para filtrar os dados."
        )

    with col4:
        # Filtro por Grau Acadêmico
        graus_disponiveis = sorted(df['Grau Acadêmico'].unique())
        graus_selecionados = st.multiselect(
            "Selecione os Graus:",
            options=graus_disponiveis,
            default=[],
            help="Selecione um ou mais graus para filtrar os dados."
        )

    # Aplicar filtros
    df_filtrado = df
    if ufs_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Sigla da UF** '].isin(ufs_selecionadas)]
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Área de Avaliação'].isin(areas_selecionadas)]
    if categorias_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Categoria Administrativa'].isin(categorias_selecionadas)]
    if graus_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Grau Acadêmico'].isin(graus_selecionados)]


    avg_mod = df_filtrado.groupby('Modalidade de Ensino')['Conceito Enade (Contínuo)'].mean().reset_index().round(2)
    avg_mod.columns = ['Modalidade', 'Média']

    st.subheader("📋 Média por Modalidade de Ensino")
    fig3 = px.pie(avg_mod, names='Modalidade', values='Média', title="")
    fig3.update_traces(hoverlabel=dict(font=dict(size=14)))
    st.plotly_chart(fig3, width='stretch')

    st.subheader("Dados da Análise")
    st.dataframe(avg_mod, width='stretch')

# Análise de Quantidade de Alunos por Curso ou Estado
elif grafico_selecionado == "Quantidade de Alunos por Curso ou Estado":
    col1, col2 = st.columns(2)

    with col1:
        # Selector para tipo de quantidade de alunos
        tipo_quantidade = st.selectbox(
            "Selecione o tipo de quantidade:",
            options=["Nº de Concluintes Inscritos", "Nº de Concluintes Participantes"]
        )
        
        # Mapear para nomes das colunas
        coluna_quantidade = 'Nº de Concluintes Inscritos' if tipo_quantidade == "Nº de Concluintes Inscritos" else 'Nº  de Concluintes Participantes'

    with col2:
        # Selector para visualização por estado ou por curso
        tipo_visualizacao = st.selectbox(
            "Selecione a visualização:",
            options=["Por Estado", "Por Curso"]
        )

    col3, col4 = st.columns(2)

    with col3:
        # Filtro por UF
        ufs_disponiveis = sorted(df['Sigla da UF** '].unique())
        ufs_selecionadas = st.multiselect(
            "Selecione as UFs:",
            options=ufs_disponiveis,
            default=[],
            help="Selecione uma ou mais UFs para filtrar os dados."
        )

    with col4:
        # Filtro por Área de Avaliação
        areas_disponiveis = sorted(df['Área de Avaliação'].unique())
        areas_selecionadas = st.multiselect(
            "Selecione as Áreas de Avaliação:",
            options=areas_disponiveis,
            default=[],
            help="Selecione uma ou mais áreas para filtrar os dados."
        )

    col5, col6, col7 = st.columns(3)

    with col5:
        # Filtro por Modalidade de Ensino
        modalidades_disponiveis = sorted(df['Modalidade de Ensino'].unique())
        modalidades_selecionadas = st.multiselect(
            "Selecione as Modalidades:",
            options=modalidades_disponiveis,
            default=[],
            help="Selecione uma ou mais modalidades para filtrar os dados."
        )

    with col6:
        # Filtro por Categoria Administrativa
        categorias_disponiveis = sorted(df['Categoria Administrativa'].unique())
        categorias_selecionadas = st.multiselect(
            "Selecione as Categorias:",
            options=categorias_disponiveis,
            default=[],
            help="Selecione uma ou mais categorias para filtrar os dados."
        )

    with col7:
        # Filtro por Grau Acadêmico
        graus_disponiveis = sorted(df['Grau Acadêmico'].unique())
        graus_selecionados = st.multiselect(
            "Selecione os Graus:",
            options=graus_disponiveis,
            default=[],
            help="Selecione um ou mais graus para filtrar os dados."
        )

    # Aplicar filtros
    df_filtrado = df
    if ufs_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Sigla da UF** '].isin(ufs_selecionadas)]
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Área de Avaliação'].isin(areas_selecionadas)]
    if modalidades_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Modalidade de Ensino'].isin(modalidades_selecionadas)]
    if categorias_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Categoria Administrativa'].isin(categorias_selecionadas)]
    if graus_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Grau Acadêmico'].isin(graus_selecionados)]



    if tipo_visualizacao == "Por Estado":
        # Agrupar por Estado
        qtd_por_estado = df_filtrado.groupby('Sigla da UF** ')[coluna_quantidade].sum().reset_index()
        qtd_por_estado.columns = ['Estado', 'Valor']
        qtd_por_estado = qtd_por_estado.sort_values('Valor', ascending=False)

        # Criar coluna formatada para texto
        qtd_por_estado['Quantidade'] = qtd_por_estado['Valor'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

        st.subheader("👥 Quantidade de Alunos por Estado")
        fig4 = px.bar(
            qtd_por_estado, 
            x='Estado', 
            y='Valor', 
            color='Valor', 
            color_continuous_scale='Greens',
            custom_data=['Quantidade']
        )
        fig4.update_layout(
            title="",
            xaxis_tickangle=0,
            height=500,
            coloraxis=dict(
                colorbar=dict(
                    len=1,
                    yanchor='middle',
                    y=0.5,
                    thickness=15
                )
            )
        )
        fig4.update_traces(hovertemplate='<b>%{x}</b><br>Quantidade: %{customdata[0]}<extra></extra>', hoverlabel=dict(font=dict(size=14)))
        st.plotly_chart(fig4, width='stretch')
        
        st.subheader("Dados da Análise")
        st.dataframe(
            qtd_por_estado[['Estado', 'Quantidade']], 
            width='stretch',
            hide_index=True
        )

    else:
        # Agrupar por Curso (Área de Avaliação) e criar abreviação
        qtd_por_curso = df_filtrado.groupby('Área de Avaliação')[coluna_quantidade].sum().reset_index()
        qtd_por_curso['Área_abrev'] = qtd_por_curso['Área de Avaliação'].map(ABBR).fillna(qtd_por_curso['Área de Avaliação'])
        qtd_por_curso.columns = ['Área de Avaliação', 'Valor', 'Área_abrev']
        qtd_por_curso = qtd_por_curso.sort_values('Valor', ascending=False)

        # Criar coluna formatada para texto
        qtd_por_curso['Quantidade'] = qtd_por_curso['Valor'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

        st.subheader("📚 Quantidade de Alunos por Curso")
        fig5 = px.bar(
            qtd_por_curso, 
            x='Área_abrev', 
            y='Valor', 
            color='Valor', 
            color_continuous_scale='Oranges',
            custom_data=['Quantidade']
        )
        fig5.update_layout(
            title="",
            title_font=dict(size=26, family="Arial Black", color="#1f1f1f"),
            xaxis_tickangle=0,
            xaxis_title='Curso',
            height=500,
            coloraxis=dict(
                colorbar=dict(
                    len=1,
                    yanchor='middle',
                    y=0.5,
                    thickness=15
                )
            )
        )
        fig5.update_traces(hovertemplate='<b>%{x}</b><br>Quantidade: %{customdata[0]}<extra></extra>', hoverlabel=dict(font=dict(size=14)))
        st.plotly_chart(fig5, width='stretch')
        
        st.subheader("Dados da Análise")
        display_df = qtd_por_curso[['Área de Avaliação', 'Área_abrev', 'Quantidade']].copy()
        display_df.columns = ['Nome do Curso', 'Sigla', 'Quantidade']
        st.dataframe(
            display_df, 
            width='stretch',
            hide_index=True
        )

# Análise de Densidade de Cursos no Brasil
elif grafico_selecionado == "Densidade de Cursos no Brasil":
    import plotly.graph_objects as go
    import requests
    
    col1 = st.columns(1)

    with col1[0]:
        # Filtro por Área de Avaliação
        areas_disponiveis = sorted(df['Área de Avaliação'].unique())
        areas_selecionadas = st.multiselect(
            "Selecione as Áreas de Avaliação:",
            options=areas_disponiveis,
            default=[],
            help="Selecione uma ou mais áreas para filtrar os dados."
        )

    col2, col3, col4 = st.columns(3)

    with col2:
        # Filtro por Modalidade de Ensino
        modalidades_disponiveis = sorted(df['Modalidade de Ensino'].unique())
        modalidades_selecionadas = st.multiselect(
            "Selecione as Modalidades:",
            options=modalidades_disponiveis,
            default=[],
            help="Selecione uma ou mais modalidades para filtrar os dados."
        )

    with col3:
        # Filtro por Categoria Administrativa
        categorias_disponiveis = sorted(df['Categoria Administrativa'].unique())
        categorias_selecionadas = st.multiselect(
            "Selecione as Categorias:",
            options=categorias_disponiveis,
            default=[],
            help="Selecione uma ou mais categorias para filtrar os dados."
        )

    with col4:
        # Filtro por Grau Acadêmico
        graus_disponiveis = sorted(df['Grau Acadêmico'].unique())
        graus_selecionados = st.multiselect(
            "Selecione os Graus:",
            options=graus_disponiveis,
            default=[],
            help="Selecione um ou mais graus para filtrar os dados."
        )

    # Aplicar filtros
    df_filtrado = df
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Área de Avaliação'].isin(areas_selecionadas)]
    if modalidades_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Modalidade de Ensino'].isin(modalidades_selecionadas)]
    if categorias_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Categoria Administrativa'].isin(categorias_selecionadas)]
    if graus_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Grau Acadêmico'].isin(graus_selecionados)]

    # Lista de todos os estados do Brasil (27 estados)
    todos_estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
                     'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 
                     'SP', 'SE', 'TO']
    
    # Calcular quantidade de cursos por estado
    cursos_por_estado = df_filtrado.groupby('Sigla da UF** ').size().reset_index()
    cursos_por_estado.columns = ['Estado', 'Quantidade de Cursos']
    
    # Adicionar estados que não têm cursos com valor 0
    estados_faltantes = [e for e in todos_estados if e not in cursos_por_estado['Estado'].values]
    if estados_faltantes:
        df_faltantes = pd.DataFrame({
            'Estado': estados_faltantes,
            'Quantidade de Cursos': 0
        })
        cursos_por_estado = pd.concat([cursos_por_estado, df_faltantes], ignore_index=True)
    
    # Calcular total de cursos (para densidade relativa)
    total_cursos = cursos_por_estado['Quantidade de Cursos'].sum()
    
    # Calcular densidade relativa (porcentagem)
    cursos_por_estado['Densidade Relativa (%)'] = (cursos_por_estado['Quantidade de Cursos'] / total_cursos * 100).round(2)
    
    # Ordenar por quantidade de cursos
    cursos_por_estado = cursos_por_estado.sort_values('Quantidade de Cursos', ascending=False)
    

    
    # Carregar GeoJSON do Brasil
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    response = requests.get(geojson_url)
    brazil_states = response.json()
    
    # Escala de cores para densidade (tons de vermelho)
    custom_colorscale = [
        [0, "#ffffff"],      # 0% - muito claro
        [0.2, "#fee0d2"],    # 5%
        [0.4, "#fcbba1"],    # 10%
        [0.5, "#fc9272"],    # 15%
        [0.6, "#fb6a4a"],    # 20%
        [0.7, "#ef3b2c"],    # 25%
        [0.8, "#cb181d"],    # 30%
        [1, "#990000"]       # mais intenso
    ]
    
    # Encontrar o valor máximo de densidade para escala
    max_densidade = cursos_por_estado['Densidade Relativa (%)'].max()
    
    # Criar mapa choropleth usando plotly.graph_objects (mesmo método da Home.py)
    st.subheader("🗺️ Densidade de Cursos no Brasil")
    fig_densidade = go.Figure(go.Choropleth(
        geojson=brazil_states,
        locations=cursos_por_estado['Estado'],
        z=cursos_por_estado['Densidade Relativa (%)'],
        featureidkey="properties.sigla",
        colorscale=custom_colorscale,
        zmin=0,
        zmax=max_densidade,
        hovertemplate='<b>%{location}</b><br>' +
                      'Quantidade de Cursos: %{customdata[0]}<br>' +
                      'Densidade Relativa: %{customdata[1]:.2f}%<extra></extra>',
        customdata=cursos_por_estado[['Quantidade de Cursos', 'Densidade Relativa (%)']].values
    ))
    
    fig_densidade.update_geos(
        scope='south america',
        showlakes=True,
        lakecolor='rgb(255, 255, 255)',
        fitbounds="locations",
        visible=False
    )
    
    fig_densidade.update_layout(
        title="",  # Remove title from inside chart
        title_font=dict(size=26, family="Arial Black", color="#1f1f1f"),
        margin=dict(r=0, t=30, l=0, b=0),
        height=600
    )
    fig_densidade.update_traces(hoverlabel=dict(font=dict(size=14)))
    st.plotly_chart(fig_densidade, width='stretch')
    
    st.subheader("Dados da Análise")
    # Exibir tabela formatada
    tabela_dados = cursos_por_estado[['Estado', 'Quantidade de Cursos', 'Densidade Relativa (%)']].copy()
    tabela_dados['Densidade Relativa (%)'] = tabela_dados['Densidade Relativa (%)'].apply(lambda x: f"{x:.2f}%")
    st.dataframe(
        tabela_dados,
        width='stretch',
        hide_index=True
    )

# Novo mapa: Densidade Relativa de Percentual de Cursos
elif grafico_selecionado == "Densidade Relativa de Percentual de Cursos":
    import plotly.graph_objects as go
    import requests

    # criar layout com colunas para filtros
    col1 = st.columns(1)

    with col1[0]:
        # Filtro por Área de Avaliação
        areas_disponiveis = sorted(df['Área de Avaliação'].unique())
        areas_selecionadas = st.multiselect(
            "Selecione as Áreas de Avaliação:",
            options=areas_disponiveis,
            default=[],
            help="Selecione uma ou mais áreas para filtrar os dados."
        )

    col2, col3, col4 = st.columns(3)
    with col2:
        modalidades_disponiveis = sorted(df['Modalidade de Ensino'].unique())
        modalidades_selecionadas = st.multiselect(
            "Selecione as Modalidades:",
            options=modalidades_disponiveis,
            default=[],
            help="Selecione uma ou mais modalidades para filtrar os dados."
        )
    with col3:
        categorias_disponiveis = sorted(df['Categoria Administrativa'].unique())
        categorias_selecionadas = st.multiselect(
            "Selecione as Categorias:",
            options=categorias_disponiveis,
            default=[],
            help="Selecione uma ou mais categorias para filtrar os dados."
        )
    with col4:
        graus_disponiveis = sorted(df['Grau Acadêmico'].unique())
        graus_selecionados = st.multiselect(
            "Selecione os Graus:",
            options=graus_disponiveis,
            default=[],
            help="Selecione um ou mais graus para filtrar os dados."
        )

    # Aplicar filtros conforme outros mapas
    df_filtrado = df
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Área de Avaliação'].isin(areas_selecionadas)]
    if modalidades_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Modalidade de Ensino'].isin(modalidades_selecionadas)]
    if categorias_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Categoria Administrativa'].isin(categorias_selecionadas)]
    if graus_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Grau Acadêmico'].isin(graus_selecionados)]

    # Cálculos para alunos por instituição
    alunos_por_estado = df_filtrado.groupby('Sigla da UF** ')["Nº de Concluintes Inscritos"].sum().reset_index()
    instituicoes_por_estado = df_filtrado.groupby('Sigla da UF** ')["Código da IES"].nunique().reset_index()
    instituicoes_por_estado.columns = ['Estado', 'Instituições']
    alunos_por_estado.columns = ['Estado', 'Alunos']

    merged = pd.merge(alunos_por_estado, instituicoes_por_estado, on='Estado', how='outer').fillna(0)
    merged['Ratio'] = merged.apply(lambda r: r['Alunos']/r['Instituições'] if r['Instituições'] > 0 else 0, axis=1)

    # Criar colunas com formatação brasileira (ponto mil, vírgula decimal)
    fmt = lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    merged['Alunos_fmt'] = merged['Alunos'].apply(lambda x: f"{x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    merged['Instituições_fmt'] = merged['Instituições'].apply(lambda x: f"{x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    merged['Ratio_fmt'] = merged['Ratio'].apply(fmt)

    # Garantir todos os estados presentes
    todos_estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
                     'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 
                     'SP', 'SE', 'TO']
    estados_faltantes = [e for e in todos_estados if e not in merged['Estado'].values]
    if estados_faltantes:
        df_faltantes = pd.DataFrame({
            'Estado': estados_faltantes,
            'Alunos': 0,
            'Instituições': 0,
            'Ratio': 0
        })
        merged = pd.concat([merged, df_faltantes], ignore_index=True)

    # Preparar mapa
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    response = requests.get(geojson_url)
    brazil_states = response.json()

    max_ratio = merged['Ratio'].max()
    custom_colorscale = [
        [0, "#ffffff"],
        [0.2, "#edf8fb"],
        [0.4, "#b2e2e2"],
        [0.6, "#66c2a4"],
        [0.8, "#2ca25f"],
        [1, "#006d2c"]
    ]

    fig_ratio = go.Figure(go.Choropleth(
        geojson=brazil_states,
        locations=merged['Estado'],
        z=merged['Ratio'],
        featureidkey="properties.sigla",
        colorscale=custom_colorscale,
        zmin=0,
        zmax=max_ratio,
        hovertemplate='<b>%{location}</b><br>' +
                      'Alunos: %{customdata[0]}<br>' +
                      'Instituições: %{customdata[1]}<br>' +
                      'Alunos/IES: %{customdata[2]}<extra></extra>',
        customdata=merged[['Alunos_fmt', 'Instituições_fmt', 'Ratio_fmt']].values
    ))

    fig_ratio.update_geos(
        scope='south america',
        showlakes=True,
        lakecolor='rgb(255, 255, 255)',
        fitbounds="locations",
        visible=False
    )

    st.subheader("📊 Densidade Relativa de Alunos por IES")
    fig_ratio.update_layout(
        title="",  # Remove title from inside chart
        title_font=dict(size=26, family="Arial Black", color="#1f1f1f"),
        margin=dict(r=0, t=30, l=0, b=0),
        height=600
    )
    fig_ratio.update_traces(hoverlabel=dict(font=dict(size=14)))
    st.plotly_chart(fig_ratio, width='stretch')

    st.subheader("Dados da Análise")
    tabela_ratio = merged[['Estado', 'Alunos_fmt', 'Instituições_fmt', 'Ratio_fmt']].copy()
    tabela_ratio.columns = ['Estado', 'Alunos', 'Instituições', 'Alunos/IES']
    st.dataframe(
        tabela_ratio,
        width='stretch',
        hide_index=True
    )

show_footer(
    advisor_text="Orientador: Prof. Dr. César Candido Xavier • Email: cesarcx@gmail.com",
    text="Pesquisador: João Octavio Venâncio Borba • UNISO - Universidade de Sorocaba • Email: joaooctaviov.borba@gmail.com",
    links=[("Github", "https://github.com/jaozes"), ("LinkedIn", "https://www.linkedin.com/in/jo%C3%A3o-octavio-vb/"), ("Currículo Lattes", "http://lattes.cnpq.br/0821075410761662")],
    bg_color="#ffffff",
    text_color="#000000",
    height_px=56
)
