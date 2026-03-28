class AlumnoModel {
  int id;
  int personaId;
  String dni;
  String nombApel;
  String? telefono;
  String? fechaNac;
  String? fechaIng;
  bool estadoActivo;
  String? domicilio;  // <-- Agregar domicilio

  AlumnoModel({
    required this.id,
    required this.personaId,
    required this.dni,
    required this.nombApel,
    this.telefono,
    this.fechaNac,
    this.fechaIng,
    required this.estadoActivo,
    this.domicilio,  // <-- Agregar aquí
  });

  factory AlumnoModel.fromJson(Map<String, dynamic> json) {
    return AlumnoModel(
      id: json['id'] ?? 0,
      personaId: json['persona_id'] ?? 0,
      dni: json['dni'] ?? '',
      nombApel: json['nomb_apel'] ?? '',
      telefono: json['telefono'],
      fechaNac: json['fecha_nac'],
      fechaIng: json['fecha_ing'],
      estadoActivo: json['estado_activo'] ?? true,
      domicilio: json['domicilio'],  // <-- Agregar aquí
    );
  }
}

class ProfesorModel {
  int id;
  int personaId;
  String dni;
  String nombApel;
  String? telefono;
  String? fechaNac;
  String? alias;
  String? email;
  String? domicilio;  // <-- Agregar este campo

  ProfesorModel({
    required this.id,
    required this.personaId,
    required this.dni,
    required this.nombApel,
    this.telefono,
    this.fechaNac,
    this.alias,
    this.email,
    this.domicilio,  // <-- Agregar aquí
  });

  factory ProfesorModel.fromJson(Map<String, dynamic> json) {
    return ProfesorModel(
      id: json['id'] ?? 0,
      personaId: json['persona_id'] ?? 0,
      dni: json['dni'] ?? '',
      nombApel: json['nomb_apel'] ?? '',
      telefono: json['telefono'],
      fechaNac: json['fecha_nac'],
      alias: json['alias'],
      email: json['email'],
      domicilio: json['domicilio'],  // <-- Agregar aquí
    );
  }
}