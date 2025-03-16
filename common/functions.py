import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import base64

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
    Genera una gráfica estilo pirámide de población para comparar equipos.
    Los valores del equipo_left se muestran como negativos y los del equipo_right como positivos.
    Se añaden anotaciones en x=0 con el nombre de cada métrica y sus valores.
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
    
    fig.update_layout(annotations=annotations,
                      barmode='overlay',
                      showlegend=True,
                      legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
                      )

    fig.update_layout(annotations=annotations)
    
    st.plotly_chart(fig, use_container_width=True)

def grafica_piramide_equipo(df, equipo, metrics):
    left_vals = []
    
    # Recorremos cada métrica y extraemos los valores para cada equipo
    for metric in metrics:
        try:
            left_val = df.loc[df['Equipo'] == equipo, metric].iloc[0]
        except IndexError:
            st.error(f"No se encontró la métrica '{metric}' para uno de los equipos.")
            return
        left_vals.append(left_val) 

    # Determinamos un gap en el centro (puede ser un porcentaje del máximo valor)
    max_val = max(left_vals)
    gap = 0.26 * max_val  # ajustá este factor según la escala de tus datos
    
    # Creamos la figura
    fig = go.Figure()
    
    # Añadimos la barra para el equipo izquierdo
    fig.add_trace(go.Bar(
        y=metrics,
        x=[-val for val in left_vals],
        base=[-gap] * len(metrics),
        name= equipo,
        orientation='h',
        marker_color='steelblue',
        customdata=left_vals,  # Pasamos los valores originales (positivos)
        hovertemplate="%{y}: %{customdata:.2f}<extra></extra>"
    ))
    
    # Actualizamos el layout para que ambas trazas se superpongan (sin offset vertical)
    fig.update_layout(
        barmode='overlay',
        showlegend=True
    )
    
    # Configuramos un rango simétrico para el eje x considerando el gap
    left_max = gap + max(left_vals)
    right_max = gap - max(left_vals)
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
            text=f"{left_vals[i]:.2f}",
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

    fig.update_layout(annotations=annotations)
    
    st.plotly_chart(fig, use_container_width=True)

# Creamos un donut chart con la distribución de posesiones.
def grafica_donut_posesiones(df, equipo, categorias, logo_path=None, colores = None):
    
    # Filtrar el DataFrame para el equipo deseado
    df_equipo = df[df["Equipo"] == equipo]
    # Tomamos la primera fila (suponiendo que es el dato que queremos graficar)
    row = df_equipo.iloc[0]

    # Extraemos los valores correspondientes
    data = {cat: row[cat] for cat in categorias}

    # Agregar la métrica derivada de tiro libre (Pos. Tiro Libre = 0.44 * TL Intentados)
    if "TLI" in row:
        tl_val = data.pop("TLI")
        data["TLI"] = 0.44 * tl_val
    
    elif "TLI rival" in row:
        tl_rival_val = data.pop("TLI rival")
        data["TLI rival"] = 0.44 * tl_rival_val

    else:
        st.error("No se encontró la columna 'TL Intentados' para calcular la posesión por tiro libre.")
        return
    
    # Si los datos son cantidades y queremos porcentajes, los convertimos.
    total = sum(data.values())
    if total != 0:
        data = {cat: (valor / total) * 100 for cat, valor in data.items()}
    
    # Convertimos el diccionario a un DataFrame
    donut_df = pd.DataFrame(list(data.items()), columns=["Categoría", "Valor"])
    
    # Crear el gráfico de rosquilla (donut) con Plotly Express
    fig = px.pie(
        donut_df,
        names="Categoría",
        values="Valor",
        hole=0.5,  # Esto crea el efecto de donut
        color_discrete_sequence=colores
    )
    
    # Configurar el texto del hover y dentro del gráfico para mostrar porcentajes y etiquetas
    fig.update_traces(textposition='inside',
                      textinfo='percent+label',
                      hovertemplate="%{label}: %{value:.2f}<extra></extra>")

    # Eliminar la leyenda
    fig.update_layout(showlegend=False,
                      margin=dict(l=50, r=50, t=35, b=35),)
    
    # Fijamos el dominio para que el donut siempre tenga centro (0.5,0.5) y dimensiones fijas.
    fig.update_traces(domain={'x': [0.05, 0.95], 'y': [0.05, 0.95]})
    
    # Si se ha pasado la ruta del logo, lo añadimos en el centro
    if logo_path:
        try:
            with open(logo_path, "rb") as image_file:
                encoded_logo = base64.b64encode(image_file.read()).decode()
            fig.add_layout_image(
                dict(
                    source="data:image/png;base64," + encoded_logo,
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    sizex=0.3, sizey=0.3,
                    xanchor="center", yanchor="middle",
                    layer="above"
                )
            )
        except Exception as e:
            st.error(f"Error al cargar el logo: {e}")
    
    # Mostrar la gráfica en Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Generamos una función para el radar comparativo
