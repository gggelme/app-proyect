# src/ui/app.py
import flet as ft
from ui.views.home import HomeView
from ui.views.menu import MenuView

#crear menu
from ui.views.crear_menu import CrearMenuView
from ui.views.crear_alumno import CrearAlumnoView  
from ui.views.crear_profesor import CrearProfesorView
from ui.views.crear_cuota import CrearCuotaView

#inscribir
from ui.views.inscribir_alumno import InscribirAlumnoView

class AcademiaApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Academia Irupé"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
    def run(self):
        """Inicia la aplicación mostrando el home"""
        self.mostrar_home()
    
    def mostrar_home(self):
        """Muestra la vista de home"""
        home = HomeView(
            self.page, 
            self.mostrar_menu,
            self.salir_de_app
        )
        self.page.clean()
        self.page.add(home.build())
        self.page.update()
    
    def mostrar_menu(self, e=None):
        """Muestra el menú principal"""
        print("📋 Mostrando menú principal...")
        self.page.clean()
        menu_view = MenuView(
            self.page,
            self.mostrar_home,
            self.mostrar_crear_menu,  
            self.mostrar_inscribir
        )
        self.page.add(menu_view.build())
        self.page.update()


    def mostrar_crear_menu(self, e=None):
        """Muestra el menú de creación"""
        print("🆕 Mostrando menú de creación...")
        self.page.clean()
        crear_view = CrearMenuView(
            self.page,
            self.mostrar_menu,           # Volver al menú principal
            self.mostrar_crear_alumno,             # Nuevo alumno
            self.mostrar_crear_profesor,             # Nuevo profesor
            self.mostrar_crear_cuota             # Nueva cuota
        )
        self.page.add(crear_view.build())
        self.page.update()

    
    def mostrar_crear_alumno(self, e=None):
        """Muestra el formulario para crear un alumno"""
        print("👤 Mostrando formulario de alumno...")
        self.page.clean()
        alumno_view = CrearAlumnoView(
            self.page,
            self.mostrar_crear_menu,  # Volver al menú de creación
            self.mostrar_inscribir
        )
        self.page.add(alumno_view.build())
        self.page.update()

    def mostrar_inscribir(self, e=None):
        """Muestra la vista de inscripción de alumnos"""
        print("📝 Mostrando inscripción de alumnos...")
        self.page.clean()
        inscribir_view = InscribirAlumnoView(
            self.page,
            self.mostrar_menu  # Volver al menú principal
        )
        self.page.add(inscribir_view.build())
        self.page.update()


    def mostrar_crear_profesor(self, e=None):
        """Muestra el formulario para crear un profesor"""
        print("👨‍🏫 Mostrando formulario de profesor...")
        self.page.clean()
        profesor_view = CrearProfesorView(
            self.page,
            self.mostrar_crear_menu  # Volver al menú de creación
        )
        self.page.add(profesor_view.build())
        self.page.update()

    def mostrar_crear_cuota(self, e=None):
        """Muestra el formulario para crear una cuota"""
        print("💰 Mostrando formulario de cuota...")
        self.page.clean()
        cuota_view = CrearCuotaView(
            self.page,
            self.mostrar_crear_menu  # Volver al menú de creación
        )
        self.page.add(cuota_view.build())
        self.page.update()    

    
    def placeholder(self, e):
        """Placeholder para botones que aún no tienen funcionalidad"""
        print("🔧 Funcionalidad en desarrollo...")
    
    def salir_de_app(self, e):
        """Callback para cerrar la aplicación"""
        print("👋 Cerrando aplicación...")
        self.page.window.close()