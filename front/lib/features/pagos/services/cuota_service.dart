// lib/services/cuota_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/cuota_model.dart';
import '../../../core/constants/api_config.dart';

class CuotaService {
  static const String baseUrl = ApiConfig.baseUrl;

  static Future<List<CuotaModel>> getCuotas() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/cuotas'),
        headers: {'Content-Type': 'application/json'},
      );

      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => CuotaModel.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar cuotas: ${response.statusCode}');
      }
    } catch (e) {
      print('Error en getCuotas: $e');
      throw Exception('Error de conexión: $e');
    }
  }

  // Solo este método de actualización, elimina el otro
  static Future<Map<String, dynamic>> actualizarCuotas(List<CuotaModel> cuotas) async {
    try {
      // Filtrar solo las cuotas que tienen cambios
      final cuotasModificadas = cuotas.where((cuota) => 
        cuota.nuevoPrecio != cuota.precio
      ).toList();
      
      if (cuotasModificadas.isEmpty) {
        return {
          'success': true,
          'message': 'No hay cambios para guardar',
          'actualizadas': 0,
          'fallidas': 0,
        };
      }
      
      print('📡 Actualizando ${cuotasModificadas.length} cuotas...');
      
      // Preparar el array simple como espera el endpoint
      final List<Map<String, dynamic>> cuotasData = cuotasModificadas.map((cuota) {
        return {
          'id': cuota.id,
          'nuevo_precio': cuota.nuevoPrecio,
        };
      }).toList();

      final response = await http.put(
        Uri.parse('$baseUrl/cuotas'),  // Quité el /api extra porque ya está en baseUrl
        headers: {'Content-Type': 'application/json'},
        body: json.encode(cuotasData),
      );

      print('📊 Response status: ${response.statusCode}');
      print('📄 Response body: ${response.body}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> result = json.decode(response.body);
        return result;
      } else {
        throw Exception('Error al actualizar cuotas: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error en actualizarCuotas: $e');
      throw Exception('Error de conexión: $e');
    }
  }
}