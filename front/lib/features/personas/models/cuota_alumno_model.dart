class CuotaAlumnoModel {
  final int idAlumnoCuota;
  final int idCuota;
  final String nombre;
  final double precioBase;
  final List<PagoCuotaModel> pagos;

  CuotaAlumnoModel({
    required this.idAlumnoCuota,
    required this.idCuota,
    required this.nombre,
    required this.precioBase,
    required this.pagos,
  });

  factory CuotaAlumnoModel.fromJson(Map<String, dynamic> json) {
    return CuotaAlumnoModel(
      idAlumnoCuota: json['id_alumno_cuota'] ?? 0,
      idCuota: json['id_cuota'] ?? 0,
      nombre: json['nombre'] ?? '',
      precioBase: (json['precio_base'] ?? 0).toDouble(),
      pagos: (json['pagos'] as List?)
              ?.map((p) => PagoCuotaModel.fromJson(p))
              .toList() ??
          [],
    );
  }
}

class PagoCuotaModel {
  final int idPago;
  final String? fechaPago;
  final bool pagadoBool;
  final String? mesCorrespondiente;
  final String? metodoPago;

  PagoCuotaModel({
    required this.idPago,
    this.fechaPago,
    required this.pagadoBool,
    this.mesCorrespondiente,
    this.metodoPago,
  });

  factory PagoCuotaModel.fromJson(Map<String, dynamic> json) {
    return PagoCuotaModel(
      idPago: json['id_pago'] ?? 0,
      fechaPago: json['fecha_pago'],
      pagadoBool: json['pagado_bool'] ?? false,
      mesCorrespondiente: json['mes_correspondiente'],
      metodoPago: json['metodo_pago'],
    );
  }

  bool get estaPagado => pagadoBool;
  
  String get mesFormateado {
    if (mesCorrespondiente == null || mesCorrespondiente!.isEmpty) return 'No disponible';
    final partes = mesCorrespondiente!.split('-');
    if (partes.length == 2) {
      return '${_getNombreMes(int.parse(partes[1]))} ${partes[0]}';
    }
    return mesCorrespondiente!;
  }

  String _getNombreMes(int mes) {
    const meses = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    return meses[mes - 1];
  }
}