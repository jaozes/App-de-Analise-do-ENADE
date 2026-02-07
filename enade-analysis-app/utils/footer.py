import streamlit as st
from typing import List, Tuple, Optional

def show_footer(
    text: str = "Seu nome • Contato: seu@email.com",
    advisor_text: Optional[str] = None,
    links: Optional[List[Tuple[str, str]]] = None,
    bg_color: str = "#0f1724",
    text_color: str = "#ffffff",
    height_px: int = 56,
):
    """
    Exibe um footer que acompanha o conteúdo (sem fixed position).
    """
    if links is None:
        links = [("GitHub", "https://github.com/"), ("LinkedIn", "https://www.linkedin.com/")]

    links_html = " &nbsp; | &nbsp; ".join(
        [f'<a href="{url}" target="_blank" style="color:{text_color}; text-decoration:underline;">{label}</a>' for label, url in links]
    )

    advisor_section = f'<div>{advisor_text}</div>' if advisor_text else ""

    html = f"""
    <style>
      .custom-footer {{
        background: {bg_color};
        color: {text_color};
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 14px;
        margin-top: 40px;
        margin-left: -16px;
        margin-right: -16px;
        margin-bottom: -16px;
        padding-left: 24px;
        padding-right: 24px;
        border-top: 1px solid rgba(255,255,255,0.2);
      }}

      .custom-footer .left {{
        text-align: left;
        flex: 1;
      }}

      .custom-footer .right {{
        text-align: right;
        flex: 1;
      }}

      .custom-footer a {{
        color: {text_color};
        margin-left: 8px;
        text-decoration: underline;
      }}

      @media (max-width: 600px) {{
        .custom-footer {{ flex-direction: column; padding: 12px; font-size: 12px; margin-left: -16px; margin-right: -16px; margin-bottom: -16px; }}
        .custom-footer .left, .custom-footer .right {{ text-align: center; margin: 4px 0; }}
      }}
    </style>

    <div class="custom-footer">
      <div class="left">
        {advisor_section}
      </div>
      <div class="right">
        <div>{text}</div>
        <div style="margin-top:4px;">{links_html}</div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)