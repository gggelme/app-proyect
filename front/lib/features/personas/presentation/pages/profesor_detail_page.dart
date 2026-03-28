import 'package:flutter/material.dart';
import '../../models/persona_model.dart';
import '../../services/personas_service.dart';

class ProfesorDetailPage extends StatefulWidget {
  final ProfesorModel profesor;
  final VoidCallback onProfesorActualizado;

  const ProfesorDetailPage({
    super.key,
    required this.profesor,
    required this.onProfesorActualizado,
  });

  @override
  State<ProfesorDetailPage> createState() => _ProfesorDetailPageState();
}

class _ProfesorDetailPageState extends State<ProfesorDetailPage> {
  bool _isEditing = false;
  bool _isSaving = false;
  
  // Controladores para los campos
  late TextEditingController _nombreController;
  late TextEditingController _dniController;
  late TextEditingController _aliasController;
  late TextEditingController _telefonoController;
  late TextEditingController _emailController;
  late TextEditingController _domicilioController;
  late TextEditingController _fechaNacController;
  
  String? _fechaNacOriginal;
  
  @override
  void initState() {
    super.initState();
    _inicializarControladores();
  }
  
  void _inicializarControladores() {
    _nombreController = TextEditingController(text: widget.profesor.nombApel);
    _dniController = TextEditingController(text: widget.profesor.dni);
    _aliasController = TextEditingController(text: widget.profesor.alias ?? '');
    _telefonoController = TextEditingController(text: widget.profesor.telefono ?? '');
    _emailController = TextEditingController(text: widget.profesor.email ?? '');
    _domicilioController = TextEditingController(text: widget.profesor.domicilio ?? '');
    _fechaNacController = TextEditingController(text: widget.profesor.fechaNac ?? '');
    _fechaNacOriginal = widget.profesor.fechaNac;
  }
  
  @override
  void dispose() {
    _nombreController.dispose();
    _dniController.dispose();
    _aliasController.dispose();
    _telefonoController.dispose();
    _emailController.dispose();
    _domicilioController.dispose();
    _fechaNacController.dispose();
    super.dispose();
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
  
  Future<void> _guardarCambios() async {
    setState(() => _isSaving = true);
    
    final profesorData = {
      'dni': _dniController.text,
      'nomb_apel': _nombreController.text,
      'fecha_nac': _fechaNacController.text.isEmpty ? null : _fechaNacController.text,
      'domicilio': _domicilioController.text.isEmpty ? null : _domicilioController.text,
      'telefono': _telefonoController.text.isEmpty ? null : _telefonoController.text,
      'alias': _aliasController.text.isEmpty ? null : _aliasController.text,
      'email': _emailController.text.isEmpty ? null : _emailController.text,
    };
    
    final success = await PersonasService.actualizarProfesor(widget.profesor.id, profesorData);
    
    setState(() => _isSaving = false);
    
    if (success) {
      widget.onProfesorActualizado();
      setState(() {
        _isEditing = false;
        // Actualizar el objeto profesor con los nuevos datos
        widget.profesor.nombApel = _nombreController.text;
        widget.profesor.dni = _dniController.text;
        widget.profesor.alias = _aliasController.text.isEmpty ? null : _aliasController.text;
        widget.profesor.telefono = _telefonoController.text.isEmpty ? null : _telefonoController.text;
        widget.profesor.email = _emailController.text.isEmpty ? null : _emailController.text;
        widget.profesor.domicilio = _domicilioController.text.isEmpty ? null : _domicilioController.text;
        widget.profesor.fechaNac = _fechaNacController.text.isEmpty ? null : _fechaNacController.text;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profesor actualizado correctamente')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al actualizar el profesor'), backgroundColor: Colors.red),
      );
    }
  }
  
  void _cancelarEdicion() {
    setState(() {
      _isEditing = false;
      _inicializarControladores();
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Editar Profesor' : 'Detalle de Profesor'),
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
                          _buildInfoRow('Nombre y Apellido: ', widget.profesor.nombApel),
                        
                        // DNI
                        if (_isEditing)
                          _buildEditField('DNI:', _dniController)
                        else
                          _buildInfoRow('DNI: ', widget.profesor.dni),
                        
                        // Alias
                        if (_isEditing)
                          _buildEditField('Alias:', _aliasController)
                        else if (widget.profesor.alias != null && widget.profesor.alias!.isNotEmpty)
                          _buildInfoRow('Alias: ', widget.profesor.alias!),
                        
                        // Teléfono
                        if (_isEditing)
                          _buildEditField('Teléfono:', _telefonoController)
                        else if (widget.profesor.telefono != null && widget.profesor.telefono!.isNotEmpty)
                          _buildInfoRow('Teléfono: ', widget.profesor.telefono!),
                        
                        // Email
                        if (_isEditing)
                          _buildEditField('Email:', _emailController)
                        else if (widget.profesor.email != null && widget.profesor.email!.isNotEmpty)
                          _buildInfoRow('Email: ', widget.profesor.email!),
                        
                        // Domicilio
                        if (_isEditing)
                          _buildEditField('Domicilio:', _domicilioController)
                        else if (widget.profesor.domicilio != null && widget.profesor.domicilio!.isNotEmpty)
                          _buildInfoRow('Domicilio: ', widget.profesor.domicilio!),
                        
                        // Fecha de Nacimiento
                        if (_isEditing)
                          _buildEditField('Fecha de Nacimiento (YYYY-MM-DD):', _fechaNacController)
                        else
                          _buildInfoRow('Fecha de Nacimiento: ', _formatearFecha(widget.profesor.fechaNac)),
                        
                        // Edad (siempre solo lectura y calculado)
                        _buildInfoRow('Edad: ', _calcularEdad(_isEditing ? _fechaNacController.text : widget.profesor.fechaNac)),
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
                          onPressed: () {
                            setState(() => _isEditing = true);
                          },
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
}