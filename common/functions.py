import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import base64
import os
import uuid
import streamlit.components.v1 as components

# Utilizamos manejo de cache
@st.cache_data
# Generamos la función para crear tablas en base al dataframe
def crear_tablas(df):
    # Indicamos las columnas para la tabla de ataque
    columnas_tabla1 = [
        'team_name', 'matches', 'pace', 'ortg', 'efg%', 'ts%', 'ppt2', 'vol2p', 'ppt3', 'vol3p', 'pptl', 'ftr', 'or%', 
        'ast%', 'st%', 'to%', 'blk%', 'four_factors'
    ]
    # Indicamos las columnas para la tabla de defensa
    columnas_tabla2 = [
        'team_name', 'matches', 'pace', 'drtg', 'dr%', 'tr%', 'efg%_opp', 'ts%_opp', 'ppt2_opp', 'vol2p_opp', 'ppt3_opp', 
        'vol3p_opp', 'pptl_opp', 'ftr_opp', 'ast%_opp', 'st%_opp', 'to%_opp', 'blk%_opp', 'four_factors_opp'
    ]
    
    # Generamos ambas tablas
    tabla1 = df[columnas_tabla1].copy()
    tabla2 = df[columnas_tabla2].copy()

    # Renombramos las columnas para las tablas
    tabla1 = tabla1.rename(columns = {'team_name':"Equipo", 'matches':"Partidos", 'pace':"Pace", 'ortg':"Eficiencia Ofensiva", 'efg%':"eFG%", 'ts%':"TS%", 'ppt2':"PPT2",
                             'vol2p':"Vol. T2%", 'ppt3':"PPT3", 'vol3p':"Vol. T3%", 'pptl':"PPTL", 'ftr':"FT Rate", 'or%':"Reb. Of.%", 'ast%':"Ast%", 'st%':"Robos%",
                             'to%':"Pérdidas%", 'blk%':"Tapones%", 'four_factors':"Four Factors"})
    
    tabla2 = tabla2.rename(columns = {'team_name':"Equipo", 'matches':"Partidos", 'pace':"Pace", 'drtg':"Eficiencia Defensiva", 'dr%':"Reb. Def.%", 'tr%':"Reb. Totales%", 
                             'efg%_opp':"eFG% Rivales", 'ts%_opp':"TS% Rivales", 'ppt2_opp':"PPT2 Rivales", 'vol2p_opp':"Vol. T2% Rivales", 'ppt3_opp':"PPT3 Rivales",
                             'vol3p_opp':"Vol. T3% Rivales", 'pptl_opp':"PPTL Rivales", 'ftr_opp':'FT Rate Rivales', 'ast%_opp': 'Ast% Rivales', 'st%_opp': 'Robos% Rivales',
                              'to%_opp': 'Pérdidas% Rivales', 'blk%_opp':'Tapones% Rivales', 'four_factors_opp':'Four Factors Rivales'})
    
    return tabla1, tabla2

# Utilizamos manejo de cache
@st.cache_data
# Generamos la gráfica estilo pirámide para dos equipos
def grafica_metricas_comparacion(df, equipo_left, equipo_right, metrics):
    
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

    # Determinamos un hueco en el centro
    max_val = max(max(left_vals), max(right_vals)) # Obtenemos el máximo valor para ajusar en torno a él
    gap = 0.26 * max_val  
    
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
        customdata=left_vals,
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
    
    # Configuramos un rango simétrico para el eje x considerando el hueco
    left_max = gap + max(left_vals)
    right_max = gap + max(right_vals)
    max_range = max(left_max, right_max)
    fig.update_xaxes(range=[-max_range * 1.1, max_range * 1.1])

    # Ocultamos los tick labels del eje y para no duplicar los nombres de las métricas
    fig.update_yaxes(showticklabels=False)
    fig.update_xaxes(showticklabels=False)
    
    # Añadimos diversas anotaciones
    annotations = []
    for i, metric in enumerate(metrics):
        # Añadimos los nombres de las métricas para x=0 (el hueco)
        annotations.append(dict(
            x=0,
            y=metric,
            text=metric,
            showarrow=False,
            font=dict(size=12),
            xanchor="center",
            yanchor="middle"
        ))
    
        # Añadimos los valores del equipo en las columnas de la izquierda
        annotations.append(dict(
            x=-gap,
            y=metric,
            text=f"{left_vals[i]:.2f}",
            showarrow=False,
            font=dict(size=12),
            xanchor="right",
            yanchor="middle"
        ))

        # Añadimos los valores del equipo en las columnas de la derecha
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
                      legend=dict(orientation='h', yanchor='top', y=1.2, xanchor='center', x=0.5)
                      )
       
    # Retornamos la figura
    return fig

