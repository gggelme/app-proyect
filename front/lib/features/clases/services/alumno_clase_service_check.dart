// lib/features/clases/services/alumnos_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants/api_config.dart';
import '../models/alumno_model_check.dart';

class AlumnoService {
  final String baseUrl = ApiConfig.baseUrl;

  Future<List<AlumnoModel>> obtenerTodosAlumnos() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/alumnos'),
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => AlumnoModel.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('Error al obtener alumnos: $e');
      return [];
    }
  }

  // ✅ Método corregido
  Future<List<AlumnoModel>> buscarAlumnosPorNombre(String query) async {
    if (query.isEmpty) return [];
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/alumnos/buscar?q=$query'),
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => AlumnoModel.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('Error buscando alumnos: $e');
      return [];
    }
  }
  
  // Método alternativo (si el endpoint es diferente)
  Future<List<AlumnoModel>> buscarAlumnos(String query) async {
    if (query.isEmpty) return [];
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/alumnos?search=$query'),
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => AlumnoModel.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('Error buscando alumnos: $e');
      return [];
    }
  }
}