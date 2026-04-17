# Implementação de Intervalo de Confiança 95% - Documentação

## 📊 Resumo da Implementação

Você perguntou se era possível implementar intervalo de confiança (IC 95%) nos gráficos de médias usando os dados disponíveis. **A resposta é SIM!** 

A implementação foi concluída e integrada à página de "Comparação Interinstitucional".

---

## ✅ O que foi feito

### 1. **Novos Dados Incorporados** (`data_loader.py`)

Foram criadas funções para carregar e processar os dados individuais dos alunos do arquivo `microdados2023_arq3.txt`:

```python
# Dados disponíveis no arquivo:
- CO_CURSO: Código do curso (chave para vincular com conceito_enade_2023.xlsx)
- NT_GER: Nota da prova geral (convertida em Conceito Enade)
- NT_FG: Nota da Formação Geral
- NT_CE: Nota do Componente Específico
```

**Estatísticas encontradas:**
- 140.263 alunos com dados válidos
- 8.947 cursos diferentes
- Média: 15,7 alunos por curso
- Alcance: 1 a 1.952 alunos por curso

### 2. **Cálculo do Intervalo de Confiança 95%**

A função `calculate_confidence_interval()` usa a **distribuição t de Student**, que é apropriada para:
- Tamanhos de amostra menores
- Estimativas de parâmetros populacionais a partir de amostras

**Fórmula:**
```
IC 95% = Média ± (Erro Padrão × t_crítico)

onde:
- Erro Padrão = desvio padrão / √n
- t_crítico = quantil da distribuição t (α=0,05, gl=n-1)
```

### 3. **Integração na Página de Comparação**

Na página [2_Comparação_Interinstitucional.py](enade-analysis-app/pages/2_Comparação_Interinstitucional.py):

- **Toggle 📊 Mostrar IC 95%**: Ativa/desativa a visualização dos intervalos
- **Barras de Erro no Gráfico**: Mostram a amplitude do IC ao redor de cada ponto
- **Funciona com todos os filtros**: UF, Município, IES, Curso, Modalidade, etc.

---

## 🎯 Como Usar

### 1. **Ativar a Visualização**

No gráfico de comparação, você verá um novo checkbox:

```
📊 Mostrar IC 95% ☐
```

Clique para ativar as bandas de erro nos gráficos.

### 2. **Interpretar as Bandas de Erro**

Quando ativado:
- **Linha do ponto**: Média calculada do conceito ENADE
- **Barras verticais**: Intervalo de confiança 95%
  - Se ICs não se sobrepõem → Diferença provavelmente significativa
  - Se ICs se sobrepõem → Diferença pode não ser significativa

### 3. **Filtrar e Comparar**

Use os filtros como de costume:
1. Selecione a 1ª instituição com os filtros
2. Selecione a 2ª instituição com os outros filtros
3. Escolha o tipo de nota (Média, Formação Geral, Componente Específico)
4. Ative o toggle de IC 95%

---

## 📈 Exemplo de Interpretação

```
Instituição A: Média 5,0, IC [4,8 - 5,2]
Instituição B: Média 4,9, IC [4,7 - 5,1]

Interpretação:
- Os ICs se sobrepõem
- Não há evidência estatística de diferença significativa
- Ambas têm desempenho similar
```

---

## 🔧 Detalhes Técnicos

### Funções Principais

| Função | Descrição |
|--------|-----------|
| `load_microdados_grades()` | Carrega NT_GER, NT_FG, NT_CE, CO_CURSO |
| `calculate_confidence_interval()` | Calcula IC 95% usando t-distribuição |
| `load_grades_with_ic()` | Agrega por CO_CURSO e calcula ICs |
| `get_ic_by_area()` | Calcula ICs agregados por Área de Avaliação |
| `create_co_curso_to_area_mapping()` | Mapeia CO_CURSO → Área de Avaliação |

### Dependências Adicionadas

```
scipy      # Para distribuição t e cálculos estatísticos
numpy      # Para operações numéricas
```

---

## ⚠️ Limitações e Considerações

1. **Tamanho amostral mínimo**: Requer ≥2 alunos por curso para calcular IC
2. **Dados faltantes**: Se um filtro resultar em < 2 alunos, IC não é exibido
3. **Mapeamento CO_CURSO**: O mapeamento entre CO_CURSO e Área de Avaliação é automático
4. **Performance**: O carregamento dos microdados é cacheado no Streamlit

---

## 📊 Validação

A implementação foi testada com:
- ✅ Carregamento de 140.263 registros de alunos
- ✅ Cálculo de IC para 8.947 cursos diferentes
- ✅ Agregação por Área de Avaliação
- ✅ Integração com o gráfico Plotly

**Status: ✅ Pronto para usar**

---

## 🚀 Próximos Passos (Opcional)

Se desejar melhorias futuras:

1. **Intervalo de confiança por bootstrap**: Mais flexível para distribuições não-normais
2. **Teste estatístico visual**: Marcar diferenças significativas automaticamente
3. **Exportar dados com IC**: Salvar os dados agregados em CSV/Excel
4. **IC por percentil**: Mostrar P25/P50/P75 além da média
5. **Análise de variabilidade**: Comparar não apenas médias, mas também dispersão

---

## 📞 Dúvidas?

A implementação usa a distribuição t de Student (padrão em estatística) com 95% de confiança.
Se tiver dúvidas sobre a interpretação estatística, consulte um estatístico.
