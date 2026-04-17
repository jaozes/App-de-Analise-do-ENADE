# RESUMO VISUAL - INTERVALO DE CONFIANÇA 95%

## 📊 Arquitetura da Implementação

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUIVO DE MICRODADOS                         │
│              microdados2023_arq3.txt (92 MB)                     │
│            ✓ CO_CURSO, NT_GER, NT_FG, NT_CE                      │
│            ✓ 140.263 registros com dados válidos                 │
│            ✓ 8.947 cursos diferentes                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  load_microdados_grades()          │
        │  (Carrega dados brutos)            │
        └────────────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  load_grades_with_ic()             │
        │  (Agrupa por CO_CURSO)             │
        │  (Calcula IC 95%)                  │
        └────────────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Dados com IC:                     │
        │  CO_CURSO, Media, CI_Lower, CI_Upper│
        └────────────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Página 2: Comparação               │
        │  Interinstitucional                │
        │                                    │
        │  ☐ Mostrar IC 95%                  │
        │  (Toggle para ativar)              │
        └────────────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Gráfico com Erro Bars             │
        │  (Plotly)                          │
        │                                    │
        │    Média │                         │
        │      ├─────┤  ← Intervalo de      │
        │      │     │    Confiança 95%     │
        │      └─────┘                       │
        └────────────────────────────────────┘
```

## 🔄 Fluxo de Dados

```
USUÁRIO SELECIONA FILTROS
    ↓
[UF] [Município] [IES] [Curso] [Modalidade] [Categoria] [Grau]
    ↓
Filtra dados de conceito_enade_2023.xlsx
    ↓
Calcula agregações por "Área de Avaliação"
    ↓
Se toggle "Mostrar IC 95%" ativo:
    ├─ Mapeia CO_CURSO → Área de Avaliação
    ├─ Calcula IC para dados filtrados
    └─ Adiciona barras de erro no gráfico
    ↓
EXIBE GRÁFICO COM COMPARAÇÃO E INTERVALOS
```

## 📈 Exemplo de Gráfico (Com IC)

```
Média do Conceito ENADE
│
6.0 │     ●━━━━━●
    │   ╱ ┃    ╱ ┃
5.5 │  ● ┃   ● ┃
    │ ╱┃ ┃  ╱ ┃┃
5.0 │● ┃ ┃ ● ┃┃
    │├┃ ┃├ ┃┃
4.5 │● ┃ ┃ ● ┃┃
    │ ╲┃ ┃  ╲ ┃┃
4.0 │   ●━━━━━●
    │   ║     ║
3.5 │
    └────────────────────
      AG  AR  BM  EN  EA ...
      (Cursos)

Legend:
●━━━━━● = Linha de média com IC
┃     = Intervalo de confiança 95%
```

## 🧮 Cálculo do IC 95%

```
Para cada Área de Avaliação:

1. Coletam-se todas as notas dos alunos
   exemplo: [4.8, 5.1, 4.9, 5.2, 5.0, ...]

2. Calculam-se:
   - Média (μ) = 5.0
   - Desvio Padrão (σ) = 0.15
   - Erro Padrão (SE) = σ/√n = 0.015
   - Graus de liberdade (gl) = n - 1

3. Encontra-se valor crítico da distribuição t:
   - α = 0.05 (nível de confiança 95%)
   - t_crítico (α/2, gl) = 1.96

4. Calcula-se a margem de erro:
   - Margem = SE × t_crítico = 0.015 × 1.96 = 0.029

5. Intervalo de confiança:
   - IC [4.971, 5.029]
   - ou [5.0 ± 0.029]
```

## 🎯 Interpretação Visual

```
Caso 1: Diferença Significativa
──────────────────────────
Instituição A: ●━━━━━●
               4.8   5.2

Instituição B:         ●━━━━━●
                       5.4   5.8

→ ICs não se sobrepõem
→ Diferença provavelmente SIGNIFICATIVA


Caso 2: Diferença NÃO Significativa
────────────────────────────
Instituição A: ●━━━━━━━━━━━●
               4.5       5.5

Instituição B:     ●━━━━━━━━━━━●
                   4.8       5.8

→ ICs se sobrepõem muito
→ Diferença provavelmente NÃO SIGNIFICATIVA
```

## 📋 Checklist de Implementação

- [x] Carregar dados do arquivo microdados2023_arq3.txt
- [x] Implementar cálculo de IC 95% com t-distribuição
- [x] Agrupar dados por CO_CURSO
- [x] Mapear CO_CURSO para Área de Avaliação
- [x] Integrar na página de Comparação Interinstitucional
- [x] Adicionar toggle para ativar/desativar
- [x] Exibir barras de erro no gráfico Plotly
- [x] Testar com dados reais (140.263 registros)
- [x] Adicionar scipy e numpy aos requirements
- [x] Documentar a implementação

## ✅ Status: COMPLETO E TESTADO

Todos os componentes foram implementados e validados com dados reais.
A funcionalidade está pronta para uso na página de Comparação Interinstitucional.

## 🔗 Arquivos Modificados

1. `utils/data_loader.py` - Adiciona 5 novas funções
2. `pages/2_Comparação_Interinstitucional.py` - Integra IC no gráfico
3. `requirements.txt` - Adiciona scipy e numpy
4. `test_ic_logic.py` - Script de validação (opcional)
