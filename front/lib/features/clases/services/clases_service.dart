// services/clases_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/horario_clases.dart';
import '../../personas/models/persona_model.dart';

class ClasesService {
  final String baseUrl = 'http://192.168.1.137:8000/api'; 

  // Obtener clases por día y hora (para la vista existente)
  Future<List<Clase>> getClases(String dia, String hora) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/clases?dia=$dia&hora=$hora'),
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => Clase.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar clases');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Buscar profesores por nombre (autocomplete)
  Future<List<ProfesorModel>> buscarProfesores(String query) async {
    if (query.isEmpty) return [];
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/profesores/buscar?q=$query'),
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => ProfesorModel.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('Error buscando profesores: $e');
      return [];
    }
  }

  // Obtener todas las clases (para la vista de inscripción)
   Future<List<Map<String, dynamic>>> obtenerTodasClases() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/clases/todas'),
      );
      
      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.cast<Map<String, dynamic>>();
      }
      return [];
    } catch (e) {
      print('Error al obtener clases: $e');
      return [];
    }
  }
}