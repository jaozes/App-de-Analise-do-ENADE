import streamlit as st
import pandas as pd
import plotly.express as px
from utils.header import show_logo
from utils.footer import show_footer

show_logo()

st.set_page_config(layout="centered", page_title="Análise Geral do Brasil - ENADE 2023")

@st.cache_data
def load_data():
    df = pd.read_excel('enade-analysis-app/data/conceito_enade_2023.xlsx', engine='openpyxl')
    df = df.dropna(subset=['Conceito Enade (Contínuo)'])
    return df

df = load_data()

st.title("📊 Análise Geral do Brasil")

# Seleção de gráfico
opcoes_graficos = [
    "Média de Conceitos por Área de Avaliação",
    "Média por Estado",
    "Média por Modalidade de Ensino",
    "Quantidade de Alunos por Curso e Estado"
]
grafico_selecionado = st.selectbox("Selecione o gráfico a exibir:", opcoes_graficos)

# Análise por Área
if grafico_selecionado == "Média de Conceitos por Área de Avaliação":
    # Filtro por UF
    ufs_disponiveis = sorted(df['Sigla da UF** '].unique())
    ufs_selecionadas = st.multiselect(
        "Selecione as UFs:",
        options=ufs_disponiveis,
        default=[],
        help="Selecione uma ou mais UFs para filtrar os dados."
    )

    # Aplicar filtro
    if ufs_selecionadas:
        df_filtrado = df[df['Sigla da UF** '].isin(ufs_selecionadas)]
    else:
        df_filtrado = df

    st.subheader("Média de Conceitos por Área de Avaliação")
    avg_area = df_filtrado.groupby('Área de Avaliação')['Conceito Enade (Contínuo)'].mean().reset_index().round(2)
    avg_area.columns = ['Área', 'Média']
    avg_area = avg_area.sort_values('Média', ascending=False)

    fig1 = px.bar(avg_area, x='Área', y='Média', color='Média', color_continuous_scale='Viridis')
    fig1.update_layout(
        xaxis_tickangle=-45, 
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
    st.plotly_chart(fig1, width='stretch')

    st.subheader("Dados da Análise")
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

    # Aplicar filtros
    df_filtrado = df
    if ufs_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Sigla da UF** '].isin(ufs_selecionadas)]
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Área de Avaliação'].isin(areas_selecionadas)]

    st.subheader("Média por Estado")
    avg_uf = df_filtrado.groupby('Sigla da UF** ')['Conceito Enade (Contínuo)'].mean().reset_index().round(2)
    avg_uf.columns = ['Estado', 'Média']
    avg_uf = avg_uf.sort_values('Média', ascending=False)

    fig2 = px.bar(avg_uf, x='Estado', y='Média', color='Média', color_continuous_scale='Blues')
    fig2.update_layout(
        coloraxis=dict(
            colorbar=dict(
                len=1,
                yanchor='middle',
                y=0.5,
                thickness=15
            )
        )
    )
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

    # Aplicar filtros
    df_filtrado = df
    if ufs_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Sigla da UF** '].isin(ufs_selecionadas)]
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Área de Avaliação'].isin(areas_selecionadas)]

    st.subheader("Média por Modalidade de Ensino")
    avg_mod = df_filtrado.groupby('Modalidade de Ensino')['Conceito Enade (Contínuo)'].mean().reset_index().round(2)
    avg_mod.columns = ['Modalidade', 'Média']

    fig3 = px.pie(avg_mod, names='Modalidade', values='Média', title="Distribuição por Modalidade")
    st.plotly_chart(fig3, width='stretch')

    st.subheader("Dados da Análise")
    st.dataframe(avg_mod, width='stretch')

# Análise de Quantidade de Alunos por Curso e Estado
elif grafico_selecionado == "Quantidade de Alunos por Curso e Estado":
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

    # Aplicar filtros
    df_filtrado = df
    if ufs_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Sigla da UF** '].isin(ufs_selecionadas)]
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Área de Avaliação'].isin(areas_selecionadas)]

    st.subheader(f"Quantidade de Alunos - {tipo_quantidade}")

    if tipo_visualizacao == "Por Estado":
        # Agrupar por Estado
        qtd_por_estado = df_filtrado.groupby('Sigla da UF** ')[coluna_quantidade].sum().reset_index()
        qtd_por_estado.columns = ['Estado', 'Valor']
        qtd_por_estado = qtd_por_estado.sort_values('Valor', ascending=False)

        # Criar coluna formatada para texto
        qtd_por_estado['Quantidade'] = qtd_por_estado['Valor'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

        fig4 = px.bar(
            qtd_por_estado, 
            x='Estado', 
            y='Valor', 
            color='Valor', 
            color_continuous_scale='Greens',
            title="Quantidade de Alunos por Estado",
            custom_data=['Quantidade']
        )
        fig4.update_layout(
            xaxis_tickangle=-45,
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
        fig4.update_traces(hovertemplate='<b>%{x}</b><br>Quantidade: %{customdata[0]}<extra></extra>')
        st.plotly_chart(fig4, width='stretch')
        
        st.subheader("Dados da Análise")
        st.dataframe(
            qtd_por_estado[['Estado', 'Quantidade']], 
            width='stretch',
            hide_index=True
        )

    else:
        # Agrupar por Curso (Área de Avaliação)
        qtd_por_curso = df_filtrado.groupby('Área de Avaliação')[coluna_quantidade].sum().reset_index()
        qtd_por_curso.columns = ['Curso', 'Valor']
        qtd_por_curso = qtd_por_curso.sort_values('Valor', ascending=False)

        # Criar coluna formatada para texto
        qtd_por_curso['Quantidade'] = qtd_por_curso['Valor'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

        fig5 = px.bar(
            qtd_por_curso, 
            x='Curso', 
            y='Valor', 
            color='Valor', 
            color_continuous_scale='Oranges',
            title="Quantidade de Alunos por Curso (Área de Avaliação)",
            custom_data=['Quantidade']
        )
        fig5.update_layout(
            xaxis_tickangle=-45,
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
        fig5.update_traces(hovertemplate='<b>%{x}</b><br>Quantidade: %{customdata[0]}<extra></extra>')
        st.plotly_chart(fig5, width='stretch')
        
        st.subheader("Dados da Análise")
        st.dataframe(
            qtd_por_curso[['Curso', 'Quantidade']], 
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
