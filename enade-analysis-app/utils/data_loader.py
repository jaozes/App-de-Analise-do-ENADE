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