def grafica_radar_comparativo(df_selected, df, teams, metrics):
    
    fig = go.Figure()

    # Si se tienen 2 equipos, asignamos colores fijos
    colors = ['steelblue', 'tomato'] if len(teams) == 2 else None
    
    # Para cada equipo seleccionado, extraemos sus valores para las métricas
    for idx, team in enumerate(teams):
        try:
            team_data = df_selected[df_selected["team_name"] == team].iloc[0]
        except IndexError:
            st.error(f"No se encontraron datos para el equipo {team} en df_selected.")
            return
        values = [team_data[m] for m in metrics]
        # Cerramos el polígono
        values_closed = values + [values[0]]
        theta = metrics + [metrics[0]]

        # Si tenemos dos equipos, usamos colores fijos; de lo contrario, dejamos la paleta por defecto.
        color = colors[idx] if colors else None

         # Si hay 2 equipos, asignamos posiciones y colores específicos:
        if len(teams) == 2:
            if idx == 0:
                textpos = "top center"
                textcolor = "steelblue"
            else:
                textpos = "bottom center"
                textcolor = "tomato"
        else:
            textpos = "middle left"
            textcolor = None
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=theta,
            fill='toself',
            name=team,
            mode="lines+markers+text",
            text=[f"{v:.2f}" for v in values_closed],
            textposition=textpos,
            textfont=dict(color=textcolor) if textcolor else None,
            marker_color=color,
            hovertemplate = "Equipo: %{fullData.name}<br>Métrica: %{theta}<br>Valor: %{r:.2f}<extra></extra>"
        ))

    # Calcular la mediana global para cada métrica
    median_values = [df[m].median() for m in metrics]
    median_values += [median_values[0]]
    theta = metrics + [metrics[0]]

    fig.add_trace(go.Scatterpolar(
        r=median_values,
        theta=theta,
        fill='none',
        name='Mediana',
        line=dict(dash='dash', color='grey'),
        hovertemplate = "Mediana: <br>Métrica: %{theta}<br>Valor: %{r:.2f}<extra></extra>"
    ))
    
    # Calculamos el máximo para definir el rango radial
    max_range = max(
        max([max(df_selected[m]) for m in metrics]),
        max([max(df[m]) for m in metrics])
    )
    
    # Actualizar el layout del gráfico
    fig.update_layout(
        polar=dict(
            domain=dict(x=[0,1], y=[0.05, 0.951]),
            radialaxis=dict(
                visible=True,
                range=[0, max_range], # Fijamos rango
                showticklabels = False,
                showline = False,
                ticks="",
            )
        ),
        showlegend=True,
        margin=dict(l=50, r=50, t=35, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    # Reordenamos los trazos para que la traza de "Mediana" se dibuje por encima.
    median_trace = [trace for trace in fig.data if trace.name == "Mediana"]
    other_traces = [trace for trace in fig.data if trace.name != "Mediana"]
    fig.data = other_traces + median_trace
    
    st.plotly_chart(fig, use_container_width=True)

