import flet as ft

class HomeView:
    def __init__(self, page, on_entrar_callback):
        self.page = page
        self.on_entrar_callback = on_entrar_callback
    
    def build(self):
        """Construye y retorna la vista de home"""
        tarjeta = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.SCHOOL, color="white", size=50),
                    ft.Text("ACADEMIA IRUPÉ", size=28, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text("Gestión de Clases", color="white70"),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Entrar", 
                        on_click=self.on_entrar_callback
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=320,
        )
        return tarjeta