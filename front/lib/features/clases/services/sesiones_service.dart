// lib/features/clases/services/sesion_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants/api_config.dart';
import '../models/sesion_agrupada.dart';

class SesionService {
  final String baseUrl = ApiConfig.baseUrl;

  Future<List<AlumnoClaseAgrupado>> obtenerTodasSesionesAgrupadas() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/sesiones/agrupadas'),
      );

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => AlumnoClaseAgrupado.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('Error al obtener sesiones agrupadas: $e');
      return [];
    }
  }

  // Cambiar el método a PUT y la URL correcta
  Future<bool> guardarHorarios(int alumnoId, int claseId, List<Map<String, dynamic>> horarios) async {
    try {
      print('📤 Enviando petición PUT a: $baseUrl/alumno-clase/horarios');
      print('   Body: ${json.encode({
        'alumno_id': alumnoId,
        'clase_id': claseId,
        'horarios': horarios,
      })}');
      
      final response = await http.put(
        Uri.parse('$baseUrl/alumno-clase/horarios'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'alumno_id': alumnoId,
          'clase_id': claseId,
          'horarios': horarios,
        }),
      );
      
      print('📥 Respuesta: ${response.statusCode}');
      print('   Body: ${response.body}');
      
      return response.statusCode == 200;
    } catch (e) {
      print('❌ Error al guardar horarios: $e');
      return false;
    }
  }
}