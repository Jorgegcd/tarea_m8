import streamlit as st
import common.menu as menu
import pandas as pd
import os
from common.functions_pag2 import caja_metricas, calcular_metricas
from common.pdf_generator import generate_pdf_pag1
from sqlalchemy import create_engine
import plotly.express as px
import base64
import streamlit.components.v1 as components

# Configurar la página para que el botón de navegación vaya hasta el principio cuando se abre la página.
st.set_page_config(page_title="Estadísticas equipos") # Cambiamos nombre de la página

# Crea el engine de conexión a la base de datos MySQL
engine = create_engine("mysql+pymysql://jgcornejo:Avellanas9?@localhost:3306/tarea_m8", echo=True)

# Leer la tabla desde MySQL
df_jornadas = pd.read_sql("SELECT * FROM matches", engine)

# Mostrar el menú lateral si el usuario está logueado.
if 'usuario' in st.session_state:
    menu.generarMenu(st.session_state['usuario'])
else:
    st.write("Por favor, inicia sesión para ver el menú.")

# Indicamos título de página
st.markdown(f"<h1 style='text-align: center;'>Comparador de totales de equipos ABA League 2</h1>", unsafe_allow_html=True)

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
        # Creamos el slider SOLO si hay datos cargados
        if not df_jornadas.empty:
            jornadas_disponibles = sorted(df_jornadas['week'].unique())
            min_jornada = int(min(jornadas_disponibles))
            max_jornada = int(max(jornadas_disponibles))

            jornada_inicio, jornada_fin = st.slider(
                "Selecciona el rango de jornadas a analizar:",
                min_value=min_jornada,
                max_value=max_jornada,
                value=(min_jornada, max_jornada)
            )

            # Guardamos el filtro en session_state (opcional)
            st.session_state.jornada_inicio = jornada_inicio
            st.session_state.jornada_fin = jornada_fin

            # Filtramos el dataframe según el slider
            df_jornadas_filtrado = df_jornadas[
                (df_jornadas['week'] >= jornada_inicio) & (df_jornadas['week'] <= jornada_fin)
            ]

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
                with col[0]:
                    if os.path.exists(logos[0]):
                        with open(logos[0], "rb") as image_file:
                            encoded_logo = base64.b64encode(image_file.read()).decode()
                        st.markdown(
                            f"""<div style="text-align:center;">
                            <img src="data:image/png;base64,{encoded_logo}" width="150">
                            </div>""",
                            unsafe_allow_html=True
                        )
                    else:
                        st.error(f"No se encontró la imagen: {logos[0]}")
            elif len(logos) == 2:
                cols = st.columns(2)
                with cols[0]:
                    if os.path.exists(logos[0]):
                        with open(logos[0], "rb") as image_file:
                            encoded_logo = base64.b64encode(image_file.read()).decode()
                        st.markdown(
                            f"""<div style="text-align:center;">
                            <img src="data:image/png;base64,{encoded_logo}" width="150">
                            </div>""",
                            unsafe_allow_html=True
                        )
                    else:
                        st.error(f"No se encontró la imagen: {logos[0]}")
                with cols[1]:
                    if os.path.exists(logos[1]):
                        with open(logos[1], "rb") as image_file:
                            encoded_logo = base64.b64encode(image_file.read()).decode()
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
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            # Diccionario para guardar métricas por equipo
            equipos_data = {}
            
            for team in selected_teams:
                # Obtenemos el ID del equipo
                team_id = df_temporada[df_temporada['team_name'] == team]['team_id'].iloc[0]

                # Filtramos las jornadas del equipo
                df_team_jornadas = df_jornadas_filtrado[
                    (df_jornadas_filtrado['team_id'] == team_id) &
                    (df_jornadas_filtrado['season'] == st.session_state.selected_season)
                ]

                # Si no hay partidos, mostramos aviso
                if df_team_jornadas.empty:
                    st.warning("No hay partidos para este equipo en el rango seleccionado.")
                    continue

                # Victories & defeats
                victorias = (df_team_jornadas['w/l'].str.upper() == 'W').sum()
                derrotas = (df_team_jornadas['w/l'].str.upper() == 'L').sum()
                partidos_jornadas = len(df_team_jornadas)

                # Suma de estadísticas necesarias
                fga = df_team_jornadas['fga'].sum()
                fta = df_team_jornadas['fta'].sum()
                to = df_team_jornadas['to'].sum()
                oreb = df_team_jornadas['or'].sum()
                pts = df_team_jornadas['pts'].sum()
                pts_opp = df_team_jornadas['pts_opp'].sum()

                # Filtrar puntos reales desde la BBDD (según jornada y equipo)
                poss =(fga + 0.44 * fta - oreb + to)

                # Calculamos la eficiencia ofensiva y defensiva del equipo seleccionado
                ortg_jornadas = (pts / poss) * 100 if poss > 0 else 0
                drtg_jornadas = (pts_opp / poss) * 100 if poss > 0 else 0

                # Total temporada
                df_total = df[(df['team_name'] == team) & (df['season'] == st.session_state.selected_season)]
                ortg_tot = df_total['ortg'].iloc[0]
                drtg_tot = df_total['drtg'].iloc[0]
                partidos_tot = df_total['matches'].iloc[0]

                # Guardamos los datos en el diccionario
                equipos_data[team] = {
                    'ortg_tot': ortg_tot,
                    'drtg_tot': drtg_tot,
                    'partidos_tot': partidos_tot,
                    'victorias': victorias,
                    'derrotas': derrotas,
                    'ortg_jornada': ortg_jornadas,
                    'drtg_jornada': drtg_jornadas,
                    'partidos': partidos_jornadas
                }
            
            if len(selected_teams) >= 1:
                team1 = selected_teams[0]
                data = equipos_data[team1]
                with col1:
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Eficiencia Ofensiva (Total Liga)", f"{data['ortg_tot']:.2f}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Eficiencia Ofensiva (Jornadas)", f"{data['ortg_jornada']:.2f}")
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Eficiencia Defensiva (Total Liga)", f"{data['drtg_tot']:.2f}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Eficiencia Defensiva (Jornadas)", f"{data['drtg_jornada']:.2f}")
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Partidos (Totales)", f"{data['partidos_tot']}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Partidos (Victorias / Derrotas)", f"{data['partidos']} ({data['victorias']} / {data['derrotas']})")
                
            if len(selected_teams) == 2:
                team2 = selected_teams[1]
                data = equipos_data[team2]
                with col4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Eficiencia Ofensiva (Total Liga)", f"{data['ortg_tot']:.2f}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Eficiencia Ofensiva (Jornadas)", f"{data['ortg_jornada']:.2f}")
                with col5:
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Eficiencia Defensiva (Total Liga)", f"{data['drtg_tot']:.2f}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Eficiencia Defensiva (Jornadas)", f"{data['drtg_jornada']:.2f}")
                with col6:
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Partidos (Totales)", f"{data['partidos_tot']}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    caja_metricas("Partidos (Victorias / Derrotas)", f"{data['partidos']} ({data['victorias']} / {data['derrotas']})")
                    st.markdown("<br>", unsafe_allow_html=True)

            if len(selected_teams) >= 1:
                tablas = {}

                for team in selected_teams:
                    df_total = df_jornadas[(df_jornadas['team_id'] == df_temporada[df_temporada['team_name'] == team]['team_id'].iloc[0]) &
                                        (df_jornadas['season'] == st.session_state.selected_season)]
                    
                    df_filtrado = df_jornadas_filtrado[
                        (df_jornadas_filtrado['team_id'] == df_temporada[df_temporada['team_name'] == team]['team_id'].iloc[0]) &
                        (df_jornadas_filtrado['season'] == st.session_state.selected_season)
                    ]

                    metrics_total = calcular_metricas(df_total, team)
                    metrics_filtrado = calcular_metricas(df_filtrado, team)

                    # Creamos DataFrame para mostrar
                    df_metrics = pd.DataFrame({
                        'Métrica': list(metrics_total.keys()),
                        'Temporada completa': list(metrics_total.values()),
                        'Jornadas seleccionadas': list(metrics_filtrado.values())
                    })

                    tablas[team] = df_metrics

                    st.markdown(f"### 📊 Tabla comparativa: {team}")
                    st.dataframe(tablas[team].set_index('Métrica'), use_container_width=True)
