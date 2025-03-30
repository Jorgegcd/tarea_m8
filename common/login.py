import streamlit as st
import pandas as pd
import os
import time
import common.menu as menu

tiempo_max_sesion = 10*60 # Damos un máximo de 10 minutos en segundos
def generarLogin():
    """Genera la ventana de login o muestra el menú si el login es valido"""    
    # Si el usuario ya está logueado, mostramos el menú   
    if st.session_state.get("logged_in", False) and 'usuario' in st.session_state:
        ahora = time.time()
        tiempo_login = st.session_state.get("login_time", ahora) # Generamos el tiempo

        if ahora - tiempo_login > tiempo_max_sesion: # Generamos que se expire la sesión si supera el tiempo
            # Sesión expirada
            st.warning("Sesión expirada. Vuelve a iniciar sesión.")
            st.session_state.clear()
            st.rerun()
        else:
            # Sesión válida, actualizamos el tiempo y mostramos menú
            st.session_state["login_time"] = ahora
            menu.generarMenu(st.session_state['usuario'], ahora) # Si ya hay usuario cargamos el menu
    else: 
        # Cargamos el formulario de login       
        with st.form('frmLogin'):
            # Introducimos título centrado
            st.markdown(f"<h1 style='text-align: center;'>Comparador de equipos ABA League 2</h1>", unsafe_allow_html=True)
            username = st.text_input('Usuario')
            password = st.text_input('Password',type='password')
            boton_login=st.form_submit_button('Entrar',type='primary')
            if boton_login:
                if username == "admin" and password == "admin":
                    st.session_state['usuario'] = username
                    st.session_state["logged_in"] = True
                    st.session_state["login_time"] = time.time()
                    # Si el usuario es correcto reiniciamos la app para que se cargue el menú
                    st.rerun()
                else:
                    # Si el usuario no es válido, mostramos el mensaje de error
                    st.error("Usuario o clave inválidos",icon=":material/gpp_maybe:")     

def logout():
    """Cierra la sesión del usuario."""
    st.session_state.password_correct = False
    st.session_state.login_time = None
    st.session_state["logged_in"] = False  # Agregamos esta línea
    st.session_state.pop('login_time', None)  # Agregamos esta línea
    st.rerun()