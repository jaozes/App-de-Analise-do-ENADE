import streamlit as st
def init_theme(page_title: str, layout: str = "wide") -> None:
    st.set_page_config(layout=layout, page_title=page_title)