# Utilizamos manejo de cache
@st.cache_data
# Generamos la gráfica de la pirámide de un equipo 
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

    # Determinamos un hueco en el centro
    max_val = max(left_vals) # Obtenemos el máximo valor para ajusar en torno a él
    gap = 0.26 * max_val
    
    # Creamos la figura
    fig = go.Figure()
    
    # Añadimos la barra para el equipo
    fig.add_trace(go.Bar(
        y=metrics,
        x=[-val for val in left_vals],
        base=[-gap] * len(metrics),
        name= equipo,
        orientation='h',
        marker_color='steelblue',
        customdata=left_vals,  
        hovertemplate="%{y}: %{customdata:.2f}<extra></extra>"
    ))
    
    # Actualizamos el layout para que ambas trazas se superpongan
    fig.update_layout(
        barmode='overlay',
        showlegend=True
    )
    
    # Configuramos un rango simétrico para el eje x considerando el hueco
    left_max = gap + max(left_vals)
    right_max = gap - max(left_vals)
    max_range = max(left_max, right_max)
    fig.update_xaxes(range=[-max_range * 1.1, max_range * 1.1])

    # Ocultamos los tick labels del eje y para no duplicar los nombres de las métricas
    fig.update_yaxes(showticklabels=False)
    fig.update_xaxes(showticklabels=False)
    
    # Añadimos diversas anotaciones
    annotations = []
    for i, metric in enumerate(metrics):
        # Añadimos los nombres de las métricas para x=0 (el hueco)
        annotations.append(dict(
            x=0,
            y=metric,
            text=metric,
            showarrow=False,
            font=dict(size=12),
            xanchor="center",
            yanchor="middle"
        ))
    
        # Añadimos los valores del equipo en las columnas de la izquierda
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

    # Retornamos la figura
    return fig

# Utilizamos manejo de cache
@st.cache_data
# Creamos un donut chart con la distribución de posesiones.
def grafica_donut_posesiones(df, equipo, categorias, colores = None):
    
    # Filtramos el DataFrame para mostrar los datos del equipo deseado
    df_equipo = df[df["Equipo"] == equipo]

    # Verificamos que exista la columna team_id
    if "team_id" not in df_equipo.columns:
        st.error("La columna 'team_id' no se encuentra en los datos. Asegúrese de incluirla en la consulta.")
        return

    # Cogemos la primera fila del dataframe filtrado
    row = df_equipo.iloc[0]

    # Extraemos los valores correspondientes
    data = {cat: row[cat] for cat in categorias}

    # Agregamos la métrica de posesiones de tiros libres (Pos. Tiro Libre = 0.44 * TL Intentados) tanto para el equipo como para el rival
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
    
    # Creamos el gráfico de donut con Plotly Express
    fig = px.pie(
        donut_df,
        names="Categoría",
        values="Valor",
        hole=0.5,  # Esto crea el hueco de donut
        color_discrete_sequence=colores
    )
    
    # Configuramos el texto del hover y dentro del gráfico para mostrar porcentajes y etiquetas
    fig.update_traces(textposition='inside',
                      textinfo='percent+label',
                      hovertemplate="%{label}: %{value:.2f}<extra></extra>")

    # Eliminamos la leyenda y fijamos márgenes
    fig.update_layout(showlegend=False,
                      margin=dict(l=50, r=50, t=35, b=35),)
    
    # Fijamos el dominio para que el donut siempre tenga centro (0.5,0.5) y dimensiones fijas.
    fig.update_traces(domain={'x': [0.05, 0.95], 'y': [0.05, 0.95]})

    # Mostramos las figuras
    return fig

