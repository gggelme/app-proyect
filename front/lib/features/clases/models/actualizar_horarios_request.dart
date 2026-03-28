// lib/features/clases/models/actualizar_horarios_request.dart
class ActualizarHorariosRequest {
  final int alumnoId;
  final int claseId;
  final List<Map<String, String>> horarios;

  ActualizarHorariosRequest({
    required this.alumnoId,
    required this.claseId,
    required this.horarios,
  });

  Map<String, dynamic> toJson() => {
        'alumno_id': alumnoId,
        'clase_id': claseId,
        'horarios': horarios,
      };
}