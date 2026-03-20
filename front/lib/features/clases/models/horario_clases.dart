// models/horario_clases.dart

class Clase {
  final int id;
  final String nombreClase;
  final String dia;
  final String hora;
  final String aula;
  final String profesor;
  final List<String> alumnos;

  Clase({
    required this.id,
    required this.nombreClase,
    required this.dia,
    required this.hora,
    required this.aula,
    required this.profesor,
    required this.alumnos,
  });

  factory Clase.fromJson(Map<String, dynamic> json) {
    return Clase(
      id: json['id'] ?? 0,
      nombreClase: json['nombre_clase'] ?? '',
      dia: json['dia'] ?? '',
      hora: json['hora'] ?? '',
      aula: json['aula'] ?? '',
      profesor: json['profesor'] ?? '',
      alumnos: List<String>.from(json['alumnos'] ?? []),
    );
  }
}

// Para crear una clase (basado en tu estructura de repos)
class ClaseCreate {
  final String nombreClase;
  final int profesorId;
  final List<HorarioClase> horarios;
  final List<int> alumnosIds;

  ClaseCreate({
    required this.nombreClase,
    required this.profesorId,
    required this.horarios,
    required this.alumnosIds,
  });

  Map<String, dynamic> toJson() {
    return {
      'nombre_clase': nombreClase,
      'profesor_id': profesorId,
      'horarios': horarios.map((h) => h.toJson()).toList(),
      'alumnos_ids': alumnosIds,
    };
  }
}

class HorarioClase {
  String dia;
  String hora;
  String aula;

  HorarioClase({
    required this.dia,
    required this.hora,
    required this.aula,
  });

  Map<String, dynamic> toJson() {
    return {
      'dia': dia,
      'hora': hora,
      'aula': aula,
    };
  }
}