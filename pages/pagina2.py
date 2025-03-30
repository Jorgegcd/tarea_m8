import streamlit as st
import common.menu as menu
import pandas as pd
import os
from common.functions_pag2 import caja_metricas, calcular_metricas, grafica_evolucion_resultados, calcular_percentiles, radar_comparativo
from common.pdf_generator_pag2 import generate_pdf_pag2
from common.functions import print_window
import common.login as login
from sqlalchemy import create_engine
import plotly.express as px
import base64
import streamlit.components.v1 as components
from fpdf import FPDF
from PIL import Image  # Necesario para abrir la imagen como objeto

# Ir al directorio padre (uno por encima de /pages)
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
logo_path = os.path.join(base_path, "images", "logo_aba_2.png") # Ruta para llegar a la carpeta y a la imagen del logo

# Cargamos la imagen del logo como objeto
logo_image = Image.open(logo_path)

# Configurar la página para que el botón de navegación vaya hasta el principio cuando se abre la página.
st.set_page_config(page_title="Comparador totales equipos", page_icon=logo_image) # Cambiamos nombre de la página e introducimos el logo de la liga en el explorador

login.generarLogin()

if 'usuario' in st.session_state:

    # Crea el engine de conexión a la base de datos MySQL
    engine = create_engine("mysql+pymysql://jgcornejo:Avellanas9?@localhost:3306/tarea_m8", echo=True)

    # Leer la tabla desde MySQL
    df_jornadas = pd.read_sql("SELECT * FROM matches", engine)

    # Indicamos título de página
    st.markdown(f"<h1 style='text-align: center;'>Comparador por jornadas y totales de equipos ABA League 2</h1>", unsafe_allow_html=True)

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
                # Creamos seis columnas para mostrar las fichas en paralelo
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
                    poss = 0.96*(fga + 0.44 * fta - oreb + to)

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
                        caja_metricas("Partidos (Victorias/ Derrotas)", f"{data['partidos']} ({data['victorias']}/{data['derrotas']})")
                    
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
                        caja_metricas("Partidos (Victorias/ Derrotas)", f"{data['partidos']} ({data['victorias']}/{data['derrotas']})")
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

                        st.markdown(f"<h4 style='text-align: center;'>Estadísticas globales temporada y selección de jornadas - {team}</h4>", unsafe_allow_html=True)
                        st.dataframe(tablas[team].set_index('Métrica'), use_container_width=True)
                    
                    # Gráficas de evolución de resultados

                    for team in selected_teams:
                        st.markdown(
                            f"<h4 style='text-align: center;'>Evolución partidos temporada {st.session_state.selected_season} {team}</h4>",
                            unsafe_allow_html=True
                        )

                        team_id = df_temporada[df_temporada['team_name'] == team]['team_id'].iloc[0]

                        # Filtramos SOLO los partidos de ese equipo
                        df_team_jornadas_total = df_jornadas[(df_jornadas['team_id'] == team_id) &
                            (df_jornadas['season'] == st.session_state.selected_season)
                        ].sort_values("week")

                        fig = grafica_evolucion_resultados(df_team_jornadas_total, team, df_temporada)
                        st.plotly_chart(fig, use_container_width=True)
                    
                if len(selected_teams) >= 1:

                    col1, col2 = st.columns(2)

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

                    teams_ids = df_temporada["team_id"].unique()
                    lista_metricas = []

                    for team in teams_ids:
                        df_team = df_jornadas_filtrado[(df_jornadas_filtrado["team_id"] == team) & (df_jornadas_filtrado["season"] == st.session_state.selected_season)]

                        if df_team.empty:
                            continue
                    
                        # Cálculamos la suma de las estadísticas
                        fgm = df_team['fgm'].sum()
                        fga = df_team['fga'].sum()
                        fg3m = df_team['fg3m'].sum()
                        fgm_opp = df_team['fgm_opp'].sum()
                        fga_opp = df_team['fga_opp'].sum()
                        fg3m_opp = df_team['fg3m_opp'].sum()
                        fta = df_team['fta'].sum()
                        fta_opp = df_team['fta_opp'].sum()
                        to = df_team['to'].sum()
                        oreb = df_team['or'].sum()
                        dr = df_team['dr'].sum()
                        ast = df_team['ass'].sum()
                        or_opp = df_team['or_opp'].sum()
                        dr_opp = df_team['dr_opp'].sum()
                        pts = df_team['pts'].sum()
                        pts_opp = df_team['pts_opp'].sum()

                        # Calculamos las posesiones
                        poss = 0.96*(fga + 0.44 * fta - oreb + to)

                        # Cálculo de métricas
                        ortg_jornadas = (pts / poss) * 100 if poss > 0 else 0
                        drtg_jornadas = (pts_opp / poss) * 100 if poss > 0 else 0
                        efg_jornadas = (fgm + (0.5 * fg3m)) / fga
                        efg_opp_jornadas = (fgm_opp + (0.5 * fg3m_opp)) / fga_opp
                        ts_jornadas = pts / (2 * (fga + 0.44 * fta))
                        ts_opp_jornadas = pts_opp / (2 * (fga_opp + 0.44 * fta_opp))
                        oreb_perc_jornadas = oreb / (oreb + dr_opp) if (oreb + dr_opp) > 0 else 0
                        dreb_perc_jornadas = dr / (dr + or_opp) if (dr + or_opp) > 0 else 0
                        ast_pct_jornadas = (ast / fga) * 100 if fgm > 0 else 0
                        to_pct_jornadas = (to / poss) * 100 if poss > 0 else 0
                        ftr_jornadas = (fta / fga) * 100 if fga > 0 else 0

                        lista_metricas.append({
                        "team_id": team,
                        "ortg": ortg_jornadas,
                        "drtg": drtg_jornadas,
                        "ts%": ts_jornadas,
                        "efg%": efg_jornadas,
                        "ts%_opp": ts_opp_jornadas,
                        "efg%_opp": efg_opp_jornadas,
                        "dr%": dreb_perc_jornadas,
                        "or%": oreb_perc_jornadas,
                        "ftr": ftr_jornadas,
                        "ast%": ast_pct_jornadas,
                        "to%": to_pct_jornadas,
                    })
                    
                # Creamos el DataFrame final para calcular percentiles
                df_liga_jornadas = pd.DataFrame(lista_metricas)
                    
                # Cambiamos nombre columnas para mostrar
                df_temporada = df_temporada.rename(columns= {'ortg':'Of.Rtg', 'drtg':'Df.Rtg', 'ts%':'TS', 'efg%':'eFG', 'ts%_opp':'TS Opp',
                                                            'efg%_opp':'eFG Opp', 'dr%':'DReb%', 'or%':'OReb%', 'ftr':'FTR', 'ast%':'Ast%', 'to%':'TO%'})
                df_liga_jornadas = df_liga_jornadas.rename(columns= {'ortg':'Of.Rtg', 'drtg':'Df.Rtg', 'ts%':'TS', 'efg%':'eFG', 'ts%_opp':'TS Opp',
                                                            'efg%_opp':'eFG Opp', 'dr%':'DReb%', 'or%':'OReb%', 'ftr':'FTR', 'ast%':'Ast%', 'to%':'TO%'})
                # Definimos las métricas para el radar
                metrics = ['Of.Rtg', 'Df.Rtg', 'TS', 'eFG', 'TS Opp', 'eFG Opp', 'DReb%', 'OReb%', 'FTR', 'Ast%', 'TO%']

                # Creamos dos columnas para mostrar las gráficas en paralelo
                col1, col2 = st.columns(2)

                if len(selected_teams) == 2:
                    # Seleccionamos equipos en df_temporada
                    team1_id = df_temporada[df_temporada["team_name"] == selected_teams[0]]["team_id"].iloc[0]
                    team2_id = df_temporada[df_temporada["team_name"] == selected_teams[1]]["team_id"].iloc[0]

                    # Calculamos percentiles totales de temporada
                    percentiles_team1_total = calcular_percentiles(df_temporada, team1_id, metrics)
                    percentiles_team2_total = calcular_percentiles(df_temporada, team2_id, metrics)

                    # Calculamos percentiles en jornadas seleccionadas
                    percentiles_team1_jorn = calcular_percentiles(df_liga_jornadas, team1_id, metrics)
                    percentiles_team2_jorn = calcular_percentiles(df_liga_jornadas, team2_id, metrics)
                            
                    with col1:
                        # Radar Temporada completa
                        st.markdown("<h3 style='text-align: center;'>Radar comparativo (Temporada completa)</h3>", unsafe_allow_html=True)
                        fig_total = radar_comparativo(team1 = selected_teams[0], data1 = percentiles_team1_total, team2= selected_teams[1],
                                                    data2 = percentiles_team2_total, titulo = "")
                        st.plotly_chart(fig_total, use_container_width=True, key="fig_total")
                        

                    with col2:
                        # Radar Jornadas seleccionadas
                        st.markdown("<h3 style='text-align: center;'>Radar comparativo (Jornadas seleccionadas)</h3>", unsafe_allow_html=True)
                        fig_jornadas = radar_comparativo(team1 = selected_teams[0], data1 = percentiles_team1_jorn, team2 = selected_teams[1],
                                                        data2 = percentiles_team2_jorn, titulo ="")
                        st.plotly_chart(fig_jornadas, use_container_width=True, key="fig_jornadas")
                        
                
                if len(selected_teams) == 1:
                    
                    # Seleccionamos equipos en df_temporada
                    team1_id = df_temporada[df_temporada["team_name"] == selected_teams[0]]["team_id"].iloc[0]
                    # Calculamos percentiles del equipo seleccionado en df_temporada
                    percentiles_team1_total = calcular_percentiles(df_temporada, team1_id, metrics)

                    # Jornadas seleccionadas
                    percentiles_team1_jorn = calcular_percentiles(df_liga_jornadas, team1_id, metrics)

                    with col1:
                        # Radar Temporada completa
                        st.markdown("<h3 style='text-align: center;'>Radar comparativo (Temporada completa)</h3>", unsafe_allow_html=True)
                        fig_total = radar_comparativo(team1 = selected_teams[0], data1 = percentiles_team1_total, titulo = "")
                        st.plotly_chart(fig_total, use_container_width=True)

                    with col2:
                        # Radar Jornadas seleccionadas
                        st.markdown("<h3 style='text-align: center;'>Radar comparativo (Jornadas seleccionadas)</h3>", unsafe_allow_html=True)
                        fig_jornadas = radar_comparativo(team1 = selected_teams[0], data1 = percentiles_team1_jorn, titulo ="")
                        st.plotly_chart(fig_jornadas, use_container_width=True)