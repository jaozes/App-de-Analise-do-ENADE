import streamlit as st
import pandas as pd
from pathlib import Path
from scipy import stats
import numpy as np

# Robust data path: relative to utils/ parent (enade-analysis-app/)
DATA_DIR = Path(__file__).parent.parent / "data"
CONCEITO_PATH = DATA_DIR / "conceito_enade_2023.xlsx"
MICRODADOS_ARQ3 = DATA_DIR / "microdados2023_arq3.txt"
MICRODADOS_PARQUET = DATA_DIR / "microdados2023_arq3.parquet"
MICRODADOS_ENRICHED_PARQUET = DATA_DIR / "microdados2023_enriched.parquet"


@st.cache_data
def load_conceito():
    """
    Load ENADE 2023 conceito data with robust path resolution and validation.
    """
    try:
        if not CONCEITO_PATH.exists():
            raise FileNotFoundError(
                f"❌ Data file not found: {CONCEITO_PATH.absolute()}\n"
                f"Expected at: {DATA_DIR.absolute()}\n\n"
                "💡 Solutions:\n"
                "• Download 'conceito_enade_2023.xlsx' from INEP ENADE 2023\n"
                "• If in .gitignore: `git add -f data/conceito_enade_2023.xlsx`\n"
                "• Verify cwd: {Path.cwd()}"
            )
        
        df = pd.read_excel(CONCEITO_PATH, engine='openpyxl')
        
        # Validate required column and clean
        if 'Conceito Enade (Contínuo)' not in df.columns:
            raise ValueError("Missing required column 'Conceito Enade (Contínuo)'")
        
        df = df.dropna(subset=['Conceito Enade (Contínuo)'])
        pass
        return df
        
    except Exception as e:
        st.error(f"❌ Failed to load data: {str(e)}")
        st.stop()


@st.cache_data
def load_microdados_grades():
    """
    Load individual student grades from microdados arq3 file (NT_GER, NT_FG, NT_CE by CO_CURSO).
    Converts grades from 0-100 scale to 0-5 scale.
    Returns DataFrame with columns: CO_CURSO, NT_GER, NT_FG, NT_CE (all in 0-5 scale)
    """
    try:
        parquet_path = MICRODADOS_PARQUET
        txt_path = MICRODADOS_ARQ3
        
        if parquet_path.exists():
            df = pd.read_parquet(parquet_path)
        else:
            if not txt_path.exists():
                st.warning(f"⚠️ Arquivo de microdados não encontrado: {txt_path}")
                return None
            
            df = pd.read_csv(
                txt_path, 
                sep=";", 
                encoding="latin1",
                usecols=["CO_CURSO", "NT_GER", "NT_FG", "NT_CE"]
            )
            df.to_parquet(parquet_path)
        
        # Remove rows with missing values in any of the grade columns
        
        # Remove rows with missing values in any of the grade columns
        df = df.dropna(subset=['NT_GER', 'NT_FG', 'NT_CE'])
        
        # Convert grades from 0-100 scale to 0-5 scale
        for col in ['NT_GER', 'NT_FG', 'NT_CE']:
            df[col] = (df[col] / 100) * 5
        
        return df
        
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar microdados: {str(e)}")
        return None


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


