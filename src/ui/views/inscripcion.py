import flet as ft

class InscripcionView:
    def __init__(self, page, on_volver_callback):
        self.page = page
        self.on_volver_callback = on_volver_callback
    
    def build(self):
        """Construye una vista simple de inscripción"""
        
        contenido = ft.Column(
            [
                ft.Icon(ft.Icons.ASSIGNMENT, color="white", size=50),
                ft.Text(
                    "INSCRIPCIONES",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Container(height=20),
                ft.Text(
                    "Módulo de inscripciones en desarrollo",
                    size=16,
                    color="white70",
                    italic=True,
                ),
                ft.Container(height=30),
                ft.ElevatedButton(
                    "VOLVER AL MENÚ",
                    on_click=self.on_volver_callback,
                    width=200,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        tarjeta = ft.Container(
            content=contenido,
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=450,
        )
        
        return tarjeta