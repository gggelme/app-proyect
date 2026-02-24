import flet as ft

class MenuView:
    def __init__(self, page, on_volver_callback, on_crear_callback, on_inscribir_callback):  # <-- Cambié el nombre del callback
        self.page = page
        self.on_volver_callback = on_volver_callback
        self.on_crear_callback = on_crear_callback  # Ahora es para "Crear"
        self.on_inscribir_callback = on_inscribir_callback  # Nuevo callback para "Inscribir"
    
    def salir(self, e):
        self.page.window.close()
    
    def build(self):
        """Construye y retorna la vista del menú con tarjeta"""
        
        contenido_menu = ft.Column(
            [
                ft.Text("MENÚ PRINCIPAL", size=26, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=20),
                ft.ElevatedButton("CREAR", on_click=self.on_crear_callback),  # <-- Cambiado
                ft.ElevatedButton("ACTUALIZAR"),
                ft.ElevatedButton("ELIMINAR"),
                ft.Container(height=10),
                ft.ElevatedButton("INSCRIBIR", on_click=self.on_inscribir_callback), 
                ft.ElevatedButton("Calendario"),
                ft.ElevatedButton("Listado de adeudores"),
                ft.ElevatedButton("Consulta SQL"),
                ft.Container(height=10),
                ft.ElevatedButton("Volver al inicio", on_click=self.on_volver_callback),
                ft.ElevatedButton("Salir", on_click=self.salir),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        
        tarjeta_menu = ft.Container(
            content=contenido_menu,
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=400,
        )
        
        return tarjeta_menu