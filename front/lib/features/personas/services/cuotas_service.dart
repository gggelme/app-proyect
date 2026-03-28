import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants/api_config.dart';

class CuotaModel {
  final int id;
  final String nombre;
  final double precio;

  CuotaModel({
    required this.id,
    required this.nombre,
    required this.precio,
  });

  factory CuotaModel.fromJson(Map<String, dynamic> json) {
    return CuotaModel(
      id: json['id'],
      nombre: json['nombre'],
      precio: json['precio'].toDouble(),
    );
  }
}

class CuotasService {
  static const String baseUrl = ApiConfig.baseUrl;

  // Obtener todas las cuotas
  static Future<List<CuotaModel>> getCuotas() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/cuotas'));
      
      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => CuotaModel.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar cuotas: ${response.statusCode}');
      }
    } catch (e) {
      print('Error en getCuotas: $e');
      return [];
    }
  }
}