import streamlit as st
import common.login as login

st.header('Página principal')
login.generarLogin()

if 'usuario' in st.session_state:
    st.subheader('Información página principal')

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Estadisticas equipos"):
            st.switch_page("pages/pagina1.py")  # Ir a la página de estadísticas de equipos

    with col2:    
        if st.button("Estadisticas jugadores"):
            st.switch_page("pages/pagina2.py") # Ir a la página de estadísticas de jugadores