@st.cache_data
def load_grades_with_ic():
    """
    Load individual grades and calculate 95% confidence intervals by CO_CURSO (vectorized).
    Grades are in 0-5 scale (converted from 0-100).
    
    Returns DataFrame with: CO_CURSO, Nota_Tipo, Media, CI_Lower, CI_Upper, SE, N_Alunos, Min, Max, Std
    """
    micro_df = load_microdados_grades()
    
    if micro_df is None or micro_df.empty:
        return None
    
    grade_cols = ['NT_GER', 'NT_FG', 'NT_CE']
    nota_names = ["Conceito", "Formação Geral", "Componente Específico"]
    stats_dfs = []
    
    for col, nota_nome in zip(grade_cols, nota_names):
        group_stats = (
            micro_df.groupby("CO_CURSO")[col]
            .agg(mean='mean', count='count', min='min', max='max', std='std')
            .round(4)
            .reset_index()
        )
        
        group_stats = group_stats.rename(columns={
            'mean': 'Media',
            'count': 'N_Alunos', 
            'min': 'Min',
            'max': 'Max',
            'std': 'Std'
        })
        
        group_stats['Nota_Tipo'] = nota_nome
        group_stats['SE'] = group_stats['Std'] / np.sqrt(group_stats['N_Alunos'])
        
        # Vectorized CI calculation for valid groups
        mask = group_stats['N_Alunos'] >= 2
        group_stats.loc[~mask, ['CI_Lower', 'CI_Upper', 'SE']] = np.nan
        
        valid_mask = mask.copy()
        if valid_mask.any():
            N = group_stats.loc[valid_mask, 'N_Alunos']
            t_crit = stats.t.ppf(0.975, N - 1)
            group_stats.loc[valid_mask, 'CI_Lower'] = group_stats.loc[valid_mask, 'Media'] - t_crit * group_stats.loc[valid_mask, 'SE']
            group_stats.loc[valid_mask, 'CI_Upper'] = group_stats.loc[valid_mask, 'Media'] + t_crit * group_stats.loc[valid_mask, 'SE']
        
        stats_dfs.append(group_stats)
    
    result_df = pd.concat(stats_dfs, ignore_index=True)
    return result_df


def create_co_curso_to_area_mapping(conceito_df):
    """
    Create a mapping from CO_CURSO to "Área de Avaliação" using the conceito dataframe.
    Returns a dictionary: {CO_CURSO: "Área de Avaliação"}
    """
    # Try to find CO_CURSO column - it might be named differently
    co_curso_cols = [col for col in conceito_df.columns if 'CO_CURSO' in col.upper() or 'CURSO' in col.upper()]
    
    if not co_curso_cols:
        return {}
    
    co_curso_col = co_curso_cols[0]
    
    mapping = dict(zip(conceito_df[co_curso_col], conceito_df['Área de Avaliação']))
    return mapping


@st.cache_data
def get_co_curso_to_area_mapping():
    """
    Cached mapping CO_CURSO → Área de Avaliação from conceito data.
    """
    conceito_df = load_conceito()
    return create_co_curso_to_area_mapping(conceito_df)


@st.cache_data
def get_ic_by_area(filtered_areas_tuple):
    """
    Calculate IC bounds for specified areas using cached data and mapping.
    
    Args:
        filtered_areas_tuple: Tuple of area names to filter, or None for all
    
    Returns:
        DataFrame with aggregated IC by "Área de Avaliação" and "Nota_Tipo"
    """
    ic_data = load_grades_with_ic()
    if ic_data is None or ic_data.empty:
        return None
    
    mapping = get_co_curso_to_area_mapping()
    if not mapping:
        return None
    
    ic_data_copy = ic_data.copy()
    ic_data_copy["Área de Avaliação"] = ic_data_copy["CO_CURSO"].map(mapping)
    ic_data_copy = ic_data_copy.dropna(subset=['Área de Avaliação'])
    
    if filtered_areas_tuple:
        ic_data_copy = ic_data_copy[ic_data_copy["Área de Avaliação"].isin(filtered_areas_tuple)]
    
    if ic_data_copy.empty:
        return None
    
    agg_dict = {
        "Media": "mean",
        "CI_Lower": "mean",
        "CI_Upper": "mean",
        "SE": "mean",
        "N_Alunos": "sum",
        "Min": "min",
        "Max": "max",
        "Std": "mean"
    }
    
    result = ic_data_copy.groupby(["Área de Avaliação", "Nota_Tipo"]).agg(agg_dict).reset_index()
    return result


