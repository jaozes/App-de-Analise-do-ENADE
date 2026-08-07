import streamlit as st

# ── Paletas ────────────────────────────────────────────────────────────────────
_LIGHT = {
    "--bg-primary":        "#ffffff",
    "--bg-secondary":      "#f0f2f6",
    "--bg-card":           "#ffffff",
    "--text-primary":      "#0e1117",
    "--text-secondary":    "#555555",
    "--text-muted":        "#888888",
    "--border-color":      "#d0d0d0",
    "--accent":            "#1f77b4",
    "--accent-hover":      "#155a8a",
    "--shadow":            "rgba(0,0,0,0.08)",
    "--df-canvas-filter":  "none",
}

_DARK = {
    "--bg-primary":        "#0e1117",
    "--bg-secondary":      "#1a1d27",
    "--bg-card":           "#1e2130",
    "--text-primary":      "#fafafa",
    "--text-secondary":    "#b0b8c8",
    "--text-muted":        "#6b7280",
    "--border-color":      "#2e3347",
    "--accent":            "#4da3e0",
    "--accent-hover":      "#74bbf0",
    "--shadow":            "rgba(0,0,0,0.35)",
    "--df-canvas-filter":  "invert(1) hue-rotate(180deg)",
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

/* Popover/menus do Streamlit (conteúdo ao abrir e itens internos) */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-testid="stPopover"],
[data-testid="stMenu"],
div[role="menu"],
div[role="dialog"],
section[role="dialog"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}}

/* itens clicáveis dentro do menu */
[data-baseweb="menu"] button,
[data-baseweb="menu"] [role="menuitem"],
[data-baseweb="popover"] button,
[data-baseweb="popover"] [role="menuitem"],
div[role="menuitem"],
div[role="menuitemradio"],
div[role="menuitemcheckbox"] {{
    background-color: transparent !important;
    color: var(--text-primary) !important;
    border-color: transparent !important;
}}

/* ações do topo (Print/Settings) podem usar botões internos */
[data-baseweb="popover"] button,
[data-testid="stToolbar"] button,
[data-testid="stTopBar"] button,
section[role="dialog"] button {{
    background-color: transparent !important;
    color: var(--text-primary) !important;
    border-color: transparent !important;
}}


/* hover/selecionado no menu */
[data-baseweb="menu"] [role="menuitem"]:hover,
[data-baseweb="popover"] [role="menuitem"]:hover,
[data-baseweb="menu"] [aria-selected="true"],
[data-baseweb="popover"] [aria-selected="true"] {{
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}}

/* garante cor em texto/tokens do popover/topbar (3 pontos) */
/* (Streamlit usa vários seletores/estruturas diferentes; estas regras são bem agressivas) */
[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
[data-testid="stToolbar"] *,
[data-testid="stTopBar"] * {{
    color: var(--text-primary) !important;
    background: transparent !important;
}}

/* Hambúrguer / print / settings: tentativa final com seletores gerais */
[data-testid="stPopover"],
[data-testid="stMenu"],
[data-baseweb="popover"],
[data-baseweb="menu"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
}}

[data-testid="stPopover"] *:not(svg):not(path),
[data-testid="stMenu"] *:not(svg):not(path),
[data-baseweb="popover"] *:not(svg):not(path),
[data-baseweb="menu"] *:not(svg):not(path) {{
    background-color: transparent !important;
    color: var(--text-primary) !important;
}}





/* ── Expanders ── */
[data-testid="stExpander"] {{
    background-color: var(--bg-card) !important;
    border-color: var(--border-color) !important;
}}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] details[open] > summary,
[data-testid="stExpander"] details[open] > summary * {{
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}}
[data-testid="stExpanderDetails"],
[data-testid="stExpanderDetails"] *:not(svg):not(path) {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
}}
/* Barra de gradiente dentro do expander não deve ser invertida */
[data-testid="stExpanderDetails"] div[style*="background: linear-gradient"],
[data-testid="stExpanderDetails"] div[style*="linear-gradient"] {{
    background-color: unset !important;
}}

/* ── Multiselect tags (chips selecionados) ── */
[data-baseweb="tag"] {{
    background-color: var(--accent) !important;
    color: #ffffff !important;
}}
[data-baseweb="tag"] span {{
    color: #ffffff !important;
}}

/* ── Inputs / selects: container, texto e placeholder ── */
[data-baseweb="select"] > div {{
    background-color: var(--bg-card) !important;
    border-color: var(--border-color) !important;
}}
[data-baseweb="select"] > div *,
[data-baseweb="select"] input,
[data-baseweb="select"] span,
[data-baseweb="select"] div {{
    color: var(--text-primary) !important;
}}
/* placeholder "Choose options" */
[data-baseweb="select"] [data-testid="stMultiSelectOption"],
[data-baseweb="select"] [aria-label="Choose options"],
[data-baseweb="select"] > div > div > div {{
    color: var(--text-muted) !important;
}}

/* ── Dropdown aberto (listbox de opções) ── */
[role="listbox"] {{
    background-color: var(--bg-card) !important;
}}
[role="option"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
}}
[role="option"]:hover,
[role="option"][aria-selected="true"] {{
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {{
    border-radius: 8px;
    overflow: hidden;
}}
[data-testid="stDataFrame"] > div {{
    background-color: var(--bg-card) !important;
    border-color: var(--border-color) !important;
    border-radius: 8px;
}}
/* Glide data grid (canvas): inverte no dark mode */
[data-testid="stDataFrame"] canvas {{
    filter: var(--df-canvas-filter, none);
}}

/* ── Tabs (standalone aria-selected para abas, não menus) ── */
[aria-selected="true"] {{
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}}


/* ── Toggles e Checkboxes ── */
[data-testid="stToggle"] label,
[data-testid="stToggle"] p,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p,
[data-testid="stRadio"] label,
[data-testid="stRadio"] p,
[data-testid="stRadio"] span {{
    color: var(--text-primary) !important;
}}

[data-testid="baseButton-secondary"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}}

/* ── Botão de Download ── */

[data-testid="stDownloadButton"] button {{

    background-color: var(--accent) !important;

    color: #ffffff !important;

    border-color: var(--accent) !important;

}}

[data-testid="stDownloadButton"] button:hover {{

    background-color: var(--accent-hover) !important;

    border-color: var(--accent-hover) !important;

}}

[data-testid="stDownloadButton"] button p,

[data-testid="stDownloadButton"] button span {{

    color: #ffffff !important;

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
