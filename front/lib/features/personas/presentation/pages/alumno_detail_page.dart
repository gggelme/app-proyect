import 'package:flutter/material.dart';
import '../../models/persona_model.dart';
import '../../models/cuota_alumno_model.dart';
import '../../models/cuota_model.dart';
import '../../services/personas_service.dart';

class AlumnoDetailPage extends StatefulWidget {
  final AlumnoModel alumno;
  final VoidCallback onAlumnoActualizado;

  const AlumnoDetailPage({
    super.key,
    required this.alumno,
    required this.onAlumnoActualizado,
  });

  @override
  State<AlumnoDetailPage> createState() => _AlumnoDetailPageState();
}

class _AlumnoDetailPageState extends State<AlumnoDetailPage> {
  List<CuotaAlumnoModel> _cuotas = [];
  bool _cargandoCuotas = true;
  bool _isEditing = false;
  bool _isSaving = false;
  
  // Variables para la edición de cuotas
  List<CuotaModel> _todasCuotas = [];
  List<int> _cuotasSeleccionadas = [];
  bool _cargandoCuotasDisponibles = false;
  
  // Controladores para los campos
  late TextEditingController _nombreController;
  late TextEditingController _dniController;
  late TextEditingController _telefonoController;
  late TextEditingController _domicilioController;
  late TextEditingController _fechaNacController;
  late TextEditingController _fechaIngController;
  
  String? _estadoActivo;

  @override
  void initState() {
    super.initState();
    _cargarCuotas();
    _inicializarControladores();
    _cargarTodasCuotas();
  }
  
  void _inicializarControladores() {
    _nombreController = TextEditingController(text: widget.alumno.nombApel);
    _dniController = TextEditingController(text: widget.alumno.dni);
    _telefonoController = TextEditingController(text: widget.alumno.telefono ?? '');
    _domicilioController = TextEditingController(text: widget.alumno.domicilio ?? '');
    _fechaNacController = TextEditingController(text: widget.alumno.fechaNac ?? '');
    _fechaIngController = TextEditingController(text: widget.alumno.fechaIng ?? '');
    _estadoActivo = widget.alumno.estadoActivo ? 'Activo' : 'Inactivo';
  }

  void _inicializarCuotasSeleccionadas() {
    _cuotasSeleccionadas = _cuotas.map((c) => c.idCuota).toList();
  }
  
  @override
  void dispose() {
    _nombreController.dispose();
    _dniController.dispose();
    _telefonoController.dispose();
    _domicilioController.dispose();
    _fechaNacController.dispose();
    _fechaIngController.dispose();
    super.dispose();
  }

  Future<void> _cargarCuotas() async {
    setState(() => _cargandoCuotas = true);
    final cuotas = await PersonasService.getCuotasByAlumno(widget.alumno.id);
    setState(() {
      _cuotas = cuotas;
      _cargandoCuotas = false;
      _inicializarCuotasSeleccionadas();
    });
  }

  Future<void> _cargarTodasCuotas() async {
    setState(() => _cargandoCuotasDisponibles = true);
    final cuotas = await PersonasService.getTodasCuotas();
    setState(() {
      _todasCuotas = cuotas;
      _cargandoCuotasDisponibles = false;
    });
  }

  void _toggleCuotaSeleccionada(int idCuota) {
    setState(() {
      if (_cuotasSeleccionadas.contains(idCuota)) {
        _cuotasSeleccionadas.remove(idCuota);
      } else {
        _cuotasSeleccionadas.add(idCuota);
      }
    });
  }

  String _calcularEdad(String? fechaNac) {
    if (fechaNac == null || fechaNac.isEmpty) return 'No disponible';
    
    try {
      final fecha = DateTime.parse(fechaNac);
      final hoy = DateTime.now();
      int edad = hoy.year - fecha.year;
      if (hoy.month < fecha.month || (hoy.month == fecha.month && hoy.day < fecha.day)) {
        edad--;
      }
      return edad.toString();
    } catch (e) {
      return 'No disponible';
    }
  }

  String _formatearFecha(String? fecha) {
    if (fecha == null || fecha.isEmpty) return 'No disponible';
    
    try {
      final fechaDate = DateTime.parse(fecha);
      return '${fechaDate.day}/${fechaDate.month}/${fechaDate.year}';
    } catch (e) {
      return fecha;
    }
  }

  String _formatearCumpleanos(String? fechaNac) {
    if (fechaNac == null || fechaNac.isEmpty) return 'No disponible';
    
    try {
      final fecha = DateTime.parse(fechaNac);
      return '${fecha.day}/${fecha.month}';
    } catch (e) {
      return 'No disponible';
    }
  }

  String _formatearFechaCorta(String? fecha) {
    if (fecha == null || fecha.isEmpty) return '';
    try {
      final fechaDate = DateTime.parse(fecha);
      return '${fechaDate.day}/${fechaDate.month}';
    } catch (e) {
      return '';
    }
  }
  
