import flet as ft

class CrearMenuView:
    def __init__(self, page, on_volver_callback, 
                 on_crear_alumno, on_crear_profesor, 
                 on_crear_aula, on_crear_instrumento):
        self.page = page
        self.on_volver_callback = on_volver_callback
        self.on_crear_alumno = on_crear_alumno
        self.on_crear_profesor = on_crear_profesor
        self.on_crear_aula = on_crear_aula
        self.on_crear_instrumento = on_crear_instrumento
    
    def build(self):
        """Construye el submenú de creación"""
        
        contenido = ft.Column(
            [
                ft.Text("¿QUÉ DESEA CREAR?", size=26, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=20),
                
                # Las 4 opciones de creación
                ft.ElevatedButton(
                    "👤 CREAR ALUMNO",
                    on_click=self.on_crear_alumno,
                    width=250,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",  # Verde
                        padding=15,
                    ),
                ),
                ft.ElevatedButton(
                    "👨‍🏫 CREAR PROFESOR",
                    on_click=self.on_crear_profesor,
                    width=250,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",  # Verde
                        padding=15,
                    ),
                ),
                ft.ElevatedButton(
                    "🏫 CREAR AULA",
                    on_click=self.on_crear_aula,
                    width=250,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",  # Verde
                        padding=15,
                    ),
                ),
                ft.ElevatedButton(
                    "🎸 CREAR INSTRUMENTO",
                    on_click=self.on_crear_instrumento,
                    width=250,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",  # Verde
                        padding=15,
                    ),
                ),
                
                ft.Container(height=20),
                ft.ElevatedButton(
                    "← Volver al menú",
                    on_click=self.on_volver_callback,
                    width=200,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Tarjeta contenedora
        tarjeta = ft.Container(
            content=contenido,
            bgcolor="#1E88E5",  # Azul
            padding=40,
            border_radius=20,
            width=400,
        )
        
        return tarjeta