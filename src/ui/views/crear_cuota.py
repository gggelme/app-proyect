# src/ui/views/crear_cuota.py
import flet as ft
from decimal import Decimal, InvalidOperation

#interacion con base de datos
from database.repos_cuota import guardar_cuota
from models.cuota import Cuota

class CrearCuotaView:
    def __init__(self, page, on_volver_callback):
        self.page = page
        self.on_volver_callback = on_volver_callback
        
        # Controladores para los campos de entrada
        self.nombre_input = ft.TextField(
            label="Nombre de la Cuota *", 
            width=300, 
            hint_text="Ej: Clase de Guitarra - Mensual",
            bgcolor="white",
            color="black",
            border_radius=10
        )
        
        self.precio_input = ft.TextField(
            label="Precio *", 
            width=300, 
            hint_text="Ej: 15000.00",
            bgcolor="white",
            color="black",
            border_radius=10,
            prefix=ft.Text("$ ")  # Agrega el símbolo de pesos
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
            "💾 GUARDAR CUOTA",
            on_click=self.guardar_cuota,
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
        
        # Limpiar campos para crear otra cuota
        self.nombre_input.value = ""
        self.precio_input.value = ""
        
        self.page.update()
    
    def validar_datos(self):
        """Valida que los campos obligatorios estén completos y tengan formato correcto"""
        # Validar nombre
        if not self.nombre_input.value or not self.nombre_input.value.strip():
            self.mostrar_error("El nombre de la cuota es obligatorio")
            return False
        
        # Validar precio
        if not self.precio_input.value or not self.precio_input.value.strip():
            self.mostrar_error("El precio es obligatorio")
            return False
        
        # Validar que el precio sea un número válido
        try:
            precio_texto = self.precio_input.value.strip().replace(',', '.')
            precio = float(precio_texto)
            if precio <= 0:
                self.mostrar_error("El precio debe ser mayor a cero")
                return False
        except ValueError:
            self.mostrar_error("El precio debe ser un número válido")
            return False
        
        return True
    
    def guardar_cuota(self, e):
        """Guarda la cuota en la base de datos usando el repositorio"""
        if not self.validar_datos():
            return
        
        try:
            # Convertir precio a Decimal
            precio_texto = self.precio_input.value.strip().replace(',', '.')
            precio_decimal = Decimal(precio_texto)
            
            # Crear objeto Cuota con los datos del formulario
            cuota = Cuota(
                nombre=self.nombre_input.value.strip(),
                precio_cuota=precio_decimal
            )
            
            # Llamar al repositorio para guardar
            id_generado = guardar_cuota(cuota)
            
            # Mostrar mensaje de éxito
            self.mostrar_exito(f"✅ Cuota guardada correctamente con ID: {id_generado}")
            
        except Exception as ex:
            self.mostrar_error(f"Error al guardar: {str(ex)}")
    
    def build(self):
        """Construye la vista para crear cuota"""
        
        # Contenedor del formulario (lo que va dentro de la tarjeta)
        formulario = ft.Column(
            [
                ft.Text("REGISTRAR NUEVA CUOTA", size=26, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=10),
                ft.Text("Los campos marcados con * son obligatorios", size=12, color="white70", italic=True),
                ft.Container(height=20),
                
                # Campos del formulario
                self.nombre_input,
                ft.Container(height=10),
                self.precio_input,
                
                ft.Container(height=20),
                
                # Mensajes de error/éxito
                self.error_container,
                self.exito_container,
                
                ft.Container(height=20),
                
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
                scroll=ft.ScrollMode.ALWAYS,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=500,
            height=500,  # Altura fija para que el scroll funcione
        )
        
        return tarjeta