// lib/features/clases/services/clase_edicion_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants/api_config.dart';
import '../models/clase_edicion_model.dart';

class ClaseEdicionService {
  final String baseUrl = ApiConfig.baseUrl;

  Future<List<ClaseEdicion>> obtenerTodasClases() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/clases/editar/todas'),
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => ClaseEdicion.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('Error al obtener clases: $e');
      return [];
    }
  }

  Future<bool> actualizarClase(int id, String nombreClase, int duracion) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/clases/$id'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'nombre_clase': nombreClase,
          'duracion': duracion,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // Corregido: acceder a data['status'] en lugar de data.status
        return data['status'] == 'success';
      }
      return false;
    } catch (e) {
      print('Error al actualizar clase: $e');
      return false;
    }
  }

  Future<Map<String, dynamic>> eliminarClase(int id) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/clases/$id?confirm=true'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // Corregido: retornar el mapa directamente
        return {
          'success': data['success'] ?? false,
          'message': data['message'] ?? 'Clase eliminada correctamente',
          'inscripciones_eliminadas': data['inscripciones_eliminadas'] ?? 0,
        };
      }
      return {
        'success': false,
        'message': 'Error al eliminar la clase',
      };
    } catch (e) {
      print('Error al eliminar clase: $e');
      return {
        'success': false,
        'message': e.toString(),
      };
    }
  }
}