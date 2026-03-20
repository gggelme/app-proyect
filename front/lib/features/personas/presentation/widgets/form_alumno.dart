import 'package:flutter/material.dart';
import '../../services/personas_service.dart';
import '../../services/cuotas_service.dart';
import '../../services/inscripcion_service.dart';

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
  final _fechaNacController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _domicilioController = TextEditingController();
  final _descuentoController = TextEditingController();
  bool _isLoading = false;
  List<CuotaModel> _cuotas = [];
  Map<int, bool> _cuotasSeleccionadas = {};
  bool _cargandoCuotas = true;

  @override
  void initState() {
    super.initState();
    _cargarCuotas();
  }

  @override
  void dispose() {
    _dniController.dispose();
    _nombreController.dispose();
    _fechaNacController.dispose();
    _telefonoController.dispose();
    _domicilioController.dispose();
    _descuentoController.dispose();
    super.dispose();
  }

  Future<void> _cargarCuotas() async {
    try {
      final cuotas = await CuotasService.getCuotas();
      setState(() {
        _cuotas = cuotas;
        _cargandoCuotas = false;
        for (var cuota in cuotas) {
          _cuotasSeleccionadas[cuota.id] = false;
        }
      });
    } catch (e) {
      setState(() {
        _cargandoCuotas = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar cuotas: $e')),
        );
      }
    }
  }

  Future<void> _seleccionarFecha() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
      helpText: 'Seleccione fecha de nacimiento',
    );
    if (picked != null) {
      setState(() {
        _fechaNacController.text = picked.toIso8601String().split('T')[0];
      });
    }
  }

  Future<void> _guardarAlumno() async {
    if (!_formKey.currentState!.validate()) return;

    if (!_cuotasSeleccionadas.containsValue(true)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Debe seleccionar al menos una cuota')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final alumnoData = {
        'dni': _dniController.text,
        'nomb_apel': _nombreController.text,
        'fecha_nac': _fechaNacController.text.isEmpty ? null : _fechaNacController.text,
        'telefono': _telefonoController.text.isEmpty ? null : _telefonoController.text,
        'domicilio': _domicilioController.text.isEmpty ? null : _domicilioController.text,
        'fecha_ing': DateTime.now().toIso8601String().split('T')[0],
        'estado_activo': true,
      };

      print('📤 Enviando datos de alumno:');
      print(alumnoData);

      final idAlumno = await PersonasService.crearAlumno(alumnoData);
      
      if (idAlumno > 0) {
        final cuotasSeleccionadasIds = _cuotasSeleccionadas.entries
            .where((entry) => entry.value)
            .map((entry) => entry.key)
            .toList();
        
        final porcentajeDescuento = _descuentoController.text.isEmpty 
            ? 0.0 
            : double.parse(_descuentoController.text);
        
        final resultado = await InscripcionService.guardarInscripcionConCuotas(
          idAlumno: idAlumno,
          idsCuotas: cuotasSeleccionadasIds,
          porcentajeDescuento: porcentajeDescuento,
        );
        
        if (mounted) {
          final pagos = resultado['data']['pagos_generados'] as List;
          double totalAPagar = 0;
          for (var pago in pagos) {
            totalAPagar += pago['monto_final'];
          }
          
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('✅ Inscripción completada'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Alumno: ${_nombreController.text}'),
                  const SizedBox(height: 8),
                  const Text('Cuotas inscritas:'),
                  ...pagos.map((pago) => Padding(
                    padding: const EdgeInsets.only(left: 16, top: 4),
                    child: Text(
                      '• ${pago['nombre_cuota']}: '
                      '\$${pago['precio_original'].toStringAsFixed(2)} '
                      '→ \$${pago['monto_final'].toStringAsFixed(2)} '
                      '(${pago['descuento_porcentaje']}% desc)',
                    ),
                  )),
                  const Divider(),
                  Text(
                    'Total a pagar: \$${totalAPagar.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Mes: ${pagos[0]['mes_correspondiente']}',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Los pagos han sido generados como pendientes',
                    style: TextStyle(fontSize: 12, color: Colors.orange),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                    Navigator.pop(context);
                  },
                  child: const Text('Aceptar'),
                ),
              ],
            ),
          );
          
          widget.onAlumnoCreado();
        }
      } else {
        throw Exception('Error al crear alumno');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nuevo Alumno'),
        backgroundColor: const Color(0xFF87CEEB),
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
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
                    // Campo de fecha de nacimiento
                    GestureDetector(
                      onTap: _seleccionarFecha,
                      child: AbsorbPointer(
                        child: TextFormField(
                          controller: _fechaNacController,
                          decoration: const InputDecoration(
                            labelText: 'Fecha de Nacimiento',
                            hintText: 'Seleccionar fecha',
                            border: OutlineInputBorder(),
                            suffixIcon: Icon(Icons.calendar_today),
                          ),
                        ),
                      ),
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
                    
                    const Text(
                      'Cuotas a inscribir *',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    if (_cargandoCuotas)
                      const Center(
                        child: Padding(
                          padding: EdgeInsets.all(20.0),
                          child: CircularProgressIndicator(),
                        ),
                      )
                    else if (_cuotas.isEmpty)
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Center(
                          child: Text('No hay cuotas disponibles'),
                        ),
                      )
                    else
                      Container(
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: ListView.separated(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: _cuotas.length,
                          separatorBuilder: (context, index) => const Divider(),
                          itemBuilder: (context, index) {
                            final cuota = _cuotas[index];
                            return CheckboxListTile(
                              title: Text(cuota.nombre),
                              subtitle: Text(
                                '\$${cuota.precio.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  color: Colors.green,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              value: _cuotasSeleccionadas[cuota.id],
                              onChanged: (bool? value) {
                                setState(() {
                                  _cuotasSeleccionadas[cuota.id] = value ?? false;
                                });
                              },
                              activeColor: const Color(0xFF87CEEB),
                            );
                          },
                        ),
                      ),
                    
                    const SizedBox(height: 24),
                    
                    TextFormField(
                      controller: _descuentoController,
                      decoration: const InputDecoration(
                        labelText: 'Descuento (%)',
                        border: OutlineInputBorder(),
                        hintText: '0',
                        helperText: 'Aplica a todas las cuotas seleccionadas',
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        if (value != null && value.isNotEmpty) {
                          if (double.tryParse(value) == null) {
                            return 'Ingrese un número válido';
                          }
                          final descuento = double.parse(value);
                          if (descuento < 0 || descuento > 100) {
                            return 'El descuento debe estar entre 0 y 100';
                          }
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ),
          
          Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.3),
                  spreadRadius: 2,
                  blurRadius: 5,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: ElevatedButton(
              onPressed: _isLoading ? null : _guardarAlumno,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF87CEEB),
                padding: const EdgeInsets.symmetric(vertical: 16),
                minimumSize: const Size(double.infinity, 48),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text(
                      'Guardar Alumno',
                      style: TextStyle(fontSize: 16),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}