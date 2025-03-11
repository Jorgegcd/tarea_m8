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

def grafica_metricas_comparacion(df, equipo_left, equipo_right, metrics):
    """
    Genera una gráfica de barras horizontal estilo pirámide de población para comparar
    dos equipos. Para cada métrica, los valores del equipo_left se muestran como negativos 
    (a la izquierda) y los del equipo_right como positivos (a la derecha).
    
    Args:
        df (DataFrame): DataFrame obtenido de la consulta SQL (sin estilos).
        equipo_left (str): Nombre del equipo que se mostrará a la izquierda.
        equipo_right (str): Nombre del equipo que se mostrará a la derecha.
        metrics (list): Lista de nombres de columnas (métricas) a comparar. Deben coincidir 
                        exactamente con los alias de la consulta SQL.
    """
    rows = []
    for metric in metrics:
        try:
            left_val = df.loc[df['Equipo'] == equipo_left, metric].iloc[0]
            right_val = df.loc[df['Equipo'] == equipo_right, metric].iloc[0]
        except IndexError:
            st.error(f"No se encontró la métrica '{metric}' para uno de los equipos.")
            return
        # Multiplicamos el valor del equipo de la izquierda por -1 para que se muestre a la izquierda
        rows.append({"Métrica": metric, "Equipo": equipo_left, "Valor": -left_val})
        rows.append({"Métrica": metric, "Equipo": equipo_right, "Valor": right_val})
    
    data_plot = pd.DataFrame(rows)
    
    # Generamos la gráfica de barras horizontal
    fig = px.bar(
        data_plot,
        x="Valor",
        y="Métrica",
        color="Equipo",
        orientation="h",
        barmode="group",
        title="Comparación de métricas entre equipos"
    )
    
    # Quitamos la leyenda
    fig.update_layout(showlegend=False)
    # Eliminamos los textos sobre las barras
    fig.update_traces(texttemplate=None)

    # Establecemos un rango simétrico para el eje x
    max_val = data_plot['Valor'].abs().max()
    fig.update_xaxes(range=[-max_val*1.1, max_val*1.1])
    
    # Agregamos una anotación en x=0 para cada métrica con el nombre de la misma, centrada
    for metric in metrics:
        fig.add_annotation(
            x=0,
            y=metric,
            text=metric,
            showarrow=False,
            font=dict(size=12, color="black"),
            xanchor="center",
            yanchor="middle"
        )
    
    st.plotly_chart(fig, use_container_width=True)