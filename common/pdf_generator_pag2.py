from fpdf import FPDF

def guardar_grafico_plotly(fig, nombre_archivo):
    fig.write_image(nombre_archivo, format='png', width=700, height=500)

# Cremaos la función para generar pdf
def generate_pdf_pag2(fig_total_path, fig_jornadas_path, tablas_dict, output_path="output_pag2.pdf"):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Informe Estadístico - Comparador Equipos", ln=True, align="C")

    # Insertar imagen radar 1
    pdf.image(fig_total_path, x=10, y=30, w=90)
    pdf.image(fig_jornadas_path, x=110, y=30, w=90)
    pdf.ln(110)

    # Insertar tablas de métricas como texto (también puedes guardarlas como imagen si prefieres)
    for equipo, df_metrics in tablas_dict.items():
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt=f"Estadísticas - {equipo}", ln=True)

        pdf.set_font("Arial", size=10)
        for i, row in df_metrics.iterrows():
            linea = f"{row['Métrica']}: Total={row['Temporada completa']} | Jornadas={row['Jornadas seleccionadas']}"
            pdf.cell(200, 7, txt=linea, ln=True)

        pdf.ln(5)

    pdf.output(output_path)
