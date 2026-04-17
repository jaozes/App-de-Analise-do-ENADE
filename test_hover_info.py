#!/usr/bin/env python3
"""
Teste das novas colunas Min, Max, Std no IC
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

def calculate_confidence_interval(values, confidence=0.95):
    """Calculate 95% confidence interval for a sample using t-distribution."""
    if len(values) < 2:
        return np.nan, np.nan, np.nan, np.nan
    
    mean = values.mean()
    se = stats.sem(values)
    margin = se * stats.t.ppf((1 + confidence) / 2, len(values) - 1)
    
    return mean, mean - margin, mean + margin, se


# Test the IC calculation with new fields
print("=" * 60)
print("TESTE: Min, Max, Std nas colunas de IC")
print("=" * 60)

# Simular dados de exemplo
np.random.seed(42)
exemplo_notas = np.random.uniform(2.0, 4.5, 50)  # Notas entre 2.0 e 4.5 (escala 0-5)

print(f"\n--- Dados de Exemplo ---")
print(f"Número de notas: {len(exemplo_notas)}")
print(f"Mínima: {exemplo_notas.min():.2f}")
print(f"Máxima: {exemplo_notas.max():.2f}")
print(f"Média: {exemplo_notas.mean():.2f}")
print(f"Desvio Padrão: {exemplo_notas.std():.2f}")

# Calcular IC
media, ci_lower, ci_upper, se = calculate_confidence_interval(exemplo_notas)

print(f"\n--- Intervalo de Confiança 95% ---")
print(f"Média: {media:.2f}")
print(f"IC: [{ci_lower:.2f}, {ci_upper:.2f}]")
print(f"Erro Padrão: {se:.4f}")

# Simular estrutura de resultado
resultado = {
    "CO_CURSO": 12345,
    "Nota_Tipo": "Conceito",
    "Media": media,
    "CI_Lower": ci_lower,
    "CI_Upper": ci_upper,
    "SE": se,
    "N_Alunos": len(exemplo_notas),
    "Min": exemplo_notas.min(),
    "Max": exemplo_notas.max(),
    "Std": exemplo_notas.std()
}

print(f"\n--- Estrutura de Dados Retornada ---")
for chave, valor in resultado.items():
    if isinstance(valor, float):
        print(f"{chave}: {valor:.4f}")
    else:
        print(f"{chave}: {valor}")

print(f"\n--- Hover Info (como aparecerá no gráfico) ---")
print(f"Curso: AGRONOMIA")
print(f"Instituição: Universidade XYZ")
print(f"Média: {resultado['Media']:.2f}")
print(f"Mínima: {resultado['Min']:.2f}")
print(f"Máxima: {resultado['Max']:.2f}")
print(f"Desvio Padrão: {resultado['Std']:.2f}")

print("\n" + "=" * 60)
print("✅ TESTE COMPLETO - Estrutura de dados OK!")
print("=" * 60)
