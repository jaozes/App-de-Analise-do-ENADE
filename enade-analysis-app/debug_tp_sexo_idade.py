import pandas as pd
import unicodedata
from pathlib import Path

# load conceito
df = pd.read_excel('data/conceito_enade_2023.xlsx', engine='openpyxl')
df.columns = [unicodedata.normalize('NFKD', str(x)).encode('ascii','ignore').decode('ascii').strip() for x in df.columns]

# find microdados files for TP_SEXO and NU_IDADE
base = Path('enade-analysis-app/data')
files = sorted(base.glob('microdados2023_arq*.txt'))
index = {}
for f in files:
    df0 = pd.read_csv(f, sep=';', encoding='latin1', nrows=0)
    for col in df0.columns:
        if col in ['TP_SEXO','NU_IDADE']:
            index[col] = f
print('index', index)

# load and map TP_SEXO
mapping = {'M': 'Masculino', 'F': 'Feminino', '9': 'Indefinido'}

f = index['TP_SEXO']
df = pd.read_csv(f, sep=';', encoding='latin1', usecols=['NU_ANO','CO_CURSO','TP_SEXO'])

def _map(v):
    if pd.isna(v):
        return v
    if isinstance(v, float) and v.is_integer():
        key = str(int(v))
    else:
        key = str(v).strip()
    return mapping.get(key, key)

df['TP_SEXO'] = df['TP_SEXO'].apply(_map)
print('TP_SEXO dtype', df['TP_SEXO'].dtype)
print('TP_SEXO unique', df['TP_SEXO'].unique()[:20])
print('TP_SEXO counts', df['TP_SEXO'].value_counts(dropna=False).head(20))

# join with conceito
left = df.rename(columns={'Ano': 'NU_ANO', 'Codigo do Curso': 'CO_CURSO'})
merged = pd.merge(df, left, on=['NU_ANO','CO_CURSO'], how='inner')
print('merged rows', len(merged))
print('merged TP_SEXO counts', merged['TP_SEXO'].value_counts(dropna=False).head(20))

# age
f_age = index['NU_IDADE']
g = pd.read_csv(f_age, sep=';', encoding='latin1', usecols=['NU_ANO','CO_CURSO','NU_IDADE'])
print('NU_IDADE dtype', g['NU_IDADE'].dtype)
print('NU_IDADE sample', sorted(g['NU_IDADE'].dropna().unique())[:20])
print('NU_IDADE min/max', g['NU_IDADE'].min(), g['NU_IDADE'].max())
