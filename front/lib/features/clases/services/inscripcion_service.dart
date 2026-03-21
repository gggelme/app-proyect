// lib/core/services/inscripcion_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class InscripcionService {
  static const String baseUrl = 'http://192.168.1.137:8000/api';
  
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
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final error = json.decode(response.body);
        return {
          'status': 'error',
          'message': error['detail'] ?? 'Error al guardar inscripción'
        };
      }
    } catch (e) {
      print('Excepción al crear inscripción: $e');
      return {'status': 'error', 'message': e.toString()};
    }
  }
}