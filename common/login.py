import streamlit as st
import pandas as pd
import os
import time
import common.menu as menu

# Damos un máximo de 10 minutos en segundos
tiempo_max_sesion = 10*60

# Creamos la función para generar login
def generarLogin():
    
    # Si el usuario ya está logueado, mostramos el menú   
    if st.session_state.get("logged_in", False) and 'usuario' in st.session_state:
        ahora = time.time() # Indicamos el tiempo de ahora
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
            
            # Introducimos usuario y password
            username = st.text_input('Usuario')
            password = st.text_input('Password',type='password')
            
            # Generamos boton de login
            boton_login=st.form_submit_button('Entrar',type='primary')
            if boton_login:
                if username == "admin" and password == "admin": # Decimos username y password correcto para nuestro modelo
                    st.session_state['usuario'] = username
                    st.session_state["logged_in"] = True
                    st.session_state["login_time"] = time.time()
                    # Si el usuario es correcto reiniciamos la app para que se cargue el menú
                    st.rerun()
                else:
                    # Si el usuario no es válido, mostramos el mensaje de error
                    st.error("Usuario o clave inválidos",icon=":material/gpp_maybe:")     

# Generamos la función que cierra sesión
def logout():
    
    st.session_state.password_correct = False
    st.session_state.login_time = None
    st.session_state["logged_in"] = False  # Agregamos esta línea
    st.session_state.pop('login_time', None)  # Agregamos esta línea
    st.rerun()