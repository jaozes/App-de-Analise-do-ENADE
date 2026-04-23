import sys
sys.path.insert(0, 'enade-analysis-app')
from utils.data_loader import load_microdados_enriched, get_ic_filtered

print('Testando load_microdados_enriched...')
df = load_microdados_enriched()
print(f'  Linhas: {len(df)}')
print(f'  Colunas: {df.columns.tolist()}')
print(f'  Areas unicas: {df["Área de Avaliação"].nunique()}')
print()

print('Testando get_ic_filtered SEM filtros (nacional)...')
ic_nacional = get_ic_filtered(areas_tuple=('MEDICINA', 'ENFERMAGEM'))
print(ic_nacional[['Área de Avaliação', 'Nota_Tipo', 'N_Alunos', 'Media', 'CI_Lower', 'CI_Upper']])
print()

print('Testando get_ic_filtered COM filtro de UF (SP)...')
ic_sp = get_ic_filtered(areas_tuple=('MEDICINA', 'ENFERMAGEM'), uf=('SP',))
print(ic_sp[['Área de Avaliação', 'Nota_Tipo', 'N_Alunos', 'Media', 'CI_Lower', 'CI_Upper']])
print()

print('Verificando se N_Alunos diminuiu com o filtro...')
if ic_nacional is not None and ic_sp is not None:
    med_nac = ic_nacional[(ic_nacional['Área de Avaliação']=='MEDICINA') & (ic_nacional['Nota_Tipo']=='Conceito')]['N_Alunos'].values[0]
    med_sp = ic_sp[(ic_sp['Área de Avaliação']=='MEDICINA') & (ic_sp['Nota_Tipo']=='Conceito')]['N_Alunos'].values[0]
    print(f'  Medicina Nacional: {med_nac} alunos')
    print(f'  Medicina SP: {med_sp} alunos')
    print(f'  Diminuiu? {med_sp < med_nac}')
    
    print()
    print('Testando get_ic_filtered COM filtro de IES...')
    # Pegar uma IES aleatoria de Medicina
    ies_exemplo = df[df['Área de Avaliação']=='MEDICINA']['Nome da IES*'].unique()[0]
    print(f'  IES escolhida: {ies_exemplo}')
    ic_ies = get_ic_filtered(areas_tuple=('MEDICINA',), ies=(ies_exemplo,))
    if ic_ies is not None and not ic_ies.empty:
        med_ies = ic_ies[(ic_ies['Área de Avaliação']=='MEDICINA') & (ic_ies['Nota_Tipo']=='Conceito')]['N_Alunos'].values[0]
        print(f'  Medicina {ies_exemplo}: {med_ies} alunos')
        print(f'  Diminuiu vs nacional? {med_ies < med_nac}')
    else:
        print('  Sem dados para essa IES')

