from fpdf import FPDF
import os
import pandas as pd

# Cremaos la función para generar pdf
def generate_pdf_pag2(fig_total_path, fig_jornadas_path, tablas):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Título
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Comparador de totales de equipos ABA League 2", ln=True, align='C')

    # Inserta los radares
    if os.path.exists(fig_total_path):
        pdf.image(fig_total_path, x=10, y=30, w=90)
    if os.path.exists(fig_jornadas_path):
        pdf.image(fig_jornadas_path, x=110, y=30, w=90)

    pdf.ln(100)  # Salto después de los radares

    # Recorremos las tablas
    for equipo, df in tablas.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Estadísticas globales - {equipo}", ln=True)

        pdf.set_font("Arial", '', 10)

        df_ = df.reset_index() if df.index.name else df
        # Añadimos encabezado
        col_names = df_.columns.tolist()
        col_width = pdf.w / len(col_names) - 10
        for col in col_names:
            pdf.cell(col_width, 10, str(col), border=1)
        pdf.ln()

        # Añadimos filas
        for _, row in df_.iterrows():
            for val in row:
                pdf.cell(col_width, 10, str(round(val, 2)) if isinstance(val, (float, int)) else str(val), border=1)
            pdf.ln()

        pdf.ln(5)

    # Guardar
    output_path = "temp/reporte.pdf"
    pdf.output(output_path)
    return output_path
