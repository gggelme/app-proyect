import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/persona_model.dart';
import '../../../core/constants/api_config.dart';
import '../models/cuota_alumno_model.dart';
import '../models/cuota_model.dart'
;
class PersonasService {
  static const String baseUrl = ApiConfig.baseUrl;

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

  static Future<int> crearAlumno(Map<String, dynamic> alumnoData) async {
    try {
      print('📤 Enviando POST a $baseUrl/alumnos');
      print('📦 Body: ${json.encode(alumnoData)}');
      
      final response = await http.post(
        Uri.parse('$baseUrl/alumnos'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(alumnoData),
      );
      
      print('📥 Status code: ${response.statusCode}');
      print('📥 Response body: ${response.body}');
      
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

  static Future<int> crearProfesor(Map<String, dynamic> profesorData) async {
    try {
      print('📤 Enviando POST a $baseUrl/profesores');
      print('📦 Body: ${json.encode(profesorData)}');
      
      final response = await http.post(
        Uri.parse('$baseUrl/profesores'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(profesorData),
      );
      
      print('📥 Status code: ${response.statusCode}');
      print('📥 Response body: ${response.body}');
      
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
  static Future<List<CuotaAlumnoModel>> getCuotasByAlumno(int idAlumno) async {
  try {
    final response = await http.get(
      Uri.parse('$baseUrl/alumnos/$idAlumno/cuotas'),
    );
    
    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return data.map((json) => CuotaAlumnoModel.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar cuotas del alumno');
    }
  } catch (e) {
    print('Error en getCuotasByAlumno: $e');
    return [];
    }
  }


  static Future<bool> actualizarProfesor(int idProfesor, Map<String, dynamic> profesorData) async {
  try {
    final response = await http.put(
      Uri.parse('$baseUrl/profesores/$idProfesor'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(profesorData),
    );
    
    if (response.statusCode == 200) {
      return true;
    } else {
      print('Error al actualizar profesor: ${response.body}');
      return false;
    }
  } catch (e) {
    print('Error en actualizarProfesor: $e');
    return false;
  }
}

static Future<bool> actualizarAlumno(int idAlumno, Map<String, dynamic> alumnoData) async {
  try {
    final response = await http.put(
      Uri.parse('$baseUrl/alumnos/$idAlumno'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(alumnoData),
    );
    
    if (response.statusCode == 200) {
      return true;
    } else {
      print('Error al actualizar alumno: ${response.body}');
      return false;
    }
  } catch (e) {
    print('Error en actualizarAlumno: $e');
    return false;
  }
}
static Future<List<CuotaModel>> getTodasCuotas() async {
  try {
    final response = await http.get(
      Uri.parse('$baseUrl/cuotas'),
    );
    
    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return data.map((json) => CuotaModel.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar cuotas');
    }
  } catch (e) {
    print('Error en getTodasCuotas: $e');
    return [];
  }
}
static Future<bool> actualizarCuotasAlumno(int idAlumno, List<int> idsCuotas) async {
  try {
    final response = await http.put(
      Uri.parse('$baseUrl/alumnos/$idAlumno/cuotas'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'ids_cuotas': idsCuotas}),
    );
    
    if (response.statusCode == 200) {
      return true;
    } else {
      print('Error al actualizar cuotas: ${response.body}');
      return false;
    }
  } catch (e) {
    print('Error en actualizarCuotasAlumno: $e');
    return false;
  }
}
}