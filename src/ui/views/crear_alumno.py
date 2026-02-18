# ui/views/crear_alumno_view.py
import flet as ft
from datetime import datetime

class CrearAlumnoView:
    def __init__(self, page, on_volver_callback, on_guardar_callback, on_inscribir_callback=None):
        self.page = page
        self.on_volver_callback = on_volver_callback
        self.on_guardar_callback = on_guardar_callback
        self.on_inscribir_callback = on_inscribir_callback

        self.mensaje = ft.Text(color="white", size=14)
        self.boton_guardar = None
        self.datos_guardados = None
        
        # Campos del formulario
        self.dni = ft.TextField(
            label="DNI *",
            width=300,
            border_color="white",
            color="white",
            label_style=ft.TextStyle(color="white70"),
            on_change=self.validar_campos,
        )
        
        self.nombre_apellido = ft.TextField(
            label="Nombre y Apellido *",
            width=300,
            border_color="white",
            color="white",
            label_style=ft.TextStyle(color="white70"),
            on_change=self.validar_campos,
        )
        
        self.fecha_nac = ft.TextField(
            label="Fecha de Nacimiento (YYYY-MM-DD) *",
            width=300,
            border_color="white",
            color="white",
            label_style=ft.TextStyle(color="white70"),
            hint_text="Ej: 1990-05-15",
            hint_style=ft.TextStyle(color="white38"),
            on_change=self.validar_campos,
        )
        
        self.domicilio = ft.TextField(
            label="Domicilio *",
            width=300,
            border_color="white",
            color="white",
            label_style=ft.TextStyle(color="white70"),
            on_change=self.validar_campos,
        )
        
        self.telefono = ft.TextField(
            label="Teléfono *",
            width=300,
            border_color="white",
            color="white",
            label_style=ft.TextStyle(color="white70"),
            on_change=self.validar_campos,
        )
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        self.fecha_ingreso = ft.TextField(
            label="Fecha de Ingreso *",
            width=300,
            border_color="white",
            color="white",
            label_style=ft.TextStyle(color="white70"),
            value=fecha_actual,
            read_only=True,
        )
        
        self.mensaje = ft.Text(color="white", size=14)
        self.boton_guardar = None
        self.datos_guardados = None  # Para guardar los datos después del éxito
    
    def validar_campos(self, e=None):
        """Valida los campos en tiempo real"""
        campos_obligatorios = [
            self.dni.value,
            self.nombre_apellido.value,
            self.fecha_nac.value,
            self.domicilio.value,
            self.telefono.value,
        ]
        
        # Validar formato de fecha
        fecha_valida = True
        if self.fecha_nac.value:
            try:
                datetime.strptime(self.fecha_nac.value, "%Y-%m-%d")
            except:
                fecha_valida = False
                self.fecha_nac.border_color = "red"
            else:
                self.fecha_nac.border_color = "white"
        
        todos_completos = all(campos_obligatorios) and fecha_valida
        
        if self.boton_guardar:
            self.boton_guardar.disabled = not todos_completos
        
        self.page.update()

    def mostrar_exito(self, nombre, alumno_id, datos_completos):
        """Muestra pantalla de éxito específica para alumno con opción de inscribir y crear otro"""
        self.page.clean()
        
        # Guardamos los datos en la página por si los necesita el callback de inscribir
        self.page.datos_alumno_actual = {
            'id': alumno_id,
            'nombre': nombre,
            'datos': datos_completos
        }
        
        contenido = ft.Column(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=60),
                ft.Text("¡Alumno guardado!", size=22, color="white", weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text(
                    f"El alumno {nombre} fue registrado con éxito.",
                    color="white", 
                    size=16, 
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=5),
                ft.Text(
                    f"ID asignado: {alumno_id}",
                    color="white70",
                    size=14,
                ),
                ft.Container(height=20),
                
                # Botón para INSCRIBIR (ámbar)
                ft.ElevatedButton(
                    "📝 INSCRIBIR A CLASE",
                    on_click=lambda _: self.on_inscribir_callback(self.page.datos_alumno_actual) if self.on_inscribir_callback else None,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#FFA000",  # Ámbar
                        padding=20,
                    ),
                    width=250,
                ),
                ft.Container(height=10),
                
                # Botón para CREAR OTRO ALUMNO (verde)
                ft.ElevatedButton(
                    "➕ CREAR OTRO ALUMNO",
                    on_click=lambda _: self.on_volver_callback(),  # Vuelve al menú crear
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2E7D32",  # Verde
                        padding=20,
                    ),
                    width=250,
                ),
                ft.Container(height=5),
                
                # Botón para VOLVER AL MENÚ PRINCIPAL (azul)
                ft.ElevatedButton(
                    "🏠 VOLVER AL MENÚ PRINCIPAL",
                    on_click=lambda _: self.page.go_back(),  # Necesita estar definido en app.py
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#1E88E5",  # Azul
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

    
    def guardar_alumno(self, e):
        """Valida campos y llama al callback de guardado"""
        
        # Validar formato de fecha
        try:
            datetime.strptime(self.fecha_nac.value, "%Y-%m-%d")
        except ValueError:
            self.mensaje.value = "❌ Formato de fecha inválido. Use YYYY-MM-DD"
            self.mensaje.color = "red"
            self.page.update()
            return
        
        # Guardamos los datos por si los necesitamos después
        self.datos_guardados = {
            'dni': self.dni.value.strip(),
            'nombre_apellido': self.nombre_apellido.value.strip(),
            'fecha_nac': self.fecha_nac.value.strip(),
            'domicilio': self.domicilio.value.strip(),
            'telefono': self.telefono.value.strip(),
            'fecha_ingreso': self.fecha_ingreso.value,
        }
        
        # Mostrar mensaje de "guardando..."
        self.mensaje.value = "⏳ Guardando alumno..."
        self.mensaje.color = "yellow"
        self.boton_guardar.disabled = True
        self.page.update()
        
        # Llamamos al callback de la app
        self.on_guardar_callback(self.datos_guardados)
    
    def build(self):
        """Construye el formulario de creación de alumno"""
        
        titulo = ft.Text(
            "CREAR ALUMNO",
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
                self.dni,
                self.nombre_apellido,
                self.fecha_nac,
                self.domicilio,
                self.telefono,
                self.fecha_ingreso,
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        self.boton_guardar = ft.ElevatedButton(
            "GUARDAR ALUMNO",
            on_click=self.guardar_alumno,
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