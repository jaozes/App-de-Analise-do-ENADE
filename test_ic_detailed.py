#!/usr/bin/env python3
"""
Teste detalhado da conversão de escala e Intervalo de Confiança
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# Função copiada do data_loader
def calculate_confidence_interval(values, confidence=0.95):
    """
    Calculate 95% confidence interval for a sample using t-distribution.        
    Returns: (mean, lower_bound, upper_bound, standard_error)
    """
    if len(values) < 2:
        return np.nan, np.nan, np.nan, np.nan

    mean = values.mean()
    se = stats.sem(values)  # Standard error
    margin = se * stats.t.ppf((1 + confidence) / 2, len(values) - 1)

    return mean, mean - margin, mean + margin, se


print("=" * 70)
print("TESTE DETALHADO DE CONVERSÃO DE ESCALA E INTERVALO DE CONFIANÇA")
print("=" * 70)

microdados_path = Path("enade-analysis-app/data/microdados2023_arq3.txt")

if not microdados_path.exists():
    print(f"❌ Arquivo não encontrado: {microdados_path.absolute()}")
    exit(1)

print(f"✅ Arquivo encontrado: {microdados_path}")

# Load data
print(f"\nCarregando dados...")
df = pd.read_csv(
    microdados_path,
    sep=";",
    encoding="latin1",
    usecols=["CO_CURSO", "NT_GER", "NT_FG", "NT_CE"],
    nrows=200000
)

# Filter valid data
df_valid = df.dropna(subset=['NT_GER', 'NT_FG', 'NT_CE'])
print(f"✅ Dados carregados: {len(df_valid)} linhas com valores válidos")

# Check original scale
print(f"\n--- VERIFICAÇÃO DE ESCALA ORIGINAL ---")
print(f"NT_GER (coluna original):")
print(f"  Min: {df_valid['NT_GER'].min():.2f}")
print(f"  Max: {df_valid['NT_GER'].max():.2f}")
print(f"  Média: {df_valid['NT_GER'].mean():.4f}")
print(f"  Std: {df_valid['NT_GER'].std():.4f}")

# Show sample of raw values
print(f"\n  Primeiras 10 valores brutos (NT_GER):")
print(f"  {df_valid['NT_GER'].head(10).values}")

# Determine the scale
if df_valid['NT_GER'].max() > 100:
    print(f"\n⚠️  ESCALA NÃO IDENTIFICADA: valores > 100")
elif df_valid['NT_GER'].max() > 10:
    print(f"\n⚠️  ESCALA 0-100 DETECTADA: valores entre 0 e {df_valid['NT_GER'].max():.2f}")
else:
    print(f"\n✓ ESCALA 0-5 DETECTADA: valores entre {df_valid['NT_GER'].min():.2f} e {df_valid['NT_GER'].max():.2f}")

# Convert to 0-5 scale if needed
print(f"\n--- CONVERSÃO PARA ESCALA 0-5 ---")
if df_valid['NT_GER'].max() > 10:
    print(f"Convertendo de 0-100 para 0-5 (dividindo por 20)...")
    df_valid['NT_GER_CONVERTED'] = df_valid['NT_GER'] / 20.0
else:
    print(f"Já está em escala 0-5, copiando...")
    df_valid['NT_GER_CONVERTED'] = df_valid['NT_GER']

print(f"\nNT_GER_CONVERTED (após conversão):")
print(f"  Min: {df_valid['NT_GER_CONVERTED'].min():.4f}")
print(f"  Max: {df_valid['NT_GER_CONVERTED'].max():.4f}")
print(f"  Média: {df_valid['NT_GER_CONVERTED'].mean():.4f}")
print(f"  Std: {df_valid['NT_GER_CONVERTED'].std():.4f}")

# Show sample of converted values
print(f"\n  Primeiros 10 valores convertidos:")
print(f"  {df_valid['NT_GER_CONVERTED'].head(10).values}")

# Test confidence interval with converted data
print(f"\n--- TESTE DE INTERVALO DE CONFIANÇA (50 amostras) ---")
sample_valores = df_valid['NT_GER_CONVERTED'].head(50).values
print(f"\nAmostra (50 primeiras notas em escala 0-5):")
print(f"  {sample_valores[:10]} ... (mostrando primeiras 10)")

media, ci_lower, ci_upper, se = calculate_confidence_interval(sample_valores)

print(f"\nResultados:")
print(f"  Média da amostra: {media:.4f}")
print(f"  IC 95%: [{ci_lower:.4f}, {ci_upper:.4f}]")
print(f"  Erro Padrão: {se:.4f}")
print(f"  Amplitude do IC: {(ci_upper - ci_lower):.4f}")
print(f"  N (tamanho da amostra): {len(sample_valores)}")

# Verify scale
if 0 <= media <= 5:
    print(f"\n✓ ESCALA VERIFICADA: Média {media:.4f} está entre 0 e 5")
else:
    print(f"\n❌ PROBLEMA NA ESCALA: Média {media:.4f} está FORA da faixa 0-5")

# Full dataset statistics
print(f"\n--- ESTATÍSTICAS DO CONJUNTO COMPLETO (após conversão) ---")
print(f"Total de registros: {len(df_valid)}")
print(f"Média global: {df_valid['NT_GER_CONVERTED'].mean():.4f}")
print(f"Desvio padrão: {df_valid['NT_GER_CONVERTED'].std():.4f}")

# Group by course
grouped = df_valid.groupby('CO_CURSO')['NT_GER_CONVERTED'].agg(['count', 'mean', 'std'])
grouped.columns = ['count', 'mean', 'std']

print(f"\nPrimeiros 5 cursos (após conversão):")
print(grouped.head(5))

print(f"\nTotal de cursos: {len(grouped)}")
print(f"Média de alunos por curso: {grouped['count'].mean():.1f}")
print(f"Mín/Máx alunos por curso: {grouped['count'].min():.0f} / {grouped['count'].max():.0f}")

print("\n" + "=" * 70)
print("✅ TESTE COMPLETO - Verifique os resultados acima")
print("=" * 70)
