import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/persona_model.dart';

class PersonasService {
  static const String baseUrl = 'http://192.168.1.131:8000/api';

  // Obtener todos los alumnos
  static Future<List<AlumnoModel>> getAlumnos() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/alumnos'));
      
      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => AlumnoModel.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar alumnos: ${response.statusCode}');
      }
    } catch (e) {
      print('Error en getAlumnos: $e');
      return [];
    }
  }

  // Obtener todos los profesores
  static Future<List<ProfesorModel>> getProfesores() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/profesores'));
      
      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => ProfesorModel.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar profesores: ${response.statusCode}');
      }
    } catch (e) {
      print('Error en getProfesores: $e');
      return [];
    }
  }

  // crear alumnos
  static Future<int> crearAlumno(Map<String, dynamic> alumnoData) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/alumnos'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(alumnoData),
    );
    
    if (response.statusCode == 200) {
      return int.parse(response.body);
    } else {
      print('Error ${response.statusCode}: ${response.body}');
      return 0;
    }
  } catch (e) {
    print('Error en crearAlumno: $e');
    return 0;
  }
}
// crear profesores
static Future<int> crearProfesor(Map<String, dynamic> profesorData) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/profesores'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(profesorData),
    );
    
    if (response.statusCode == 200) {
      return int.parse(response.body);
    } else {
      print('Error ${response.statusCode}: ${response.body}');
      return 0;
    }
  } catch (e) {
    print('Error en crearProfesor: $e');
    return 0;
  }
}
}