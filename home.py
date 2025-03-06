import streamlit as st
import common.login as login

st.header('Página principal')
login.generarLogin()
if 'usuario' in st.session_state:
    st.subheader('Información página principal')
