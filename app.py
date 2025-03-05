import streamlit as st
from auth import check_password, logout_button

# Inicializamos el estado de sesión si aún no está definido
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    st.write("¡Bienvenido a la aplicación!")
    # Aquí pones el contenido que quieres que vean los usuarios autenticados
    st.write("Este es el contenido protegido de tu app.")
    logout_button()
else:
    check_password()
