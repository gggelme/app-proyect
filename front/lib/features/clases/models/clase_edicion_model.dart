// lib/features/clases/models/clase_edicion_model.dart
class ClaseEdicion {
  final int id;
  final String nombreClase;
  final int duracion;
  final int profesorId;
  final String profesorNombre;
  final int cantidadInscripciones;

  ClaseEdicion({
    required this.id,
    required this.nombreClase,
    required this.duracion,
    required this.profesorId,
    required this.profesorNombre,
    required this.cantidadInscripciones,
  });

  factory ClaseEdicion.fromJson(Map<String, dynamic> json) {
    return ClaseEdicion(
      id: json['id'] ?? 0,
      nombreClase: json['nombre_clase'] ?? '',
      duracion: json['duracion'] ?? 60,
      profesorId: json['profesor_id'] ?? 0,
      profesorNombre: json['profesor_nombre'] ?? '',
      cantidadInscripciones: json['cantidad_inscripciones'] ?? 0,
    );
  }
}