  Future<void> _guardarCambios() async {
    setState(() => _isSaving = true);
    
    final alumnoData = <String, dynamic>{
      'nomb_apel': _nombreController.text,
      'fecha_nac': _fechaNacController.text.isEmpty ? null : _fechaNacController.text,
      'domicilio': _domicilioController.text.isEmpty ? null : _domicilioController.text,
      'telefono': _telefonoController.text.isEmpty ? null : _telefonoController.text,
      'fecha_ing': _fechaIngController.text.isEmpty ? null : _fechaIngController.text,
      'estado_activo': _estadoActivo == 'Activo',
    };
    
    // Solo incluir DNI si cambió respecto al original
    if (_dniController.text != widget.alumno.dni) {
      alumnoData['dni'] = _dniController.text;
    }
    
    // 1. Actualizar datos personales
    final successAlumno = await PersonasService.actualizarAlumno(widget.alumno.id, alumnoData);
    
    // 2. Actualizar cuotas
    final successCuotas = await PersonasService.actualizarCuotasAlumno(
      widget.alumno.id, 
      _cuotasSeleccionadas
    );
    
    setState(() => _isSaving = false);
    
    if (successAlumno && successCuotas) {
      widget.onAlumnoActualizado();
      setState(() {
        _isEditing = false;
        // Actualizar el objeto alumno con los nuevos datos
        widget.alumno.nombApel = _nombreController.text;
        if (alumnoData.containsKey('dni')) {
          widget.alumno.dni = _dniController.text;
        }
        widget.alumno.telefono = _telefonoController.text.isEmpty ? null : _telefonoController.text;
        widget.alumno.domicilio = _domicilioController.text.isEmpty ? null : _domicilioController.text;
        widget.alumno.fechaNac = _fechaNacController.text.isEmpty ? null : _fechaNacController.text;
        widget.alumno.fechaIng = _fechaIngController.text.isEmpty ? null : _fechaIngController.text;
        widget.alumno.estadoActivo = _estadoActivo == 'Activo';
      });
      
      // Recargar cuotas para mostrar los cambios
      _cargarCuotas();
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Alumno y cuotas actualizados correctamente')),
      );
    } else {
      String errorMsg = '';
      if (!successAlumno) errorMsg = 'Error al actualizar datos personales';
      if (!successCuotas) errorMsg = errorMsg.isEmpty ? 'Error al actualizar cuotas' : '$errorMsg y cuotas';
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(errorMsg), backgroundColor: Colors.red),
      );
    }
  }
  
  void _cancelarEdicion() {
    setState(() {
      _isEditing = false;
      _inicializarControladores();
      _inicializarCuotasSeleccionadas();
    });
  }

  void _iniciarEdicion() {
    _inicializarCuotasSeleccionadas();
    setState(() {
      _isEditing = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Editar Alumno' : 'Detalle de Alumno'),
        backgroundColor: const Color(0xFF87CEEB),
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Información Personal',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const Divider(),
                        const SizedBox(height: 10),
                        
                        // Nombre y Apellido
                        if (_isEditing)
                          _buildEditField('Nombre y Apellido:', _nombreController)
                        else
                          _buildInfoRow('Nombre y Apellido: ', widget.alumno.nombApel),
                        
                        // DNI
                        if (_isEditing)
                          _buildEditField('DNI:', _dniController)
                        else
                          _buildInfoRow('DNI: ', widget.alumno.dni),
                        
                        // Teléfono
                        if (_isEditing)
                          _buildEditField('Teléfono:', _telefonoController)
                        else if (widget.alumno.telefono != null && widget.alumno.telefono!.isNotEmpty)
                          _buildInfoRow('Teléfono: ', widget.alumno.telefono!),
                        
                        // Domicilio
                        if (_isEditing)
                          _buildEditField('Domicilio:', _domicilioController)
                        else
                          _buildInfoRow(
                            'Domicilio: ', 
                            widget.alumno.domicilio != null && widget.alumno.domicilio!.isNotEmpty 
                                ? widget.alumno.domicilio! 
                                : 'No disponible'
                          ),
                        
                        // Fecha de Nacimiento
                        if (_isEditing)
                          _buildEditField('Fecha de Nacimiento (YYYY-MM-DD):', _fechaNacController)
                        else
                          _buildInfoRow('Fecha de Nacimiento: ', _formatearFecha(widget.alumno.fechaNac)),
                        
                        // Edad (siempre solo lectura)
                        _buildInfoRow('Edad: ', _calcularEdad(_isEditing ? _fechaNacController.text : widget.alumno.fechaNac)),
                        
                        // Cumpleaños (siempre solo lectura)
                        _buildInfoRow('Cumpleaños: ', _formatearCumpleanos(_isEditing ? _fechaNacController.text : widget.alumno.fechaNac)),
                        
                        // Fecha de Ingreso
                        if (_isEditing)
                          _buildEditField('Fecha de Ingreso (YYYY-MM-DD):', _fechaIngController)
                        else
                          _buildInfoRow('Fecha de Ingreso: ', _formatearFecha(widget.alumno.fechaIng)),
                        
                        // Estado
                        if (_isEditing)
                          _buildDropdownField('Estado: ', _estadoActivo!, (value) {
                            setState(() {
                              _estadoActivo = value;
                            });
                          })
                        else
                          _buildInfoRow(
                            'Estado: ',
                            widget.alumno.estadoActivo ? 'Activo' : 'Inactivo',
                            valueColor: widget.alumno.estadoActivo ? Colors.green : Colors.red,
                          ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Cuotas',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const Divider(),
                        if (_cargandoCuotasDisponibles || _cargandoCuotas)
                          const Padding(
                            padding: EdgeInsets.all(20),
                            child: Center(child: CircularProgressIndicator()),
                          )
                        else if (_isEditing)
                          // Modo edición: mostrar todas las cuotas con checkboxes
                          Column(
                            children: [
                              const Text(
                                'Selecciona las cuotas que paga el alumno:',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              const SizedBox(height: 16),
                              ..._todasCuotas.map((cuota) => _buildCuotaCheckbox(cuota)),
                            ],
                          )
                        else if (_cuotas.isEmpty)
                          const Center(
                            child: Padding(
                              padding: EdgeInsets.all(20),
                              child: Text(
                                'No tiene cuotas asociadas',
                                style: TextStyle(color: Colors.grey),
                              ),
                            ),
                          )
                        else
                          ..._cuotas.map((cuota) => _buildCuotaCard(cuota)),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  offset: const Offset(0, -2),
                  blurRadius: 4,
                  color: Colors.black.withOpacity(0.05),
                ),
              ],
            ),
            child: Row(
              children: _isEditing
                  ? [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isSaving ? null : _guardarCambios,
                          icon: _isSaving
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.save),
                          label: const Text('GUARDAR'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _cancelarEdicion,
                          icon: const Icon(Icons.cancel),
                          label: const Text('CANCELAR'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.grey,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                        ),
                      ),
                    ]
                  : [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _iniciarEdicion,
                          icon: const Icon(Icons.edit),
                          label: const Text('EDITAR'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF87CEEB),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            // Lógica de eliminar después
                          },
                          icon: const Icon(Icons.delete),
                          label: const Text('ELIMINAR'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                        ),
                      ),
                    ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCuotaCheckbox(CuotaModel cuota) {
    final isSelected = _cuotasSeleccionadas.contains(cuota.id);
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        border: Border.all(
          color: isSelected ? const Color(0xFF87CEEB) : Colors.grey.shade300,
        ),
        borderRadius: BorderRadius.circular(8),
      ),
      child: CheckboxListTile(
        value: isSelected,
        onChanged: (_) => _toggleCuotaSeleccionada(cuota.id),
        title: Text(
          cuota.nombre,
          style: const TextStyle(
            fontWeight: FontWeight.w500,
          ),
        ),
        subtitle: Text(
          '\$${cuota.precio.toStringAsFixed(2)}',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
        activeColor: const Color(0xFF87CEEB),
        checkboxShape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.grey,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: valueColor,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildEditField(String label, TextEditingController controller) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.grey,
              ),
            ),
          ),
          Expanded(
            child: TextField(
              controller: controller,
              decoration: InputDecoration(
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildDropdownField(String label, String value, ValueChanged<String> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.grey,
              ),
            ),
          ),
          Expanded(
            child: DropdownButtonFormField<String>(
              value: value,
              decoration: InputDecoration(
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              items: const [
                DropdownMenuItem(value: 'Activo', child: Text('Activo')),
                DropdownMenuItem(value: 'Inactivo', child: Text('Inactivo')),
              ],
              onChanged: (newValue) {
                if (newValue != null) {
                  onChanged(newValue);
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCuotaCard(CuotaAlumnoModel cuota) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF87CEEB).withOpacity(0.1),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    cuota.nombre,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '\$${cuota.precioBase.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF87CEEB),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (cuota.pagos.isEmpty)
                  const Text(
                    'Sin pagos registrados',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey,
                    ),
                  )
                else
                  ...cuota.pagos.map((pago) => _buildPagoRow(pago)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPagoRow(PagoCuotaModel pago) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(
            pago.estaPagado ? Icons.check_circle : Icons.pending,
            size: 16,
            color: pago.estaPagado ? Colors.green : Colors.orange,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              pago.mesFormateado,
              style: const TextStyle(fontSize: 13),
            ),
          ),
          Text(
            pago.estaPagado ? 'Pagado' : 'Pendiente',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w500,
              color: pago.estaPagado ? Colors.green : Colors.grey.shade600,
            ),
          ),
          if (pago.estaPagado && pago.fechaPago != null) ...[
            const SizedBox(width: 8),
            Text(
              _formatearFechaCorta(pago.fechaPago),
              style: const TextStyle(
                fontSize: 11,
                color: Colors.grey,
              ),
            ),
          ],
        ],
      ),
    );
  }
}