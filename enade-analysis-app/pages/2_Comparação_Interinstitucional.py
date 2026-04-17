import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.header import show_logo
from utils.footer import show_footer
from utils.header import inject_css

#inject_css()
show_logo()

st.set_page_config(layout="wide", page_title="Comparação Interinstitucional - ENADE 2023")

# Carregar os dados
from utils.data_loader import load_conceito, load_grades_with_ic, get_ic_by_area

df = load_conceito()

# Carregar dados de ICs dos microdados (se disponível)
ic_df = load_grades_with_ic()

# abreviações dos cursos para exibição nos eixos X
ABBR = {
    "AGRONOMIA": "AG",
    "ARQUITETURA E URBANISMO": "AR",
    "BIOMEDICINA": "BM",
    "ENFERMAGEM": "EN",
    "ENGENHARIA AMBIENTAL": "EA",
    "ENGENHARIA CIVIL": "CV",
    "ENGENHARIA DE ALIMENTOS": "AL",
    "ENGENHARIA DE COMPUTAÇÃO I": "CO",
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
st.markdown("# Médias do Conceito Enade por Curso")

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

# Seletor para escolher qual nota exibir
col_selector, col_checkbox, col_ic = st.columns([1, 2, 1.5])
with col_selector:
    nota_selecionada = st.selectbox(
        "Selecionar nota",
        ["Média Conceito", "Formação Geral", "Componente Específico"],
        index=0
    )

# Mapear seleção para nome da coluna
mapa_notas = {
    "Média Conceito": "Média",
    "Formação Geral": "Formação Geral",
    "Componente Específico": "Componente Específico"
}
coluna_nota = mapa_notas[nota_selecionada]

# Checkbox para mostrar apenas cursos em comum
with col_checkbox:
    apenas_comum = st.checkbox("Mostrar apenas cursos em comum", value=False)

# Toggle para mostrar intervalos de confiança (se dados disponíveis)
with col_ic:
    mostrar_ic = False
    if ic_df is not None and not ic_df.empty:
        mostrar_ic = st.checkbox("📊 Mostrar IC 95%", value=False, help="Intervalo de confiança calculado a partir dos dados individuais dos alunos (notas convertidas de 0-100 para 0-5)")

# Mostrar aviso sobre conversão de escala quando IC está ativo
if mostrar_ic and ic_df is not None and not ic_df.empty:
    st.info("📊 **Notas Convertidas**: As notas foram convertidas de 0-100 para 0-5 para melhor visualização do intervalo de confiança. O eixo Y do gráfico mostra a escala 0-5.")


# Verificar se ambos os dataframes têm dados
if not filtered_df.empty and not filtered_df2.empty:
    # Determinar nome da instituição 1
    has_filters1 = bool(selected_uf or selected_municipio or selected_curso or selected_modalidade or selected_categoria or selected_grau or selected_ies)
    if selected_ies and len(selected_ies) == 1:
        nome_inst1 = selected_ies[0]
    elif has_filters1:
        nome_inst1 = "Instituição 1"
    else:
        nome_inst1 = "Média Nacional"
    
    # Determinar nome da instituição 2
    has_filters2 = bool(selected_uf2 or selected_municipio2 or selected_curso2 or selected_modalidade2 or selected_categoria2 or selected_grau2 or selected_ies2)
    if selected_ies2 and len(selected_ies2) == 1:
        nome_inst2 = selected_ies2[0]
    elif has_filters2:
        nome_inst2 = "Instituição 2"
    else:
        nome_inst2 = "Média Nacional"
    
    # Recalcular os dataframes sem o sort para manter a ordem original
    # agrupa pelo nome original para manter coluna completa, depois adiciona abreviatura
    avg_df = filtered_df.groupby('Área de Avaliação')['Conceito Enade (Contínuo)'].mean().reset_index().copy()
    avg_df['Área_abrev'] = avg_df['Área de Avaliação'].map(ABBR).fillna(avg_df['Área de Avaliação'])
    avg_df['Média'] = avg_df['Conceito Enade (Contínuo)'].round(2)
    avg_df['Formação Geral'] = filtered_df.groupby('Área de Avaliação')['Nota Padronizada - FG'].mean().round(2).reindex(avg_df['Área de Avaliação']).values
    avg_df['Componente Específico'] = filtered_df.groupby('Área de Avaliação')['Nota Padronizada - CE'].mean().round(2).reindex(avg_df['Área de Avaliação']).values
    avg_df["Instituicao"] = nome_inst1
    avg_df = avg_df.rename(columns={'Área_abrev': 'Sigla Área'})
    
    avg_df2 = filtered_df2.groupby('Área de Avaliação')['Conceito Enade (Contínuo)'].mean().reset_index().copy()
    avg_df2['Área_abrev'] = avg_df2['Área de Avaliação'].map(ABBR).fillna(avg_df2['Área de Avaliação'])
    avg_df2['Média'] = avg_df2['Conceito Enade (Contínuo)'].round(2)
    avg_df2['Formação Geral'] = filtered_df2.groupby('Área de Avaliação')['Nota Padronizada - FG'].mean().round(2).reindex(avg_df2['Área de Avaliação']).values
    avg_df2['Componente Específico'] = filtered_df2.groupby('Área de Avaliação')['Nota Padronizada - CE'].mean().round(2).reindex(avg_df2['Área de Avaliação']).values
    avg_df2["Instituicao"] = nome_inst2
    avg_df2 = avg_df2.rename(columns={'Área_abrev': 'Sigla Área'})
    
    # Pré-criar colunas de Min, Max, Std se mostrar_ic estiver ativo
    if mostrar_ic:
        for nota in ['Média', 'Formação Geral', 'Componente Específico']:
            avg_df[f'{nota}_Min'] = np.nan
            avg_df[f'{nota}_Max'] = np.nan
            avg_df[f'{nota}_Std'] = np.nan
            avg_df[f'{nota}_CI_Lower'] = np.nan
            avg_df[f'{nota}_CI_Upper'] = np.nan
            avg_df[f'{nota}_SE'] = np.nan
            avg_df2[f'{nota}_Min'] = np.nan
            avg_df2[f'{nota}_Max'] = np.nan
            avg_df2[f'{nota}_Std'] = np.nan
            avg_df2[f'{nota}_CI_Lower'] = np.nan
            avg_df2[f'{nota}_CI_Upper'] = np.nan
            avg_df2[f'{nota}_SE'] = np.nan
    
    # Adicionar dados de intervalo de confiança, se selecionado
    if mostrar_ic and ic_df is not None and not ic_df.empty:
        # Calcular ICs para as instituições filtradas
        ic_data1 = get_ic_by_area(filtered_df, ic_df)
        ic_data2 = get_ic_by_area(filtered_df2, ic_df)
        
        # Mapear tipo de nota para coluna
        nota_tipo_map = {
            "Conceito": "Média",
            "Formação Geral": "Formação Geral",
            "Componente Específico": "Componente Específico"
        }
        
        # Adicionar ICs, Min, Max, Std ao avg_df usando merge
        if ic_data1 is not None and not ic_data1.empty:
            # Criar dicionários para cada tipo de nota
            for nota_tipo in ic_data1['Nota_Tipo'].unique():
                ic_subset = ic_data1[ic_data1['Nota_Tipo'] == nota_tipo].copy()
                coluna_nota_tipo = nota_tipo_map.get(nota_tipo)
                
                if coluna_nota_tipo:
                    # Fazer merge dos dados
                    for _, row in ic_subset.iterrows():
                        area = row['Área de Avaliação']
                        if pd.isna(area):
                            continue
                        
                        # Encontrar a linha correspondente
                        idx = avg_df[avg_df['Área de Avaliação'] == area].index
                        if len(idx) > 0:
                            idx_val = idx[0]
                            # Usar .at[] que é mais seguro para atribuições escalares
                            if 'CI_Lower' in row.index:
                                avg_df.at[idx_val, f'{coluna_nota_tipo}_CI_Lower'] = float(row['CI_Lower']) if pd.notna(row['CI_Lower']) else np.nan
                            if 'CI_Upper' in row.index:
                                avg_df.at[idx_val, f'{coluna_nota_tipo}_CI_Upper'] = float(row['CI_Upper']) if pd.notna(row['CI_Upper']) else np.nan
                            if 'Min' in row.index and pd.notna(row['Min']):
                                avg_df.at[idx_val, f'{coluna_nota_tipo}_Min'] = round(float(row['Min']), 2)
                            if 'Max' in row.index and pd.notna(row['Max']):
                                avg_df.at[idx_val, f'{coluna_nota_tipo}_Max'] = round(float(row['Max']), 2)
                            if 'Std' in row.index and pd.notna(row['Std']):
                                avg_df.at[idx_val, f'{coluna_nota_tipo}_Std'] = round(float(row['Std']), 2)
        
        # Adicionar ICs, Min, Max, Std ao avg_df2 usando merge
        if ic_data2 is not None and not ic_data2.empty:
            # Criar dicionários para cada tipo de nota
            for nota_tipo in ic_data2['Nota_Tipo'].unique():
                ic_subset = ic_data2[ic_data2['Nota_Tipo'] == nota_tipo].copy()
                coluna_nota_tipo = nota_tipo_map.get(nota_tipo)
                
                if coluna_nota_tipo:
                    # Fazer merge dos dados
                    for _, row in ic_subset.iterrows():
                        area = row['Área de Avaliação']
                        if pd.isna(area):
                            continue
                        
                        # Encontrar a linha correspondente
                        idx = avg_df2[avg_df2['Área de Avaliação'] == area].index
                        if len(idx) > 0:
                            idx_val = idx[0]
                            # Usar .at[] que é mais seguro para atribuições escalares
                            if 'CI_Lower' in row.index:
                                avg_df2.at[idx_val, f'{coluna_nota_tipo}_CI_Lower'] = float(row['CI_Lower']) if pd.notna(row['CI_Lower']) else np.nan
                            if 'CI_Upper' in row.index:
                                avg_df2.at[idx_val, f'{coluna_nota_tipo}_CI_Upper'] = float(row['CI_Upper']) if pd.notna(row['CI_Upper']) else np.nan
                            if 'Min' in row.index and pd.notna(row['Min']):
                                avg_df2.at[idx_val, f'{coluna_nota_tipo}_Min'] = round(float(row['Min']), 2)
                            if 'Max' in row.index and pd.notna(row['Max']):
                                avg_df2.at[idx_val, f'{coluna_nota_tipo}_Max'] = round(float(row['Max']), 2)
                            if 'Std' in row.index and pd.notna(row['Std']):
                                avg_df2.at[idx_val, f'{coluna_nota_tipo}_Std'] = round(float(row['Std']), 2)
    
    # Unir os dois dataframes
    df_comparacao = pd.concat([avg_df, avg_df2], ignore_index=True)
    
    # Preparar dados de erro se mostrar_ic está ativo
    error_column = None
    if mostrar_ic:
        # Criar coluna de erro baseada no tipo de nota selecionada
        error_col_lower = f'{coluna_nota}_CI_Lower'
        error_col_upper = f'{coluna_nota}_CI_Upper'
        
        if error_col_lower in df_comparacao.columns and error_col_upper in df_comparacao.columns:
            # Calcular margens de erro (erro simétrico: metade da amplitude do IC)
            df_comparacao['erro'] = (
                (df_comparacao[error_col_upper] - df_comparacao[error_col_lower]) / 2
            ).fillna(0)
            error_column = 'erro'
        else:
            # Se não tiver colunas de IC, desabilitar mostrar_ic
            mostrar_ic = False
    
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
    
    # Obter lista de cursos ordenada (ordem alfabética)
    # ordenar com base na abreviatura para manter eixo X curto
    cursos_ordenados = sorted(df_comparacao['Sigla Área'].unique())
    
    # Converter colunas para categoria ordenada usando abreviação
    df_comparacao['Sigla Área'] = pd.Categorical(df_comparacao['Sigla Área'], categories=cursos_ordenados, ordered=True)
    df_comparacao = df_comparacao.sort_values(['Sigla Área', 'Instituicao'])
    
    # Criar gráfico de linha comparativo
    fig_params = {
        'data_frame': df_comparacao,
        'x': 'Sigla Área',
        'y': coluna_nota,
        'color': 'Instituicao',
        'markers': True,
        'line_shape': 'linear',
        'title': "",
        'custom_data': ['Área de Avaliação','Instituicao','Média','Formação Geral','Componente Específico']
    }
    
    # Adicionar colunas Min, Max, Std ao custom_data se mostrar_ic está ativo
    if mostrar_ic:
        fig_params['custom_data'].extend([
            f'{coluna_nota}_Min',
            f'{coluna_nota}_Max',
            f'{coluna_nota}_Std'
        ])
    
    # Adicionar error_y se mostrar_ic está ativo e temos dados de erro
    if mostrar_ic and error_column:
        fig_params['error_y'] = error_column
    
    fig_comparativo = px.line(**fig_params)
    
    # Definir rótulo do eixo Y conforme a nota selecionada
    labels_y = {
        "Média": "Média do Conceito ENADE",
        "Formação Geral": "Nota Padronizada - Formação Geral",
        "Componente Específico": "Nota Padronizada - Componente Específico"
    }
    
    fig_comparativo.update_layout(
        title="",
        xaxis_tickangle=0,
        template="plotly_white",
        xaxis_title='Curso',
        yaxis_title=labels_y[coluna_nota],
        yaxis=dict(range=[0, 5]),  # Escala de 0 a 5 para as notas convertidas
        height=600
    )
    
    # Definir hovertemplate conforme o IC está ativo ou não
    if mostrar_ic:
        # Template com Min, Max, Std
        hover_template = (
            '<b>%{customdata[0]}</b><br>'
            'Instituição: %{customdata[1]}<br>'
            'Média: %{y:.2f}<br>'
            'Mínima: %{customdata[5]:.2f}<br>'
            'Máxima: %{customdata[6]:.2f}<br>'
            'Desvio Padrão: %{customdata[7]:.2f}<extra></extra>'
        )
    else:
        # Template padrão
        hover_template = (
            '<b>%{customdata[0]}</b><br>'
            'Instituição: %{customdata[1]}<br>'
            'Média Conceito: %{customdata[2]:.2f}<br>'
            'Formação Geral: %{customdata[3]:.2f}<br>'
            'Componente Específico: %{customdata[4]:.2f}<extra></extra>'
        )
    
    fig_comparativo.update_traces(
        hovertemplate=hover_template,
        hoverlabel=dict(font=dict(size=14)),
        line=dict(width=4),
        marker=dict(size=8)
    )
    # Forçar a ordem dos cursos no eixo X (já são abreviados)
    fig_comparativo.update_xaxes(categoryorder='array', categoryarray=cursos_ordenados)
    st.plotly_chart(fig_comparativo, width='stretch')
    
    # Exibir tabelas de médias por curso de cada instituição
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        st.subheader(f'{nome_inst1} - Médias por Curso')
        # mostramos também a abreviatura para facilitar visualização
        st.dataframe(avg_df[['Sigla Área','Área de Avaliação', 'Média', 'Formação Geral', 'Componente Específico']], height=400, width='stretch', hide_index=True)
    with col_tab2:
        st.subheader(f'{nome_inst2} - Médias por Curso')
        st.dataframe(avg_df2[['Sigla Área','Área de Avaliação', 'Média', 'Formação Geral', 'Componente Específico']], height=400, width='stretch', hide_index=True)
    
elif filtered_df.empty and filtered_df2.empty:
    st.write('Nenhum dado encontrado com os filtros selecionados para ambas as instituições.')
elif filtered_df.empty:
    st.write('Nenhum dado encontrado com os filtros selecionados para a primeira instituição.')
elif filtered_df2.empty:
    st.write('Nenhum dado encontrado com os filtros selecionados para a segunda instituição.')

show_footer(
    advisor_text="Orientador: Prof. Dr. César Candido Xavier • /n Email: cesarcx@gmail.com",
    text="Pesquisador: João Octavio Venâncio Borba • UNISO - Universidade de Sorocaba • Email: joaooctaviov.borba@gmail.com",
    links=[("Github", "https://github.com/jaozes"), ("LinkedIn", "https://www.linkedin.com/in/jo%C3%A3o-octavio-vb/"), ("Currículo Lattes", "http://lattes.cnpq.br/0821075410761662")],
    bg_color="#ffffff",
    text_color="#000000",
    height_px=56,
    citation="Como citar: BORBA, J. O. V. Mapeando o desempenho e o perfil do estudante no Enade: uma plataforma interativa para comparações interinstitucionais. Sorocaba, SP, 2026."
)
