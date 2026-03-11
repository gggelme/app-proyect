import 'package:flutter/material.dart';
import '../../models/persona_model.dart';
import '../../services/personas_service.dart';

class FormAlumno extends StatefulWidget {
  final Function() onAlumnoCreado;

  const FormAlumno({super.key, required this.onAlumnoCreado});

  @override
  State<FormAlumno> createState() => _FormAlumnoState();
}

class _FormAlumnoState extends State<FormAlumno> {
  final _formKey = GlobalKey<FormState>();
  final _dniController = TextEditingController();
  final _nombreController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _domicilioController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _dniController.dispose();
    _nombreController.dispose();
    _telefonoController.dispose();
    _domicilioController.dispose();
    super.dispose();
  }

  Future<void> _guardarAlumno() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final alumnoData = {
        'dni': _dniController.text,
        'nomb_apel': _nombreController.text,
        'telefono': _telefonoController.text.isEmpty ? null : _telefonoController.text,
        'domicilio': _domicilioController.text.isEmpty ? null : _domicilioController.text,
        'fecha_ing': DateTime.now().toIso8601String().split('T')[0], // Fecha actual
        'estado_activo': true,
      };

      final id = await PersonasService.crearAlumno(alumnoData);
      
      if (id > 0) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Alumno creado correctamente')),
        );
        widget.onAlumnoCreado();
        Navigator.pop(context);
      } else {
        throw Exception('Error al crear alumno');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nuevo Alumno'),
        backgroundColor: const Color(0xFF87CEEB),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                controller: _dniController,
                decoration: const InputDecoration(
                  labelText: 'DNI *',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'El DNI es obligatorio';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _nombreController,
                decoration: const InputDecoration(
                  labelText: 'Nombre y Apellido *',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'El nombre es obligatorio';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _telefonoController,
                decoration: const InputDecoration(
                  labelText: 'Teléfono',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _domicilioController,
                decoration: const InputDecoration(
                  labelText: 'Domicilio',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _guardarAlumno,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF87CEEB),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Guardar Alumno',
                        style: TextStyle(fontSize: 16),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}