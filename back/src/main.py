import flet as ft

def main(page: ft.Page):
    # Configuración básica de la página
    page.title = "App Profesor"
    page.window_width = 390
    page.window_height = 800
    page.bgcolor = "#FFFFFF"
    page.padding = 20

    # --- 1. CABECERA ---
    header = ft.Column(
        controls=[
            ft.Text("Hola, Profesor", size=32, weight="bold", color="#0D47A1"),
            ft.Text("Aquí está tu resumen de hoy.", size=16, color="#616161"),
        ],
        spacing=5
    )

    # --- 2. TARJETAS DE RESUMEN ---
    # Nota: En 0.80+ el primer argumento de Icon es el nombre (sin el parámetro 'name=')
    card_cobrar = ft.Container(
        content=ft.Column([
            ft.Icon("wallet", color="#FFFFFF", size=24),
            ft.Text("POR COBRAR", size=12, weight="bold", color="#FFFFFF"),
            ft.Text("0", size=40, weight="bold", color="#FFFFFF"),
        ], spacing=5),
        bgcolor="#2196F3",
        padding=20,
        border_radius=15,
        expand=True,
    )

    card_clases = ft.Container(
        content=ft.Column([
            ft.Icon("calendar_today", color="#2196F3", size=24),
            ft.Text("CLASES HOY", size=12, weight="bold", color="#9E9E9E"),
            ft.Text("2", size=40, weight="bold", color="#000000"),
        ], spacing=5),
        bgcolor="#FFFFFF",
        padding=20,
        border_radius=15,
        border=ft.border.all(1, "#F5F5F5"),
        expand=True,
    )

    resumen_row = ft.Row([card_cobrar, card_clases], spacing=15)

    # --- 3. AGENDA DIARIA ---
    agenda_vacia = ft.Container(
        content=ft.Column([
            ft.Icon("event_busy", color="#BDBDBD", size=50),
            ft.Text("No hay clases programadas para hoy.", color="#9E9E9E", text_align="center"),
        ], horizontal_alignment="center", alignment="center"),
        height=200,
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=15,
        alignment=ft.alignment.center,
    )

    # --- 4. BARRA DE NAVEGACIÓN ---
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="home", label="Inicio"),
            ft.NavigationBarDestination(icon="person", label="Alumnos"),
            ft.NavigationBarDestination(icon="calendar_month", label="Clases"),
            ft.NavigationBarDestination(icon="payments", label="Pagos"),
        ],
    )

    page.add(
        header,
        ft.Container(height=10),
        resumen_row,
        ft.Container(height=20),
        ft.Text("Agenda Diaria", size=20, weight="bold", color="#0D47A1"),
        agenda_vacia
    )

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Según tu error de Deprecation, 'run' es el nuevo estándar en 0.80.0
    ft.run(main)