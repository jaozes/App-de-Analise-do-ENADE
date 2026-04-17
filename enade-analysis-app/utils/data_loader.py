import streamlit as st
import pandas as pd
from pathlib import Path
from scipy import stats
import numpy as np

# Robust data path: relative to utils/ parent (enade-analysis-app/)
DATA_DIR = Path(__file__).parent.parent / "data"
CONCEITO_PATH = DATA_DIR / "conceito_enade_2023.xlsx"
MICRODADOS_ARQ3 = DATA_DIR / "microdados2023_arq3.txt"

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
        if not MICRODADOS_ARQ3.exists():
            st.warning(f"⚠️ Arquivo de microdados não encontrado: {MICRODADOS_ARQ3}")
            return None
        
        df = pd.read_csv(
            MICRODADOS_ARQ3, 
            sep=";", 
            encoding="latin1",
            usecols=["CO_CURSO", "NT_GER", "NT_FG", "NT_CE"]
        )
        
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
    Load individual grades and calculate 95% confidence intervals by CO_CURSO.
    Grades are in 0-5 scale (converted from 0-100).
    
    Returns DataFrame with: CO_CURSO, Nota_Tipo, Media, CI_Lower, CI_Upper, SE, N_Alunos, Min, Max, Std
    (columns for both NT_GER, NT_FG, and NT_CE)
    """
    micro_df = load_microdados_grades()
    
    if micro_df is None or micro_df.empty:
        return None
    
    results = []
    
    # Group by course code
    # Note: Values are already in 0-5 scale
    for co_curso, group in micro_df.groupby("CO_CURSO"):
        for nota_col, nota_nome in [("NT_GER", "Conceito"), ("NT_FG", "Formação Geral"), ("NT_CE", "Componente Específico")]:
            valores = group[nota_col].dropna()
            
            if len(valores) >= 2:
                media, ci_lower, ci_upper, se = calculate_confidence_interval(valores)
                nota_min = valores.min()
                nota_max = valores.max()
                nota_std = valores.std()
                
                results.append({
                    "CO_CURSO": co_curso,
                    "Nota_Tipo": nota_nome,
                    "Media": media,
                    "CI_Lower": ci_lower,
                    "CI_Upper": ci_upper,
                    "SE": se,
                    "N_Alunos": len(valores),
                    "Min": nota_min,
                    "Max": nota_max,
                    "Std": nota_std
                })
    
    return pd.DataFrame(results)


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


def get_ic_by_area(filtered_df, ic_data):
    """
    Calculate IC bounds for each Área de Avaliação from filtered data.
    Uses the IC data to compute aggregate error bars.
    
    Args:
        filtered_df: The filtered conceito dataframe (already filtered by user selections)
        ic_data: DataFrame with IC information by CO_CURSO
    
    Returns:
        DataFrame with CI bounds by "Área de Avaliação" and nota type
    """
    if ic_data is None or ic_data.empty:
        return None
    
    # Try to create mapping between CO_CURSO and Área
    mapping = create_co_curso_to_area_mapping(filtered_df)
    
    if not mapping:
        return None
    
    # Add "Área de Avaliação" to ic_data
    ic_data_copy = ic_data.copy()
    ic_data_copy["Área de Avaliação"] = ic_data_copy["CO_CURSO"].map(mapping)
    
    # Group by area and note type, then aggregate
    result = ic_data_copy.groupby(["Área de Avaliação", "Nota_Tipo"]).agg({
        "Media": "mean",
        "CI_Lower": "mean",
        "CI_Upper": "mean",
        "SE": "mean",
        "N_Alunos": "sum",
        "Min": "min",  # Nota mínima entre todos os cursos
        "Max": "max",  # Nota máxima entre todos os cursos
        "Std": "mean"  # Média dos desvios padrão
    }).reset_index()
    
    return result

