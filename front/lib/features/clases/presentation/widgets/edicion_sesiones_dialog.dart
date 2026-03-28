// lib/features/clases/presentation/widgets/edicion_sesiones_dialog.dart
import 'package:flutter/material.dart';
import '../../models/sesion_model.dart';
import '../../models/sesion_agrupada.dart'; // Asegúrate de que este import sea correcto para HorarioSesion


import '../../services/sesiones_service.dart'; // Asegúrate que la ruta sea correcta

class EditarSesionDialog extends StatefulWidget {
  final SesionModel sesion;
  final List<HorarioSesion> horariosIniciales;
  final VoidCallback onSave;

  const EditarSesionDialog({
    super.key,
    required this.sesion,
    required this.horariosIniciales,
    required this.onSave,
  });

  @override
  State<EditarSesionDialog> createState() => _EditarSesionDialogState();
}

class _EditarSesionDialogState extends State<EditarSesionDialog> {
  late List<HorarioItem> _horarios;
  late List<HorarioItem> _horariosOriginales; // Para comparar cambios
  final SesionService _sesionService = SesionService();
  bool _isSaving = false;
  
  final List<String> _dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
  final List<String> _horas = [
    '09:00', '10:00', '11:00', '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00'
  ];
  final List<String> _aulas = ['A', 'B', 'C', 'D'];

  String _normalizarHora(String hora) {
    if (hora.length > 5) {
      return hora.substring(0, 5);
    }
    return hora;
  }

  @override
  void initState() {
    super.initState();
    // MAPEAMOS TODOS LOS HORARIOS RECIBIDOS A LA LISTA EDITABLE
    _horarios = widget.horariosIniciales.map((h) => HorarioItem(
      id: h.sesionId,
      dia: h.dia,
      hora: _normalizarHora(h.hora),
      aula: h.aula,
    )).toList();
    
    // Guardamos una copia original para comparar después
    _horariosOriginales = widget.horariosIniciales.map((h) => HorarioItem(
      id: h.sesionId,
      dia: h.dia,
      hora: _normalizarHora(h.hora),
      aula: h.aula,
    )).toList();
  }

  // Función para verificar si hubo cambios
  bool _hayCambios() {
    if (_horarios.length != _horariosOriginales.length) return true;
    
    // Ordenamos ambas listas para comparar
    _horarios.sort((a, b) => a.dia.compareTo(b.dia));
    _horariosOriginales.sort((a, b) => a.dia.compareTo(b.dia));
    
    for (int i = 0; i < _horarios.length; i++) {
      if (_horarios[i].dia != _horariosOriginales[i].dia ||
          _horarios[i].hora != _horariosOriginales[i].hora ||
          _horarios[i].aula != _horariosOriginales[i].aula) {
        return true;
      }
    }
    return false;
  }

  void _agregarHorario() {
    setState(() {
      _horarios.add(HorarioItem(
        id: null,
        dia: 'Lunes',
        hora: '09:00',
        aula: 'A',
      ));
    });
  }

  void _eliminarHorario(int index) {
    setState(() {
      _horarios.removeAt(index);
    });
  }

  void _guardarCambios() async {
    // Validaciones
    if (_horarios.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Debe haber al menos un horario'), backgroundColor: Colors.orange),
      );
      return;
    }
    
    // Validar que todos los horarios tengan aula seleccionada
    final horariosSinAula = _horarios.where((h) => h.aula.isEmpty).toList();
    if (horariosSinAula.isNotEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Todos los horarios deben tener un aula seleccionada'), 
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }
    
