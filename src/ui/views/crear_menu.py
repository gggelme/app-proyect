# src/ui/views/crear_menu.py
import flet as ft

class CrearMenuView:
    def __init__(self, page, on_volver_callback, 
                 on_nuevo_alumno, on_nuevo_profesor, 
                 on_nueva_cuota):  # <--- Solo 3 callbacks
        self.page = page
        self.on_volver_callback = on_volver_callback
        self.on_nuevo_alumno = on_nuevo_alumno
        self.on_nuevo_profesor = on_nuevo_profesor
        self.on_nueva_cuota = on_nueva_cuota
    
    def build(self):
        """Construye el menú para elegir qué crear"""
        
        contenido = ft.Column(
            [
                ft.Text("¿QUÉ DESEA CREAR?", size=26, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=20),
                
                # 3 botones para las opciones de creación
                ft.ElevatedButton(
                    "👤 NUEVO ALUMNO",
                    on_click=self.on_nuevo_alumno,
                    width=250,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",  # Verde
                        padding=15,
                    ),
                ),
                ft.ElevatedButton(
                    "👨‍🏫 NUEVO PROFESOR",
                    on_click=self.on_nuevo_profesor,
                    width=250,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",  # Verde
                        padding=15,
                    ),
                ),
                ft.ElevatedButton(
                    "💰 NUEVA CUOTA",
                    on_click=self.on_nueva_cuota,
                    width=250,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",  # Verde
                        padding=15,
                    ),
                ),
                
                ft.Container(height=20),
                
                # Botón para volver
                ft.ElevatedButton(
                    "← Volver al menú principal",
                    on_click=self.on_volver_callback,
                    width=250,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Tarjeta contenedora
        tarjeta = ft.Container(
            content=contenido,
            bgcolor="#1E88E5",  # Azul
            padding=40,
            border_radius=20,
            width=450,
        )
        
        return tarjeta