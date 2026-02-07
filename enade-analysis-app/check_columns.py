import pandas as pd

df = pd.read_excel('data/conceito_enade_2023.xlsx', engine='openpyxl')
print(df.columns.tolist())
