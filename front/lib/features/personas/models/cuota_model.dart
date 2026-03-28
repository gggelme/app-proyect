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
      id: json['id'] ?? 0,
      nombre: json['nombre'] ?? '',
      precio: (json['precio'] ?? 0).toDouble(),
    );
  }
}