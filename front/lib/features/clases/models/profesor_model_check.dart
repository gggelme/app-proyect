// lib/models/profesor_model.dart
class ProfesorModel {
  final int id;
  final String dni;
  final String nombApel;
  final String? fechaNac;
  final String? domicilio;
  final String? telefono;
  final String? alias;
  final String? email;

  ProfesorModel({
    required this.id,
    required this.dni,
    required this.nombApel,
    this.fechaNac,
    this.domicilio,
    this.telefono,
    this.alias,
    this.email,
  });

  factory ProfesorModel.fromJson(Map<String, dynamic> json) {
    return ProfesorModel(
      id: json['id'],
      dni: json['dni'] ?? '',
      nombApel: json['nomb_apel'] ?? '',
      fechaNac: json['fecha_nac'],
      domicilio: json['domicilio'],
      telefono: json['telefono'],
      alias: json['alias'],
      email: json['email'],
    );
  }

  String get nombreCompleto => nombApel;
}