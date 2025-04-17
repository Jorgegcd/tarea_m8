import streamlit as st
import common.menu as menu
import pandas as pd
import os
from common.functions import crear_tablas, grafica_metricas_comparacion, grafica_piramide_equipo, grafica_donut_posesiones,grafica_radar_comparativo, scatter_eficiencia, guardar_grafica_plotly
from common.pdf_generator import generate_pdf_pag1
from sqlalchemy import create_engine
import common.login as login
import plotly.express as px
import base64
import streamlit.components.v1 as components
from PIL import Image  # Necesario para abrir la imagen como objeto

# Indicamos la ruta para mostrar el icono de la liga en la pestaña web
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
logo_path = os.path.join(base_path, "images", "logo_aba_2.png") # Ruta para llegar a la carpeta y a la imagen del logo

# Cargamos la imagen del logo como objeto
logo_image = Image.open(logo_path)

# Configuramos la página para que el botón de navegación vaya hasta el principio cuando se abre la página.
st.set_page_config(page_title="Comparador total temporada", page_icon=logo_image) # Cambiamos nombre de la página e introducimos el logo de la liga en el explorador

# Introducimos el login para que se cierre si sobrepasa el tiempo o le damos a cerrar estando en la página
login.generarLogin()

# Indicamos lo que ocurre si usuario es correcto
if 'usuario' in st.session_state:

    # Creamos el engine de conexión a la base de datos
    engine = create_engine("sqlite:///data/tarea_m8.db", echo=True)

    # Indicamos título de página
    st.markdown(f"<h1 style='text-align: center;'>Comparador de totales de equipos ABA League 2</h1>", unsafe_allow_html=True)

    # Leemos el CSV de advanced data para crear los datos de estadística avanzada que utilizaremos
    df = pd.read_csv("data/advanced_data.csv")

    # Generamos el primer formulario para seleccionar la temporada
    with st.form("form_temporada"):
        # Desplegable con las temporadas 2022/2023 y 2023/2024 (las que habíamos descargado en el dataset)
        temporadas = sorted(df['season'].unique())
        temporada_seleccionada = st.selectbox("Selecciona la temporada", temporadas)
        submit_temporada = st.form_submit_button("Seleccionar temporada")

    # Si se envió el formulario, guardamos la selección en el session_state
    if submit_temporada:
        st.session_state.selected_season = temporada_seleccionada

    # Si se ha seleccionado una temporada, mostramos el desplegable de equipos
    if "selected_season" in st.session_state:
        # Filtramos el dataframe para la temporada seleccionada
        df_temporada = df[df['season'] == st.session_state.selected_season]
        
        # Creamos desplegable múltiple para seleccionar hasta 2 equipos (multiselect)
        equipos = sorted(df_temporada['team_name'].unique())
        selected_teams = st.multiselect("Selecciona equipos (máximo 2)", equipos)
        
        # Validamos que no se seleccionen más de 2 equipos
        if len(selected_teams) > 2:
            st.error("Por favor, selecciona un máximo de 2 equipos.")
        else:
            # Mostramos los escudos según la cantidad de equipos seleccionados.
            logos = []
            # Obtenemos la ruta absoluta usando os.getcwd()
            current_dir = os.getcwd()
            for team in selected_teams:
                # Se asume que en el DataFrame existe la columna 'team_id'
                team_id = df_temporada.loc[df_temporada['team_name'] == team, 'team_id'].iloc[0]
                # Construimos la ruta absoluta: images está en la raíz (tarea_m8/images)
                logo_path = os.path.join(current_dir, "images", "teams", f"{team_id}.png") # Decimos que el nombre de los logos son equivalentes al id y que están en carpeta images
                logos.append(logo_path)
            
            if logos:
                if len(logos) == 1:
                    col = st.columns(1) # Indicamos que solo haya 1 columna
                    with col[0]:
                        if os.path.exists(logos[0]):
                            with open(logos[0], "rb") as image_file:
                                encoded_logo = base64.b64encode(image_file.read()).decode() # Buscamos el logo según el id
                            st.markdown(
                                f"""<div style="text-align:center;">
                                <img src="data:image/png;base64,{encoded_logo}" width="150">
                                </div>""",
                                unsafe_allow_html=True
                            )
                        else:
                            st.error(f"No se encontró la imagen: {logos[0]}")
                elif len(logos) == 2:
                    cols = st.columns(2) # Indicamos que se divida en 2 columnas la parte de la página
                    with cols[0]: # El primer equipo en la primera columna
                        if os.path.exists(logos[0]):
                            with open(logos[0], "rb") as image_file:
                                encoded_logo = base64.b64encode(image_file.read()).decode() # Buscamos el logo según el id del primer equipo
                            st.markdown(
                                f"""<div style="text-align:center;">
                                <img src="data:image/png;base64,{encoded_logo}" width="150">
                                </div>""",
                                unsafe_allow_html=True
                            )
                        else:
                            st.error(f"No se encontró la imagen: {logos[0]}")
                    with cols[1]: # El segundo equipo en la segunda columna
                        if os.path.exists(logos[1]):
                            with open(logos[1], "rb") as image_file:
                                encoded_logo = base64.b64encode(image_file.read()).decode() # Buscamos el logo según el id del segundo equipo
                            st.markdown(
                                f"""<div style="text-align:center;">
                                <img src="data:image/png;base64,{encoded_logo}" width="150">
                                </div>""",
                                unsafe_allow_html=True
                            )
                        else:
                            st.error(f"No se encontró la imagen: {logos[1]}")

            if len(selected_teams) > 0:
                # Creamos dos columnas para mostrar las tablas en paralelo
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h3 style='text-align: center;'>Promedios por partido equipo</h3>", unsafe_allow_html=True)
                    # Generamos un string con los nombres entre comillas, separados por coma
                    equipos_str = ", ".join([f"'{team}'" for team in selected_teams])
                    # Generamos el pdf según la base de datos que tenemos para los promedios por partido de los equipos
                    query = f"""
                    SELECT 
                        t.team_name AS 'Equipo',
                        t.team_id AS 'team_id',
                        COUNT(m.match) AS 'Partidos',
                        AVG(m.pts) AS 'Puntos',
                        AVG(m.fg2m) AS 'T2A',
                        AVG(m.fg2a) AS 'T2I',
                        100*(AVG(m.fg2m) / AVG(m.fg2a)) AS 'T2 Porc',
                        AVG(m.fg3m) AS 'T3A',
                        AVG(m.fg3a) AS 'T3I',
                        100*(AVG(m.fg3m) / AVG(m.fg3a)) AS 'T3 Porc',
                        AVG(m.fgm) AS 'TCA',
                        AVG(m.fga) AS 'TCI',
                        100*(AVG(m.fgm) / AVG(m.fga)) AS 'TC Porc',
                        AVG(m.ftm) AS 'TLA',
                        AVG(m.fta) AS 'TLI',
                        100*(AVG(m.ftm) / AVG(m.fta)) AS 'TL Porc',
                        AVG(m."or") AS 'Reb of',
                        AVG(m.dr) AS 'Reb def',
                        AVG(m.tr) AS 'Reb tot',
                        AVG(m.ass) AS 'Ast',
                        AVG(m.st) AS 'Robos',
                        AVG(m.blk) AS 'Tapones',
                        AVG(m."to") AS 'Pérdidas'
                    FROM matches m
                    JOIN teams t ON m.team_id = t.team_id
                    WHERE t.team_name IN ({equipos_str}) AND m.season = '{temporada_seleccionada}'
                    GROUP BY t.team_name, t.team_id, m.season
                    ORDER BY t.team_name, t.team_id, m.season;
                    """

                    # Ejecutamos la consulta y la leemos en un DataFrame
                    df_sql_team = pd.read_sql(query, engine)
                    df_team = df_sql_team.drop(columns = 'team_id')
                    numeric_cols = df_team.select_dtypes(include=['number']).columns
                    formato = {col: "{:.2f}" for col in numeric_cols}
                    styled_sql_team = df_team.style.format(formato)
                    # Mostramos la tabla en Streamlit
                    st.dataframe(styled_sql_team)
                
                with col2:
                    st.markdown("<h3 style='text-align: center;'>Promedios por partido de los rivales</h3>", unsafe_allow_html=True)
                    # Generamos un string con los nombres entre comillas, separados por coma
                    equipos_str = ", ".join([f"'{team}'" for team in selected_teams])
                    # Generamos el pdf según la base de datos que tenemos para los promedios por partido de los rivales
                    query = f"""
                    SELECT 
                        t.team_name AS 'Equipo',
                        t.team_id AS 'team_id',
                        COUNT(m.match) AS 'Partidos',
                        AVG(m.pts_opp) AS 'Puntos recibidos',
                        AVG(m.fg2m_opp) AS 'T2A rival',
                        AVG(m.fga_opp) AS 'T2I rival',
                        100*(AVG(m.fg2m_opp) / AVG(m.fg2a_opp)) AS 'T2 Porc rival',
                        AVG(m.fg3m_opp) AS 'T3A rival',
                        AVG(m.fg3a_opp) AS 'T3I rival',
                        100*(AVG(m.fg3m_opp) / AVG(m.fg3a_opp)) AS 'T3 Porc rival',
                        AVG(m.fgm_opp) AS 'TCA rival',
                        AVG(m.fga_opp) AS 'TCI rival',
                        100*(AVG(m.fgm_opp) / AVG(m.fga_opp)) AS 'TC Porc rival',
                        AVG(m.ftm_opp) AS 'TLA rival',
                        AVG(m.fta_opp) AS 'TLI rival',
                        100*(AVG(m.ftm_opp) / AVG(m.fta_opp)) AS 'TL Porc rival',
                        AVG(m.or_opp) AS 'Reb of rival',
                        AVG(m.dr_opp) AS 'Reb def rival',
                        AVG(m.tr_opp) AS 'Reb tot rival',
                        AVG(m.ass_opp) AS 'Ast rival',
                        AVG(m.st_opp) AS 'Robos rival',
                        AVG(m.blk_opp) AS 'Tapones rival',
                        AVG(m.to_opp) AS 'Pérdidas rival'
                    FROM matches m
                    JOIN teams t ON m.team_id = t.team_id
                    WHERE t.team_name IN ({equipos_str}) AND m.season = '{temporada_seleccionada}'
                    GROUP BY t.team_name, t.team_id, m.season
                    ORDER BY t.team_name, t.team_id, m.season;
                    """

                    # Ejecutamos la consulta y la leemos en un DataFrame
                    df_sql_opp = pd.read_sql(query, engine)
                    df_opp = df_sql_opp.drop(columns = 'team_id')
                    numeric_cols = df_opp.select_dtypes(include=['number']).columns
                    formato = {col: "{:.2f}" for col in numeric_cols}
                    styled_sql_opp = df_opp.style.format(formato)
                    # Mostramos la tabla en Streamlit
                    st.dataframe(styled_sql_opp)
            
            # Valoramos si tenemos dos equipos
            if len(selected_teams) == 2:
                # Creamos dos columnas para mostrar las gráficas en paralelo
                col1, col2 = st.columns(2)

                # Asumimos que la lista selected_teams respeta el orden de selección
                equipo_left = selected_teams[0]
                equipo_right = selected_teams[1]
                
                with col1:
                    
                    # Definimos las métricas que deseas comparar, con los nombres indicados en la consulta SQL
                    metrics = ["Puntos", "T2 Porc", "T3 Porc", "TC Porc", "TL Porc", "Reb of", "Reb def", "Ast", "Robos", "Tapones", "Pérdidas"]
                    
                    # Llamamos a la función de la gráfica de pirámide de 2 equipos pasando el DataFrame original de la consulta
                    st.markdown("<h3 style='text-align: center;'>Comparación promedios ataque</h3>", unsafe_allow_html=True)
                    fig_piramide_1 = grafica_metricas_comparacion(df_sql_team, equipo_left, equipo_right, metrics)
                    ruta_piramide_1 = guardar_grafica_plotly(fig_piramide_1, "piramide_ataque_1.png")
                    st.plotly_chart(fig_piramide_1, use_container_width=True, key = 'piramide_ataque')
                
                with col2:
                    # Definimos las métricas que deseas comparar, con los nombres indicados en la consulta SQL
                    metrics = ["Puntos recibidos", "T2 Porc rival", "T3 Porc rival", "TC Porc rival", "TL Porc rival", "Reb of rival",
                            "Reb def rival", "Ast rival", "Robos rival", "Tapones rival", "Pérdidas rival"]  # Ajusta según tus necesidades
                    
                    # Llamamos a la función de pirámide de 2 equipos pasando el DataFrame original de la consulta
                    st.markdown("<h3 style='text-align: center;'>Comparación promedios defensa</h3>", unsafe_allow_html=True)
                    fig_piramide_2 = grafica_metricas_comparacion(df_sql_opp, equipo_left, equipo_right, metrics)
                    ruta_piramide_2 = guardar_grafica_plotly(fig_piramide_2, "piramide_ataque_2.png")
                    st.plotly_chart(fig_piramide_2, use_container_width=True, key = 'piramide_defensa')
            
            # Valoramos si tenemos un único equipo
            elif len(selected_teams) == 1:
                # Creamos dos columnas para mostrar las gráficas en paralelo
                col1, col2 = st.columns(2)

                # Asumimos que la lista selected_teams respeta el orden de selección
                equipo = selected_teams[0]

                with col1:
                    
                    # Definimos las métricas que deseas comparar, con los nombres indicados en la consulta SQL
                    metrics = ["Puntos", "T2 Porc", "T3 Porc", "TC Porc", "TL Porc", "Reb of", "Reb def", "Ast", "Robos", "Tapones", "Pérdidas"]
                    
                    # Llamamos a la función de pirámide de 1 único equipo pasando el DataFrame original de la consulta
                    st.markdown("<h3 style='text-align: center;'>Promedios ataque</h3>", unsafe_allow_html=True)
                    fig_piramide_3 = grafica_piramide_equipo(df_sql_team, equipo, metrics)
                    ruta_piramide_3 = guardar_grafica_plotly(fig_piramide_3, "piramide_ataque_3.png")
                    st.plotly_chart(fig_piramide_3, use_container_width=True, key = 'piramide_ataque_2')
                
                with col2:
                    
                    # Definimos las métricas que deseas comparar, con los nombres indicados en la consulta SQL
                    metrics = ["Puntos recibidos", "T2 Porc rival", "T3 Porc rival", "TC Porc rival", "TL Porc rival", "Reb of rival",
                            "Reb def rival", "Ast rival", "Robos rival", "Tapones rival", "Pérdidas rival"]  # Ajusta según tus necesidades
                    
                    # Llamamos a la función de pirámide de 1 único equipo pasando el DataFrame original de la consulta
                    st.markdown("<h3 style='text-align: center;'>Promedios defensa</h3>", unsafe_allow_html=True)
                    fig_piramide_4 = grafica_piramide_equipo(df_sql_opp, equipo, metrics)
                    ruta_piramide_4 = guardar_grafica_plotly(fig_piramide_4, "piramide_ataque_4.png")
                    st.plotly_chart(fig_piramide_4, use_container_width=True, key = 'piramide_defensa_2')

            # Mostramos la tabla filtrada con los datos de los equipos seleccionados
            if len(selected_teams) > 0:
                # Filtramos el dataframe para los equipos seleccionados
                df_filtrado = df_temporada[df_temporada['team_name'].isin(selected_teams)]
                
                # Llamamos a la función que genera las dos tablas a partir del DataFrame filtrado
                tabla_ataque, tabla_defensa = crear_tablas(df_filtrado)
                
                # Creamos dos columnas para mostrar las tablas en paralelo
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h3 style='text-align: center;'>Estadísticas avanzadas ataque</h3>", unsafe_allow_html=True)
                    # Para formatear los números, obtenemos las columnas numéricas de la tabla de ataque y aplicamos formato
                    numeric_cols = tabla_ataque.select_dtypes(include=['number']).columns
                    formato = {col: "{:.2f}" for col in numeric_cols}
                    styled_tabla_ataque = tabla_ataque.style.format(formato)
                    st.dataframe(styled_tabla_ataque)
                
                with col2:
                    st.markdown("<h3 style='text-align: center;'>Estadísticas avanzadas defensa</h3>", unsafe_allow_html=True)
                    # Para formatear los números, obtenemos las columnas numéricas de la tabla de defensa y aplicamos formato
                    numeric_cols = tabla_defensa.select_dtypes(include=['number']).columns
                    formato = {col: "{:.2f}" for col in numeric_cols}
                    styled_tabla_defensa = tabla_defensa.style.format(formato)
                    st.dataframe(styled_tabla_defensa)
            
            # Realizamos las gráficas comparación de eficiencia defensiva y ofensiva
            if len(selected_teams) > 0:
                st.markdown("<h3 style='text-align: center;'>Eficiencia ofensiva vs eficiencia defensiva</h3>", unsafe_allow_html=True)
                scatter_fig = scatter_eficiencia(df_temporada, selected_teams)
                ruta_scatter = guardar_grafica_plotly(scatter_fig, "scatter_eficiencia.png")
                st.plotly_chart(scatter_fig, use_container_width=True, key = 'ef_defensa_vs_ef_ataque')
                
                # Posteriormente dividimos en 3 columnas para mostrar gráficos diversos
                col1, col2, col3 = st.columns(3, vertical_alignment="top")
                
                with col1:
                    # Si hay 2 equipos seleccionados, incluimos lo siguiente en la columna 1
                    if len(selected_teams) == 2:
                        # Asumimos que la lista selected_teams respeta el orden de selección
                        equipo_left = selected_teams[0]
                        equipo_right = selected_teams[1]
                        st.markdown(f"<h3 style='text-align: center;'>Distribución posesiones {equipo_left} </h3>", unsafe_allow_html=True)
                        # Indicamos las métricas a incluir en la gráfica radar
                        posesiones_equipo = ['T2I', 'T3I', 'Pérdidas', 'TLI']
                        # Filtramos los colores azules para la gráfica de donut
                        colores_azules = ["steelblue", "blue", "#33fff6", "#44b1de"]
                        # Hacemos gráfica donut para el primer equipo de sus datos
                        fig_donut_1 = grafica_donut_posesiones(df_sql_team, equipo_left, posesiones_equipo, colores=colores_azules)
                        ruta_donut_1 = guardar_grafica_plotly(fig_donut_1, "donut_equipo_1.png")
                        st.plotly_chart(fig_donut_1, use_container_width=True, key = 'donut_comparativo_ataque')

                    # Si hay 1 equipo seleccionado, incluimos lo siguiente en la columna 1
                    elif len(selected_teams) == 1:
                        equipo = selected_teams[0]
                        st.markdown(f"<h3 style='text-align: center;'>Distribución posesiones {equipo} </h3>", unsafe_allow_html=True)
                        # Indicamos las métricas a incluir en la gráfica radar
                        posesiones_equipo = ['T2I', 'T3I', 'Pérdidas', 'TLI']
                        # Filtramos los colores azules para la gráfica de donut
                        colores_azules = ["steelblue", "blue", "#33fff6", "#44b1de"]
                        # Hacemos gráfica donut para el equipo seleccionado de sus datos
                        fig_donut_2 = grafica_donut_posesiones(df_sql_team, equipo, posesiones_equipo, colores=colores_azules)
                        ruta_donut_2 = guardar_grafica_plotly(fig_donut_2, "donut_equipo_2.png")
                        st.plotly_chart(fig_donut_2, use_container_width=True, key = 'donut_individual_1_ataque')
                        
                with col2:
                    # Si hay 2 equipos seleccionados, incluimos lo siguiente en la columna 2
                    if len(selected_teams) == 2:
                        # Asumimos que la lista selected_teams respeta el orden de selección
                        equipo_left = selected_teams[0]
                        equipo_right = selected_teams[1]
                        st.markdown("<h3 style='text-align: center;'>Comparación estadísticas avanzadas equipo en ataque</h3>", unsafe_allow_html=True)
                        # Generamos el dataframe para el radar de ataque
                        df_radar_ataque = df_temporada.copy()
                        # Renombramos las columnas
                        df_radar_ataque = df_radar_ataque.rename(columns = {'ortg':'Of. Rtg', 'efg%': 'eFG%', 'ts%':'TS%', 'ftr':'FT Rate','vol2p':'Vol. T2%',
                                                                            'vol3p':'Vol. T3%', 'or%':'Of. Reb%', 'ast%':'Ast%', 'to%':'Pérdidas%',
                                                                            'four_factors':'Four Factors'})
                        # Filtramos el dataframe entre los equipos seleccionados
                        df_selected = df_radar_ataque[df_radar_ataque['team_name'].isin(selected_teams)]
                        
                        # Escogemos las métricas para el radar
                        est_ataque = ['Of. Rtg', 'eFG%', 'TS%', 'FT Rate', 'Vol. T2%', 'Vol. T3%', 'Of. Reb%', 'Ast%', 'Pérdidas%', 'Four Factors']
                        # Indicamos los equipos a introducir en el radar
                        teams = [equipo_left, equipo_right]
                        # Generamos la gráfica radar comparativa
                        fig_radar_1 = grafica_radar_comparativo(df_selected, df_radar_ataque, teams, metrics = est_ataque)
                        ruta_radar_1 = guardar_grafica_plotly(fig_radar_1, "radar_comparativo_1.png")
                        st.plotly_chart(fig_radar_1, use_container_width=True, key = 'radar_1')

                    # Si hay 1 equipo seleccionado, incluimos lo siguiente en la columna 2
                    elif len(selected_teams) == 1:
                        # Indicamos que se selecciona el único equipo que hay
                        equipo_left = selected_teams[0]
                        st.markdown("<h3 style='text-align: center;'>Estadísticas avanzadas equipo en ataque</h3>", unsafe_allow_html=True)
                        # Generamos el dataframe para el radar de ataque
                        df_radar_ataque = df_temporada.copy()
                        # Renombramos las columnas
                        df_radar_ataque = df_radar_ataque.rename(columns = {'ortg':'Of. Rtg', 'efg%': 'eFG%', 'ts%':'TS%', 'ftr':'FT Rate','vol2p':'Vol. T2%',
                                                                            'vol3p':'Vol. T3%', 'or%':'Of. Reb%', 'ast%':'Ast%', 'to%':'Pérdidas%',
                                                                            'four_factors':'Four Factors'})
                        # Filtramos el dataframe entre los equipos seleccionados
                        df_selected = df_radar_ataque[df_radar_ataque['team_name'].isin(selected_teams)]
                        
                        # Asumimos que la lista selected_teams respeta el orden de selección
                        est_ataque = ['Of. Rtg', 'eFG%', 'TS%', 'FT Rate', 'Vol. T2%', 'Vol. T3%', 'Of. Reb%', 'Ast%', 'Pérdidas%', 'Four Factors']
                        teams = [equipo_left]
                        # Generamos la gráfica radar comparativa
                        fig_radar_2 = grafica_radar_comparativo(df_selected, df_radar_ataque, teams, metrics = est_ataque)
                        ruta_radar_2 = guardar_grafica_plotly(fig_radar_2, "radar_comparativo_2.png")
                        st.plotly_chart(fig_radar_2, use_container_width=True, key = 'radar_2')
                
                with col3:
                    # Si hay 2 equipos seleccionados, incluimos lo siguiente en la columna 3
                    if len(selected_teams) == 2:
                        # Asumimos que la lista selected_teams respeta el orden de selección
                        equipo_left = selected_teams[0]
                        equipo_right = selected_teams[1]
                        st.markdown(f"<h3 style='text-align: center;'>Distribución posesiones {equipo_right} </h3>", unsafe_allow_html=True)
                        # Indicamos las métricas a incluir en la gráfica radar
                        posesiones_equipo = ['T2I', 'T3I', 'Pérdidas', 'TLI']
                        # Filtramos los colores rojos para la gráfica de donut
                        colores_rojos = ["tomato", "red", "#b11f1f", "#f88686"]
                        # Hacemos gráfica donut para el equipo seleccionado de sus datos
                        fig_donut_3 = grafica_donut_posesiones(df_sql_team, equipo_right, posesiones_equipo, colores = colores_rojos)
                        ruta_donut_3 = guardar_grafica_plotly(fig_donut_3, "donut_equipo_3.png")
                        st.plotly_chart(fig_donut_3, use_container_width=True, key = 'donut_comparativo_2_ataque')
                        

                    elif len(selected_teams) == 1:
                        # Si hay 1 equipo seleccionado, incluimos lo siguiente en la columna 3
                        equipo = selected_teams[0]
                        st.markdown(f"<h3 style='text-align: center;'>Distribución posesiones rivales de {equipo} </h3>", unsafe_allow_html=True)
                        # Filtramos los colores rojos para la gráfica de donut
                        colores_rojos = ["tomato", "red", "#b11f1f", "#f88686"]
                        # Indicamos las métricas a incluir en la gráfica radar
                        posesiones_rival = ['T2I rival', 'T3I rival', 'Pérdidas rival', 'TLI rival']
                        # Hacemos gráfica donut para el equipo seleccionado de sus datos
                        fig_donut_4 = grafica_donut_posesiones(df_sql_opp, equipo, posesiones_rival, colores = colores_rojos)
                        ruta_donut_4 = guardar_grafica_plotly(fig_donut_4, "donut_equipo_4.png")
                        st.plotly_chart(fig_donut_4, use_container_width=True, key = 'donut_individual_2_ataque')
                
                # Generamos nueva línea para la segunda fila de gráficas
                col1, col2, col3 = st.columns(3, vertical_alignment="top")
                
                with col1:
                    # Si hay 2 equipos seleccionados, incluimos lo siguiente en la columna 1
                    if len(selected_teams) == 2:
                        # Asumimos que la lista selected_teams respeta el orden de selección
                        equipo_left = selected_teams[0]
                        equipo_right = selected_teams[1]                  
                        st.markdown(f"<h3 style='text-align: center;'>Distribución posesiones rivales de {equipo_left} </h3>", unsafe_allow_html=True)
                        # Indicamos las métricas a incluir en la gráfica radar
                        posesiones_rival = ['T2I rival', 'T3I rival', 'Pérdidas rival', 'TLI rival']
                        # Hacemos gráfica donut para el equipo seleccionado de sus datos
                        fig_donut_5 = grafica_donut_posesiones(df_sql_opp, equipo_left, posesiones_rival, colores = colores_azules)
                        ruta_donut_5 = guardar_grafica_plotly(fig_donut_5, "donut_equipo_5.png")
                        st.plotly_chart(fig_donut_5, use_container_width=True, key = 'donut_comparativo_1_defensa')

                with col2:
                    # Si hay 2 equipos seleccionados, incluimos lo siguiente en la columna 2
                    if len(selected_teams) == 2:
                        # Asumimos que la lista selected_teams respeta el orden de selección
                        equipo_left = selected_teams[0]
                        equipo_right = selected_teams[1]
                        
                        st.markdown(f"<h3 style='text-align: center;'>Comparación estadísticas avanzadas equipo en defensa</h3>", unsafe_allow_html=True)
                        
                        # Generamos el dataframe para el radar de defensa
                        df_radar_defensa = df_temporada.copy()
                        # Renombramos las columnas
                        df_radar_defensa = df_radar_defensa.rename(columns = {'drtg':'Def. Rtg', 'dr%':'Def. Reb%', 'efg%_opp': 'eFG% Rivales', 'ts%_opp':'TS% Rivales',
                                                                            'ftr_opp':'FT Rate Rivales','vol2p_opp':'Vol. T2% Rivales', 'vol3p_opp':'Vol. T3% Rivales',
                                                                            'ast%_opp':'Ast% Rivales', 'to%_opp':'Pérdidas% Rivales', 'st%':'Robos%',
                                                                            'four_factors_opp':'Four Factors Rivales'})
                        # Filtramos el dataframe entre los equipos seleccionados
                        df_selected = df_radar_defensa[df_radar_defensa['team_name'].isin(selected_teams)]
                        # Escogemos las métricas para el radar
                        est_defensa = ['Def. Rtg', 'Def. Reb%', 'eFG% Rivales', 'TS% Rivales', 'FT Rate Rivales', 'Vol. T2% Rivales', 'Vol. T3% Rivales', 'Ast% Rivales',
                                    'Pérdidas% Rivales', 'Robos%', 'Four Factors Rivales']
                        # Generamos la gráfica radar comparativa
                        fig_radar_3 = grafica_radar_comparativo(df_selected, df_radar_defensa, teams, metrics = est_defensa)
                        ruta_radar_3 = guardar_grafica_plotly(fig_radar_3, "radar_comparativo_3.png")
                        st.plotly_chart(fig_radar_3, use_container_width=True, key = 'radar_3')

                    elif len(selected_teams) == 1:
                        # Si hay 1 equipo seleccionado, incluimos lo siguiente en la columna 2
                        equipo_left = selected_teams[0]
                        st.markdown("<h3 style='text-align: center;'>Estadísticas rivales</h3>", unsafe_allow_html=True)
                        # Generamos el dataframe para el radar de defensa
                        df_radar_defensa = df_temporada.copy()
                        # Renombramos las columnas
                        df_radar_defensa = df_radar_defensa.rename(columns = {'drtg':'Def. Rtg', 'dr%':'Def. Reb%', 'efg%_opp': 'eFG% Rivales', 'ts%_opp':'TS% Rivales',
                                                                            'ftr_opp':'FT Rate Rivales','vol2p_opp':'Vol. T2% Rivales', 'vol3p_opp':'Vol. T3% Rivales',
                                                                            'ast%_opp':'Ast% Rivales', 'to%_opp':'Pérdidas% Rivales', 'st%':'Robos%',
                                                                            'four_factors_opp':'Four Factors Rivales'})
                        # Filtramos el dataframe entre los equipos seleccionados
                        df_selected = df_radar_defensa[df_radar_defensa['team_name'].isin(selected_teams)]
                        # Escogemos las métricas para el radar
                        est_defensa = ['Def. Rtg', 'Def. Reb%', 'eFG% Rivales', 'TS% Rivales', 'FT Rate Rivales', 'Vol. T2% Rivales', 'Vol. T3% Rivales', 'Ast% Rivales',
                                    'Pérdidas% Rivales', 'Robos%', 'Four Factors Rivales']
                        fig_radar_4 = grafica_radar_comparativo(df_selected, df_radar_defensa, teams, metrics = est_defensa)
                        ruta_radar_4 = guardar_grafica_plotly(fig_radar_4, "radar_comparativo_4.png")
                        st.plotly_chart(fig_radar_4, use_container_width=True, key = 'radar_4')
                
                with col3:
                    if len(selected_teams) == 2:
                        # Asumimos que la lista selected_teams respeta el orden de selección
                        equipo_left = selected_teams[0]
                        equipo_right = selected_teams[1]
                        st.markdown(f"<h3 style='text-align: center;'>Distribución posesiones rivales de {equipo_right} </h3>", unsafe_allow_html=True)
                        # Indicamos las métricas a incluir en la gráfica radar    
                        posesiones_rival = ['T2I rival', 'T3I rival', 'Pérdidas rival', 'TLI rival']
                        # Hacemos gráfica donut para el equipo seleccionado de sus datos
                        fig_donut_6 = grafica_donut_posesiones(df_sql_opp, equipo_right, posesiones_rival, colores = colores_rojos)
                        ruta_donut_6 = guardar_grafica_plotly(fig_donut_6, "donut_equipo_6.png")
                        st.plotly_chart(fig_donut_6, use_container_width=True, key = 'donut_comparativo_2_defensa')
                
            # Si es mayor que 0 los equipos seleccionados, generamos pdf y botón de página
            if len(selected_teams) > 0:
                if st.button("Generar PDF"):

                    if not os.path.exists('temp'):
                        os.makedirs('temp')
                    
                    posesiones_equipo = ['T2I', 'T3I', 'Pérdidas', 'TLI']
                    colores_azules = ["steelblue", "blue", "#33fff6", "#44b1de"]
                    
                    pdf = generate_pdf_pag1(page_title = 'Comparador de equipos ABA League 2', selected_teams = selected_teams, df_temporada = df_temporada, df_sql_team = df_sql_team,
                                            df_sql_opp = df_sql_opp, tabla_ataque = tabla_ataque, tabla_defensa = tabla_defensa, 
                                            output_filename= 'common/pdf_pestana1.pdf')
                    
                    # Ruta al archivo generado
                    pdf_path = os.path.join("common", "pdf_pestana1.pdf")

                    # Leemos el PDF en binario
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()

                    # Botón para descargar el PDF
                    st.download_button(
                        label="📄 Descargar PDF",
                        data=pdf_bytes,
                        file_name="informe_equipo_ABA_League_2.pdf",
                        mime="application/pdf"
                    )
