# 🎓 Mapeando o Desempenho do Estudante no ENADE: Uma Plataforma Interativa Para Comparações Interinstitucionais

Aplicação interativa desenvolvida em **Streamlit** para análise e visualização dos dados do **Exame Nacional de Desempenho de Estudantes (ENADE) 2023**. A plataforma permite explorar o desempenho das instituições de ensino superior brasileiras, comparar resultados entre diferentes grupos e analisar o perfil socioeconômico dos participantes.

---

## 📋 Sumário

- [Visão Geral](#-visão-geral)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Instalação e Execução](#-instalação-e-execução)
- [Fontes de Dados](#-fontes-de-dados)
- [Páginas da Aplicação](#-páginas-da-aplicação)
  - [Home](#home)
  - [Análise Geral do Brasil](#análise-geral-do-brasil)
  - [Comparação Interinstitucional](#comparação-interinstitucional)
  - [Perfil Socioeconômico](#perfil-socioeconômico)
- [Metodologia Estatística](#-metodologia-estatística)
- [Autores e Créditos](#-autores-e-créditos)
- [Como Citar](#-como-citar)

---

## 🔭 Visão Geral

Este projeto tem como objetivo democratizar o acesso às informações do ENADE, transformando dados brutos do Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP) em visualizações interativas e de fácil interpretação. A plataforma foi desenvolvida como parte de uma pesquisa acadêmica da **Universidade de Sorocaba (UNISO)** e permite:

- Comparar o desempenho entre cursos, instituições e regiões;
- Analisar tendências de qualidade no ensino superior brasileiro;
- Identificar variações por modalidade de ensino e categoria administrativa;
- Fornecer insights estatísticos para análises educacionais;
- Explorar o perfil socioeconômico dos estudantes participantes do exame.

---

## ✨ Funcionalidades Principais

| Funcionalidade | Descrição |
|----------------|-----------|
| **🗺️ Mapa Coroplético Interativo** | Visualização do conceito médio ENADE por estado brasileiro com escala de cores personalizada |
| **📊 Gráficos Comparativos** | Comparação lado a lado entre duas instituições ou grupos de filtros |
| **📈 Intervalo de Confiança 95%** | Barras de erro baseadas na distribuição t de Student para inferência estatística |
| **📦 Box Plot com Dados Individuais** | Distribuição completa das notas dos alunos (mediana, quartis, outliers) |
| **🔍 Filtros em Cascata** | Filtros dinâmicos por UF, município, IES, curso, modalidade, categoria e grau acadêmico |
| **📋 Perfil Socioeconômico** | Análise de 26 questões do questionário socioeconômico (QE_I01 a QE_I26) mais sexo e idade |
| **🎨 Formatação Brasileira** | Números e percentuais no padrão brasileiro (ponto para milhares, vírgula para decimais) |
| **📱 Layout Responsivo** | Interface adaptada para diferentes tamanhos de tela |

---

## 🗂️ Estrutura do Projeto

```
enade-analysis-app/
│
├── Home.py                          # Página inicial com mapa coroplético e métricas gerais
├── requirements.txt                 # Dependências do projeto
├── logoUniso.webp                   # Logo da Universidade de Sorocaba
│
├── .streamlit/
│   └── config.toml                  # Configurações do tema Streamlit
│
├── data/                            # Diretório de dados (não versionado)
│   ├── conceito_enade_2023.xlsx     # Dados agregados de conceitos ENADE por curso
│   ├── microdados2023_arq3.txt      # Notas individuais dos alunos (NT_GER, NT_FG, NT_CE)
│   ├── microdados2023_arq3.parquet  # Cache Parquet das notas individuais
│   ├── microdados2023_enriched.parquet  # Cache Parquet dos microdados enriquecidos
│   └── microdados2023_arq[5-32].txt # Arquivos de microdados com questionário socioeconômico
│
├── pages/                           # Páginas adicionais da aplicação Streamlit
│   ├── 1_Análise_Geral_do_Brasil.py # Análises exploratórias do Brasil
│   ├── 2_Comparação_Interinstitucional.py  # Comparação entre instituições com IC 95%
│   └── 3_Perfil_Socioeconomico.py   # Análise do questionário socioeconômico
│
└── utils/                           # Módulos utilitários
    ├── data_loader.py               # Funções de carregamento e processamento de dados
    ├── filters.py                   # Funções auxiliares de filtragem
    ├── formatting.py                # Formatação de números no padrão brasileiro
    ├── header.py                    # Exibição do logo e injeção de CSS customizado
    └── footer.py                    # Rodapé com informações dos autores e citação
```

---

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)** — Framework para criação de aplicações web interativas em Python
- **[Pandas](https://pandas.pydata.org/)** — Manipulação e análise de dados tabulares
- **[Plotly](https://plotly.com/python/)** — Visualizações interativas (gráficos de barras, linhas, mapas, box plots)
- **[NumPy](https://numpy.org/)** — Computação numérica e operações estatísticas
- **[SciPy](https://scipy.org/)** — Distribuição t de Student para cálculo de intervalos de confiança
- **[OpenPyXL](https://openpyxl.readthedocs.io/)** — Leitura de arquivos Excel (.xlsx)
- **[Requests](https://requests.readthedocs.io/)** — Consumo da API GeoJSON para o mapa do Brasil

---

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Passo a passo

1. **Clone o repositório** (ou extraia o projeto):

```bash
cd enade-analysis-app
```

2. **Crie um ambiente virtual** (recomendado):

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

3. **Instale as dependências**:

```bash
pip install -r requirements.txt
```

4. **Baixe os dados do ENADE 2023** do [site do INEP](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacoes-e-exames-nacionais/enade) e coloque-os na pasta `data/`:
   - `conceito_enade_2023.xlsx`
   - `microdados2023_arq3.txt` (notas dos alunos)
   - `microdados2023_arq5.txt` a `microdados2023_arq32.txt` (questionário socioeconômico)

5. **Execute a aplicação**:

```bash
streamlit run Home.py
```

6. **Acesse no navegador**: O terminal exibirá o endereço local (geralmente `http://localhost:8501`).

---

## 📊 Fontes de Dados

| Arquivo | Origem | Conteúdo |
|---------|--------|----------|
| `conceito_enade_2023.xlsx` | INEP / ENADE 2023 | Conceitos ENADE (contínuo e faixa), notas padronizadas, dados dos cursos e IES |
| `microdados2023_arq3.txt` | INEP / ENADE 2023 | Notas individuais dos alunos: NT_GER, NT_FG, NT_CE e código do curso (CO_CURSO) |
| `microdados2023_arq[5-32].txt` | INEP / ENADE 2023 | Respostas ao questionário socioeconômico (variáveis QE_I01 a QE_I26, TP_SEXO, NU_IDADE) |

> **Nota:** Os arquivos de microdados não estão incluídos no repositório por questões de tamanho e licenciamento. É necessário baixá-los diretamente do portal de microdados do INEP.

---

## 📑 Páginas da Aplicação

### 🏠 Home

Página inicial que apresenta uma visão geral do ENADE 2023 através de:

- **Métricas gerais**: Total de inscritos, participantes, cursos e IES;
- **Mapa coroplético interativo**: Conceito médio ENADE por estado, com escala de cores personalizada (branco/azul claro para conceitos baixos, azul escuro/preto para conceitos altos);
- **Hover informativo**: Ao passar o mouse sobre um estado, são exibidos: conceito médio, inscritos, participantes, quantidade de IES e a melhor IES do estado;
- **Legenda acessível**: Expansor com explicação detalhada da escala de cores e instruções de interação.

---

### 📊 Análise Geral do Brasil

Página dedicada a análises exploratórias com **6 tipos de visualizações** selecionáveis via dropdown:

1. **Média de Conceitos por Área de Avaliação** — Gráfico de barras colorido (escala Viridis) com abreviações dos cursos no eixo X;
2. **Média por Estado** — Gráfico de barras horizontais ordenado por conceito médio;
3. **Média por Modalidade de Ensino** — Gráfico de pizza (presencial, EAD, etc.);
4. **Quantidade de Alunos por Curso ou Estado** — Gráfico de barras com inscritos ou participantes;
5. **Densidade de Cursos no Brasil** — Mapa coroplético com densidade relativa de cursos por estado (escala de vermelho);
6. **Densidade de Alunos por Instituição de Ensino** — Mapa coroplético com razão alunos/IES por estado (escala de verde).

Todas as visualizações contam com **filtros dinâmicos** por UF, área de avaliação, modalidade, categoria administrativa e grau acadêmico, além de tabelas de dados formatadas no padrão brasileiro.

---

### ⚖️ Comparação Interinstitucional

Página principal da plataforma, que permite comparar o desempenho de **duas instituições ou grupos de filtros** lado a lado.

#### Funcionalidades:

- **Dois painéis independentes de filtros**: UF, município, IES, curso, modalidade, categoria e grau acadêmico;
- **Filtros em cascata**: As opções de cada filtro são atualizadas dinamicamente conforme as seleções anteriores;
- **Seleção de tipo de nota**: Média do Conceito ENADE, Formação Geral ou Componente Específico;
- **Filtro de cursos em comum**: Opção para exibir apenas cursos presentes em ambos os grupos comparados;
- **Gráfico comparativo de linhas**: Visualização lado a lado com hover detalhado;
- **📊 Desvio Padrão / Intervalo de Confiança**: Toggle para exibir barras de erro representando a dispersão dos alunos filtrados;
- **📦 Box Plot com dados individuais**: Quando o desvio padrão está ativo, exibe a distribuição completa das notas (mediana, quartis, bigodes e outliers);
- **Tabelas comparativas**: Exibição tabular das médias por curso para cada instituição.

#### Metodologia do IC:

O intervalo de confiança é calculado sobre os **dados individuais dos alunos** (microdados), não apenas sobre as médias agregadas. Isso permite uma inferência estatística mais robusta sobre as diferenças de desempenho entre instituições.

---

### 📋 Perfil Socioeconômico

Página para análise das respostas ao **questionário socioeconômico** aplicado aos participantes do ENADE 2023.

#### Variáveis disponíveis (28 no total):

- **26 questões do questionário QE** (QE_I01 a QE_I26): estado civil, cor/raça, nacionalidade, escolaridade dos pais, renda familiar, situação de trabalho, bolsas de estudo, auxílios, intercâmbio, ação afirmativa, tipo de escola do ensino médio, motivação para o curso, entre outras;
- **TP_SEXO**: Sexo do participante (Masculino/Feminino);
- **NU_IDADE**: Idade em anos.

#### Funcionalidades:

- **Tradução automática**: Códigos das respostas são convertidos para textos descritivos completos;
- **Abreviações inteligentes**: Nos gráficos, respostas longas são abreviadas para melhor legibilidade;
- **Ordenação lógica**: Respostas são ordenadas pela sequência das alternativas (A, B, C, D...) e não por frequência;
- **Modo comparativo**: Toggle para ativar comparação interinstitucional lado a lado, com gráfico de linhas e tabelas de frequência;
- **Gráfico de linhas interativo**: Percentual de respostas por categoria, com hover detalhado;
- **Tabela de distribuição**: Contagem e percentual formatados no padrão brasileiro.

---

## 📐 Metodologia Estatística

### Intervalo de Confiança 95%

O cálculo do intervalo de confiança utiliza a **distribuição t de Student**, apropriada para amostras de tamanho variável:

```
IC 95% = Média ± (Erro Padrão × t_crítico)

Onde:
- Erro Padrão (SE) = Desvio Padrão / √n
- t_crítico = quantil da distribuição t (α = 0,05, gl = n - 1)
```

**Condições:**
- Requer no mínimo 2 alunos no grupo filtrado;
- Notas individuais são convertidas da escala 0-100 para 0-5;
- O IC é calculado sobre o subconjunto de alunos que atendem aos filtros aplicados.

### Escala de Notas

| Tipo de Nota | Descrição | Escala |
|--------------|-----------|--------|
| **Conceito Enade (Contínuo)** | Nota geral do aluno convertida para conceito | 0 a 5 |
| **Formação Geral (FG)** | Nota padronizada da prova de formação geral | 0 a 5 |
| **Componente Específico (CE)** | Nota padronizada da prova do componente específico | 0 a 5 |

---

## 👥 Autores e Créditos

**Pesquisador:**
- **João Octavio Venâncio Borba**
  - Universidade de Sorocaba (UNISO)
  - E-mail: joaooctaviov.borba@gmail.com
  - [GitHub](https://github.com/jaozes) | [LinkedIn](https://www.linkedin.com/in/jo%C3%A3o-octavio-vb/) | [Lattes](http://lattes.cnpq.br/0821075410761662)

**Orientador:**
- **Prof. Dr. César Candido Xavier**
  - E-mail: cesarcx@gmail.com
  - [Currículo Lattes](http://lattes.cnpq.br/2281060219061831)

**Instituição:**
- [Universidade de Sorocaba (UNISO)](https://www.uniso.br)

---

## 📝 Como Citar

Se utilizar esta plataforma ou os dados apresentados em sua pesquisa, por favor cite:

> BORBA, J. O. V. ; XAVIER, C. C. *Mapeando o desempenho e o perfil do estudante no Enade: uma plataforma interativa para comparações interinstitucionais*. Sorocaba, SP, 2026.

---

## 📄 Licença

Este projeto é de uso acadêmico. Os dados do ENADE são de domínio público e disponibilizados pelo INEP. O código-fonte da aplicação está disponível para fins educacionais e de pesquisa.

---

<p align="center">
  <strong>Desenvolvido com ❤️ na UNISO — 2026</strong>
</p>

