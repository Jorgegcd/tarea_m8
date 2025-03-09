import streamlit as st
import common.menu as menu
import pandas as pd

# Configurar la página para que el botón de navegación vaya hasta el principio cuando se abre la página.
st.set_page_config(page_title="Stats") # Cambiamos nombre de la página

# Mostrar el menú lateral si el usuario está logueado.
if 'usuario' in st.session_state:
    menu.generarMenu(st.session_state['usuario'])
else:
    st.write("Por favor, inicia sesión para ver el menú.")

st.header("Estadísticas Equipos - Team Stats")
st.write("Contenido de la página de estadísticas de equipos")

# Leemos el CSV de advanced data (ajusta la ruta según corresponda)
df = pd.read_csv("data/advanced_data.csv")

# Primer desplegable: temporadas únicas
temporadas = sorted(df['season'].unique())
temporada_seleccionada = st.selectbox("Selecciona la temporada", temporadas)

# Filtramos el dataframe para la temporada seleccionada
df_temporada = df[df['season'] == temporada_seleccionada]

# Segundo desplegable: equipos que participaron en esa temporada
# Se asume que en el CSV la columna con el nombre del equipo se llama 'team_name'
equipos = sorted(df_temporada['team_name'].unique())
equipo_seleccionado = st.selectbox("Selecciona el equipo", equipos)

# Puedes mostrar los datos filtrados, por ejemplo:
st.write("Datos del equipo:", df_temporada[df_temporada['team_name'] == equipo_seleccionado])