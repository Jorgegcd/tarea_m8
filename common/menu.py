import streamlit as st
import pandas as pd

def generarMenu(user):
    """Genera el menú dependiendo del usuario

    Args:
        usuario (str): usuario utilizado para generar el menú
    """        
    with st.sidebar:
        
        #Mostramos el nombre del usuario
        st.write(f"Hola **:blue-background[{user}]** ")
        # Mostramos los enlaces de páginas
        st.page_link("home.py", label="Home", icon=":material/home:")
        st.subheader("Tableros")
        st.page_link("pages/pagina1.py", label="Stats", icon=":material/sell:")
        st.page_link("pages/pagina2.py", label="Players", icon=":material/shopping_cart:")
        st.page_link("pages/pagina3.py", label="Teams", icon=":material/group:")    
        # Botón para cerrar la sesión
        btnSalir=st.button("Salir")
        if btnSalir:
            st.session_state.clear()
            # Luego de borrar el Session State reiniciamos la app para mostrar la opción de usuario y clave
            st.rerun()