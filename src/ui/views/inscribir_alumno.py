# src/ui/views/inscribir_alumno.py
import flet as ft
from database.repos_alumno import buscar_alumnos
from database.repos_clase import obtener_todas_clases
from database.repos_alumno_clase import guardar_alumno_clase
from database.repos_horario import guardar_horario
from database.repos_horario_clase import guardar_horario_clase
from datetime import date, time
from models.horario import Horario

class InscribirAlumnoView:
    def __init__(self, page, on_volver_callback):
        self.page = page
        self.on_volver_callback = on_volver_callback
        
        # ============================================
        # 1. SECCIÓN: BÚSQUEDA DE ALUMNO
        # ============================================
        self.alumno_seleccionado = None
        
        self.busqueda_input = ft.TextField(
            label="Buscar alumno por DNI o nombre",
            width=350,
            bgcolor="white",
            color="black",
            border_radius=10,
            on_submit=self.buscar_alumnos
        )
        
        self.btn_buscar = ft.ElevatedButton(
            "🔍 Buscar",
            on_click=self.buscar_alumnos,
            width=100,
        )
        
        self.resultados_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)
        
        # Label para mostrar alumno seleccionado (ahora muestra también el ID de alumno)
        self.alumno_seleccionado_text = ft.Text("", color="green", size=16, weight=ft.FontWeight.BOLD)
        
        # ============================================
        # 2. SECCIÓN: SELECCIÓN DE CLASE
        # ============================================
        self.clases_disponibles = []
        self.clase_seleccionada_id = None
        self.clase_seleccionada_nombre = ""
        
        # Contenedor para los botones de clases
        self.clases_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        # ============================================
        # 3. SECCIÓN: DÍAS Y HORARIOS DINÁMICOS
        # ============================================
        self.dias_horarios = []
        
        # Contenedor para los días y horarios agregados
        self.dias_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        # Botón para agregar un nuevo día/horario
        self.btn_agregar_dia = ft.ElevatedButton(
            "➕ AGREGAR DÍA/HORARIO",
            on_click=self.agregar_dia_horario,
            width=250,
            style=ft.ButtonStyle(
                color="white",
                bgcolor="#FF9800",
                padding=15,
            ),
        )
        
        # ============================================
        # 4. BOTONES DE ACCIÓN
        # ============================================
        self.btn_inscribir = ft.ElevatedButton(
            "📝 INSCRIBIR A ESTA CLASE",
            on_click=self.inscribir_a_clase,
            width=250,
            visible=False,
            style=ft.ButtonStyle(
                color="white",
                bgcolor="#2E7D32",
                padding=15,
            ),
        )
        
        self.btn_terminar = ft.ElevatedButton(
            "✅ TERMINAR INSCRIPCIONES",
            on_click=self.on_volver_callback,
            width=250,
            style=ft.ButtonStyle(
                color="white",
                bgcolor="#9C27B0",
                padding=15,
            ),
        )
        
        # ============================================
        # 5. MENSAJES
        # ============================================
        self.error_container = ft.Container(
            content=ft.Text("", color="red", size=14, weight=ft.FontWeight.BOLD),
            bgcolor="white",
            padding=10,
            border_radius=8,
            visible=False,
            width=350
        )
        
        self.exito_container = ft.Container(
            content=ft.Text("", color="green", size=14, weight=ft.FontWeight.BOLD),
            bgcolor="white",
            padding=10,
            border_radius=8,
            visible=False,
            width=350
        )
        
        self.btn_volver = ft.ElevatedButton(
            "← Volver al menú",
            on_click=self.on_volver_callback,
            width=200,
        )
        
        # Cargar datos iniciales
        self.cargar_clases()
    
    # ============================================
    # MÉTODOS AUXILIARES
    # ============================================
    def mostrar_error(self, mensaje):
        self.error_container.content.value = mensaje
        self.error_container.visible = True
        self.exito_container.visible = False
        self.page.update()
    
    def mostrar_exito(self, mensaje):
        self.exito_container.content.value = mensaje
        self.exito_container.visible = True
        self.error_container.visible = False
        self.page.update()
    
    # ============================================
    # 1. BÚSQUEDA DE ALUMNO
    # ============================================
    def buscar_alumnos(self, e):
        texto = self.busqueda_input.value
        if not texto or not texto.strip():
            self.mostrar_error("Ingrese un texto para buscar")
            return
        
        resultados = buscar_alumnos(texto)
        self.resultados_list.controls.clear()
        
        if resultados:
            for alum in resultados:
                # Mostrar tanto el ID de alumno como el de persona para depuración
                btn_alumno = ft.ElevatedButton(
                    f"{alum['dni']} - {alum['nomb_apel']} (ID Alumno: {alum['id']})",
                    on_click=lambda _, a=alum: self.seleccionar_alumno(a),
                    width=330,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#2196F3",
                        padding=10,
                    ),
                )
                self.resultados_list.controls.append(btn_alumno)
        else:
            self.resultados_list.controls.append(
                ft.Text("No se encontraron alumnos", color="white70", italic=True)
            )
        
        self.page.update()
    
    def seleccionar_alumno(self, alumno):
        """Guarda el alumno seleccionado con su ID de alumno (no de persona)"""
        self.alumno_seleccionado = {
            'id': alumno['id'],  # <--- ESTE DEBE SER EL ID DE ALUMNO
            'dni': alumno['dni'],
            'nomb_apel': alumno['nomb_apel']
        }
        self.alumno_seleccionado_text.value = f"Alumno seleccionado: {alumno['nomb_apel']} (ID Alumno: {alumno['id']})"
        self.alumno_seleccionado_text.color = "green"
        
        # Limpiar selecciones anteriores
        self.clase_seleccionada_id = None
        self.clase_seleccionada_nombre = ""
        self.dias_horarios.clear()
        self.dias_container.controls.clear()
        self.btn_inscribir.visible = False
        
        self.page.update()
    
    # ============================================
    # 2. CLASES
    # ============================================
    def cargar_clases(self):
        """Carga todas las clases disponibles como botones"""
        try:
            self.clases_disponibles = obtener_todas_clases()
            
            # Crear botones para cada clase
            botones = []
            for clase in self.clases_disponibles:
                btn_clase = ft.ElevatedButton(
                    f"{clase['nombre_clase']} - {clase.get('profesor_nombre', 'Sin profe')}",
                    on_click=lambda _, c=clase: self.seleccionar_clase(c),
                    width=330,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#FF9800",
                        padding=10,
                    ),
                )
                botones.append(btn_clase)
                botones.append(ft.Container(height=5))
            
            self.clases_container.controls = [
                ft.Text("CLASES DISPONIBLES", size=16, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=10),
                *botones,
            ]
            
        except Exception as e:
            print(f"Error cargando clases: {e}")
    
    def seleccionar_clase(self, clase):
        """Cuando se selecciona una clase, habilita la sección de horarios"""
        if not self.alumno_seleccionado:
            self.mostrar_error("Primero debe seleccionar un alumno")
            return
        
        self.clase_seleccionada_id = clase['id']
        self.clase_seleccionada_nombre = clase['nombre_clase']
        
        # Limpiar horarios anteriores
        self.dias_horarios.clear()
        self.dias_container.controls.clear()
        
        # Mostrar información de la clase seleccionada
        self.dias_container.controls.append(
            ft.Text(f"Clase seleccionada: {self.clase_seleccionada_nombre}", 
                size=16, weight=ft.FontWeight.BOLD, color="white")
        )
        self.dias_container.controls.append(ft.Container(height=10))
        self.dias_container.controls.append(
            ft.Text("Agregue los días y horarios para esta clase:", color="white70")
        )
        self.dias_container.controls.append(ft.Container(height=10))
        
        # AGREGAR EL BOTÓN PRIMERO
        self.dias_container.controls.append(self.btn_agregar_dia)
        self.dias_container.controls.append(ft.Container(height=15))
        
        # Títulos de las columnas
        titulos = ft.Row([
            ft.Text("DÍA", width=120, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("INICIO", width=100, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("FIN", width=100, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(width=40),
        ], alignment=ft.MainAxisAlignment.CENTER)
        self.dias_container.controls.append(titulos)
        self.dias_container.controls.append(ft.Container(height=5))
        
        # Agregar el primer día/horario automáticamente
        self.agregar_dia_horario()
        
        self.btn_inscribir.visible = True
        self.page.update()
    
    # ============================================
    # 3. DÍAS Y HORARIOS DINÁMICOS
    # ============================================
    def agregar_dia_horario(self, e=None):
        """Agrega un nuevo conjunto de campos para día y horario"""
        
        dia_row = ft.Row([
            ft.Dropdown(
                label="",
                width=120,
                options=[
                    ft.dropdown.Option("Lunes"),
                    ft.dropdown.Option("Martes"),
                    ft.dropdown.Option("Miércoles"),
                    ft.dropdown.Option("Jueves"),
                    ft.dropdown.Option("Viernes"),
                    ft.dropdown.Option("Sábado"),
                ],
                value="Lunes",
                bgcolor="white",
                color="black",
                text_size=14,
            ),
            ft.TextField(
                label="",
                width=100,
                hint_text="09:00",
                bgcolor="white",
                color="black",
                text_size=14,
            ),
            ft.TextField(
                label="",
                width=100,
                hint_text="10:30",
                bgcolor="white",
                color="black",
                text_size=14,
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color="red",
                icon_size=20,
                on_click=self.eliminar_dia_horario,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Guardar este conjunto en la lista
        self.dias_horarios.append({
            'row': dia_row,
            'dia': dia_row.controls[0],
            'hora_init': dia_row.controls[1],
            'hora_fin': dia_row.controls[2],
        })
        
        # Agregar al contenedor después de los títulos
        insert_index = -1
        for i, control in enumerate(self.dias_container.controls):
            if isinstance(control, ft.Row) and len(control.controls) > 0 and isinstance(control.controls[0], ft.Text):
                if control.controls[0].value == "DÍA":
                    insert_index = i + 2
                    break
        
        if insert_index != -1:
            self.dias_container.controls.insert(insert_index, dia_row)
            self.dias_container.controls.insert(insert_index + 1, ft.Container(height=5))
        else:
            self.dias_container.controls.append(dia_row)
            self.dias_container.controls.append(ft.Container(height=5))
        
        self.page.update()
    
    def eliminar_dia_horario(self, e):
        """Elimina un conjunto de día/horario"""
        row_a_eliminar = e.control.parent
        
        for i, item in enumerate(self.dias_horarios):
            if item['row'] == row_a_eliminar:
                self.dias_horarios.pop(i)
                break
        
        if row_a_eliminar in self.dias_container.controls:
            index = self.dias_container.controls.index(row_a_eliminar)
            self.dias_container.controls.pop(index)
            if index < len(self.dias_container.controls) and isinstance(self.dias_container.controls[index], ft.Container):
                self.dias_container.controls.pop(index)
        
        self.page.update()
    
    # ============================================
    # 4. INSCRIPCIÓN
    # ============================================
    def inscribir_a_clase(self, e):
        if not self.alumno_seleccionado:
            self.mostrar_error("Debe seleccionar un alumno")
            return
        
        if not self.clase_seleccionada_id:
            self.mostrar_error("Debe seleccionar una clase")
            return
        
        if not self.dias_horarios:
            self.mostrar_error("Debe agregar al menos un día/horario")
            return
        
        # Validar que todos los campos estén completos
        horarios_validos = []
        for item in self.dias_horarios:
            dia = item['dia'].value
            hora_init = item['hora_init'].value
            hora_fin = item['hora_fin'].value
            
            if not dia or not hora_init or not hora_fin:
                self.mostrar_error("Complete todos los campos de día y horario")
                return
            
            # Validar formato de hora
            try:
                time.fromisoformat(hora_init)
                time.fromisoformat(hora_fin)
            except:
                self.mostrar_error("Formato de hora inválido. Use HH:MM")
                return
            
            horarios_validos.append({
                'dia': dia,
                'hora_init': hora_init,
                'hora_fin': hora_fin
            })
        
        try:
            # 1. Inscribir alumno en la clase (USANDO ID DE ALUMNO)
            print(f"🔍 Inscribiendo alumno ID: {self.alumno_seleccionado['id']} en clase ID: {self.clase_seleccionada_id}")
            id_inscripcion = guardar_alumno_clase(
                self.alumno_seleccionado['id'],  # <--- ESTE ES EL ID DE ALUMNO
                self.clase_seleccionada_id,
                date.today()
            )
            
            # 2. Por cada horario, guardarlo y asociarlo a la clase
            for horario_data in horarios_validos:
                
                horario_obj = Horario(
                    dia=horario_data['dia'],
                    hora_init=horario_data['hora_init'],
                    hora_fin=horario_data['hora_fin']
                )

                id_horario = guardar_horario(horario_obj)
                guardar_horario_clase(id_horario, self.clase_seleccionada_id)
            
            self.mostrar_exito(f"✅ Alumno inscrito en {self.clase_seleccionada_nombre} con {len(horarios_validos)} horario(s)")
            
            # Limpiar para poder inscribir en otra clase
            self.clase_seleccionada_id = None
            self.clase_seleccionada_nombre = ""
            self.dias_horarios.clear()
            self.dias_container.controls.clear()
            self.btn_inscribir.visible = False
            self.page.update()
            
        except Exception as ex:
            self.mostrar_error(f"Error al inscribir: {str(ex)}")
            import traceback
            traceback.print_exc()
    
    # ============================================
    # BUILD
    # ============================================
    def build(self):
        formulario = ft.Column(
            [
                ft.Text("INSCRIBIR ALUMNO A CLASES", size=26, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=20),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("1. BUSCAR ALUMNO", size=18, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(height=10),
                        ft.Row([self.busqueda_input, self.btn_buscar], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=10),
                        self.resultados_list,
                        ft.Container(height=10),
                        self.alumno_seleccionado_text,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#1565C0",
                    padding=20,
                    border_radius=10,
                    width=500,
                ),
                
                ft.Container(height=20),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("2. CLASES DISPONIBLES", size=18, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(height=10),
                        self.clases_container,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#1565C0",
                    padding=20,
                    border_radius=10,
                    width=500,
                ),
                
                ft.Container(height=20),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("3. DÍAS Y HORARIOS", size=18, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(height=10),
                        self.dias_container,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#1565C0",
                    padding=20,
                    border_radius=10,
                    width=500,
                ),
                
                ft.Container(height=20),
                
                self.btn_inscribir,
                ft.Container(height=10),
                self.btn_terminar,
                
                ft.Container(height=10),
                
                self.error_container,
                self.exito_container,
                
                ft.Container(height=10),
                
                self.btn_volver,
                
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
        )
        
        tarjeta = ft.Container(
            content=ft.Column([formulario], scroll=ft.ScrollMode.ALWAYS),
            bgcolor="#1E88E5",
            padding=40,
            border_radius=20,
            width=650,
            height=750,
        )
        
        return tarjeta