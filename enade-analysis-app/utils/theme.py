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

/* evita que chaves do f-string quebrem caso algum trecho tenha {{}} */




/* Títulos/labels do menu e itens (sidebar) */
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {{
    color: var(--text-primary) !important;
}}

/* “strip” superior (menu de 3 pontos / popover do Streamlit) */
[data-baseweb="menu"],
[data-baseweb="popover"],
[data-testid="stToolbar"],
[data-testid="stTopBar"],
.st-expander > div,
.stMarkdown p {{
    color: var(--text-primary) !important;
}}

/* garante cor em texto/tokens do popover/topbar (3 pontos) */
/* (Streamlit usa vários seletores/estruturas diferentes; estas regras são bem agressivas) */
[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
[data-testid="stToolbar"] *,
[data-testid="stTopBar"] *, {{
    color: var(--text-primary) !important;
    background: transparent !important;
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

    # Reforço para cabeçalho (barra superior / toolbar) via classe
    # (ajuste de cor por tema para ficar consistente com o toggle)
    app_header_bg = "#1e293b" if st.session_state.dark_mode else "#f8fafc"
    toggle_bg = "#111827" if st.session_state.dark_mode else "#e5e7eb"
    toggle_border = "#374151" if st.session_state.dark_mode else "#cbd5e1"
    toggle_text = "#f9fafb" if st.session_state.dark_mode else "#0f172a"

    st.markdown(
        f"""
<style>
    .stAppHeader {{
        background-color: {app_header_bg} !important;
    }}

    /* Toggle (botão do modo) na sidebar */
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] [data-testid="stButton"] button,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
        background-color: {toggle_bg} !important;
        border-color: {toggle_border} !important;
        color: {toggle_text} !important;
    }}

    section[data-testid="stSidebar"] button span,
    section[data-testid="stSidebar"] button svg,
    section[data-testid="stSidebar"] button .stMarkdown {{
        color: {toggle_text} !important;
    }}
</style>
""",
        unsafe_allow_html=True,
    )


def show_theme_toggle() -> None:
    """Exibe o toggle de tema na sidebar (🌙 / ☀️).

    Chame esta função uma vez por página, logo após init_theme().
    """
    dark  = st.session_state.get("dark_mode", False)
    icon  = "☀️ Modo Claro"  if dark else "🌙 Modo Escuro"
    label = "Mudar para modo claro" if dark else "Mudar para modo escuro"

    with st.sidebar:
        st.markdown("---")
        if st.button(icon, help=label, use_container_width=True):
            st.session_state.dark_mode = not dark
            st.rerun()


def is_dark_mode() -> bool:
    return bool(st.session_state.get("dark_mode", False))


def get_plotly_template() -> str:
    """Template principal do Plotly conforme o tema atual."""
    return "plotly_dark" if is_dark_mode() else "plotly_white"


def get_plotly_layout_common() -> dict:
    """Parâmetros de layout para manter fonte/legend/hover legíveis no light/dark."""
    if is_dark_mode():
        fg        = "#E5E7EB"
        fg_strong = "#F9FAFB"
        border    = "rgba(255,255,255,0.15)"
        legend_bg = "rgba(17,24,39,0.80)"
        hover_bg  = "rgba(17,24,39,0.95)"
    else:
        fg        = "#0E1117"
        fg_strong = "#0E1117"
        border    = "rgba(0,0,0,0.10)"
        legend_bg = "rgba(255,255,255,0.90)"
        hover_bg  = "rgba(255,255,255,0.95)"

    return {
        "template":      get_plotly_template(),
        "plot_bgcolor":  "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font":    {"color": fg},
        "legend":  {
            "bgcolor":     legend_bg,
            "bordercolor": border,
            "borderwidth": 1,
            "font":        {"color": fg},
        },
        "hoverlabel": {
            "bgcolor": hover_bg,
            "font":    {"color": fg_strong},
        },
        "xaxis": {"tickfont": {"color": fg}},
        "yaxis": {"tickfont": {"color": fg}},
        "coloraxis": {
            "colorbar": {
                "tickfont": {"color": fg},
                # "titlefont" foi removido no Plotly v4 — usar "title.font"
                "title": {"font": {"color": fg}},
            }
        },
    }


def apply_plotly_dark_layout(fig) -> None:
    """Aplica layout comum do tema atual em um fig de Plotly."""
    fig.update_layout(**get_plotly_layout_common())
