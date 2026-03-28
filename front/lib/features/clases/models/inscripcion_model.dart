// lib/models/inscripcion_model.dart
class InscripcionModel {
  final int alumnoId;
  final String alumnoNombre;
  final int claseId;
  final String claseNombre;
  final List<HorarioInscripcion> horarios;

  InscripcionModel({
    required this.alumnoId,
    required this.alumnoNombre,
    required this.claseId,
    required this.claseNombre,
    required this.horarios,
  });

  factory InscripcionModel.fromJson(Map<String, dynamic> json) {
    return InscripcionModel(
      alumnoId: json['alumno_id'] ?? 0,
      alumnoNombre: json['alumno_nombre'] ?? '',
      claseId: json['clase_id'] ?? 0,
      claseNombre: json['clase_nombre'] ?? '',
      horarios: (json['horarios'] as List?)
              ?.map((h) => HorarioInscripcion.fromJson(h))
              .toList() ?? [],
    );
  }
}

class HorarioInscripcion {
  final String dia;
  final String hora;
  final String aula;

  HorarioInscripcion({
    required this.dia,
    required this.hora,
    required this.aula,
  });

  factory HorarioInscripcion.fromJson(Map<String, dynamic> json) {
    return HorarioInscripcion(
      dia: json['dia'] ?? '',
      hora: json['hora'] ?? '',
      aula: json['aula'] ?? '',
    );
  }

  String get horarioCompleto => '$dia $hora - Aula $aula';
}