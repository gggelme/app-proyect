import 'dart:convert';
import 'package:http/http.dart' as http;

class InscripcionService {
  static const String baseUrl = 'http://192.168.1.129:8000/api';

  // Guardar inscripción con cuotas
  static Future<Map<String, dynamic>> guardarInscripcionConCuotas({
    required int idAlumno,
    required List<int> idsCuotas,
    required double porcentajeDescuento,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/inscripcion-cuotas'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'id_alumno': idAlumno,
          'ids_cuotas': idsCuotas,
          'porcentaje_descuento': porcentajeDescuento,
        }),
      );
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al guardar inscripción: ${response.statusCode}');
      }
    } catch (e) {
      print('Error en guardarInscripcionConCuotas: $e');
      rethrow;
    }
  }
}