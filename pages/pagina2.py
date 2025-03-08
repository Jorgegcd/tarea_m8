import streamlit as st
import common.menu as menu

# Configurar la página para que el botón de navegación vaya hasta el principio cuando se abre la página.
st.set_page_config(page_title="Players") # Cambiamos nombre de la página

# Mostrar el menú lateral si el usuario está logueado.
if 'usuario' in st.session_state:
    menu.generarMenu(st.session_state['usuario'])
else:
    st.write("Por favor, inicia sesión para ver el menú.")

st.header("Estadísticas Jugadores - Players Stats")
st.write("Contenido de la página de estadísticas de jugadores")