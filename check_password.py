import streamlit as st

def check_password():
    st.title("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        # Validación básica: cambia estos valores o conecta con tu base de datos
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
            st.success("¡Inicio de sesión exitoso!")
        else:
            st.error("Usuario o contraseña incorrectos")

def logout_button():
    if st.button("Cerrar sesión"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()