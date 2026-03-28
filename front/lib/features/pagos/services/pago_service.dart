import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/pago_model.dart';
import '../../../core/constants/api_config.dart';

class PagoService {
  static const String baseUrl = ApiConfig.baseUrl;

  static Future<List<PagoPendienteModel>> getPagosPendientes() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/pagos/pendientes'),
      );
      
      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => PagoPendienteModel.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar pagos pendientes: ${response.statusCode}');
      }
    } catch (e) {
      print('Error en getPagosPendientes: $e');
      return [];
    }
  }
  
  static Future<Map<String, dynamic>> registrarPago({
    required int alumnoId,
    required int mesesAPagar,
    required String metodoPago,
    required bool mantenerDescuento,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/pagos/registrar'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'alumno_id': alumnoId,
          'meses_a_pagar': mesesAPagar,
          'metodo_pago': metodoPago,
          'mantener_descuento': mantenerDescuento,
        }),
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al registrar pago: ${response.statusCode}');
      }
    } catch (e) {
      print('Error en registrarPago: $e');
      rethrow;
    }
  }
}