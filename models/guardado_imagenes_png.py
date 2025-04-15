import os

# Función para guardar las gráficas generadas en imágenes para el PDF
def guardar_graficas_equipos_pdf(fig_piramide_ataque=None, fig_piramide_defensa=None,
                                 fig_donut_1=None, fig_donut_2=None, fig_donut_3=None,
                                 fig_donut_4=None, fig_donut_5=None, fig_donut_6=None,
                                 fig_radar_ataque=None, fig_radar_defensa=None,
                                 fig_scatter=None,
                                 carpeta="temp"):

    rutas = {}

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    figuras = {
        "piramide_ataque": fig_piramide_ataque,
        "piramide_defensa": fig_piramide_defensa,
        "donut_1": fig_donut_1,
        "donut_2": fig_donut_2,
        "donut_3": fig_donut_3,
        "donut_4": fig_donut_4,
        "donut_5": fig_donut_5,
        "donut_6": fig_donut_6,
        "radar_ataque": fig_radar_ataque,
        "radar_defensa": fig_radar_defensa,
        "scatter": fig_scatter
    }

    for nombre, figura in figuras.items():
        if figura is not None:
            try:
                ruta = os.path.join(carpeta, f"{nombre}.png")
                figura.write_image(ruta, engine="orca")
                rutas[nombre] = ruta
            except Exception as e:
                print(f"Error al guardar {nombre}:", e)

    return rutas
