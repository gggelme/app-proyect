// lib/core/services/alumno_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class AlumnoService {
  static const String baseUrl = 'http://192.168.1.129:8000/api'; 
  
  Future<List<Map<String, dynamic>>> buscarAlumnosPorNombre(String texto) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/alumnos/buscar-por-nombre/${Uri.encodeComponent(texto)}'),
      );
      
      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.cast<Map<String, dynamic>>();
      } else {
        print('Error al buscar alumnos: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('Excepción al buscar alumnos: $e');
      return [];
    }
  }
}