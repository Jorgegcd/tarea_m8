from fpdf import FPDF
import os
import pandas as pd
import textwrap

# Creamos la función para generar el pdf
def generate_pdf_pag2(page_title, selected_teams, season, df_temporada, data_team_1, fig_total_path = None, fig_jornadas_path= None, tablas = None, data_team_2 = None):
    
    # Generamos el PDF vertical
    class PDF(FPDF):
        def __init__(self):
            super().__init__(unit='mm', format='A4')
            self.set_auto_page_break(auto=True, margin=20)
            # Obtenemos la ruta de la fuente
            font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", "DejaVuSans.ttf")
            if os.path.exists(font_path):
                # Agregamos la fuente
                self.add_font("DejaVu", "", font_path, uni=True)
                self.add_font("DejaVu", "B", font_path, uni=True)
                self.myfont = "DejaVu"
            else:
                self.myfont = "Arial"  # Usamos Arial por defecto si la fuente no se encuentra.
            # Si la fuente no existe, se usará Arial por defecto.

        # Generamos el encabezado
        def header(self):
            current_dir = os.getcwd()
            header_path_down = os.path.join(current_dir, "images", "lineaV2_horizontal.png")
            header_path_right = os.path.join(current_dir, "images", "SDC_Hor_250.png")
            if os.path.exists(header_path_down):
                self.image(header_path_down, 5, 15, 200) # Línea horizontal azul claro que ocupe el ancho
            if os.path.exists(header_path_right):
                self.image(header_path_right, 180, 5, 20, 10) # Logo Sports Data Campus a la derecha
            
            # Designamos la fuente que queremos y que ya hemos elegido previamente al tamaño 16
            self.set_text_color(67, 142, 189) # Color de la fuente
            self.set_font(self.myfont, "", 16) # Tipo de fuente
            
            self.set_y(10)  # Posición vertical del texto
            self.set_x((self.w - self.get_string_width("Tarea Módulo 8:Página 1")) / 2)  # Centramos horizontalmente el título en el encabezado
            self.cell(55,3, "Tarea Módulo 8:Página 1", border=0, align="C")

            # Designamos la fuente que queremos: Arial 8
            self.set_text_color(67, 142, 189) # Color de la fuente
            self.set_font(self.myfont, "", 8) # Tipo de fuente
                
            self.set_y(10)  # Posición vertical del texto
            self.cell(55,3, "Jorge Gómez-Cornejo Díaz", border=0, align="L") # Situamos el texto a la izquierda
            # Realizamos un salto de línea
            self.ln(20)

        # Generamos el pie de página
        def footer(self):
            current_dir = os.getcwd()
            footer_path = os.path.join(current_dir, "images", "footer_tarea.png") # Introducimos una imagen del footer que queremos
            if os.path.exists(footer_path):
                self.image(footer_path, 0, 285, 210) # Imagen del footer
            self.set_y(-20) # Posición al pie
            # Designamos la fuente que queremos, en este caso Times con tamaño 8
            self.set_font("Times","", 8)
            # Imprimimos el número de página
            self.cell(0, 28, f"Página {self.page_no()}", align="C")

        # Generamos la función para mostrar las tablas en el pdf
        def create_table(self, headers, data, col_width=None, line_height=6, margin_left=8):
            # Si existe 'team_id' en headers, eliminamos la columna correspondiente de cada fila
            if "team_id" in headers:
                idx = headers.index("team_id")
                headers = headers[:idx] + headers[idx+1:]
                data = [row[:idx] + row[idx+1:] for row in data]
            
            n = len(headers)
            # Calculamos la base del ancho de modo que sea ancho_total = 1.5 * base + (n - 1) * base = base*(n + 0.5)
            base_width = (self.w - 2 * self.l_margin) / (n + 0.5)
            widths = [2 * base_width] + [base_width] * (n - 1)
            
            # Los encabezados son con la fuente seleccionada, en negrita y tamaño 7
            self.set_font(self.myfont, 'B', 7)
            self.set_x(margin_left)

            # Envolvemos el texto de cada encabezado
            header_lines = []  # Cada elemento es una lista de líneas para el header de esa columna
            max_lines = 0
            # Usamos "M" para estimar el ancho promedio de un caracter
            avg_char_width = self.get_string_width("M")
            for i, header in enumerate(headers):
                max_chars = max(1, int(widths[i] / avg_char_width))
                lines = textwrap.wrap(header, width=max_chars)
                header_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)
            header_height = max_lines * line_height
            y_start = self.get_y()
            
            # Mostramos cada celda de encabezado
            for i, lines in enumerate(header_lines):
                x_cell = margin_left + sum(widths[:i])
                for j in range(max_lines):
                    self.set_xy(x_cell, y_start + j * line_height)
                    # Si la celda tiene menos líneas, se imprime vacío en las restantes
                    cell_text = lines[j] if j < len(lines) else ""
                    self.cell(widths[i], line_height, cell_text, border=0, align='C')
            # Dibujamos los bordes para cada celda de encabezado
            for i in range(n):
                self.rect(margin_left + sum(widths[:i]), y_start, widths[i], header_height)
            # Posicionamos el cursor justo al final de la cabecera, sin espacio extra
            self.set_xy(margin_left, y_start + header_height)
            
            # Mostramos los datos con fuente normal y tamaño 7
            self.set_font(self.myfont, '', 7)
            for row in data:
                # Para cada celda de la fila, obtenemos las líneas
                cell_lines = []
                max_lines = 0
                for i in range(n):
                    try:
                        # Intentamos darle formato a los valores numéricos de la tabla
                        num = float(row[i])
                        if len(headers) < 18:
                            cell_text = f"{num:.2f}"
                        else:
                            cell_text = f"{num:.1f}"
                    except (ValueError, TypeError):
                        cell_text = str(row[i])
                    # Centramos los valores en cada celda
                    lines = self.multi_cell(widths[i], line_height, cell_text, border=0, align='C', split_only=True)
                    cell_lines.append(lines)
                    if len(lines) > max_lines:
                        max_lines = len(lines)
                
                # Seleccionamos la altura de las filas
                row_height = max_lines * line_height
                y_start = self.get_y()
                for i in range(n):
                    x = margin_left + sum(widths[:i])
                    for j in range(max_lines):
                        self.set_xy(x, y_start + j * line_height)
                        text_to_print = cell_lines[i][j] if j < len(cell_lines[i]) else ""
                        self.cell(widths[i], line_height, text_to_print, border=0, align='C')
                
                # Dibujar el borde de cada celda de la fila
                for i in range(n):
                    self.rect(margin_left + sum(widths[:i]), y_start, widths[i], row_height)
                self.set_xy(margin_left, y_start + row_height)

    # Instanciamos la clase
    pdf = PDF()
    pdf.add_page()

    # Título de la página
    pdf.set_fill_color(255, 255, 255)  # Fondo de texto blanco
    pdf.set_text_color(67, 142, 189)  # Letra de texto Azul para títulos de encabezados
    pdf.set_font(pdf.myfont, "B", size=14) # Texto en Arial 14 en negrita
    title = page_title # Mostramos el título de la página
    pdf.cell(0, 10, title, 0, 1, 'C')  # Mostramos el texto en el centro
    pdf.ln(5)

    # Mostramos texto (título) de lo que trata el pdf
    pdf.set_font(pdf.myfont, "", 12)
    equipos_text = ", ".join(selected_teams)
    pdf.cell(0, 10, f"Comparación por jornadas y totales de {equipos_text} en {season}", 0, 1, "C")
    pdf.ln(5)

    # Obtenemos ancho de la página considerando márgenes
    page_width = pdf.w - 2 * pdf.l_margin
    current_y = pdf.get_y()

    if len(selected_teams) == 1:
        # Si hay un solo equipo, centramos el logo 
        team_id = df_temporada.loc[df_temporada['team_name'] == selected_teams[0], 'team_id'].iloc[0] # El archivo se llama con team_id del equipo
        logo_path = os.path.join(os.getcwd(), "images", "teams", f"{team_id}.png")
        if os.path.exists(logo_path):
            # Centramos: se ubica en x = margen + (page_width - width_logo)/2
            logo_width = page_width / 7  # Definimos ancho deseado
            x_position = pdf.l_margin + (page_width - logo_width) / 2
            pdf.image(logo_path, x=x_position, y=current_y, w=logo_width)
        else:
            pdf.cell(0, 10, f"No se encontró logo para {selected_teams[0]}", 0, 1, "C")
        pdf.ln(30)

    elif len(selected_teams) == 2:
        # Si hay dos equipos, se muestran en dos columnas
        team_id_1 = df_temporada.loc[df_temporada['team_name'] == selected_teams[0], 'team_id'].iloc[0]
        team_id_2 = df_temporada.loc[df_temporada['team_name'] == selected_teams[1], 'team_id'].iloc[0]
        logo_path_1 = os.path.join(os.getcwd(), "images", "teams", f"{team_id_1}.png")
        logo_path_2 = os.path.join(os.getcwd(), "images", "teams", f"{team_id_2}.png")
        # Definimos el ancho para cada logo
        logo_width = (page_width) / 7
        
        # Mostramos los logos en dos columnas
        if os.path.exists(logo_path_1):
            pdf.image(logo_path_1, x=(pdf.l_margin + (page_width - logo_width) / 2)/2, y=current_y, w=logo_width)
        else:
            pdf.cell(0, 10, f"No se encontró logo para {selected_teams[0]}", 0, 1, "L")
        if os.path.exists(logo_path_2):
            pdf.image(logo_path_2, x= 3*(pdf.l_margin + (page_width - logo_width)/2)/2, y=current_y, w=logo_width)
        else:
            pdf.cell(0, 10, f"No se encontró logo para {selected_teams[1]}", 0, 1, "R")
        
        pdf.ln(35)

    pdf.set_text_color(0, 0, 0) # Color de fuente negro para la descripción
    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10 en negrita
    
    # Mostramos título de sección
    pdf.cell(page_width/2, 2, f'Valores generales liga {selected_teams[0]}', border = str(0), align="C")
    pdf.cell(page_width/2, 2, f'Valores generales liga {selected_teams[1]}', border = str(0), align="C")
    pdf.ln(8)

    # METER FUNCIÓN DE CAJAS DE MÉTRICAS TOTALES LIGA (CAMBIAR ANCHOS Y TAMAÑOS, METER UN IF > 1)

    pdf.ln(10)

    pdf.cell(page_width/2, 2, f'Valores jornadas seleccionadas {selected_teams[0]}', border = str(0), align="C")
    pdf.cell(page_width/2, 2, f'Valores jornadas seleccionadas {selected_teams[1]}', border = str(0), align="C")
    pdf.ln(8)   

    # METER FUNCIÓN DE CAJAS DE MÉTRICAS JORNADAS SELECCIONADAS

    pdf.ln(10)
    
    pdf.set_text_color(0, 0, 0) # Color de fuente negro para la descripción
    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10 en negrita

    # Mostramos título de sección
    pdf.cell(page_width, 2, f'Estadísticas globales y por jornadas {selected_teams[0]}', border = str(0), align="C")
    pdf.ln(8)

    # Introducimos la tabla de comparativa de estadisticas
    headers_globales = ['Métrica', 'Temporada Completa', 'Jornadas Seleccionadas']
    
    # Indicamos el ancho de la columna para las tablas
    col_width_adv_of = page_width / len(headers_globales)
    # Creamos la tabla
    pdf.create_table(headers_globales, data_team_1, col_width=col_width_adv_of)
    pdf.ln(10)
    
    if len (selected_teams) > 1:
        pdf.set_text_color(0, 0, 0) # Color de fuente negro para la descripción
        pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10 en negrita

        # Mostramos título de sección
        pdf.cell(page_width, 2, f'Estadísticas globales y por jornadas {selected_teams[1]}', border = str(0), align="C")
        pdf.ln(8)

        # Creamos la tabla
        pdf.create_table(headers_globales, data_team_2, col_width=col_width_adv_of)
        pdf.ln(10)
    
    else:
        pass

    pdf.cell(page_width, 2, f'Evolución partidos temporada {season} {selected_teams[0]}', border = str(0), align="C")
    pdf.ln(8)

    # METER GRÁFICAS EVOLUCIÓN POR JORNADAS
    pdf.ln (10)

    if len (selected_teams) > 1:
        pdf.cell(page_width, 2, f'Evolución partidos temporada {season} {selected_teams[1]}', border = str(0), align="C")
        pdf.ln(8)   

        # METER GRÁFICAS EVOLUCIÓN POR JORNADAS
        pdf.ln (10)
    else:
        pass
    
    pdf.cell(page_width/2, 2, f'Radar (Temporada completa)', border = str(0), align="C")
    pdf.cell(page_width/2, 2, f'Radar (Jornadas seleccionadas)', border = str(0), align="C")
    pdf.ln(8)  

    # METER EN PARALELO LOS RADARES COMPARATIVOS

    # Guardamos
    output_path = "temp/reporte.pdf"
    pdf.output(output_path)
    return output_path