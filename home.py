import streamlit as st
import common.login as login
import os

st.markdown(f"<h1 style='text-align: center;'>Comparador de equipos ABA League 2</h1>", unsafe_allow_html=True)
login.generarLogin()

if 'usuario' in st.session_state:

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Comparador total temporada"):
            st.switch_page("pages/pagina1.py")  # Ir a la página de estadísticas de equipos

    with col2:    
        if st.button("Comparador por jornadas"):
            st.switch_page("pages/pagina2.py") # Ir a la página de estadísticas de jugadores
    