import streamlit as st
import pandas as pd
import os
import common.menu as menu

def generarLogin():
    """Genera la ventana de login o muestra el menú si el login es valido
    """    
    # Validamos si el usuario ya fue ingresado    
    if 'usuario' in st.session_state:
        menu.generarMenu(st.session_state['usuario']) # Si ya hay usuario cargamos el menu        
    else: 
        # Cargamos el formulario de login       
        with st.form('frmLogin'):
            username = st.text_input('Usuario')
            password = st.text_input('Password',type='password')
            btnLogin=st.form_submit_button('Entrar',type='primary')
            if btnLogin:
                if username == "admin" and password == "admin":
                    st.session_state['usuario'] = username
                    # Si el usuario es correcto reiniciamos la app para que se cargue el menú
                    st.rerun()
                else:
                    # Si el usuario es invalido, mostramos el mensaje de error
                    st.error("Usuario o clave inválidos",icon=":material/gpp_maybe:")     

def logout():
    """Cierra la sesión del usuario."""
    st.session_state.password_correct = False
    st.session_state.login_time = None
    st.session_state["logged_in"] = False  # Agregamos esta línea
    st.rerun()