    // Verificar si realmente hay cambios
    if (!_hayCambios()) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No hay cambios para guardar'), backgroundColor: Colors.grey),
        );
        Navigator.pop(context);
      }
      return;
    }
    
    // Mostrar loading
    setState(() {
      _isSaving = true;
    });
    
    try {
      // Convertir horarios al formato que espera la API
      final horariosParaGuardar = _horarios.map((h) => {
        'dia': h.dia,
        'hora': h.hora,
        'aula': h.aula.isNotEmpty ? h.aula : 'A', // Asegurar que nunca esté vacío
      }).toList();
      
      print('📝 Intentando guardar:');
      print('   Alumno ID: ${widget.sesion.alumnoId}');
      print('   Clase ID: ${widget.sesion.claseId}');
      print('   Horarios: $horariosParaGuardar');
      
      // Llamar al servicio
      final success = await _sesionService.guardarHorarios(
        widget.sesion.alumnoId,
        widget.sesion.claseId,
        horariosParaGuardar,
      );
      
      if (mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Horarios actualizados correctamente'), backgroundColor: Colors.green),
          );
          widget.onSave(); // Recargar datos
          Navigator.pop(context);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Error al guardar los horarios'), backgroundColor: Colors.red),
          );
        }
      }
    } catch (e) {
      print('❌ Error al guardar: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.all(12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        width: double.maxFinite,
        constraints: BoxConstraints(
          maxHeight: MediaQuery.of(context).size.height * 0.85,
        ),
        child: _isSaving
            ? const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text('Guardando cambios...'),
                    ],
                  ),
                ),
              )
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // HEADER FIJO
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.edit_calendar, color: Colors.blue.shade700),
                        const SizedBox(width: 8),
                        const Expanded(
                          child: Text('Editar Sesiones', 
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)
                          )
                        ),
                        IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(context)),
                      ],
                    ),
                  ),
                  
                  // CONTENIDO SCROLEABLE
                  Flexible(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          _buildInfoAlumno(),
                          const SizedBox(height: 20),
                          _buildHorariosHeader(),
                          const SizedBox(height: 12),
                          ..._horarios.asMap().entries.map((entry) => _buildHorarioEditor(entry.key, entry.value)).toList(),
                        ],
                      ),
                    ),
                  ),
                  
                  // BOTONES DE ACCIÓN FIJOS ABAJO
                  _buildActionButtons(),
                ],
              ),
      ),
    );
  }

  // ... (resto de los métodos _buildInfoAlumno, _buildHorariosHeader, etc. se mantienen igual)
  
  Widget _buildInfoAlumno() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(widget.sesion.alumnoNombre, 
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)
          ),
          Text('${widget.sesion.claseNombre} • ${widget.sesion.profesorNombre}',
            style: TextStyle(color: Colors.grey.shade700)
          ),
        ],
      ),
    );
  }

  Widget _buildHorariosHeader() {
    return Row(
      children: [
        Text('Horarios (${_horarios.length})', 
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)
        ),
        const Spacer(),
        TextButton.icon(
          onPressed: _agregarHorario, 
          icon: const Icon(Icons.add), 
          label: const Text('Agregar')
        ),
      ],
    );
  }

  Widget _buildHorarioEditor(int index, HorarioItem horario) {
    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _dias.contains(horario.dia) ? horario.dia : _dias.first,
                    items: _dias.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
                    onChanged: (v) => setState(() => horario.dia = v!),
                    decoration: const InputDecoration(labelText: 'Día', isDense: true, border: OutlineInputBorder()),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _horas.contains(horario.hora) ? horario.hora : _horas.first,
                    items: _horas.map((h) => DropdownMenuItem(value: h, child: Text(h))).toList(),
                    onChanged: (v) => setState(() => horario.hora = v!),
                    decoration: const InputDecoration(labelText: 'Hora', isDense: true, border: OutlineInputBorder()),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _aulas.contains(horario.aula) ? horario.aula : _aulas.first,
                    items: _aulas.map((a) => DropdownMenuItem(value: a, child: Text('Aula $a'))).toList(),
                    onChanged: (v) => setState(() => horario.aula = v!),
                    decoration: const InputDecoration(labelText: 'Aula', isDense: true, border: OutlineInputBorder()),
                  ),
                ),
                if (_horarios.length > 1) ...[
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.red),
                    onPressed: () => _eliminarHorario(index),
                  ),
                ]
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButtons() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () => Navigator.pop(context), 
              child: const Text('Cancelar')
            )
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ElevatedButton(
              onPressed: _guardarCambios, 
              style: ElevatedButton.styleFrom(backgroundColor: Colors.blue, foregroundColor: Colors.white),
              child: const Text('Guardar')
            )
          ),
        ],
      ),
    );
  }
}

class HorarioItem {
  int? id;
  String dia;
  String hora;
  String aula;

  HorarioItem({this.id, required this.dia, required this.hora, required this.aula});
}