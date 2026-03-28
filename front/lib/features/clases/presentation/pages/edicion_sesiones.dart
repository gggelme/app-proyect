// lib/features/clases/presentation/pages/editar_sesiones_page.dart
import 'package:flutter/material.dart';
import '../../services/sesiones_service.dart';
import '../../models/sesion_model.dart';
import '../widgets/edicion_sesiones_dialog.dart';
import '../../models/sesion_agrupada.dart';

class EditarSesionesPage extends StatefulWidget {
  const EditarSesionesPage({super.key});

  @override
  State<EditarSesionesPage> createState() => _EditarSesionesPageState();
}

class _EditarSesionesPageState extends State<EditarSesionesPage> {
  final SesionService _service = SesionService();
  List<AlumnoClaseAgrupado> _grupos = [];
  bool _cargando = true;

  @override
  void initState() {
    super.initState();
    _cargarSesiones();
  }

  Future<void> _cargarSesiones() async {
    setState(() {
      _cargando = true;
    });
    
    final grupos = await _service.obtenerTodasSesionesAgrupadas();
    
    setState(() {
      _grupos = grupos;
      _cargando = false;
    });
  }

  void _abrirEdicionSesion(AlumnoClaseAgrupado grupo) {
    if (grupo.horarios.isEmpty) return;
    
    final primerHorario = grupo.horarios.first;
    
    // Sesión base para datos del alumno/clase
    final sesionTemp = SesionModel(
      sesionId: primerHorario.sesionId,
      alumnoId: grupo.alumnoId,
      alumnoNombre: grupo.alumnoNombre,
      claseId: grupo.claseId,
      claseNombre: grupo.claseNombre,
      claseDuracion: grupo.claseDuracion,
      profesorId: grupo.profesorId,
      profesorNombre: grupo.profesorNombre,
      horarioId: primerHorario.horarioId,
      dia: primerHorario.dia,
      hora: primerHorario.hora,
      aula: primerHorario.aula,
      fechaInscripcion: primerHorario.fechaInscripcion,
    );
    
    showDialog(
      context: context,
      builder: (context) => EditarSesionDialog(
        sesion: sesionTemp,
        // ESTA ES LA PARTE CLAVE QUE CORRIGE EL ERROR
        horariosIniciales: grupo.horarios, 
        onSave: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✅ Cambios guardados'),
              backgroundColor: Colors.green,
            ),
          );
          _cargarSesiones();
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : _grupos.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.calendar_today, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'No hay sesiones registradas',
                        style: TextStyle(fontSize: 16, color: Colors.grey),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: _grupos.length,
                  itemBuilder: (context, index) {
                    final grupo = _grupos[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 16),
                      child: InkWell(
                        onTap: () => _abrirEdicionSesion(grupo),
                        borderRadius: BorderRadius.circular(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.blue.shade50,
                                borderRadius: const BorderRadius.only(
                                  topLeft: Radius.circular(12),
                                  topRight: Radius.circular(12),
                                ),
                              ),
                              child: Row(
                                children: [
                                  CircleAvatar(
                                    backgroundColor: Colors.blue.shade200,
                                    child: Text(
                                      grupo.alumnoNombre.isNotEmpty
                                          ? grupo.alumnoNombre[0].toUpperCase()
                                          : '?',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: Colors.blue.shade800,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          grupo.alumnoNombre,
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 16,
                                          ),
                                        ),
                                        Text(
                                          grupo.claseNombre,
                                          style: TextStyle(
                                            fontSize: 14,
                                            color: Colors.blue.shade700,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Text(
                                      '${grupo.horarios.length} horario${grupo.horarios.length != 1 ? 's' : ''}',
                                      style: TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.blue.shade700,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            ...grupo.horarios.map((horario) {
                              return Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  border: Border(
                                    bottom: BorderSide(
                                      color: Colors.grey.shade200,
                                    ),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    Icon(
                                      Icons.schedule,
                                      size: 16,
                                      color: Colors.grey.shade600,
                                    ),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Text(
                                        '${horario.dia} ${horario.hora}',
                                        style: const TextStyle(fontSize: 14),
                                      ),
                                    ),
                                    Icon(
                                      Icons.meeting_room,
                                      size: 16,
                                      color: Colors.grey.shade600,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      'Aula ${horario.aula}',
                                      style: TextStyle(
                                        fontSize: 14,
                                        color: Colors.grey.shade700,
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}