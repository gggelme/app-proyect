class AlumnoModel {
  final int id;
  final int personaId;
  final String dni;
  final String nombApel;
  final String? telefono;
  final String? fechaIng;
  final bool estadoActivo;

  AlumnoModel({
    required this.id,
    required this.personaId,
    required this.dni,
    required this.nombApel,
    this.telefono,
    this.fechaIng,
    required this.estadoActivo,
  });

  factory AlumnoModel.fromJson(Map<String, dynamic> json) {
    return AlumnoModel(
      id: json['id'] ?? 0,
      personaId: json['persona_id'] ?? 0,
      dni: json['dni'] ?? '',
      nombApel: json['nomb_apel'] ?? '',
      telefono: json['telefono'],
      fechaIng: json['fecha_ing'],
      estadoActivo: json['estado_activo'] ?? true,
    );
  }
}

class ProfesorModel {
  final int id;
  final int personaId;
  final String dni;
  final String nombApel;
  final String? telefono;
  final String? alias;
  final String? email;

  ProfesorModel({
    required this.id,
    required this.personaId,
    required this.dni,
    required this.nombApel,
    this.telefono,
    this.alias,
    this.email,
  });

  factory ProfesorModel.fromJson(Map<String, dynamic> json) {
    return ProfesorModel(
      id: json['id'] ?? 0,
      personaId: json['persona_id'] ?? 0,
      dni: json['dni'] ?? '',
      nombApel: json['nomb_apel'] ?? '',
      telefono: json['telefono'],
      alias: json['alias'],
      email: json['email'],
    );
  }
}