@st.cache_data
def load_microdados_enriched():
    """
    Load microdados merged with conceito metadata for each student.
    Adds: Área de Avaliação, Nome da IES, UF, Município, Modalidade, Categoria, Grau.
    Converts grades from 0-100 to 0-5. Cached as Parquet.
    
    Returns DataFrame with columns:
    CO_CURSO, NT_GER, NT_FG, NT_CE, Área de Avaliação, Nome da IES*, 
    Sigla da UF** , Município do Curso**, Modalidade de Ensino, 
    Categoria Administrativa, Grau Acadêmico
    """
    try:
        if MICRODADOS_ENRICHED_PARQUET.exists():
            return pd.read_parquet(MICRODADOS_ENRICHED_PARQUET)
        
        # Load basic microdados
        micro_df = load_microdados_grades()
        if micro_df is None or micro_df.empty:
            return None
        
        # Load conceito with metadata columns
        conceito_df = load_conceito()
        if conceito_df is None or conceito_df.empty:
            return None
        
        # Select only needed columns from conceito
        meta_cols = [
            'Código do Curso',
            'Área de Avaliação',
            'Nome da IES*',
            'Sigla da UF** ',
            'Município do Curso**',
            'Modalidade de Ensino',
            'Categoria Administrativa',
            'Grau Acadêmico'
        ]
        
        # Check which columns actually exist
        available_meta_cols = [c for c in meta_cols if c in conceito_df.columns]
        if 'Código do Curso' not in available_meta_cols:
            st.warning("⚠️ Coluna 'Código do Curso' não encontrada no conceito.")
            return None
        
        conceito_meta = conceito_df[available_meta_cols].copy()
        conceito_meta['Código do Curso'] = conceito_meta['Código do Curso'].astype(int)
        
        # Merge microdados with metadata
        micro_df['CO_CURSO'] = micro_df['CO_CURSO'].astype(int)
        enriched = micro_df.merge(
            conceito_meta,
            left_on='CO_CURSO',
            right_on='Código do Curso',
            how='left'
        )
        
        # Drop rows without area mapping
        enriched = enriched.dropna(subset=['Área de Avaliação'])
        
        if enriched.empty:
            st.warning("⚠️ Nenhum aluno pôde ser mapeado para Área de Avaliação.")
            return None
        
        # Save enriched parquet for fast loading next time
        enriched.to_parquet(MICRODADOS_ENRICHED_PARQUET, index=False)
        
        return enriched
        
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar microdados enriquecidos: {str(e)}")
        return None


@st.cache_data
def get_ic_filtered(areas_tuple=(), uf=(), municipio=(), ies=(), modalidade=(), categoria=(), grau=()):
    """
    Calculate 95% confidence intervals over the FILTERED raw student sample.
    
    Args:
        areas_tuple: Tuple of area names to include
        uf, municipio, ies, modalidade, categoria, grau: Filter values (tuples/lists)
    
    Returns:
        DataFrame with columns: Área de Avaliação, Nota_Tipo, Media, CI_Lower, CI_Upper,
        SE, N_Alunos, Min, Max, Std
    """
    df = load_microdados_enriched()
    if df is None or df.empty:
        return None
    
    # Apply filters dynamically
    if areas_tuple:
        df = df[df['Área de Avaliação'].isin(areas_tuple)]
    if uf:
        df = df[df['Sigla da UF** '].isin(uf)]
    if municipio:
        df = df[df['Município do Curso**'].isin(municipio)]
    if ies:
        df = df[df['Nome da IES*'].isin(ies)]
    if modalidade:
        df = df[df['Modalidade de Ensino'].isin(modalidade)]
    if categoria:
        df = df[df['Categoria Administrativa'].isin(categoria)]
    if grau:
        df = df[df['Grau Acadêmico'].isin(grau)]
    
    if df.empty:
        return None
    
    nota_map = {
        'NT_GER': 'Conceito',
        'NT_FG': 'Formação Geral',
        'NT_CE': 'Componente Específico'
    }
    
    results = []
    
    for col, nota_nome in nota_map.items():
        # Group by area and calculate stats on raw student data
        grouped = df.groupby('Área de Avaliação')[col]
        
        for area, group in grouped:
            values = group.dropna()
            n = len(values)
            if n < 2:
                continue
            
            mean, ci_lower, ci_upper, se = calculate_confidence_interval(values)
            
            results.append({
                'Área de Avaliação': area,
                'Nota_Tipo': nota_nome,
                'Media': round(mean, 4),
                'CI_Lower': round(ci_lower, 4) if pd.notna(ci_lower) else np.nan,
                'CI_Upper': round(ci_upper, 4) if pd.notna(ci_upper) else np.nan,
                'SE': round(se, 4) if pd.notna(se) else np.nan,
                'N_Alunos': n,
                'Min': round(float(values.min()), 4),
                'Max': round(float(values.max()), 4),
                'Std': round(float(values.std(ddof=1)), 4)
            })
    
    if not results:
        return None
    
    return pd.DataFrame(results)


