def filter_by_uf(df, uf):
    if uf:
        return df[df['Sigla da UF** '].isin(uf)]
    return df

def filter_by_municipio(df, municipio):
    if municipio:
        return df[df['Município do Curso**'].isin(municipio)]
    return df

def filter_by_ies(df, ies):
    if ies:
        return df[df['Nome da IES*'].isin(ies)]
    return df

def filter_by_curso(df, curso):
    if curso:
        return df[df['Área de Avaliação'].isin(curso)]
    return df

def filter_by_modalidade(df, modalidade):
    if modalidade:
        return df[df['Modalidade de Ensino'].isin(modalidade)]
    return df

def filter_by_categoria(df, categoria):
    if categoria:
        return df[df['Categoria Administrativa'].isin(categoria)]
    return df

def filter_by_grau(df, grau):
    if grau:
        return df[df['Grau Acadêmico'].isin(grau)]
    return df

def apply_filters(df, uf=None, municipio=None, ies=None, curso=None, modalidade=None, categoria=None, grau=None):
    df = filter_by_uf(df, uf)
    df = filter_by_municipio(df, municipio)
    df = filter_by_ies(df, ies)
    df = filter_by_curso(df, curso)
    df = filter_by_modalidade(df, modalidade)
    df = filter_by_categoria(df, categoria)
    df = filter_by_grau(df, grau)
    return df