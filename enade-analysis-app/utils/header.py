import streamlit as st
import os
import base64

def show_logo(path='logoUniso.webp', max_pct_width=60, top_margin_px=4, bottom_margin_px=8):
    """
    Exibe o logo centralizado e responsivo.
    - max_pct_width: largura máxima em % do container.
    - top_margin_px: espaço superior em pixels (reduza para aproximar do topo).
    - bottom_margin_px: espaço inferior em pixels.
    """
    base = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(base, '..'))
    logo_path = os.path.join(project_root, path)

    if not os.path.exists(logo_path):
        st.warning(f'Logo não encontrado: {logo_path}')
        return

    with open(logo_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('utf-8')

    html = f'''
    <div style="width:100%; display:flex; justify-content:center; align-items:center;
                margin-top:{top_margin_px}px; margin-bottom:{bottom_margin_px}px;">
      <img src="data:image/webp;base64,{b64}" style="max-width:{max_pct_width}%; height:auto; display:block;" />
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

    # Injetar CSS global para aumentar o tamanho da fonte
    st.markdown("""
    <style>
    /* Base fonts */
    body, p, div, span, label, .stMarkdown, .stText {
        font-size: 16px !important;
    }
    .stCaption {
        font-size: 14px !important;
    }
    
    /* Page/Section titles - Aumentados 20% */
    h1 {
        font-size: 3em !important;
        font-weight: bold !important;
        line-height: 1.2 !important;
    }
    h2 {
        font-size: 2.4em !important;
        font-weight: bold !important;
        line-height: 1.3 !important;
    }
    h3 {
        font-size: 2.2em !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
    }
    h4, h5, h6 {
        font-size: 1.8em !important;
    }
    
    /* Metrics */
    .stMetric {
        font-size: 48px !important;
    }
    .stMetric div, .stMetric span {
        font-size: 48px !important;
    }
    
    /* Plotly Graph Titles - FIX PRINCIPAL (era pequeno no cloud) */
    .js-plotly-plot .gtitle text,
    .js-plotly-plot .plotly .gtitle {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    
    /* Plotly axis titles/labels */
    .js-plotly-plot .xtitle text,
    .js-plotly-plot .ytitle text {
        font-size: 18px !important;
        font-weight: 500 !important;
    }
    
    /* Plotly legend */
    .js-plotly-plot .legendtext {
        font-size: 14px !important;
    }
    
    /* Responsive for mobile/cloud */
    @media (max-width: 768px) {
        h1 { font-size: 2.2em !important; }
        h2 { font-size: 1.8em !important; }
        h3 { font-size: 1.6em !important; }
        .js-plotly-plot .gtitle text { font-size: 20px !important; }
    }
    </style>
    """, unsafe_allow_html=True)
