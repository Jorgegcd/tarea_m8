import streamlit as st
import time

def check_password():
    if "login_time" not in st.session_state:
        st.session_state.login_time = None

    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        # Verificar si han pasado más de 30 minutos desde el último login
        if st.session_state.login_time and time.time() - st.session_state.login_time > 1800:
            st.session_state.password_correct = False
            st.session_state.login_time = None

    if not st.session_state.password_correct:
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            # Validación básica: cambia estos valores o conecta con tu base de datos
            if username == "admin" and password == "admin":
                st.session_state["logged_in"] = True
                st.session_state.password_correct = True
                st.session_state.login_time = time.time()
                # Cambiamos el parámetro para "redireccionar" a dashboard
                st.query_params = {"page": "dashboard"}
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        return False
    return True

def logout():
    """Cierra la sesión del usuario."""
    st.session_state.password_correct = False
    st.session_state.login_time = None
    st.rerun()