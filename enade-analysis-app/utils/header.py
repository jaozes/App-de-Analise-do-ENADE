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
    
    st.markdown("""
    <style>
    /* 110% ZOOM BY DEFAULT */
     html, body {
     transform: scale(1.1) !important;
     transform-origin: 0 0 !important;
    }
    .stApp {
     transform: scale(1.1) !important;
     transform-origin: 0 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def inject_css():
    st.markdown("""
 <style>

    /* PRIORIDADE MÁXIMA (evita override do tema) */
    html body .stApp h1,
    html body .stApp h2,
    html body .stApp h3,
    html body .stMarkdown h1,
    html body .stMarkdown h2,
    html body .stMarkdown h3,
    html body [data-testid="stMarkdownContainer"] h1,
    html body [data-testid="stMarkdownContainer"] h2,
    html body [data-testid="stMarkdownContainer"] h3 {

    font-weight: 700 !important;
    }
    /* tamanhos separados (mais estável) */
    html body .stApp h1 { font-size: 3em !important; }
    html body .stApp h2 { font-size: 2.4em !important; }
    html body .stApp h3 { font-size: 2em !important; }

    html body .stApp p, 
    html body .stApp div, 
    html body .stApp span, 
    html body .stApp label {
        font-size: 16px !important;
    }

    html body .stApp h4, 
    html body .stApp h5, 
    html body .stApp h6 {
        font-size: 1.6em !important;
    }

    /* STREAMLIT MARKDOWN (CRUCIAL) */
    html body .stMarkdown h1 { font-size: 3em !important; }
    html body .stMarkdown h2 { font-size: 2.4em !important; }
    html body .stMarkdown h3 { font-size: 2em !important; }

    /* METRICS (forma estável no cloud) */
    html body [data-testid="stMetricValue"] {
        font-size: 48px !important;
    }

    /* PLOTLY */
    html body .js-plotly-plot .gtitle text {
        font-size: 32px !important;
        font-weight: 900 !important;
    }

    /* ANTI-FLICKER REAL */
    * {
        animation: none !important;
        transition: none !important;
    }

    /* RESPONSIVO */
    @media (max-width: 768px) {
        html body .stApp h1 { font-size: 2.2em !important; }
        html body .stApp h2 { font-size: 1.8em !important; }
    }

    </style>
    """ , unsafe_allow_html=True)
