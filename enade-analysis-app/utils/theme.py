import streamlit as st

# ── Paletas ────────────────────────────────────────────────────────────────────
_LIGHT = {
    "--bg-primary":     "#ffffff",
    "--bg-secondary":   "#f0f2f6",
    "--bg-card":        "#ffffff",
    "--text-primary":   "#0e1117",
    "--text-secondary": "#555555",
    "--text-muted":     "#888888",
    "--border-color":   "#d0d0d0",
    "--accent":         "#1f77b4",
    "--accent-hover":   "#155a8a",
    "--shadow":         "rgba(0,0,0,0.08)",
}

_DARK = {
    "--bg-primary":     "#0e1117",
    "--bg-secondary":   "#1a1d27",
    "--bg-card":        "#1e2130",
    "--text-primary":   "#fafafa",
    "--text-secondary": "#b0b8c8",
    "--text-muted":     "#6b7280",
    "--border-color":   "#2e3347",
    "--accent":         "#4da3e0",
    "--accent-hover":   "#74bbf0",
    "--shadow":         "rgba(0,0,0,0.35)",
}


def _build_css(palette: dict) -> str:
    vars_css = "\n".join(f"    {k}: {v};" for k, v in palette.items())
    is_dark   = palette == _DARK
    df_filter = "invert(1) hue-rotate(180deg)" if is_dark else "none"

    return f"""
<style>
:root {{
{vars_css}
}}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}}

[data-testid="stSidebar"] {{
    background-color: var(--bg-secondary) !important;
}}

h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, label,
.stSelectbox label, .stMultiSelect label, .stCheckbox label {{
    color: var(--text-primary) !important;
}}

[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stMultiSelect"] div[data-baseweb="select"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}}

[data-baseweb="popover"], [data-baseweb="menu"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
}}

[data-testid="stDataFrame"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
}}
iframe[title="st.dataframe"] {{
    filter: {df_filter};
}}

[data-testid="stMetric"] {{
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 8px 12px;
}}
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {{
    color: var(--text-primary) !important;
}}

[data-testid="stAlert"] {{
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}}

[data-baseweb="tab-list"] {{
    background-color: var(--bg-secondary) !important;
}}
[data-baseweb="tab"] {{
    color: var(--text-secondary) !important;
}}
[aria-selected="true"] {{
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}}

[data-testid="baseButton-secondary"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}}
</style>
"""


def init_theme(page_title: str, layout: str = "wide") -> None:
    """Configura a página e aplica o tema salvo no session_state."""
    st.set_page_config(layout=layout, page_title=page_title)

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    palette = _DARK if st.session_state.dark_mode else _LIGHT
    st.markdown(_build_css(palette), unsafe_allow_html=True)


def show_theme_toggle() -> None:
    """
    Exibe o toggle de tema na sidebar (🌙 / ☀️).
    Chame esta função uma vez por página, logo após init_theme().
    """
    dark = st.session_state.get("dark_mode", False)
    icon  = "☀️ Modo Claro"  if dark else "🌙 Modo Escuro"
    label = "Mudar para modo claro" if dark else "Mudar para modo escuro"

    with st.sidebar:
        st.markdown("---")
        if st.button(icon, help=label, use_container_width=True):
            st.session_state.dark_mode = not dark
            st.rerun()
