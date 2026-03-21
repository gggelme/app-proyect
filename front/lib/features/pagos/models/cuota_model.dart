// lib/models/cuota_model.dart
class CuotaModel {
  final int id;
  final String nombre;
  final double precio;  // La API devuelve "precio"
  double nuevoPrecio;

  CuotaModel({
    required this.id,
    required this.nombre,
    required this.precio,
    required this.nuevoPrecio,
  });

  factory CuotaModel.fromJson(Map<String, dynamic> json) {
    return CuotaModel(
      id: json['id'],
      nombre: json['nombre'],
      precio: json['precio'].toDouble(),  // La API devuelve "precio"
      nuevoPrecio: json['precio'].toDouble(), // Inicialmente igual al actual
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'nuevoPrecio': nuevoPrecio,
    };
  }
}