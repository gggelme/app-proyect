// lib/features/clases/models/sesion_model.dart
class SesionModel {
  final int sesionId;
  final int alumnoId;
  final String alumnoNombre;
  final int claseId;
  final String claseNombre;
  final int claseDuracion;
  final int profesorId;
  final String profesorNombre;
  final int horarioId;
  final String dia;
  final String hora;
  final String aula;
  final String fechaInscripcion;

  SesionModel({
    required this.sesionId,
    required this.alumnoId,
    required this.alumnoNombre,
    required this.claseId,
    required this.claseNombre,
    required this.claseDuracion,
    required this.profesorId,
    required this.profesorNombre,
    required this.horarioId,
    required this.dia,
    required this.hora,
    required this.aula,
    required this.fechaInscripcion,
  });
}