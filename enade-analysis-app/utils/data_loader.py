import streamlit as st
import pandas as pd
from pathlib import Path

# Robust data path: relative to utils/ parent (enade-analysis-app/)
DATA_DIR = Path(__file__).parent.parent / "data"
CONCEITO_PATH = DATA_DIR / "conceito_enade_2023.xlsx"

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

