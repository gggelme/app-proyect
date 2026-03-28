// lib/core/services/profesor_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants/api_config.dart';
import '../models/profesor_model_check.dart';

class ProfesorService {
  static const String baseUrl = ApiConfig.baseUrl;

  Future<List<ProfesorModel>> obtenerTodosProfesores() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/profesores'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => ProfesorModel.fromJson(json)).toList();
      } else {
        print('Error al obtener profesores: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('Excepción al obtener profesores: $e');
      return [];
    }
  }

  Future<List<ProfesorModel>> buscarProfesores(String query) async {
    if (query.trim().isEmpty) {
      return [];
    }

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/profesores?search=${Uri.encodeComponent(query)}'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => ProfesorModel.fromJson(json)).toList();
      } else {
        return [];
      }
    } catch (e) {
      print('Excepción al buscar profesores: $e');
      return [];
    }
  }
}