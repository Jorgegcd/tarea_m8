import streamlit as st
import common.login as login
import os
from PIL import Image

# Cargamos el logo como objeto de imagen
base_path = os.path.dirname(__file__)
logo_path = os.path.join(base_path, "images", "logo_aba_2.png")
print("Ruta del logo que intenta abrir:", logo_path)

# Cargamos la imagen del logo como objeto
logo_image = Image.open(logo_path)

st.set_page_config(page_title="Inicio", page_icon=logo_image) # Cambiamos nombre de la página e introducimos el logo de la liga en el explorador



# Introducimos la función generar login
login.generarLogin()

if 'usuario' in st.session_state:

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    # Generamos botones que redirigen a la página que deseamos
    with col3:
        if st.button("Comparador total temporada"):
            st.switch_page("pages/pagina1.py")  # Ir a la página de estadísticas de equipos
    with col4:    
        if st.button("Comparador por jornadas"):
            st.switch_page("pages/pagina2.py") # Ir a la página de estadísticas de jugadores
    
    # Mostramos logo de la liga en el centro
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        st.image(logo_image, use_container_width=True)