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
    
    # Desplegable múltiple para seleccionar equipos (multiselect)
    equipos = sorted(df_temporada['team_name'].unique())
    selected_teams = st.multiselect("Selecciona equipos (máximo 3)", equipos)
    
    # Validamos que no se seleccionen más de 3 equipos
    if len(selected_teams) > 3:
        st.error("Por favor, selecciona un máximo de 3 equipos.")
    else:
        # Mostrar los escudos según la cantidad de equipos seleccionados.
        # Se asume que el nombre de la imagen es el team_id y que está en "../images/"
        logos = []
        for team in selected_teams:
            # Obtenemos el team_id del equipo (suponiendo que 'team_id' está en el CSV)
            team_id = df_temporada.loc[df_temporada['team_name'] == team, 'team_id'].iloc[0]
            logo_path = f"../images/{team_id}.png"
            logos.append(logo_path)
        
        if logos:
            if len(logos) == 1:
                col = st.columns(1)
                col[0].image(logos[0], use_column_width=True)
            elif len(logos) == 2:
                cols = st.columns(2)
                cols[0].image(logos[0], use_column_width=True)
                cols[1].image(logos[1], use_column_width=True)
            elif len(logos) == 3:
                cols = st.columns(3)
                cols[0].image(logos[0], use_column_width=True)
                cols[1].image(logos[1], use_column_width=True)
                cols[2].image(logos[2], use_column_width=True)


        # Filtramos el dataframe para los equipos seleccionados
        df_filtrado = df_temporada[df_temporada['team_name'].isin(selected_teams)]
        # Obtener solo las columnas numéricas
        numeric_cols = df_filtrado.select_dtypes(include=['number']).columns

        # Crear un diccionario de formateo para las columnas numéricas
        formato = {col: "{:.2f}" for col in numeric_cols}

        # Aplicar el formateo y mostrar el DataFrame
        styled_df = df_filtrado.style.format(formato)
        st.dataframe(styled_df)