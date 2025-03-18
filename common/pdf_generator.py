from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):

    def __init__(self):
        super().__init__(unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.image("images/lineaV2_horizontal.png", 5, 15, 200) # Línea horizontal azul claro que ocupe el ancho
        self.image("images/SDC_Hor_250.png", 180, 5, 20, 10) # Logo Sports Data Campus a la derecha
        
        # Designamos la fuente que queremos: Arial 16
        self.set_text_color(67, 142, 189) # Color de la fuente
        self.set_font("Arial", "", 16) # Tipo de fuente
            
        self.set_y(10)  # Posición vertical del texto
        self.set_x((self.w - self.get_string_width("Tarea Módulo 8")) / 2)  # Centramos horizontalmente
        self.cell(55,3, "Tarea Módulo 8", border=0, align="C")
            
        # Realizamos un salto de línea
        self.ln(20)

    def footer(self):
        self.image("footer_tarea.png", 0, 285, 210) # Imagen del footer
        self.set_y(-15) # Posición al pie
        # Designamos la fuente que queremos: Times 8
        self.set_font("Times","", 8)
        # Imprimimos el número de página
        self.cell(0, 28, f"Page {self.page_no()}", align="C")

    def create_table(self, headers, data):
        self.set_font('Arial', 'B', 10)
        line_height = 6
        col_width = 45
        
        # Establecer margen izquierdo de 1.5 cm (15 mm)
        margin_left = 15
        
        # Encabezados
        self.set_x(margin_left)
        for header in headers:
            header_clean = header.encode('ascii', 'replace').decode()
            self.cell(col_width, line_height, header_clean, 1, 0, 'C')
        self.ln()
        
        # Datos
        self.set_font('Arial', '', 9)
        for row in data:
            self.set_x(margin_left)
            for item in row:
                item_clean = str(item).encode('ascii', 'replace').decode()
                self.cell(col_width, line_height, item_clean, 1, 0, 'C')
            self.ln()

def generar_pdf(jugador, historico_jugador, radar_path, evolucion_path):
    pdf = PDF()
    pdf.add_page()

    # Título del jugador
    pdf.set_font('Arial', 'B', 16)
    nombre_clean = jugador["nombre"].encode('ascii', 'replace').decode()
    pdf.cell(0, 10, nombre_clean, 0, 1, 'C')
    pdf.ln(5)

    # Primera sección
    pdf.set_font('Arial', 'B', 12)
    pdf.set_x(15)  # Alinear con las tablas
    pdf.cell(0, 10, 'Informacion del Jugador', 0, 1, 'L')
    
    # Tabla de información básica
    info_headers = ['Caracteristica', 'Valor']
    info_data = [
        ['Pais', jugador["pais"]],
        ['Edad', f'{int(jugador["edad"])} anos'],
        ['Posicion', jugador["posicion"]],
        ['Club', jugador["club"]],
        ['Altura', f'{int(jugador["altura"])} cm'],
        ['Peso', f'{int(jugador["peso"])} kg'],
        ['Valor', f'{jugador["valor_actual"]:.2f}M EUR']
    ]
    
    current_y = pdf.get_y()
    pdf.create_table(info_headers, info_data)
    
    # Gráfico de radar
    pdf.image(radar_path, x=107, y=current_y-12, w=105)
    
    # Segunda sección
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_x(15)  # Alinear con las tablas
    pdf.cell(0, 10, 'Estadisticas Ultimos 6 Meses', 0, 1, 'L')
    
    # Tabla de estadísticas
    ultimos_6_meses = historico_jugador.tail(6)
    stats_headers = ['Metrica', 'Valor']
    stats_data = [
        ['Partidos', str(int(ultimos_6_meses["partidos_jugados"].sum()))],
        ['Goles', str(int(ultimos_6_meses["goles"].sum()))],
        ['Asistencias', str(int(ultimos_6_meses["asistencias"].sum()))],
        ['Minutos', str(int(ultimos_6_meses["minutos_jugados"].sum()))],
        ['Indice Rend.', f'{ultimos_6_meses["indice_rendimiento"].mean():.2f}']
    ]
    
    current_y = pdf.get_y()
    pdf.create_table(stats_headers, stats_data)
    
    # Gráfico de evolución
    pdf.image(evolucion_path, x=120, y=current_y-10, w=80)
    
    # Marco decorativo para toda la página
    pdf.rect(10, 10, 190, 277)
    
    return pdf