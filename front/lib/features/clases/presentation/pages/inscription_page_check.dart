// presentation/form/inscription.dart
import 'package:flutter/material.dart';
import '../../services/alumnos_service_check.dart';
import '../../services/clases_service_check.dart';
import '../../services/inscripcion_service_check.dart';
// import '../../models/clase_model.dart'; // ← Eliminar esta línea si no la usas
import '../../models/profesor_model_check.dart';

// Mover el enum fuera de la clase
enum TipoInscripcion { sesion, clase }

class InscriptionPage extends StatefulWidget {
  const InscriptionPage({super.key});

  @override
  State<InscriptionPage> createState() => _InscriptionPageState();
}

class _InscriptionPageState extends State<InscriptionPage> {
  final AlumnoService _alumnoService = AlumnoService();
  final ClasesService _claseService = ClasesService();
  final InscripcionService _inscripcionService = InscripcionService();
  
  // Tipo de inscripción
  TipoInscripcion? _tipoSeleccionado;
  
  // Alumnos (para sesión)
  final List<_AlumnoField> _alumnos = [];
  
  // Clase seleccionada (para sesión)
  List<Map<String, dynamic>> _clases = [];
  Map<String, dynamic>? _claseSeleccionada;
  bool _cargandoClases = true;
  
  // Horarios (para sesión)
  final List<_HorarioField> _horarios = [];
  final List<String> _dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
  final List<String> _aulas = ['A', 'B', 'C', 'D'];
  
  // Campos para crear nueva clase
  final TextEditingController _nombreClaseController = TextEditingController();
  ProfesorModel? _profesorSeleccionado;
  List<ProfesorModel> _profesores = [];
  List<ProfesorModel> _profesoresFiltrados = [];
  bool _cargandoProfesores = true;
  bool _buscandoProfesor = false;
  final TextEditingController _busquedaProfesorController = TextEditingController();
  
  int _duracionClase = 60;
  
  @override
  void initState() {
    super.initState();
    _agregarAlumno();
    _agregarHorario();
    _cargarClases();
    _cargarProfesores();
  }
  
  Future<void> _cargarClases() async {
    setState(() {
      _cargandoClases = true;
    });
    
    final clases = await _claseService.obtenerTodasClases();
    
    setState(() {
      _clases = clases;
      _cargandoClases = false;
    });
  }
  
  Future<void> _cargarProfesores() async {
    setState(() {
      _cargandoProfesores = true;
    });
    
    final profesores = await _claseService.obtenerTodosProfesores();
    
    setState(() {
      _profesores = profesores;
      _profesoresFiltrados = profesores;
      _cargandoProfesores = false;
    });
  }
  
  void _buscarProfesor(String query) {
    setState(() {
      _buscandoProfesor = true;
      if (query.isEmpty) {
        _profesoresFiltrados = _profesores;
      } else {
        _profesoresFiltrados = _profesores.where((profesor) =>
          profesor.nombApel.toLowerCase().contains(query.toLowerCase()) ||
          (profesor.alias?.toLowerCase().contains(query.toLowerCase()) ?? false)
        ).toList();
      }
      _buscandoProfesor = false;
    });
  }
  
  void _agregarAlumno() {
    setState(() {
      _alumnos.add(_AlumnoField());
    });
  }
  
  void _eliminarAlumno(int index) {
    setState(() {
      _alumnos[index].controller.dispose();
      _alumnos.removeAt(index);
    });
  }
  
  void _agregarHorario() {
    setState(() {
      _horarios.add(_HorarioField());
    });
  }
  
  void _eliminarHorario(int index) {
    setState(() {
      _horarios.removeAt(index);
    });
  }
  
