import streamlit as st
import plotly.express as px
import os
import base64

def caja_metricas(titulo, valor, color_fondo="#f0f2f6"):
    st.markdown(f"""
        <div style='background-color: {color_fondo}; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0px 0px 6px rgba(0,0,0,0.1);height: 160px; 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
        '>
            <div style='font-size: 18px; font-weight: bold; color: #333;'>{titulo}</div>
            <div style='font-size: 28px; font-weight: bold; margin-top: 10px; color: #1f77b4;'>{valor}</div>
        </div>
    """, unsafe_allow_html=True)

def calcular_metricas(df, team_name, season=None):
    if season:
        df = df[(df['team_name'] == team_name) & (df['season'] == season)]
    else:
        df = df.copy()

    if df.empty:
        return {}

    # Datos agregados
    pts = df['pts'].sum()
    pts_opp = df['pts_opp'].sum()
    fga = df['fga'].sum()
    fta = df['fta'].sum()
    to = df['to'].sum()
    or_ = df['or'].sum()
    dr = df['dr'].sum()
    ast = df['ass'].sum()
    fgm = df['fgm'].sum()
    fg3m = df['fg3m'].sum()
    fgm_opp = df['fgm_opp'].sum()
    fg3m_opp = df['fg3m_opp'].sum()

    fga_opp = df['fga_opp'].sum()
    fta_opp = df['fta_opp'].sum()
    or_opp = df['or_opp'].sum()
    dr_opp = df['dr_opp'].sum()

    poss = 0.96* (fga + 0.44 * fta - or_ + to)

    ortg = (pts / poss) * 100 if poss > 0 else 0
    drtg = (pts_opp / poss) * 100 if poss > 0 else 0
    efg = (fgm + (0.5 * fg3m)) / fga
    efg_opp = (fgm_opp + (0.5 * fg3m_opp)) / fga_opp
    ts = pts / (2 * (fga + 0.44 * fta))
    ts_opp = pts_opp / (2 * (fga_opp + 0.44 * fta_opp))
    reb_of = or_ / (or_ + dr_opp) if (or_ + dr_opp) > 0 else 0
    reb_def = dr / (dr + or_opp) if (dr + or_opp) > 0 else 0
    ast_pct = (ast / fga) * 100 if fgm > 0 else 0
    to_pct = (to / poss) * 100 if poss > 0 else 0
    ftr = (fta / fga) * 100 if fga > 0 else 0

    return {
        'Partidos': len(df),
        'Of. Rating': round(ortg, 2),
        'Def. Rating': round(drtg, 2),
        'TS%': round(ts * 100, 1),
        'eFG%': round(efg * 100, 1),
        '%TS rivales': round(ts * 100, 1),
        'eFG rivales': round(efg_opp * 100, 1),
        '% Rebote Of': round(reb_of * 100, 1),
        '% Rebote Def': round(reb_def * 100, 1),
        'FT Rate': round(ftr, 2),
        '% Asistencias': round(ast_pct, 1),
        '% Pérdidas': round(to_pct, 1)
    }

def grafica_evolucion_resultados(df_team_jornadas, team_name):
    # Calculamos la diferencia de puntos
    df_team_jornadas = df_team_jornadas.copy()
    df_team_jornadas["diff"] = df_team_jornadas["pts"] - df_team_jornadas["pts_opp"]
    df_team_jornadas["resultado"] = df_team_jornadas["w/l"].str.upper().map({"W": "Victoria", "L": "Derrota"})
    df_team_jornadas["color"] = df_team_jornadas["resultado"].map({"Victoria": "blue", "Derrota": "red"})

    fig = px.scatter(
        df_team_jornadas,
        x="week",
        y="diff",
        color="resultado",
        title=f"Evolución de resultados {team_name}",
        labels={"week": "Jornada", "diff": "Diferencia de puntos"},
    )

    # Calculamos un tamaño para los logos (por ejemplo, 5% del rango de cada eje)
    x_range = df_team_jornadas["week"].max() - df_team_jornadas["week"].min()
    y_range = df_team_jornadas["diff"].max() - df_team_jornadas["diff"].min()
    sizex = x_range * 0.2
    sizey = y_range * 0.2
    
    # Obtenemos la ruta absoluta usando os.getcwd()
    current_dir = os.getcwd()

    for _, row in df_team_jornadas.iterrows():
        team_opp = row["team_id_opp"]
        
        # Construimos la ruta absoluta: images está en la raíz (tarea_m8/images)
        logo_path = os.path.join(current_dir, "images", "teams", f"{team_opp}.png")

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                encoded_logo = base64.b64encode(image_file.read()).decode()

            fig.add_layout_image(
                dict(
                    source="data:image/png;base64," + encoded_logo,
                    x=row["week"],
                    y=row["diff"],
                    xref="x",
                    yref="y",
                    sizex=sizex,
                    sizey=sizey,
                    xanchor="center",
                    yanchor="middle",
                    layer="above"
                )
            )
        else:
            st.error(f"No se encontró la imagen: {logo_path}")

    fig.update_traces(marker=dict(size=12, line=dict(width=1)))
    fig.update_layout(showlegend=False, height=400)
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='gray')
    return fig
