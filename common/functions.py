import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

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
    Genera una gráfica estilo pirámide de población para comparar dos equipos.
    Los valores del equipo_left se muestran como negativos (a la izquierda) y los
    del equipo_right como positivos (a la derecha). Se añaden anotaciones centradas
    en x=0 con el nombre de cada métrica.
    
    Args:
        df (DataFrame): DataFrame crudo obtenido de la consulta SQL, con columna "Equipo".
        equipo_left (str): Nombre del equipo que se mostrará a la izquierda (primer seleccionado).
        equipo_right (str): Nombre del equipo que se mostrará a la derecha (segundo seleccionado).
        metrics (list): Lista de métricas (cuyos alias deben coincidir con los de df) a comparar.
    """
    left_vals = []
    right_vals = []
    # Recorremos cada métrica y extraemos los valores para cada equipo
    for metric in metrics:
        try:
            left_val = df.loc[df['Equipo'] == equipo_left, metric].iloc[0]
            right_val = df.loc[df['Equipo'] == equipo_right, metric].iloc[0]
        except IndexError:
            st.error(f"No se encontró la métrica '{metric}' para uno de los equipos.")
            return
        left_vals.append(left_val)  # Multiplicamos por -1 para que aparezca a la izquierda
        right_vals.append(right_val)

    # Determinamos un gap en el centro (puede ser un porcentaje del máximo valor)
    max_val = max(max(left_vals), max(right_vals))
    gap = 0.26 * max_val  # ajustá este factor según la escala de tus datos
    
    # Creamos la figura
    fig = go.Figure()
    
    # Añadimos la barra para el equipo izquierdo
    fig.add_trace(go.Bar(
        y=metrics,
        x=[-val for val in left_vals],
        base=[-gap] * len(metrics),
        name=equipo_left,
        orientation='h',
        marker_color='steelblue',
        customdata=left_vals,  # Pasamos los valores originales (positivos)
        hovertemplate="%{y}: %{customdata:.2f}<extra></extra>"
    ))
    
    # Añadimos la barra para el equipo derecho
    fig.add_trace(go.Bar(
        y=metrics,
        x=right_vals,
        base=[gap] * len(metrics),
        name=equipo_right,
        orientation='h',
        marker_color='tomato',
        hovertemplate="%{y}: %{x:.2f}<extra></extra>"
    ))
    
    # Actualizamos el layout para que ambas trazas se superpongan (sin offset vertical)
    fig.update_layout(
        barmode='overlay',
        showlegend=True,  # Mostramos leyenda
    )
    
    # Configuramos un rango simétrico para el eje x considerando el gap
    left_max = gap + max(left_vals)
    right_max = gap + max(right_vals)
    max_range = max(left_max, right_max)
    fig.update_xaxes(range=[-max_range * 1.1, max_range * 1.1])

    # Ocultamos los tick labels del eje y para no duplicar los nombres de las métricas
    fig.update_yaxes(showticklabels=False)
    fig.update_xaxes(showticklabels=False)
    
    # Añadimos una anotación centrada en x=0 para cada métrica (en el eje y)
    annotations = []
    for i, metric in enumerate(metrics):
        annotations.append(dict(
            x=0,
            y=metric,
            text=metric,
            showarrow=False,
            font=dict(size=12),
            xanchor="center",
            yanchor="middle"
        ))
    
        # Valor del equipo de la izquierda (mostrar valor positivo)
        annotations.append(dict(
            x=-gap,
            y=metric,
            text=f"{left_vals[i]:.2f}",
            showarrow=False,
            font=dict(size=12),
            xanchor="right",
            yanchor="middle"
        ))

        # Valor del equipo de la derecha (mostrar valor negativo)
        annotations.append(dict(
            x=gap,
            y=metric,
            text=f"{right_vals[i]:.2f}",
            showarrow=False,
            font=dict(size=12),
            xanchor="left",
            yanchor="middle"
        ))

    fig.update_layout(annotations=annotations)
    
    st.plotly_chart(fig, use_container_width=True)