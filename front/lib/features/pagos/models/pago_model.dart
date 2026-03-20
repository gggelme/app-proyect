class PagoPendienteModel {
  final int alumnoId;
  final String nombreAlumno;
  final DateTime mesCorrespondiente;
  final double totalAPagar;
  final bool tieneDescuento;  // Este campo debe ser requerido

  PagoPendienteModel({
    required this.alumnoId,
    required this.nombreAlumno,
    required this.mesCorrespondiente,
    required this.totalAPagar,
    required this.tieneDescuento,
  });

  factory PagoPendienteModel.fromJson(Map<String, dynamic> json) {
    return PagoPendienteModel(
      alumnoId: json['alumno_id'],
      nombreAlumno: json['nombre_alumno'],
      mesCorrespondiente: DateTime.parse(json['mes_correspondiente']),
      totalAPagar: json['total_a_pagar'].toDouble(),
      tieneDescuento: json['tiene_descuento'] ?? false,  // Si por alguna razón llega null, usa false
    );
  }

  String get mesFormateado {
    final meses = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    return '${meses[mesCorrespondiente.month - 1]} ${mesCorrespondiente.year}';
  }
}