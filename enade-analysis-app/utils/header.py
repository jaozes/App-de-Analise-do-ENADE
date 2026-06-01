import streamlit as st
import os
import base64


def show_logo(
    path='logoUniso.webp',
    path_dark: str | None = None,
    max_pct_width=60,
    top_margin_px=4,
    bottom_margin_px=8,
):
    """
    Exibe o logo centralizado e responsivo.

    Args:
        path: caminho do logo para o tema claro (relativo à raiz do projeto).
        path_dark: caminho alternativo para o tema escuro. Se None, usa o mesmo logo.
        max_pct_width: largura máxima em % do container.
        top_margin_px: espaço superior em pixels.
        bottom_margin_px: espaço inferior em pixels.
    """
    base = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(base, '..'))

    dark_mode = st.session_state.get("dark_mode", False)

    # Escolhe o logo correto conforme o tema
    chosen_path = path
    if dark_mode and path_dark is not None:
        candidate = os.path.join(project_root, path_dark)
        if os.path.exists(candidate):
            chosen_path = path_dark

    logo_path = os.path.join(project_root, chosen_path)

    if not os.path.exists(logo_path):
        st.warning(f'Logo não encontrado: {logo_path}')
        return

    with open(logo_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('utf-8')

    ext = os.path.splitext(chosen_path)[-1].lstrip('.').lower()
    mime_map = {'webp': 'image/webp', 'png': 'image/png', 'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg', 'svg': 'image/svg+xml'}
    mime = mime_map.get(ext, 'image/webp')

    # No dark mode sem logo alternativo, adiciona filtro CSS para não parecer invasivo
    extra_style = ""
    if dark_mode and path_dark is None:
        extra_style = "filter: brightness(0.92);"

    html = f'''
    <div style="width:100%; display:flex; justify-content:center; align-items:center;
                margin-top:{top_margin_px}px; margin-bottom:{bottom_margin_px}px;">
      <img src="data:{mime};base64,{b64}"
           style="max-width:{max_pct_width}%; height:auto; display:block; {extra_style}" />
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)
