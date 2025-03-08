import streamlit as st
import common.menu as menu

st.set_page_config(page_title="Players") # Configuramos la página para que el botón traiga hasta aquí desde la página inicio

# Verificamos si el usuario está logueado
if 'usuario' in st.session_state:
    menu.generarMenu(st.session_state['usuario'])
else:
    st.write("Por favor, inicia sesión para ver el menú.")

st.header("Estadísticas Jugadores")
st.write("Contenido Estadísticas Jugadores")