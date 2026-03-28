// lib/features/clases/models/clase.dart
class Clase {
  final int alumnoClaseId;
  final int claseId;
  final String nombreClase;
  final String profesorNombre;
  final int? duracion;
  final Horario horario;
  final List<String> alumnos;
  final String aula;  // ← Ahora es requerido

  Clase({
    required this.alumnoClaseId,
    required this.claseId,
    required this.nombreClase,
    required this.profesorNombre,
    this.duracion,
    required this.horario,
    required this.alumnos,
    required this.aula,
  });

  factory Clase.fromJson(Map<String, dynamic> json) {
    return Clase(
      alumnoClaseId: json['alumno_clase_id'] ?? 0,
      claseId: json['clase_id'] ?? 0,
      nombreClase: json['nombre_clase'] ?? '',
      profesorNombre: json['profesor_nombre'] ?? '',
      duracion: json['duracion'],
      horario: Horario.fromJson(json['horario'] ?? {}),
      alumnos: List<String>.from(json['alumnos'] ?? []),
      aula: json['aula'] ?? 'A',  // ← Obtener aula con valor por defecto
    );
  }
}

class Horario {
  final int horarioId;
  final String dia;
  final String hora;

  Horario({
    required this.horarioId,
    required this.dia,
    required this.hora,
  });

  factory Horario.fromJson(Map<String, dynamic> json) {
    return Horario(
      horarioId: json['horario_id'] ?? 0,
      dia: json['dia'] ?? '',
      hora: json['hora'] ?? '',
    );
  }
}