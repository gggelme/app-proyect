// lib/features/clases/services/inscripcion_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants/api_config.dart';

class InscripcionService {
  final String baseUrl = ApiConfig.baseUrl;

  Future<Map<String, dynamic>> crearInscripcion({
    required int idClase,
    required List<Map<String, dynamic>> horarios,
    required List<Map<String, dynamic>> alumnos,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/inscripcion'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'id_clase': idClase,
          'horarios': horarios,
          'alumnos': alumnos,
        }),
      );

      print('📤 Creando inscripción para clase: $idClase');
      print('📥 Respuesta: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'status': 'success',
          'message': data['message'] ?? 'Inscripción realizada exitosamente',
          'data': data
        };
      } else {
        final error = json.decode(response.body);
        return {
          'status': 'error',
          'message': error['detail'] ?? 'Error al realizar la inscripción'
        };
      }
    } catch (e) {
      print('❌ Excepción al crear inscripción: $e');
      return {'status': 'error', 'message': e.toString()};
    }
  }
}