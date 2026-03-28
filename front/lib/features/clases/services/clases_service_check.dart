// lib/features/clases/services/clases_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants/api_config.dart';
import '../models/clase_model_check.dart';  // Solo importar este
import '../models/profesor_model_check.dart';

class ClasesService {
  final String baseUrl = ApiConfig.baseUrl;

  // Obtener clases por día y hora
  Future<List<Clase>> getClases(String dia, String hora) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/clases?dia=$dia&hora=$hora'),
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        print('📦 Datos recibidos: ${data.length} clases');
        
        return data.map((json) {
          // Debug: imprimir estructura
          print('Clase: ${json['nombre_clase']}, Alumnos: ${json['alumnos']}');
          
          return Clase.fromJson(json);
        }).toList();
      } else {
        throw Exception('Error al cargar clases: ${response.statusCode}');
      }
    } catch (e) {
      print('Error en getClases: $e');
      throw Exception('Error de conexión: $e');
    }
  }

  // Buscar profesores por nombre
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

  // Obtener todos los profesores
  Future<List<ProfesorModel>> obtenerTodosProfesores() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/profesores'),
        headers: {'Content-Type': 'application/json'},
      );

      print('🔍 URL consultada: $baseUrl/profesores');
      print('📡 Status code: ${response.statusCode}');

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        print('✅ Datos parseados: ${data.length} profesores');
        return data.map((json) => ProfesorModel.fromJson(json)).toList();
      } else {
        print('❌ Error: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('❌ Excepción al obtener profesores: $e');
      return [];
    }
  }

  // Crear una nueva clase
  Future<Map<String, dynamic>> crearClase(String nombreClase, int idProfesor, int duracion) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/clases'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'nombre_clase': nombreClase,
        'id_profesor': idProfesor,  // ← Este es el profesor_id
        'duracion': duracion,
      }),
    );

    print('📤 Creando clase: $nombreClase, profesor_id: $idProfesor');
    print('📥 Respuesta: ${response.statusCode}');

    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = json.decode(response.body);
      return {
        'status': 'success',
        'message': data['message'] ?? 'Clase creada exitosamente',
        'id': data['id']
      };
    } else {
      final error = json.decode(response.body);
      return {
        'status': 'error',
        'message': error['detail'] ?? 'Error al crear clase'
      };
    }
  } catch (e) {
    print('❌ Excepción al crear clase: $e');
    return {'status': 'error', 'message': e.toString()};
  }
}
  
  
}