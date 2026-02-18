# ui/views/crear_habitacion_view.py
import flet as ft

class CrearHabitacionView:
    def __init__(self, page, on_volver_callback, on_guardar_callback):
        self.page = page
        self.on_volver_callback = on_volver_callback
        self.on_guardar_callback = on_guardar_callback
        
        # Campos del formulario
        self.nombre = ft.TextField(
            label="Nombre de la Habitación *",
            width=300,
            border_color="white",
            color="white",
            label_style=ft.TextStyle(color="white70"),
            on_change=self.validar_campos,
            capitalization=ft.TextCapitalization.WORDS,
            hint_text="Ej: Sala 101, Aula Magna, etc.",
            hint_style=ft.TextStyle(color="white38"),
        )
        
        self.capacidad = ft.TextField(
            label="Capacidad *",
            width=300,
            border_color="white",
            color="white",
            label_style=ft.TextStyle(color="white70"),
            hint_text="Ej: 30",
            hint_style=ft.TextStyle(color="white38"),
            on_change=self.validar_campos,
            keyboard_type=ft.KeyboardType.NUMBER,  # Teclado numérico
        )
        
        self.mensaje = ft.Text(color="white", size=14)
        self.boton_guardar = None
        self.datos_guardados = None
    
    def validar_campos(self, e=None):
        """Valida los campos en tiempo real"""
        campos_obligatorios = [
            self.nombre.value,
            self.capacidad.value,
        ]
        
        # Validar que la capacidad sea un número entero positivo
        capacidad_valida = True
        if self.capacidad.value:
            try:
                capacidad = int(self.capacidad.value)
                if capacidad <= 0:
                    capacidad_valida = False
                    self.capacidad.border_color = "red"
                else:
                    self.capacidad.border_color = "white"
            except ValueError:
                capacidad_valida = False
                self.capacidad.border_color = "red"
        else:
            capacidad_valida = False
        
        todos_completos = all(campos_obligatorios) and capacidad_valida
        
        if self.boton_guardar:
            self.boton_guardar.disabled = not todos_completos
        
        self.page.update()
    
    def guardar_habitacion(self, e):
        """Valida campos y llama al callback de guardado"""
        
        # Validar que la capacidad sea un número entero válido
        try:
            capacidad = int(self.capacidad.value)
            if capacidad <= 0:
                self.mensaje.value = "❌ La capacidad debe ser un número positivo"
                self.mensaje.color = "red"
                self.page.update()
                return
        except ValueError:
            self.mensaje.value = "❌ La capacidad debe ser un número entero"
            self.mensaje.color = "red"
            self.page.update()
            return
        
        # Guardamos los datos
        self.datos_guardados = {
            'nombre': self.nombre.value.strip().upper(),
            'capacidad': capacidad,
        }
        
        # Mostrar mensaje de "guardando..."
        self.mensaje.value = "⏳ Guardando habitación..."
        self.mensaje.color = "yellow"
        self.boton_guardar.disabled = True
        self.page.update()
        
        # Llamamos al callback de la app
        self.on_guardar_callback(self.datos_guardados)
    
    def mostrar_exito(self, nombre, habitacion_id):
        """Muestra pantalla de éxito específica para habitación"""
        self.page.clean()
        
        contenido = ft.Column(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=60),
                ft.Text("¡Habitación guardada!", size=22, color="white", weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text(
                    f"La habitación {nombre} fue registrada con éxito.",
                    color="white", 
                    size=16, 
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=5),
                ft.Text(
                    f"ID asignado: {habitacion_id}",
                    color="white70",
                    size=14,
                ),
                ft.Container(height=20),
                
                # Botón para CREAR OTRA HABITACIÓN (verde)
                ft.ElevatedButton(
                    "➕ CREAR OTRA HABITACIÓN",
                    on_click=lambda _: self.on_volver_callback(),
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",
                        padding=20,
                    ),
                    width=250,
                ),
                ft.Container(height=5),
                
                # Botón para VOLVER AL MENÚ PRINCIPAL (azul)
                ft.ElevatedButton(
                    "🏠 VOLVER AL MENÚ PRINCIPAL",
                    on_click=lambda _: self.page.go_back(),
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#1E88E5",
                        padding=20,
                    ),
                    width=250,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
        
        tarjeta = ft.Container(
            content=contenido,
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=450,
        )
        
        self.page.add(tarjeta)
        self.page.update()
    
    def build(self):
        """Construye el formulario de creación de habitación"""
        
        titulo = ft.Text(
            "CREAR HABITACIÓN",
            size=26,
            weight=ft.FontWeight.BOLD,
            color="white"
        )
        
        subtitulo = ft.Text(
            "Los campos marcados con * son obligatorios",
            size=12,
            color="white70",
            italic=True,
        )
        
        formulario = ft.Column(
            [
                self.nombre,
                self.capacidad,
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        self.boton_guardar = ft.ElevatedButton(
            "GUARDAR HABITACIÓN",
            on_click=self.guardar_habitacion,
            style=ft.ButtonStyle(
                color="white",
                bgcolor="#2E7D32",
                padding=20,
            ),
            width=200,
            disabled=True,
        )
        
        botones = ft.Row(
            [
                self.boton_guardar,
                ft.ElevatedButton(
                    "CANCELAR",
                    on_click=self.on_volver_callback,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#d32f2f",
                        padding=20,
                    ),
                    width=200,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        
        contenido_completo = ft.Column(
            [
                titulo,
                subtitulo,
                ft.Container(height=20),
                formulario,
                ft.Container(height=10),
                self.mensaje,
                ft.Container(height=10),
                botones,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
        
        tarjeta = ft.Container(
            content=contenido_completo,
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=450,
        )
        
        # Validar campos inicialmente
        self.validar_campos()
        
        return tarjeta