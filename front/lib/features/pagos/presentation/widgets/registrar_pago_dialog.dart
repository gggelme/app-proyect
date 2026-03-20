import 'package:flutter/material.dart';
import '../../services/pago_service.dart';

class RegistrarPagoDialog extends StatefulWidget {
  final int alumnoId;
  final String nombreAlumno;
  final double totalPendiente;
  final bool tieneDescuento;

  const RegistrarPagoDialog({
    super.key,
    required this.alumnoId,
    required this.nombreAlumno,
    required this.totalPendiente,
    required this.tieneDescuento,
  });

  @override
  State<RegistrarPagoDialog> createState() => _RegistrarPagoDialogState();
}

class _RegistrarPagoDialogState extends State<RegistrarPagoDialog> {
  final TextEditingController _mesesController = TextEditingController(text: '1');
  String? _metodoPago;
  bool _isLoading = false;
  bool? _mantenerDescuento;

  final List<String> _metodosPago = [
    'Efectivo',
    'Transferencia Bancaria',
    'Tarjeta de Crédito',
    'Tarjeta de Débito',
    'Mercado Pago',
  ];

  Future<void> _registrarPago() async {
    print("🔍 [FRONTEND] Iniciando registro de pago");
    print("   alumnoId: ${widget.alumnoId}");
    print("   tieneDescuento: ${widget.tieneDescuento}");
    print("   _mantenerDescuento (antes de validar): $_mantenerDescuento");
    
    if (_metodoPago == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Debe seleccionar un método de pago')),
      );
      return;
    }

    int mesesAPagar = int.tryParse(_mesesController.text) ?? 1;
    if (mesesAPagar < 1) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Debe pagar al menos 1 mes')),
      );
      return;
    }

    // Si tiene descuento y aún no respondió la pregunta
    if (widget.tieneDescuento && _mantenerDescuento == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Debe indicar si desea mantener el descuento')),
      );
      return;
    }

    // Valor que se va a enviar
    final valorMantenerDescuento = _mantenerDescuento ?? true;
    print("🔍 [FRONTEND] Valor a enviar - mantenerDescuento: $valorMantenerDescuento");
    print("   mesesAPagar: $mesesAPagar");
    print("   metodoPago: $_metodoPago");

    setState(() => _isLoading = true);

    try {
      final resultado = await PagoService.registrarPago(
        alumnoId: widget.alumnoId,
        mesesAPagar: mesesAPagar,
        metodoPago: _metodoPago!,
        mantenerDescuento: valorMantenerDescuento,
      );

      print("🔍 [FRONTEND] Respuesta del backend:");
      print("   resultado: $resultado");

      if (mounted) {
        Navigator.pop(context, true);
        
        final data = resultado['data'];
        final totalPagado = data['total_pagado'];
        final mesesProcesados = data['meses_procesados'];
        final descuentoMantenido = data['descuento_mantenido'];
        
        print("🔍 [FRONTEND] Datos recibidos:");
        print("   mesesProcesados: $mesesProcesados");
        print("   totalPagado: $totalPagado");
        print("   descuentoMantenido: $descuentoMantenido");
        
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('✅ Pago Registrado'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Alumno: ${widget.nombreAlumno}'),
                const SizedBox(height: 8),
                Text('Meses pagados: $mesesProcesados'),
                Text('Total pagado: \$${totalPagado.toStringAsFixed(2)}'),
                Text('Método: $_metodoPago'),
                if (widget.tieneDescuento)
                  Text(
                    descuentoMantenido ? '✅ Descuento mantenido' : '❌ Descuento eliminado',
                    style: TextStyle(
                      color: descuentoMantenido ? Colors.green : Colors.orange,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Aceptar'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      print("❌ [FRONTEND] Error en registro de pago: $e");
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Registrar Pago'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Alumno: ${widget.nombreAlumno}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Text('Total pendiente:'),
            Text(
              '\$${widget.totalPendiente.toStringAsFixed(2)}',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.red,
              ),
            ),
            const SizedBox(height: 24),
            const Text('Meses a pagar:'),
            const SizedBox(height: 8),
            TextField(
              controller: _mesesController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Ej: 1, 2, 3...',
                helperText: 'Número de meses a pagar (mínimo 1)',
              ),
            ),
            const SizedBox(height: 24),
            const Text('Método de pago:'),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _metodoPago,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              items: _metodosPago.map((metodo) {
                return DropdownMenuItem(
                  value: metodo,
                  child: Text(metodo),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _metodoPago = value;
                });
              },
              validator: (value) {
                if (value == null) {
                  return 'Seleccione un método de pago';
                }
                return null;
              },
            ),
            // Pregunta de descuento solo si tiene descuento
            if (widget.tieneDescuento) ...[
              const SizedBox(height: 24),
              const Text(
                '¿Desea continuar con el descuento?',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        print("🔍 [FRONTEND] Usuario seleccionó: SÍ (mantener descuento)");
                        setState(() {
                          _mantenerDescuento = true;
                        });
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _mantenerDescuento == true 
                            ? const Color(0xFF87CEEB) 
                            : Colors.grey[300],
                        foregroundColor: _mantenerDescuento == true 
                            ? Colors.white 
                            : Colors.black,
                      ),
                      child: const Text('SÍ'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        print("🔍 [FRONTEND] Usuario seleccionó: NO (quitar descuento)");
                        setState(() {
                          _mantenerDescuento = false;
                        });
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _mantenerDescuento == false 
                            ? const Color(0xFF87CEEB) 
                            : Colors.grey[300],
                        foregroundColor: _mantenerDescuento == false 
                            ? Colors.white 
                            : Colors.black,
                      ),
                      child: const Text('NO'),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () {
            print("🔍 [FRONTEND] Usuario canceló el pago");
            Navigator.pop(context, false);
          },
          child: const Text('Cancelar'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _registrarPago,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF87CEEB),
          ),
          child: _isLoading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Aceptar'),
        ),
      ],
    );
  }
}