import streamlit as st

def check_password():
    st.title("Iniciar sesión")
    def password_entered():
        if st.session_state['password'] == 'admin':
            st.session_state['password_correct'] = True
            del st.session_state("password")
        else:
            st.session_state['password_correct'] = False
        
    if 'password_correct' not in st.session_state:
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password", on_change = password_entered, key = "password")
        return False
    elif not st.session_state['password_correct']:
        password
        st.error("Contraseña incorrecta")
        return False
    
    if st.button("Login"):
        # Validación básica: cambia estos valores o conecta con tu base de datos
        if username == "admin" and password == "admin":
            st.session_state["logged_in"] = True
            st.success("¡Inicio de sesión exitoso!")
        else:
            st.error("Usuario o contraseña incorrectos")

def logout_button():
    if st.button("Cerrar sesión"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()
