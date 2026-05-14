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