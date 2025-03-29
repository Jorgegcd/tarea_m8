import streamlit as st

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

    fga_opp = df['fga_opp'].sum()
    fta_opp = df['fta_opp'].sum()
    to_opp = df['to_opp'].sum()
    or_opp = df['or_opp'].sum()
    dr_opp = df['dr_opp'].sum()

    poss = (fga + 0.44 * fta - or_ + to)

    ortg = (pts / poss) * 100 if poss > 0 else 0
    drtg = (pts_opp / poss) * 100 if poss > 0 else 0
    reb_of = or_ / (or_ + dr_opp) if (or_ + dr_opp) > 0 else 0
    reb_def = dr / (dr + or_opp) if (dr + or_opp) > 0 else 0
    ast_pct = (ast / fgm) * 100 if fgm > 0 else 0
    to_pct = (to / poss) * 100 if poss > 0 else 0

    return {
        'Partidos': len(df),
        'ORTG': round(ortg, 2),
        'DRTG': round(drtg, 2),
        '% Rebote Of': round(reb_of * 100, 1),
        '% Rebote Def': round(reb_def * 100, 1),
        '% Asistencias': round(ast_pct * 100, 1),
        '% Pérdidas': round(to_pct * 100, 1)
    }
