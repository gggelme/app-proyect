// lib/features/clases/models/alumno_model.dart
class AlumnoModel {
  final int id;
  final String nombre;
  final String? dni;
  final String? telefono;
  final String? fechaNac;
  final String? domicilio;

  AlumnoModel({
    required this.id,
    required this.nombre,
    this.dni,
    this.telefono,
    this.fechaNac,
    this.domicilio,
  });

  factory AlumnoModel.fromJson(Map<String, dynamic> json) {
    return AlumnoModel(
      id: json['id'] ?? json['alumno_id'] ?? 0,
      nombre: json['nombre_alumno'] ?? json['nomb_apel'] ?? '',
      dni: json['dni'],
      telefono: json['telefono'],
      fechaNac: json['fecha_nac'],
      domicilio: json['domicilio'],
    );
  }
}