import streamlit as st
import common.menu as menu
import pandas as pd
import os
from common.functions import crear_tablas, grafica_metricas_comparacion
from sqlalchemy import create_engine
import plotly.express as px

# Configurar la página para que el botón de navegación vaya hasta el principio cuando se abre la página.
st.set_page_config(page_title="Estadísticas equipos") # Cambiamos nombre de la página

# Crea el engine de conexión a la base de datos MySQL
engine = create_engine("mysql+pymysql://jgcornejo:Avellanas9?@localhost:3306/tarea_m8", echo=True)

# Mostrar el menú lateral si el usuario está logueado.
if 'usuario' in st.session_state:
    menu.generarMenu(st.session_state['usuario'])
else:
    st.write("Por favor, inicia sesión para ver el menú.")

st.markdown("<h1 style='text-align: center;'>Comparador de estadísticas equipos ABA League 2</h1>", unsafe_allow_html=True)

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
    selected_teams = st.multiselect("Selecciona equipos (máximo 2)", equipos)
    
    # Validamos que no se seleccionen más de 2 equipos
    if len(selected_teams) > 2:
        st.error("Por favor, selecciona un máximo de 2 equipos.")
    else:
        # Mostrar los escudos según la cantidad de equipos seleccionados.
        logos = []
        # Obtenemos la ruta absoluta usando os.getcwd()
        current_dir = os.getcwd()
        for team in selected_teams:
            # Se asume que en el DataFrame existe la columna 'team_id'
            team_id = df_temporada.loc[df_temporada['team_name'] == team, 'team_id'].iloc[0]
            # Construimos la ruta absoluta: images está en la raíz (tarea_m8/images)
            logo_path = os.path.join(current_dir, "images", "teams", f"{team_id}.png")
            logos.append(logo_path)
        
        if logos:
            if len(logos) == 1:
                col = st.columns(1)
                if os.path.exists(logos[0]):
                    col[0].image(logos[0], width=150)
                else:
                    col[0].error(f"No se encontró la imagen: {logos[0]}")
            elif len(logos) == 2:
                # Creamos tres columnas: el primer logo en la primera y el segundo en la tercera.
                cols = st.columns([1, 1, 1])
                # Ubica el primer logo en la primera columna (más a la izquierda)
                if os.path.exists(logos[0]):
                    cols[0].image(logos[0], width=150)
                else:
                    cols[0].error(f"No se encontró la imagen: {logos[0]}")
                # Ubica el segundo logo en la última columna (más a la derecha)
                if os.path.exists(logos[1]):
                    cols[2].image(logos[1], width=150)
                else:
                    cols[2].error(f"No se encontró la imagen: {logos[1]}")

        if len(selected_teams) > 0:
            # Creamos dos columnas para mostrar las tablas en paralelo
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h3 style='text-align: center;'>Promedios por partido equipo</h3>", unsafe_allow_html=True)
                # Generamos un string con los nombres entre comillas, separados por coma
                equipos_str = ", ".join([f"'{team}'" for team in selected_teams])
                query = f"""
                SELECT 
                    t.team_name AS "Equipo",
                    COUNT(m.match) AS "Partidos",
                    AVG(m.pts) AS "Puntos",
                    AVG(m.fg2m) AS "T2A",
                    AVG(m.fg2a) AS "T2I",
                    100*(AVG(m.fg2m) / AVG(m.fg2a)) AS "T2 Porc",
                    AVG(m.fg3m) AS "T3A",
                    AVG(m.fg3a) AS "T3I",
                    100*(AVG(m.fg3m) / AVG(m.fg3a)) AS "T3 Porc",
                    AVG(m.fgm) AS "TCA",
                    AVG(m.fga) AS "TCI",
                    100*(AVG(m.fgm) / AVG(m.fga)) AS "TC Porc",
                    AVG(m.ftm) AS "TLA",
                    AVG(m.fta) AS "TLI",
                    100*(AVG(m.ftm) / AVG(m.fta)) AS "TL Porc",
                    AVG(m.or) AS "Reb of",
                    AVG(m.dr) AS "Reb def",
                    AVG(m.tr) AS "Reb tot",
                    AVG(m.ass) AS "Ast",
                    AVG(m.st) AS "Robos",
                    AVG(m.blk) AS "Tapones",
                    AVG(m.to) AS "Pérdidas"
                FROM matches m
                JOIN teams t ON m.team_id = t.team_id
                WHERE t.team_name IN ({equipos_str}) AND m.season = '{temporada_seleccionada}'
                GROUP BY t.team_name, m.season
                ORDER BY t.team_name, m.season;
                """

                # Ejecutamos la consulta y la leemos en un DataFrame
                df_sql_team = pd.read_sql(query, engine)
                numeric_cols = df_sql_team.select_dtypes(include=['number']).columns
                formato = {col: "{:.2f}" for col in numeric_cols}
                styled_sql_team = df_sql_team.style.format(formato)
                # Mostramos la tabla en Streamlit
                st.dataframe(styled_sql_team)
            
            with col2:
                st.markdown("<h3 style='text-align: center;'>Promedios por partido de los rivales</h3>", unsafe_allow_html=True)
                # Generamos un string con los nombres entre comillas, separados por coma
                equipos_str = ", ".join([f"'{team}'" for team in selected_teams])
                query = f"""
                SELECT 
                    t.team_name AS "Equipo",
                    COUNT(m.match) AS "Partidos",
                    AVG(m.pts_opp) AS "Puntos recibidos",
                    AVG(m.fg2m_opp) AS "T2A rival",
                    AVG(m.fga_opp) AS "T2I rival",
                    100*(AVG(m.fg2m_opp) / AVG(m.fg2a_opp)) AS "T2 Porc rival",
                    AVG(m.fg3m_opp) AS "T3A rival",
                    AVG(m.fg3a_opp) AS "T3I rival",
                    100*(AVG(m.fg3m_opp) / AVG(m.fg3a_opp)) AS "T3 Porc rival",
                    AVG(m.fgm_opp) AS "TCA rival",
                    AVG(m.fga_opp) AS "TCI rival",
                    100*(AVG(m.fgm_opp) / AVG(m.fga_opp)) AS "TC Porc rival",
                    AVG(m.ftm_opp) AS "TLA rival",
                    AVG(m.fta_opp) AS "TLI rival",
                    100*(AVG(m.ftm_opp) / AVG(m.fta_opp)) AS "TL Porc rival",
                    AVG(m.or_opp) AS "Reb of rival",
                    AVG(m.dr_opp) AS "Reb def rival",
                    AVG(m.tr_opp) AS "Reb tot rival",
                    AVG(m.ass_opp) AS "Ast rival",
                    AVG(m.st_opp) AS "Robos rival",
                    AVG(m.blk_opp) AS "Tapones rival",
                    AVG(m.to_opp) AS "Pérdidas rival"
                FROM matches m
                JOIN teams t ON m.team_id = t.team_id
                WHERE t.team_name IN ({equipos_str}) AND m.season = '{temporada_seleccionada}'
                GROUP BY t.team_name, m.season
                ORDER BY t.team_name, m.season;
                """

                # Ejecutamos la consulta y la leemos en un DataFrame
                df_sql_opp = pd.read_sql(query, engine)
                numeric_cols = df_sql_opp.select_dtypes(include=['number']).columns
                formato = {col: "{:.2f}" for col in numeric_cols}
                styled_sql_opp = df_sql_opp.style.format(formato)
                # Mostramos la tabla en Streamlit
                st.dataframe(styled_sql_opp)
            
        else:
            st.info("Por favor, selecciona equipos para ver los datos.")
        
        # Mostramos título de sección centrado
        st.markdown("<h3 style='text-align: center;'>Comparación de valores promedio de equipos y producidos por rivales</h3>", unsafe_allow_html=True)

        if len(selected_teams) > 0:
            # Creamos dos columnas para mostrar las gráficas en paralelo
            col1, col2 = st.columns(2)
            
            with col1:
                
                # Asumimos que la lista selected_teams respeta el orden de selección
                equipo_left = selected_teams[0]
                equipo_right = selected_teams[1]
                
                # Define las métricas que deseas comparar (deben coincidir con los alias de la consulta SQL)
                metrics = ["Puntos", "T2 Porc", "T3 Porc", "TC Porc", "TL Porc", "Reb of", "Reb def", "Ast", "Robos", "Tapones", "Pérdidas"]
                
                # Llamamos a la función de la gráfica, pasando el DataFrame original de la consulta
                grafica_metricas_comparacion(df_sql_team, equipo_left, equipo_right, metrics)
            
            with col2:
                 # Asumimos que la lista selected_teams respeta el orden de selección
                equipo_left = selected_teams[0]
                equipo_right = selected_teams[1]
                
                # Define las métricas que deseas comparar (deben coincidir con los alias de la consulta SQL)
                metrics = ["Puntos recibidos", "T2 Porc rival", "T3 Porc rival", "TC Porc rival", "TL Porc rival", "Reb of rival",
                           "Reb def rival", "Ast rival", "Robos rival", "Tapones rival", "Pérdidas rival"]  # Ajusta según tus necesidades
                
                # Llamamos a la función de la gráfica, pasando el DataFrame original de la consulta
                grafica_metricas_comparacion(df_sql_opp, equipo_left, equipo_right, metrics)
        else:
            st.info("Selecciona exactamente 2 equipos para ver la gráfica en formato pirámide.")

        # Mostrar la tabla filtrada con los datos de los equipos seleccionados
        if len(selected_teams) > 0:
            # Filtramos el dataframe para los equipos seleccionados
            df_filtrado = df_temporada[df_temporada['team_name'].isin(selected_teams)]
            
            # Llamamos a la función que genera las dos tablas a partir del DataFrame filtrado
            tabla_ataque, tabla_defensa = crear_tablas(df_filtrado)
            
            # Creamos dos columnas para mostrar las tablas en paralelo
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h3 style='text-align: center;'>Estadísticas avanzadas ataque</h3>", unsafe_allow_html=True)
                # Para formatear los números, obtenemos las columnas numéricas y aplicamos formato
                numeric_cols = tabla_ataque.select_dtypes(include=['number']).columns
                formato = {col: "{:.2f}" for col in numeric_cols}
                styled_tabla_ataque = tabla_ataque.style.format(formato)
                st.dataframe(styled_tabla_ataque)
            
            with col2:
                st.markdown("<h3 style='text-align: center;'>Estadísticas avanzadas defensa</h3>", unsafe_allow_html=True)
                numeric_cols = tabla_defensa.select_dtypes(include=['number']).columns
                formato = {col: "{:.2f}" for col in numeric_cols}
                styled_tabla_defensa = tabla_defensa.style.format(formato)
                st.dataframe(styled_tabla_defensa)