# Utilizamos manejo de cache
@st.cache_data
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
        
        # Generamos el radar de los equipos
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

    # Calculamos la mediana global para cada métrica
    median_values = [df[m].median() for m in metrics]
    median_values += [median_values[0]]
    theta = metrics + [metrics[0]]

    # Generamos las líneas de la mediana
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
    
    # Actualizamos el layout del gráfico
    fig.update_layout(
        polar=dict(
            domain=dict(x=[0,1], y=[0.05, 0.951]),
            radialaxis=dict(
                visible=True,
                range=[0, max_range], # Fijamos rango del radar
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
    
    # Mostramos la figura
    return fig

# Utilizamos manejo de cache
@st.cache_data
# Generamos función para scatter de eficiencia en el que se muestran los escudos de los equipos
def scatter_eficiencia (df, selected_teams):
   
   # Creamos una copia para no modificar el DataFrame original
    df_plot = df.copy()
    
    # Agregamos la columna "opacity": 1 si el equipo es seleccionado y, si no 0.3
    df_plot['opacity'] = df_plot['team_name'].apply(lambda x: 1 if x in selected_teams else 0.3)
   
   # Creamos el scatterplot usando Plotly Express
    fig = px.scatter(
        df,
        x="ortg",
        y="drtg",
        
        labels={"ortg": "Eficiencia Ofensiva", "drtg": "Eficiencia Defensiva", "team_name":"Equipo"},
        hover_data=["team_name", "drtg", "ortg"]
    )
    
    # Actualizamos los marcadores con opacidades individuales
    fig.update_traces(marker=dict(opacity=0))
    
    # Ajustamos los ejes:
    # El eje y va de 95 hasta un poco más que el máximo de drtg. Además, invertimos el eje y.
    x_min = 95
    x_max = df["ortg"].max() * 1.02
    y_min = 95
    y_max = df["drtg"].max() * 1.02
    fig.update_xaxes(range=[x_min, x_max], showgrid=False)
    fig.update_yaxes(range=[y_min, y_max], showgrid=False, autorange="reversed")

    # Añadimos un trace invisible que usaremos para el hover con información personalizada.
    fig.add_trace(go.Scatter(
        x=df["ortg"],
        y=df["drtg"],
        mode="markers",
        marker=dict(opacity=0, size=20),
        customdata=df[["team_name", "ortg", "drtg"]].values,
        hovertemplate=(
            "%{customdata[0]}<br>" +
            "Eficiencia Ofensiva: %{customdata[1]:.2f}<br>" +
            "Eficiencia Defensiva: %{customdata[2]:.3f}<extra></extra>"
        )
    ))
    
    # Calculamos un tamaño para los logos (15% del rango de cada eje)
    x_range = df["ortg"].max() - df["ortg"].min()
    y_range = df["drtg"].max() - df["drtg"].min()
    sizex = x_range * 0.15
    sizey = y_range * 0.15

    # Obtenemos la ruta absoluta usando os.getcwd()
    current_dir = os.getcwd()

    for _, row in df_plot.iterrows():
        team_id = row["team_id"]
        
        # Construimos la ruta absoluta (tarea_m8/images)
        logo_path = os.path.join(current_dir, "images", "teams", f"{team_id}.png")

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                encoded_logo = base64.b64encode(image_file.read()).decode()
            
            # Usamos la opacidad del equipo
            logo_opacity = row["opacity"]

            fig.add_layout_image(
                dict(
                    source="data:image/png;base64," + encoded_logo,
                    x=row["ortg"],
                    y=row["drtg"],
                    xref="x",
                    yref="y",
                    sizex=sizex,
                    sizey=sizey,
                    xanchor="center",
                    yanchor="middle",
                    opacity = logo_opacity,
                    layer="above"
                )
            )
        else:
            st.error(f"No se encontró la imagen: {logo_path}")
        
    # Calculamos las medianas para agregar las líneas de referencia
    median_x = df["ortg"].median()
    median_y = df["drtg"].median()

    # Añadimos la línea vertical en la mediana de Eficiencia Ofensiva
    fig.add_shape(
        type="line",
        x0=median_x, x1=median_x,
        y0=y_min, y1=y_max,
        xref="x", yref="y",
        line=dict(dash="dash", color = "grey")
    )
    # Añadimos la línea horizontal en la mediana de Eficiencia Defensiva
    fig.add_shape(
        type="line",
        x0=x_min, x1=x_max,
        y0=median_y, y1=median_y,
        xref="x", yref="y",
        line=dict(dash="dash", color = "grey")
    )
   
    # Agregamos las anotaciones en cada esquina con un tono de gris clarito para indicar las diferentes zonas
    fig.add_annotation(
        x=x_max - 0.5 , y=y_max - 0.25,
        text="Buen ataque/mala defensa",
        showarrow=False,
        font=dict(color="#c2c1c0", size=12),
        xanchor="right", yanchor="top"
    )
    fig.add_annotation(
        x=x_max -0.5, y=y_min +0.25,
        text="Buen ataque/buena defensa",
        showarrow=False,
        font=dict(color="#c2c1c0", size=12),
        xanchor="right", yanchor="bottom"
    )
    fig.add_annotation(
        x=x_min + 0.5, y=y_max - 0.25,
        text="Mal ataque/mala defensa",
        showarrow=False,
        font=dict(color="#c2c1c0", size=12),
        xanchor="left", yanchor="top"
    )
    fig.add_annotation(
        x=x_min +0.5, y=y_min -0.25,
        text="Mal ataque/buena defensa",
        showarrow=False,
        font=dict(color="#c2c1c0", size=12),
        xanchor="left", yanchor="bottom"
    )

    # Quitamos la leyenda
    fig.update_layout(showlegend=False, width = 415, height = 830)

    # Mostramos la figura
    return fig

def print_window():
    components.html("""
        <script>
            window.print();
        </script>
        """, height=0,
            width=0)