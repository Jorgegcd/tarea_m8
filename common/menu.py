import streamlit as st
import pandas as pd

# Creamos la función de generar menú con su sidebar, con los parámetros del usuario registrado y el tiempo
def generarMenu(user, tiempo= None):        
    
    with st.sidebar:
        
        #Mostramos el nombre del usuario
        st.write(f"Hola **{user}** ")
        # Mostramos los enlaces de páginas
        st.page_link("home.py", label="Inicio", icon=":material/home:")
        st.subheader("Páginas")
        st.page_link("pages/pagina1.py", label="Comparador total temporada", icon=":material/groups:")
        st.page_link("pages/pagina2.py", label="Comparador por jornadas", icon=":material/person:") 
        
        # Botón para cerrar la sesión
        btnSalir=st.button("Salir", key="boton_salir_sidebar")
        if btnSalir:
            st.session_state.clear()
            # Después de borrar el Session State reiniciamos la app para mostrar la opción de usuario y clave
            st.rerun()