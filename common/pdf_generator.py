from fpdf import FPDF
from datetime import datetime
import os
import base64

def generate_pdf_pag1(page_title, selected_teams, df_temporada, df_sql_team, df_sql_opp, output_filename = None):
    
    # Generamos el PDF vertical
    class PDF(FPDF):
        def __init__(self):
            super().__init__(unit='mm', format='A4')
            self.set_auto_page_break(auto=True, margin=20)
            # Obtenemos la ruta de la fuente
            font_path = os.path.join(os.getcwd(), "fonts", "DejaVuSans.ttf")
            if os.path.exists(font_path):
                # Agregamos la fuente con un alias, por ejemplo "DejaVu"
                self.add_font("DejaVu", "", font_path, uni=True)
            # Si la fuente no existe, se usará Arial por defecto.

        def header(self):
            current_dir = os.getcwd()
            header_path_down = os.path.join(current_dir, "images", "lineaV2_horizontal.png")
            header_path_right = os.path.join(current_dir, "images", "SDC_Hor_250.png")
            if os.path.exists(header_path_down):
                self.image(header_path_down, 5, 15, 200) # Línea horizontal azul claro que ocupe el ancho
            if os.path.exists(header_path_right):
                self.image(header_path_right, 180, 5, 20, 10) # Logo Sports Data Campus a la derecha
            
            # Designamos la fuente que queremos: Arial 16
            font_to_use = "DejaVu" if "DejaVu" in self.fonts else "Arial"
            self.set_text_color(67, 142, 189) # Color de la fuente
            self.set_font(font_to_use, "", 16) # Tipo de fuente
                
            self.set_y(10)  # Posición vertical del texto
            self.set_x((self.w - self.get_string_width("Tarea Módulo 8:Página 1")) / 2)  # Centramos horizontalmente
            self.cell(55,3, "Tarea Módulo 8:Página 1", border=0, align="C")

            # Designamos la fuente que queremos: Arial 16
            self.set_text_color(67, 142, 189) # Color de la fuente
            self.set_font(font_to_use, "", 8) # Tipo de fuente
                
            self.set_y(10)  # Posición vertical del texto
            self.cell(55,3, "Jorge Gómez-Cornejo Díaz", border=0, align="L")    
            # Realizamos un salto de línea
            self.ln(20)

        def footer(self):
            current_dir = os.getcwd()
            footer_path = os.path.join(current_dir, "images", "footer_tarea.png")
            if os.path.exists(footer_path):
                self.image(footer_path, 0, 285, 210) # Imagen del footer
            self.set_y(-20) # Posición al pie
            # Designamos la fuente que queremos: Times 8
            self.set_font("Times","", 8)
            # Imprimimos el número de página:
            self.cell(0, 28, f"Página {self.page_no()}", align="C")

        def create_table(self, headers, data, col_width=None, line_height=6, margin_left=10):
            # Si existe 'team_id' en headers, la removemos y eliminamos la columna correspondiente de cada fila
            if "team_id" in headers:
                idx = headers.index("team_id")
                headers = headers[:idx] + headers[idx+1:]
                data = [row[:idx] + row[idx+1:] for row in data]
            
            n = len(headers)
            # Calculamos la base de ancho. Queremos que la primera columna sea 1.5 veces el ancho de las demás.
            # Así, el ancho total se reparte como: ancho_total = 1.5 * base + (n - 1) * base = base*(n + 0.5)
            base_width = (self.w - 2 * self.l_margin) / (n + 0.5)
            widths = [2 * base_width] + [base_width] * (n - 1)
            
            # Encabezados con fuente en negrita y tamaño 10
            self.set_font('Arial', 'B', 8)
            self.set_x(margin_left)
            for i, header in enumerate(headers):
                header_clean = header.encode('ascii', 'replace').decode()
                self.cell(widths[i], line_height, header_clean, 1, 0, 'C')
            self.ln()
            
            # Datos con fuente normal y tamaño 8
            self.set_font('Arial', '', 8)
            for row in data:
                # Guardamos la posición inicial de la fila
                x0 = self.get_x()
                y0 = self.get_y()
                
                # Para la primera columna, usamos MultiCell para que ajuste el texto
                first_item = row[0]
                try:
                    num = float(first_item)
                    item_str = f"{num:.2f}"
                except (ValueError, TypeError):
                    item_str = str(first_item)
                item_clean = item_str.encode('ascii', 'replace').decode()
                
                # Imprimimos la primera celda con MultiCell y un borde; MultiCell ajusta la altura según el contenido.
                self.multi_cell(widths[0], line_height, item_clean, border=1, align='C')
                new_y = self.get_y()  # Altura final después de la MultiCell
                row_height = new_y - y0
                
                # Para las demás columnas, posicionamos el cursor en la misma línea (y0) y usamos Cell con la misma altura.
                for i in range(1, n):
                    self.set_xy(x0 + sum(widths[:i]), y0)
                    try:
                        num = float(row[i])
                        item_str = f"{num:.2f}"
                    except (ValueError, TypeError):
                        item_str = str(row[i])
                    item_clean = item_str.encode('ascii', 'replace').decode()
                    self.cell(widths[i], row_height, item_clean, border=1, align='C')
                # Posicionamos el cursor al inicio de la siguiente fila
                self.set_xy(margin_left, new_y)

    # Instanciamos la clase
    pdf = PDF()
    pdf.add_page()

    # Creamos fondo blanco para los títulos y luego el texto en azul
    pdf.set_fill_color(255, 255, 255)  # Fondo de texto blanco
    pdf.set_text_color(67, 142, 189)  # Letra de texto Azul para títulos
    pdf.set_font("Arial", "B",size=14) # Texto en Arial 14 en negrita
    title = page_title.encode('ascii', 'replace').decode()
    pdf.cell(0, 10, title, 0, 1, 'C')
    pdf.ln(5)

    # Texto de equipos seleccionados
    pdf.set_font("Arial", "", 12)
    equipos_text = ", ".join(selected_teams)
    pdf.cell(0, 10, f"Comparación entre {equipos_text}", 0, 1, "C")
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
        # Definimos el ancho para cada logo, por ejemplo la mitad de page_width menos un pequeño margen
        logo_width = (page_width) / 7
        
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
    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10
    
    pdf.cell(page_width, 2, 'Promedios por partido equipo', border = str(0), align="C")
    pdf.ln(8)

    # Introducimos las tablas
    headers = ['Equipo', 'Part', 'Pts', 'T2A','T2I','T2%', 'T3A', 'T3I', 'T3%', 'TCA', 'TCI', 'TC%', 'TLA', 'TLI', 'TL%', 'R.Of', 'R.Df',
               'R.Tot', 'Ast', 'Rob', 'Tap', 'TO%']
    data_team = df_sql_team.values.tolist()
    data_opp = df_sql_opp.values.tolist()

    # Guardamos la posición actual (para la tabla izquierda)
    x_left = pdf.get_x()
    y_left = pdf.get_y()
    
    # Imprimir tabla para "Promedios por partido equipo"
    # Ajustamos el ancho de cada columna de la tabla en función del número de columnas
    col_width_team = page_width / len(headers)
    pdf.create_table(headers, data_team, col_width=col_width_team)
    pdf.ln(10)
    
    # Introducimos la tabla de los rivales
    pdf.set_text_color(0, 0, 0) # Color de fuente negro para la descripción
    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10
    pdf.cell(page_width, 2, 'Promedios por partido de los rivales', border = str(0), align="C")
    pdf.ln(8)
    col_width_opp = page_width / len(headers)
    pdf.create_table(headers, data_opp, col_width=col_width_opp)
    pdf.ln(10)

    # if len(selected_teams) == 1:

    # elif len(selected_teams) == 2:

    pdf.set_text_color(0, 0, 0) # Color de fuente negro para la descripción
    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10
    pdf.cell(page_width/2, 2, 'Comparación promedios ataque', border = str(0), align="C")
    pdf.cell(page_width/2, 2, 'Comparación promedios defensa', border = str(0), align="C") 
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10
    pdf.cell(page_width/2, 2, 'Estadísticas avanzadas ataque', border = str(0), align="C")
    pdf.ln(8)

    # Introducimos la tabla de los rivales
    pdf.cell(page_width/2, 2, 'Estadísticas avanzadas defensa', border = str(0), align="C")
    pdf.ln(8)
    
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10
    pdf.cell(page_width, 2, 'Eficiencia ofensiva vs eficiencia defensiva', border = str(0), align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10
    pdf.cell(page_width/2, 2, f'Distribución posesiones', border = str(0), align="C")
    pdf.cell(page_width/2, 2, f'Distribución posesiones', border = str(0), align="C")
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10
    pdf.cell(page_width/2, 2, 'Comparación est. avanzadas ataque', border = str(0), align="C")
    pdf.cell(page_width/2, 2, 'Comparación est. avanzadas defensa', border = str(0), align="C")
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=10) # Letra de texto arial 10
    pdf.cell(page_width/2, 2, 'Distribución posesiones rivales', border = str(0), align="C")
    pdf.cell(page_width/2, 2, 'Distribución posesiones rivales', border = str(0), align="C")
    pdf.ln(10)

    pdf.output(output_filename)

    return pdf