// lib/features/clases/presentation/pages/editar_clases_page.dart
import 'package:flutter/material.dart';
import '../../services/clases_edicion_service.dart';
import '../../models/clase_edicion_model.dart';

class EditarClasesPage extends StatefulWidget {
  const EditarClasesPage({super.key});

  @override
  State<EditarClasesPage> createState() => _EditarClasesPageState();
}

class _EditarClasesPageState extends State<EditarClasesPage> {
  final ClaseEdicionService _service = ClaseEdicionService();
  List<ClaseEdicion> _clases = [];
  bool _cargando = true;

  @override
  void initState() {
    super.initState();
    _cargarClases();
  }

  Future<void> _cargarClases() async {
    setState(() {
      _cargando = true;
    });
    
    final clases = await _service.obtenerTodasClases();
    
    setState(() {
      _clases = clases;
      _cargando = false;
    });
  }

  void _abrirDialogoEdicion(ClaseEdicion clase) {
    final nombreController = TextEditingController(text: clase.nombreClase);
    final duracionController = TextEditingController(text: clase.duracion.toString());
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Editar Clase'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nombreController,
              decoration: const InputDecoration(
                labelText: 'Nombre de la clase',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: duracionController,
              decoration: const InputDecoration(
                labelText: 'Duración (minutos)',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () async {
              final nuevoNombre = nombreController.text.trim();
              final nuevaDuracion = int.tryParse(duracionController.text.trim());
              
              if (nuevoNombre.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('El nombre no puede estar vacío')),
                );
                return;
              }
              
              if (nuevaDuracion == null || nuevaDuracion <= 0) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Duración inválida')),
                );
                return;
              }
              
              final resultado = await _service.actualizarClase(
                clase.id,
                nuevoNombre,
                nuevaDuracion,
              );
              
              Navigator.pop(context);
              
              if (resultado) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('✅ Clase actualizada'), backgroundColor: Colors.green),
                );
                _cargarClases();
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('❌ Error al actualizar'), backgroundColor: Colors.red),
                );
              }
            },
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
  }

  void _confirmarEliminacion(ClaseEdicion clase) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('⚠️ Eliminar Clase'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('¿Estás seguro de eliminar la clase "${clase.nombreClase}"?'),
            const SizedBox(height: 12),
            Text(
              '⚠️ Esta acción:',
              style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red.shade700),
            ),
            const SizedBox(height: 8),
            Text('• Eliminará la clase permanentemente'),
            Text('• Eliminará ${clase.cantidadInscripciones} inscripciones asociadas'),
            const Text('• No se puede deshacer'),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red.shade200),
              ),
              child: Text(
                'ADVERTENCIA: Los cambios afectarán a todos los alumnos inscritos en esta clase.',
                style: TextStyle(color: Colors.red.shade800, fontSize: 12),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              
              final confirmado = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Confirmación Final'),
                  content: const Text('¿Estás ABSOLUTAMENTE seguro de eliminar esta clase? Esta acción es irreversible.'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: const Text('No'),
                    ),
                    ElevatedButton(
                      onPressed: () => Navigator.pop(context, true),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                      child: const Text('Sí, eliminar', style: TextStyle(color: Colors.white)),
                    ),
                  ],
                ),
              );
              
              if (confirmado == true) {
                final resultado = await _service.eliminarClase(clase.id);
                
                if (resultado['success'] == true) {
                  // ACTUALIZACIÓN AUTOMÁTICA EN PANTALLA
                  setState(() {
                    _clases.removeWhere((item) => item.id == clase.id);
                  });

                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(resultado['message'] ?? 'Clase eliminada'),
                      backgroundColor: Colors.green,
                    ),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(resultado['message'] ?? 'Error al eliminar'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Eliminar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Se quitó el AppBar y el color celeste
      body: SafeArea( // SafeArea evita que el contenido se tape con el notch o la hora
        child: _cargando
            ? const Center(child: CircularProgressIndicator())
            : _clases.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.class_, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text(
                          'No hay clases registradas',
                          style: TextStyle(fontSize: 16, color: Colors.grey),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: _clases.length,
                    itemBuilder: (context, index) {
                      final clase = _clases[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(12),
                          title: Text(
                            clase.nombreClase,
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 4),
                              Text('Profesor: ${clase.profesorNombre}'),
                              Text('Duración: ${clase.duracion} minutos'),
                              Text(
                                'Inscripciones: ${clase.cantidadInscripciones}',
                                style: TextStyle(
                                  color: clase.cantidadInscripciones > 0 
                                      ? Colors.orange.shade700 
                                      : Colors.grey,
                                ),
                              ),
                            ],
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.edit, color: Colors.blue),
                                onPressed: () => _abrirDialogoEdicion(clase),
                                tooltip: 'Editar clase',
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete, color: Colors.red),
                                onPressed: () => _confirmarEliminacion(clase),
                                tooltip: 'Eliminar clase',
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}