import streamlit as st
import common.login as login

import streamlit as st
import common.login as login

st.header('Página principal')
login.generarLogin()

if 'usuario' in st.session_state:
    st.subheader('Información página principal')

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Ir a Stats"):
            st.switch_page("Stats")  # Asegurate que el nombre "Stats" coincida con el título o nombre de la página en la carpeta pages.

    with col2:    
        if st.button("Ir a Players"):
            st.switch_page("Players") # Asegurate que el nombre "Players" coincida con el título o nombre de la página en la carpeta pages.

    with col3:    
        if st.button("Ir a Teams"):
            st.switch_page("Teams") # Asegurate que el nombre "Teams" coincida con el título o nombre de la página en la carpeta pages.