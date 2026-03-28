// lib/features/clases/models/sesion_agrupada_model.dart
class HorarioSesion {
  final int sesionId;
  final int horarioId;
  final String dia;
  final String hora;
  final String aula;
  final String fechaInscripcion;

  HorarioSesion({
    required this.sesionId,
    required this.horarioId,
    required this.dia,
    required this.hora,
    required this.aula,
    required this.fechaInscripcion,
  });

  factory HorarioSesion.fromJson(Map<String, dynamic> json) {
    return HorarioSesion(
      sesionId: json['sesion_id'] ?? 0,
      horarioId: json['horario_id'] ?? 0,
      dia: json['dia'] ?? '',
      hora: json['hora'] ?? '',
      aula: json['aula'] ?? '',
      fechaInscripcion: json['fecha_inscripcion'] ?? '',
    );
  }
}

class AlumnoClaseAgrupado {
  final int alumnoId;
  final String alumnoNombre;
  final int claseId;
  final String claseNombre;
  final int claseDuracion;
  final int profesorId;
  final String profesorNombre;
  final List<HorarioSesion> horarios;

  AlumnoClaseAgrupado({
    required this.alumnoId,
    required this.alumnoNombre,
    required this.claseId,
    required this.claseNombre,
    required this.claseDuracion,
    required this.profesorId,
    required this.profesorNombre,
    required this.horarios,
  });

  factory AlumnoClaseAgrupado.fromJson(Map<String, dynamic> json) {
    return AlumnoClaseAgrupado(
      alumnoId: json['alumno_id'] ?? 0,
      alumnoNombre: json['alumno_nombre'] ?? '',
      claseId: json['clase_id'] ?? 0,
      claseNombre: json['clase_nombre'] ?? '',
      claseDuracion: json['clase_duracion'] ?? 60,
      profesorId: json['profesor_id'] ?? 0,
      profesorNombre: json['profesor_nombre'] ?? '',
      horarios: (json['horarios'] as List?)
          ?.map((h) => HorarioSesion.fromJson(h))
          .toList() ?? [],
    );
  }
}