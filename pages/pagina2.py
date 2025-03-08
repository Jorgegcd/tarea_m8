import streamlit as st
import common.menu as menu

# Verificamos si el usuario está logueado
if 'usuario' in st.session_state:
    menu.generarMenu(st.session_state['usuario'])
else:
    st.write("Por favor, inicia sesión para ver el menú.")

st.header("Estadísticas Jugadores")
st.write("Contenido Estadísticas Jugadores")