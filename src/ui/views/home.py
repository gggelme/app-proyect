# src/ui/views/home.py
import flet as ft

class HomeView:
    def __init__(self, page, on_entrar_callback, on_salir_callback):
        self.page = page
        self.on_entrar_callback = on_entrar_callback
        self.on_salir_callback = on_salir_callback
    
    def build(self):
        """Construye y retorna la vista de home"""
        tarjeta = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.SCHOOL, color="white", size=50),
                    ft.Text("ACADEMIA IRUPÉ", size=28, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text("Gestión de Clases", color="white70"),
                    ft.Container(height=20),
                    
                    # Botón Entrar
                    ft.ElevatedButton(
                        "Entrar", 
                        on_click=self.on_entrar_callback,
                        width=200,
                    ),
                    
                    ft.Container(height=10),
                    
                    # Botón Salir
                    ft.ElevatedButton(
                        "Salir", 
                        on_click=self.on_salir_callback,
                        width=200,
                        bgcolor="red400",
                        color="white"
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO
            ),
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=320,
        )
        return tarjeta