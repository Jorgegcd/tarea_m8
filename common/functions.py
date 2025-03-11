import pandas as pd
import plotly.express as px
import streamlit as st

# Supongamos que "df" es tu DataFrame original
def crear_tablas(df):
    # Columnas para la tabla de ataque
    columnas_tabla1 = [
        'team_name', 'matches', 'pace', 'ortg', 'efg%', 'ts%', 'ppt2', 'vol2p', 'ppt3', 'vol3p', 'pptl', 'ftr', 'or%', 
        'ast%', 'st%', 'to%', 'blk%', 'four_factors'
    ]
    # Columnas para la tabla de defensa
    columnas_tabla2 = [
        'team_name', 'matches', 'pace', 'drtg', 'dr%', 'tr%', 'efg%_opp', 'ts%_opp', 'ppt2_opp', 'vol2p_opp', 'ppt3_opp', 
        'vol3p_opp', 'pptl_opp', 'ftr_opp', 'ast%_opp', 'st%_opp', 'to%_opp', 'blk%_opp', 'four_factors_opp'
    ]
    
    tabla1 = df[columnas_tabla1].copy()
    tabla2 = df[columnas_tabla2].copy()

    tabla1 = tabla1.rename(columns = {'team_name':"Equipo", 'matches':"Partidos", 'pace':"Pace", 'ortg':"Eficiencia Ofensiva", 'efg%':"eFG%", 'ts%':"TS%", 'ppt2':"PPT2",
                             'vol2p':"Vol. T2%", 'ppt3':"PPT3", 'vol3p':"Vol. T3%", 'pptl':"PPTL", 'ftr':"FT Rate", 'or%':"Reb. Of.%", 'ast%':"Ast%", 'st%':"Robos%",
                             'to%':"Pérdidas%", 'blk%':"Tapones%", 'four_factors':"Four Factors"})
    
    tabla2 = tabla2.rename(columns = {'team_name':"Equipo", 'matches':"Partidos", 'pace':"Pace", 'drtg':"Eficiencia Defensiva", 'dr%':"Reb. Def.%", 'tr%':"Reb. Totales%", 
                             'efg%_opp':"eFG% Rivales", 'ts%_opp':"TS% Rivales", 'ppt2_opp':"PPT2 Rivales", 'vol2p_opp':"Vol. T2% Rivales", 'ppt3_opp':"PPT3 Rivales",
                             'vol3p_opp':"Vol. T3% Rivales", 'pptl_opp':"PPTL Rivales", 'ftr_opp':'FT Rate Rivales', 'ast%_opp': 'Ast% Rivales', 'st%_opp': 'Robos% Rivales',
                              'to%_opp': 'Pérdidas% Rivales', 'blk%_opp':'Tapones% Rivales', 'four_factors_opp':'Four Factors Rivales'})
    
    return tabla1, tabla2

def grafica_metricas_comparacion(df, selected_teams, metrics):
    """
    Genera una gráfica de barras horizontal que compara para cada métrica
    los valores de los equipos seleccionados y la mediana de todos los equipos.
    
    Args:
        df (DataFrame): DataFrame filtrado para la temporada seleccionada.
        selected_teams (list): Lista de nombres de equipos seleccionados.
        metrics (list): Lista de métricas (columnas numéricas) a comparar.
    """
    rows = []
    for metric in metrics:
        # Calcular la mediana de la métrica para todos los equipos en la temporada
        median_val = df[metric].median()
        # Agregar los valores para cada equipo seleccionado
        for team in selected_teams:
            try:
                # Se asume que cada equipo tiene una única fila en df
                team_val = df.loc[df['Equipo'] == team, metric].iloc[0]
            except IndexError:
                team_val = None
            rows.append({"Métrica": metric, "Equipo": team, "Valor": team_val})
        # Agregar la mediana
        rows.append({"Métrica": metric, "Equipo": "Mediana", "Valor": median_val})
    
    data_plot = pd.DataFrame(rows)
    
    fig = px.bar(
        data_plot,
        x="Valor",
        y="Métrica",
        color="Equipo",
        orientation="h",
        barmode="group",
        title="Comparación de métricas vs Mediana"
    )
    st.plotly_chart(fig, use_container_width=True)