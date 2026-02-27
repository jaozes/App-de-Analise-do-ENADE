import pandas as pd

df = pd.read_excel('enade-analysis-app/data/conceito_enade_2023.xlsx', engine='openpyxl')
print(df.columns.tolist())
