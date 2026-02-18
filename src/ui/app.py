# ui/app.py
import flet as ft
from ui.views.home import HomeView
from ui.views.inscripcion import InscripcionView
from ui.views.menu import MenuView
from ui.views.crear_menu import CrearMenuView
from ui.views.crear_profesor import CrearProfesorView
from ui.views.crear_alumno import CrearAlumnoView

from database.profesor_repo import guardar_profesor as guardar_profesor_repo
from database.profesor_repo import ErrorGuardarProfesor
from database.alumno_repo import guardar_alumno as guardar_alumno_repo
from database.alumno_repo import ErrorGuardarAlumno
from models.persona import Profesor, Alumno

from database.instrumento_repo import guardar_instrumento as guardar_instrumento_repo
from database.instrumento_repo import ErrorGuardarInstrumento
from models.instrumento import Instrumento
from ui.views.crear_instrumento import CrearInstrumentoView


from database.habitacion_repo import guardar_habitacion as guardar_habitacion_repo
from database.habitacion_repo import ErrorGuardarHabitacion
from models.habitacion import Habitacion
from ui.views.crear_habitacion import CrearHabitacionView

class AcademiaApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self._configurar_pagina()
        # Agregamos método para volver al menú principal
        self.page.go_back = self.mostrar_menu
    
    def _configurar_pagina(self):
        self.page.title = "Academia Irupé"
        self.page.bgcolor = "#222222"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    def mostrar_menu(self, e=None):
        self.page.clean()
        menu_view = MenuView(
            self.page, 
            self.mostrar_home,
            self.mostrar_crear_menu,
            self.mostrar_inscribir
        )
        self.page.add(menu_view.build())
        self.page.update()
    
    def mostrar_home(self, e=None):
        self.page.clean()
        home_view = HomeView(self.page, self.mostrar_menu)
        self.page.add(home_view.build())
        self.page.update()
    
    def mostrar_crear_menu(self, e=None):
        self.page.clean()
        crear_menu = CrearMenuView(
            self.page,
            self.mostrar_menu,
            self.mostrar_crear_alumno,
            self.mostrar_crear_profesor,
            self.mostrar_crear_aula,
            self.mostrar_crear_instrumento
        )
        self.page.add(crear_menu.build())
        self.page.update()
    
    def mostrar_crear_profesor(self, e=None):
        self.page.clean()
        profesor_view = CrearProfesorView(
            self.page,
            self.mostrar_crear_menu,  # Vuelve al menú crear
            self.guardar_profesor
        )
        self.page.add(profesor_view.build())
        self.page.update()
    
    def mostrar_crear_alumno(self, e=None):
        self.page.clean()
        alumno_view = CrearAlumnoView(
            self.page,
            self.mostrar_crear_menu,  # Vuelve al menú crear
            self.guardar_alumno,
            self.mostrar_inscribir_alumno  # Callback para inscribir
        )
        self.page.add(alumno_view.build())
        self.page.update()
    
    def guardar_profesor(self, datos_profesor):
        """Guarda el profesor y delega el éxito a la vista"""
        try:
            from datetime import datetime
            fecha_nac = datetime.strptime(datos_profesor['fecha_nac'], "%Y-%m-%d").date()
            fecha_ingreso = datetime.strptime(datos_profesor['fecha_ingreso'], "%Y-%m-%d").date()
            
            profesor = Profesor(
                dni=datos_profesor['dni'],
                nombre_apellido=datos_profesor['nombre_apellido'],
                fecha_nac=fecha_nac,
                domicilio=datos_profesor['domicilio'],
                telefono=datos_profesor['telefono'],
                fecha_ingreso=fecha_ingreso,
                alias_mp=datos_profesor['alias_mp']
            )
            
            persona_id = guardar_profesor_repo(profesor)
            
            # La vista de profesor se encarga de mostrar el éxito
            # Pero necesitamos una referencia a la vista anterior
            # Una opción es guardar la vista en el page o usar un callback
            
            # Por ahora, creamos una nueva instancia de la vista y mostramos éxito
            vista_exito = CrearProfesorView(self.page, self.mostrar_crear_menu, None)
            vista_exito.mostrar_exito(datos_profesor['nombre_apellido'], persona_id)
            
        except ErrorGuardarProfesor as e:
            self.mostrar_error(str(e), "profesor")
        except Exception as e:
            import traceback
            self.mostrar_error(f"Error inesperado: {str(e)}", "profesor", traceback.format_exc())
    
    def guardar_alumno(self, datos_alumno):
        """Guarda el alumno y delega el éxito a la vista"""
        try:
            from datetime import datetime
            fecha_nac = datetime.strptime(datos_alumno['fecha_nac'], "%Y-%m-%d").date()
            fecha_ingreso = datetime.strptime(datos_alumno['fecha_ingreso'], "%Y-%m-%d").date()
            
            alumno = Alumno(
                dni=datos_alumno['dni'],
                nombre_apellido=datos_alumno['nombre_apellido'],
                fecha_nac=fecha_nac,
                domicilio=datos_alumno['domicilio'],
                telefono=datos_alumno['telefono'],
                fecha_ingreso=fecha_ingreso
            )
            
            persona_id = guardar_alumno_repo(alumno)
            
            # La vista de alumno se encarga de mostrar el éxito con opción de inscribir
            vista_exito = CrearAlumnoView(
                self.page, 
                self.mostrar_crear_menu, 
                None,
                self.mostrar_inscribir_alumno
            )
            vista_exito.mostrar_exito(datos_alumno['nombre_apellido'], persona_id, datos_alumno)
            
        except ErrorGuardarAlumno as e:
            self.mostrar_error(str(e), "alumno")
        except Exception as e:
            import traceback
            self.mostrar_error(f"Error inesperado: {str(e)}", "alumno", traceback.format_exc())

    def guardar_instrumento(self, datos_instrumento):
        """Guarda el instrumento usando el repositorio"""
        try:
            # Creamos el objeto Instrumento
            instrumento = Instrumento(
                nombre=datos_instrumento['nombre'],
                precio_hora=datos_instrumento['precio_hora']
            )
            
            # Llamamos al repositorio
            instrumento_id = guardar_instrumento_repo(instrumento)
            
            # Mostramos éxito usando la vista
            vista_exito = CrearInstrumentoView(
                self.page, 
                self.mostrar_crear_menu, 
                None
            )
            vista_exito.mostrar_exito(datos_instrumento['nombre'], instrumento_id)
            
        except ErrorGuardarInstrumento as e:
            self.mostrar_error(
                mensaje=str(e),
                tipo="instrumento"
            )
        except Exception as e:
            import traceback
            self.mostrar_error(
                mensaje=f"Error inesperado: {str(e)}",
                tipo="instrumento",
                detalle=traceback.format_exc()
            )
    def guardar_habitacion(self, datos_habitacion):
        """Guarda la habitación usando el repositorio"""
        try:
            # Creamos el objeto Habitacion
            habitacion = Habitacion(
                nombre=datos_habitacion['nombre'],
                capacidad=datos_habitacion['capacidad']
            )
            
            # Validar que la capacidad sea positiva
            if habitacion.capacidad <= 0:
                raise ValueError("La capacidad debe ser un número positivo")
            
            # Llamamos al repositorio
            habitacion_id = guardar_habitacion_repo(habitacion)
            
            # Mostramos éxito usando la vista
            vista_exito = CrearHabitacionView(
                self.page, 
                self.mostrar_crear_menu, 
                None
            )
            vista_exito.mostrar_exito(datos_habitacion['nombre'], habitacion_id)
            
        except ErrorGuardarHabitacion as e:
            self.mostrar_error(
                mensaje=str(e),
                tipo="aula"
            )
        except Exception as e:
            import traceback
            self.mostrar_error(
                mensaje=f"Error inesperado: {str(e)}",
                tipo="aula",
                detalle=traceback.format_exc()
            )
            
    
    def mostrar_error(self, mensaje, tipo="", detalle=""):
        """Muestra error y vuelve a la vista correspondiente"""
        self.page.clean()
        
        # Determinar función de volver según el tipo
        if tipo == "alumno":
            volver_func = lambda _: self.mostrar_crear_alumno(None)
        elif tipo == "profesor":
            volver_func = lambda _: self.mostrar_crear_profesor(None)
        elif tipo == "instrumento":
            volver_func = lambda _: self.mostrar_crear_instrumento(None)
        elif tipo == "aula":
            volver_func = lambda _: self.mostrar_crear_aula(None)
        else:
            volver_func = lambda _: self.mostrar_menu() 
        
        # Construir contenido del error
        contenido = [
            ft.Icon(ft.Icons.ERROR_OUTLINE, color="red", size=60),
            ft.Text("ERROR", size=22, color="white", weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Text(mensaje, color="white", size=16, text_align=ft.TextAlign.CENTER),
        ]
        
        # Si hay detalle técnico, mostrarlo en un cuadro
        if detalle:
            contenido.extend([
                ft.Container(height=15),
                ft.Text("🔍 Detalle:", size=14, color="white", weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(
                        detalle,
                        color="white",
                        size=11,
                        text_align=ft.TextAlign.LEFT,
                        font_family="monospace",
                    ),
                    bgcolor="#330000",
                    padding=15,
                    border_radius=10,
                    width=400,
                ),
            ])
        
        # Botones de acción
        contenido.extend([
            ft.Container(height=20),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "VOLVER",
                        on_click=volver_func,
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="#1E88E5",
                        ),
                    ),
                    ft.ElevatedButton(
                        "MENÚ PRINCIPAL",
                        on_click=self.mostrar_menu,
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="#2E7D32",
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        ])
        
        # Crear y mostrar la tarjeta de error
        error_view = ft.Container(
            content=ft.Column(
                contenido,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor="#d32f2f",  # Rojo
            padding=40,
            border_radius=20,
            width=500,
        )
        
        self.page.add(error_view)
        self.page.update()
    
    # Placeholders
    def mostrar_inscribir(self, e=None):
        """Muestra la vista de inscripciones (vacía por ahora)"""
        self.page.clean()
        inscripcion_view = InscripcionView(
            self.page,
            self.mostrar_menu  # Solo necesita volver al menú
        )
        self.page.add(inscripcion_view.build())
        self.page.update()
    
    def mostrar_inscribir_alumno(self, datos_alumno_actual):
        """Redirige a la vista de inscripciones (la misma del menú)"""
        # Si quieres pasar los datos del alumno a la vista de inscripción
        self.page.datos_alumno_actual = datos_alumno_actual
        
        # Llama a la misma función que usa el menú
        self.mostrar_inscribir()
        
    def mostrar_crear_aula(self, e=None):
        """Muestra el formulario para crear habitación/aula"""
        self.page.clean()
        habitacion_view = CrearHabitacionView(
            self.page,
            self.mostrar_crear_menu,  # Vuelve al menú crear
            self.guardar_habitacion
        )
        self.page.add(habitacion_view.build())
        self.page.update()
    
    def mostrar_crear_instrumento(self, e=None):
        """Muestra el formulario para crear instrumento"""
        self.page.clean()
        instrumento_view = CrearInstrumentoView(
            self.page,
            self.mostrar_crear_menu,  # Vuelve al menú crear
            self.guardar_instrumento
        )
        self.page.add(instrumento_view.build())
        self.page.update()
    
    def run(self):
        self.mostrar_home()