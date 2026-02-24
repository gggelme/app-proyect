# src/ui/views/crear_profesor.py
import flet as ft
from datetime import datetime

#interacion con base de datos
from database.repos_profesor import guardar_profesor
from models.persona import Profesor
from datetime import date

class CrearProfesorView:
    def __init__(self, page, on_volver_callback):
        self.page = page
        self.on_volver_callback = on_volver_callback
        
        # Controladores para los campos de entrada
        self.dni_input = ft.TextField(
            label="DNI *", 
            width=300, 
            hint_text="Ej: 12345678",
            bgcolor="white",
            color="black",
            border_radius=10
        )
        
        self.nombre_input = ft.TextField(
            label="Nombre y Apellido *", 
            width=300, 
            hint_text="Ej: Juan Pérez",
            bgcolor="white",
            color="black",
            border_radius=10
        )
        
        self.fecha_nac_input = ft.TextField(
            label="Fecha de Nacimiento", 
            width=300, 
            hint_text="AAAA-MM-DD (opcional)",
            bgcolor="white",
            color="black",
            border_radius=10
        )
        
        self.domicilio_input = ft.TextField(
            label="Domicilio", 
            width=300, 
            hint_text="Calle y número (opcional)",
            bgcolor="white",
            color="black",
            border_radius=10
        )
        
        self.telefono_input = ft.TextField(
            label="Teléfono", 
            width=300, 
            hint_text="Ej: 1234-567890 (opcional)",
            bgcolor="white",
            color="black",
            border_radius=10
        )
        
        # Campos específicos de profesor
        self.alias_input = ft.TextField(
            label="Alias", 
            width=300, 
            hint_text="Ej: Profe Juan (opcional)",
            bgcolor="white",
            color="black",
            border_radius=10
        )
        
        self.email_input = ft.TextField(
            label="Email", 
            width=300, 
            hint_text="Ej: profesor@academia.com (opcional)",
            bgcolor="white",
            color="black",
            border_radius=10
        )
        
        # Contenedor para mensaje de error (recuadro blanco)
        self.error_container = ft.Container(
            content=ft.Text("", color="red", size=14, weight=ft.FontWeight.BOLD),
            bgcolor="white",
            padding=10,
            border_radius=8,
            visible=False,
            width=300
        )
        
        # Contenedor para mensaje de éxito (recuadro blanco)
        self.exito_container = ft.Container(
            content=ft.Text("", color="green", size=14, weight=ft.FontWeight.BOLD),
            bgcolor="white",
            padding=10,
            border_radius=8,
            visible=False,
            width=300
        )
        
        # Botones de acción
        self.btn_guardar = ft.ElevatedButton(
            "💾 GUARDAR PROFESOR",
            on_click=self.guardar_profesor,
            width=200,
            style=ft.ButtonStyle(
                color="white",
                bgcolor="#2E7D32",  # Verde
                padding=15,
            ),
        )
        
        self.btn_volver = ft.ElevatedButton(
            "← Volver al menú",
            on_click=self.on_volver_callback,
            width=200,
        )
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en recuadro blanco"""
        self.error_container.content.value = mensaje
        self.error_container.visible = True
        self.exito_container.visible = False
        self.page.update()

    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito en recuadro blanco y limpia el formulario"""
        self.exito_container.content.value = mensaje
        self.exito_container.visible = True
        self.error_container.visible = False
        
        # Limpiar campos para crear otro profesor
        self.dni_input.value = ""
        self.nombre_input.value = ""
        self.fecha_nac_input.value = ""
        self.domicilio_input.value = ""
        self.telefono_input.value = ""
        self.alias_input.value = ""
        self.email_input.value = ""
        
        self.page.update()
    
    def validar_datos(self):
        """Valida que los campos obligatorios estén completos y tengan formato correcto"""
        # Campos obligatorios
        if not self.dni_input.value or not self.dni_input.value.strip():
            self.mostrar_error("El DNI es obligatorio")
            return False
        
        if not self.nombre_input.value or not self.nombre_input.value.strip():
            self.mostrar_error("El nombre y apellido es obligatorio")
            return False
        
        # Validar que el DNI solo tenga números
        dni = self.dni_input.value.strip()
        if not dni.isdigit():
            self.mostrar_error("El DNI debe contener solo números")
            return False
        
        # Validar teléfono si se ingresó
        if self.telefono_input.value:
            telefono = self.telefono_input.value.strip()
            if not all(c.isdigit() or c in " +-" for c in telefono):
                self.mostrar_error("El teléfono solo puede contener números, espacios, + y -")
                return False
        
        # Validar email si se ingresó (formato básico)
        if self.email_input.value:
            email = self.email_input.value.strip()
            if "@" not in email or "." not in email:
                self.mostrar_error("El email no tiene un formato válido")
                return False
        
        # Validar formato de fecha si se ingresó
        if self.fecha_nac_input.value:
            try:
                datetime.strptime(self.fecha_nac_input.value.strip(), "%Y-%m-%d")
            except ValueError:
                self.mostrar_error("La fecha de nacimiento debe tener formato AAAA-MM-DD")
                return False
        
        return True
    
    def guardar_profesor(self, e):
        """Guarda el profesor en la base de datos usando el repositorio"""
        if not self.validar_datos():
            return
        
        try:
            # Crear objeto Profesor con los datos del formulario
            profesor = Profesor(
                dni=self.dni_input.value.strip(),
                nomb_apel=self.nombre_input.value.strip(),
                fecha_nac=date.fromisoformat(self.fecha_nac_input.value.strip()) if self.fecha_nac_input.value else None,
                domicilio=self.domicilio_input.value.strip() if self.domicilio_input.value else None,
                telefono=self.telefono_input.value.strip() if self.telefono_input.value else None,
                alias=self.alias_input.value.strip() if self.alias_input.value else None,
                email=self.email_input.value.strip() if self.email_input.value else None
            )
            
            # Llamar al repositorio para guardar
            id_generado = guardar_profesor(profesor)
            
            # Mostrar mensaje de éxito
            self.mostrar_exito(f"✅ Profesor guardado correctamente con ID: {id_generado}")
            
        except Exception as ex:
            self.mostrar_error(f"Error al guardar: {str(ex)}")
    
    def build(self):
        """Construye la vista para crear profesor"""
        
        # Contenedor del formulario (lo que va dentro de la tarjeta)
        formulario = ft.Column(
            [
                ft.Text("REGISTRAR NUEVO PROFESOR", size=26, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=10),
                ft.Text("Los campos marcados con * son obligatorios", size=12, color="white70", italic=True),
                ft.Container(height=10),
                
                # Campos del formulario
                self.dni_input,
                self.nombre_input,
                self.fecha_nac_input,
                self.domicilio_input,
                self.telefono_input,
                self.alias_input,
                self.email_input,
                
                ft.Container(height=10),
                
                # Mensajes de error/éxito
                self.error_container,
                self.exito_container,
                
                ft.Container(height=10),
                
                # Botones
                ft.Row(
                    [self.btn_guardar],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                ft.Container(height=10),
                
                ft.Row(
                    [self.btn_volver],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Espacio extra al final
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
        
        # Tarjeta contenedora con scroll
        tarjeta = ft.Container(
            content=ft.Column(
                [formulario],
                scroll=ft.ScrollMode.ALWAYS,  # <--- SCROLL AQUÍ
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=500,
            height=600,  # Altura fija para que el scroll funcione
        )
        
        return tarjeta