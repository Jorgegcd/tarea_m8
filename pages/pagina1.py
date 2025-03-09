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

# Primer formulario para seleccionar la temporada
with st.form("form_temporada"):
    # Desplegable con las temporadas únicas (por ejemplo, "2022/2023" y "2023/2024")
    temporadas = sorted(df['season'].unique())
    temporada_seleccionada = st.selectbox("Selecciona la temporada", temporadas)
    submit_temporada = st.form_submit_button("Seleccionar temporada")

# Si se envió el formulario, guardamos la selección en el session_state
if submit_temporada:
    st.session_state.selected_season = temporada_seleccionada

# Solo si se ha seleccionado una temporada, mostramos el desplegable de equipos
if "selected_season" in st.session_state:
    # Filtramos el dataframe para la temporada seleccionada
    df_temporada = df[df['season'] == st.session_state.selected_season]
    # Obtenemos los equipos únicos para esa temporada
    equipos = sorted(df_temporada['team_name'].unique())
    
    # Desplegable múltiple para seleccionar equipos (multiselect)
    selected_teams = st.multiselect("Selecciona equipos (máximo 3)", equipos)
    
    # Validamos que no se seleccionen más de 3 equipos
    if len(selected_teams) > 3:
        st.error("Por favor, selecciona un máximo de 3 equipos.")
    elif len(selected_teams) > 0:
        # Filtramos el dataframe para los equipos seleccionados
        df_filtrado = df_temporada[df_temporada['team_name'].isin(selected_teams)]
        # Redondeamos los datos a 2 decimales
        df_filtrado = df_filtrado.round(2)
        # Aplica un estilo básico para centrar el texto (esto es solo un ejemplo)
        styled_df = df_filtrado.style.format("{:.2f}")
        st.dataframe(styled_df)