  Future<void> _buscarAlumnos(String texto, _AlumnoField campo) async {
    if (texto.trim().isEmpty) {
      setState(() {
        campo.sugerencias = [];
        campo.existeEnBD = null;
      });
      return;
    }
    
    setState(() {
      campo.buscando = true;
    });
    
    final resultados = await _alumnoService.buscarAlumnosPorNombre(texto);
    
    setState(() {
      campo.sugerencias = resultados;
      campo.buscando = false;
      if (resultados.length == 1 && resultados[0]['nomb_apel'].toLowerCase() == texto.toLowerCase()) {
        campo.existeEnBD = true;
        campo.alumnoSeleccionado = resultados[0];
      } else {
        campo.existeEnBD = resultados.isNotEmpty;
      }
    });
  }
  
  @override
  void dispose() {
    for (var alumno in _alumnos) {
      alumno.controller.dispose();
    }
    _nombreClaseController.dispose();
    _busquedaProfesorController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nueva Inscripción'),
        backgroundColor: const Color(0xFF87CEEB),
        toolbarHeight: 50,
      ),
      body: Column(
        children: [
          /// BOTONES DE SELECCIÓN
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: _buildBotonSeleccion(
                    texto: 'Sesión',
                    tipo: TipoInscripcion.sesion,
                    icon: Icons.calendar_today,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildBotonSeleccion(
                    texto: 'Clase',
                    tipo: TipoInscripcion.clase,
                    icon: Icons.class_,
                  ),
                ),
              ],
            ),
          ),
          
          /// CONTENIDO PRINCIPAL
          Expanded(
            child: _tipoSeleccionado == null
                ? _buildMensajeSeleccion()
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(12),
                    child: _tipoSeleccionado == TipoInscripcion.sesion
                        ? _buildFormularioSesion()
                        : _buildFormularioClase(),
                  ),
          ),
          
          /// BOTÓN CONFIRMAR FIJO ABAJO
          if (_tipoSeleccionado != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _tipoSeleccionado == TipoInscripcion.sesion
                      ? _confirmarSesion
                      : _confirmarClase,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    backgroundColor: Colors.green,
                  ),
                  child: Text(
                    _tipoSeleccionado == TipoInscripcion.sesion
                        ? 'Confirmar Inscripción a Sesión'
                        : 'Guardar Clase',
                    style: const TextStyle(fontSize: 14),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
  
  Widget _buildBotonSeleccion({
    required String texto,
    required TipoInscripcion tipo,
    required IconData icon,
  }) {
    final isSelected = _tipoSeleccionado == tipo;
    
    return ElevatedButton(
      onPressed: () {
        setState(() {
          _tipoSeleccionado = tipo;
        });
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected ? Colors.blue : Colors.grey.shade300,
        foregroundColor: isSelected ? Colors.white : Colors.black87,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 18),
          const SizedBox(width: 8),
          Text(texto, style: const TextStyle(fontSize: 14)),
        ],
      ),
    );
  }
  
  Widget _buildMensajeSeleccion() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.info_outline,
            size: 48,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 12),
          Text(
            'Seleccionar inscripción',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Elija entre Sesión o Clase para continuar',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade500,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildFormularioSesion() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        /// SELECTOR DE CLASE
        Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(8),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<Map<String, dynamic>>(
              isExpanded: true,
              hint: const Text('Seleccionar clase'),
              value: _claseSeleccionada,
              items: _clases.map((clase) {
                return DropdownMenuItem(
                  value: clase,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        clase['nombre_clase'],
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                      Text(
                        '${clase['profesor']} - ${clase['duracion']} min',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                );
              }).toList(),
              onChanged: _cargandoClases
                  ? null
                  : (Map<String, dynamic>? nuevaClase) {
                      setState(() {
                        _claseSeleccionada = nuevaClase;
                      });
                    },
            ),
          ),
        ),
        
        /// HORARIOS
        const Text(
          'Horarios',
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 6),
        
        ..._horarios.asMap().entries.map((entry) {
          int index = entry.key;
          var horario = entry.value;
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: horario.diaSeleccionado,
                          decoration: const InputDecoration(
                            isDense: true,
                            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                            border: OutlineInputBorder(),
                            labelText: 'Día',
                            labelStyle: TextStyle(fontSize: 12),
                          ),
                          items: _dias.map((dia) {
                            return DropdownMenuItem(
                              value: dia,
                              child: Text(dia, style: const TextStyle(fontSize: 13)),
                            );
                          }).toList(),
                          onChanged: (value) {
                            setState(() {
                              horario.diaSeleccionado = value;
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.remove_circle, size: 24, color: Colors.red),
                        onPressed: () => _eliminarHorario(index),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: horario.horaController,
                          decoration: const InputDecoration(
                            isDense: true,
                            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                            hintText: 'HH:MM',
                            labelText: 'Hora',
                            labelStyle: TextStyle(fontSize: 12),
                            border: OutlineInputBorder(),
                          ),
                          style: const TextStyle(fontSize: 13),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: horario.aulaSeleccionada,
                          decoration: const InputDecoration(
                            isDense: true,
                            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                            border: OutlineInputBorder(),
                            labelText: 'Aula',
                            labelStyle: TextStyle(fontSize: 12),
                          ),
                          items: _aulas.map((aula) {
                            return DropdownMenuItem(
                              value: aula,
                              child: Text(aula, style: const TextStyle(fontSize: 13)),
                            );
                          }).toList(),
                          onChanged: (value) {
                            setState(() {
                              horario.aulaSeleccionada = value;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        }).toList(),
        
        SizedBox(
          width: double.infinity,
          child: TextButton.icon(
            onPressed: _agregarHorario,
            icon: const Icon(Icons.add, size: 16),
            label: const Text('Agregar horario', style: TextStyle(fontSize: 12)),
            style: TextButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 8),
              minimumSize: const Size(0, 36),
            ),
          ),
        ),
        
        const Divider(height: 24),
        
        /// ALUMNOS
        const Text(
          'Alumnos',
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 6),
        
        ..._alumnos.asMap().entries.map((entry) {
          int index = entry.key;
          var campo = entry.value;
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: TextField(
                        controller: campo.controller,
                        decoration: InputDecoration(
                          isDense: true,
                          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                          border: const OutlineInputBorder(),
                          hintText: 'Nombre del alumno',
                          hintStyle: const TextStyle(fontSize: 12),
                          suffixIcon: campo.buscando
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : (campo.existeEnBD != null && campo.controller.text.isNotEmpty
                                  ? Icon(
                                      campo.existeEnBD! 
                                          ? Icons.check_circle 
                                          : Icons.cancel,
                                      color: campo.existeEnBD! 
                                          ? Colors.green 
                                          : Colors.red,
                                      size: 18,
                                    )
                                  : null),
                        ),
                        style: const TextStyle(fontSize: 13),
                        onChanged: (value) {
                          _buscarAlumnos(value, campo);
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.remove_circle, size: 24, color: Colors.red),
                      onPressed: () => _eliminarAlumno(index),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
                if (campo.sugerencias.isNotEmpty)
                  Container(
                    margin: const EdgeInsets.only(top: 4),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: campo.sugerencias.length > 3 ? 3 : campo.sugerencias.length,
                      itemBuilder: (context, sugerenciaIndex) {
                        final alumno = campo.sugerencias[sugerenciaIndex];
                        return ListTile(
                          dense: true,
                          leading: const Icon(Icons.person, size: 14),
                          title: Text(
                            alumno['nomb_apel'],
                            style: const TextStyle(fontSize: 12),
                          ),
                          subtitle: Text(
                            'DNI: ${alumno['dni']}',
                            style: const TextStyle(fontSize: 10),
                          ),
                          onTap: () {
                            setState(() {
                              campo.controller.text = alumno['nomb_apel'];
                              campo.alumnoSeleccionado = alumno;
                              campo.existeEnBD = true;
                              campo.sugerencias = [];
                            });
                          },
                        );
                      },
                    ),
                  ),
              ],
            ),
          );
        }).toList(),
        
        SizedBox(
          width: double.infinity,
          child: TextButton.icon(
            onPressed: _agregarAlumno,
            icon: const Icon(Icons.add, size: 16),
            label: const Text('Agregar alumno', style: TextStyle(fontSize: 12)),
            style: TextButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 8),
              minimumSize: const Size(0, 36),
            ),
          ),
        ),
        
        const SizedBox(height: 16),
      ],
    );
  }
  
  Widget _buildFormularioClase() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        /// NOMBRE DE LA CLASE
        TextField(
          controller: _nombreClaseController,
          decoration: const InputDecoration(
            labelText: 'Nombre de la clase',
            hintText: 'Ej: Yoga Avanzado',
            border: OutlineInputBorder(),
            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
          ),
          style: const TextStyle(fontSize: 14),
        ),
        
        const SizedBox(height: 16),
        
        /// SELECCIONAR PROFESOR
        const Text(
          'Profesor',
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        
        if (_cargandoProfesores)
          const Center(child: CircularProgressIndicator())
        else
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TextField(
                controller: _busquedaProfesorController,
                decoration: InputDecoration(
                  labelText: 'Buscar profesor',
                  hintText: 'Escriba el nombre del profesor',
                  border: const OutlineInputBorder(),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                  suffixIcon: _buscandoProfesor
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : (_profesorSeleccionado != null
                          ? IconButton(
                              icon: const Icon(Icons.clear, size: 18),
                              onPressed: () {
                                setState(() {
                                  _profesorSeleccionado = null;
                                  _busquedaProfesorController.clear();
                                  _profesoresFiltrados = _profesores;
                                });
                              },
                            )
                          : null),
                ),
                style: const TextStyle(fontSize: 14),
                onChanged: _buscarProfesor,
              ),
              
              const SizedBox(height: 8),
              
              if (_profesorSeleccionado != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    border: Border.all(color: Colors.green.shade200),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.person, color: Colors.green, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _profesorSeleccionado!.nombApel,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                            if (_profesorSeleccionado!.alias != null)
                              Text(
                                _profesorSeleccionado!.alias!,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              
              if (_profesorSeleccionado == null && _profesoresFiltrados.isNotEmpty)
                Container(
                  margin: const EdgeInsets.only(top: 8),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _profesoresFiltrados.length > 5 ? 5 : _profesoresFiltrados.length,
                    itemBuilder: (context, index) {
                      final profesor = _profesoresFiltrados[index];
                      return ListTile(
                        dense: true,
                        leading: const Icon(Icons.person, size: 16),
                        title: Text(
                          profesor.nombApel,
                          style: const TextStyle(fontSize: 13),
                        ),
                        subtitle: profesor.alias != null
                            ? Text(
                                profesor.alias!,
                                style: const TextStyle(fontSize: 11),
                              )
                            : null,
                        onTap: () {
                          setState(() {
                            _profesorSeleccionado = profesor;
                            _busquedaProfesorController.text = profesor.nombApel;
                            _profesoresFiltrados = _profesores;
                          });
                        },
                      );
                    },
                  ),
                ),
              
              if (_profesorSeleccionado == null && _profesoresFiltrados.isEmpty && _busquedaProfesorController.text.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    'No se encontraron profesores',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ),
            ],
          ),
        
        const SizedBox(height: 16),
        
        /// DURACIÓN DE LA CLASE
        const Text(
          'Duración (minutos)',
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(8),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<int>(
              isExpanded: true,
              value: _duracionClase,
              items: const [
                DropdownMenuItem(value: 30, child: Text('30 minutos')),
                DropdownMenuItem(value: 45, child: Text('45 minutos')),
                DropdownMenuItem(value: 60, child: Text('60 minutos')),
                DropdownMenuItem(value: 75, child: Text('75 minutos')),
                DropdownMenuItem(value: 90, child: Text('90 minutos')),
                DropdownMenuItem(value: 120, child: Text('120 minutos')),
              ],
              onChanged: (value) {
                setState(() {
                  _duracionClase = value ?? 60;
                });
              },
            ),
          ),
        ),
        
        const SizedBox(height: 24),
      ],
    );
  }
  
  Future<void> _confirmarSesion() async {
    // Validar que haya clase seleccionada
    if (_claseSeleccionada == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Seleccioná una clase'), backgroundColor: Colors.orange),
      );
      return;
    }
    
    // Validar que haya al menos un horario con datos completos
    final horariosValidos = _horarios.where((h) => 
      h.diaSeleccionado != null && 
      h.horaController.text.isNotEmpty && 
      h.aulaSeleccionada != null
    ).toList();
    
    if (horariosValidos.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Agregá al menos un horario válido'), backgroundColor: Colors.orange),
      );
      return;
    }
    
    // Validar que haya al menos un alumno con nombre seleccionado
    final alumnosValidos = _alumnos.where((a) => 
      a.controller.text.isNotEmpty && a.alumnoSeleccionado != null
    ).toList();
    
    if (alumnosValidos.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Agregá al menos un alumno válido'), backgroundColor: Colors.orange),
      );
      return;
    }
    
    // Preparar datos de horarios
    final horariosData = horariosValidos.map((h) => {
      'dia': h.diaSeleccionado,
      'hora': h.horaController.text,
      'aula': h.aulaSeleccionada,
    }).toList();
    
    // Preparar datos de alumnos
    final alumnosData = alumnosValidos.map((a) {
      final alumno = a.alumnoSeleccionado!;
      int idAlumno = alumno['alumno_id'] ?? alumno['id'];
      
      return {
        'id_alumno': idAlumno,
      };
    }).toList();
    
    // Mostrar diálogo de carga
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );
    
    // Llamar al servicio
    final resultado = await _inscripcionService.crearInscripcion(
      idClase: _claseSeleccionada!['id'],
      horarios: horariosData,
      alumnos: alumnosData,
    );
    
    // Cerrar diálogo
    Navigator.pop(context);
    
    if (resultado['status'] == 'success') {
      // Éxito
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(resultado['message']), backgroundColor: Colors.green),
      );
      
      // Limpiar formulario después de guardar
      setState(() {
        _claseSeleccionada = null;
        _horarios.clear();
        _alumnos.clear();
        _agregarHorario();
        _agregarAlumno();
      });
    } else {
      // Error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(resultado['message']), backgroundColor: Colors.red),
      );
    }
  }
  
  Future<void> _confirmarClase() async {
    // Validaciones
    if (_nombreClaseController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ingrese el nombre de la clase'), backgroundColor: Colors.orange),
      );
      return;
    }
    
    if (_profesorSeleccionado == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Seleccione un profesor'), backgroundColor: Colors.orange),
      );
      return;
    }
    
    // Mostrar diálogo de carga
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );
    
    // Llamar al servicio con 3 parámetros
    final resultado = await _claseService.crearClase(
      _nombreClaseController.text.trim(),
      _profesorSeleccionado!.id,
      _duracionClase,
    );
    
    // Cerrar diálogo
    Navigator.pop(context);
    
    if (resultado['status'] == 'success') {
      // Éxito
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Clase creada exitosamente'), backgroundColor: Colors.green),
      );
      
      // Limpiar formulario
      setState(() {
        _nombreClaseController.clear();
        _profesorSeleccionado = null;
        _busquedaProfesorController.clear();
        _profesoresFiltrados = _profesores;
        _duracionClase = 60;
        
        // Recargar lista de clases para el formulario de sesión
        _cargarClases();
      });
    } else {
      // Error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(resultado['message'] ?? 'Error al crear la clase'), backgroundColor: Colors.red),
      );
    }
  }
}

// Clase auxiliar para alumnos
class _AlumnoField {
  final TextEditingController controller;
  List<Map<String, dynamic>> sugerencias;
  Map<String, dynamic>? alumnoSeleccionado;
  bool? existeEnBD;
  bool buscando;
  
  _AlumnoField()
      : controller = TextEditingController(),
        sugerencias = [],
        alumnoSeleccionado = null,
        existeEnBD = null,
        buscando = false;
}

// Clase auxiliar para horarios
class _HorarioField {
  String? diaSeleccionado;
  final TextEditingController horaController;
  String? aulaSeleccionada;
  
  _HorarioField()
      : horaController = TextEditingController(),
        diaSeleccionado = null,
        aulaSeleccionada = null;
}