// lib/presentation/pagos/pages/pagos_page.dart
import 'package:flutter/material.dart';
import '../../models/pago_model.dart';
import '../../services/pago_service.dart';
import '../widgets/registrar_pago_dialog.dart';
import 'editar_cuotas_page.dart'; // CAMBIAR EL IMPORT

class PagosPage extends StatefulWidget {
  const PagosPage({super.key});

  @override
  State<PagosPage> createState() => _PagosPageState();
}

class _PagosPageState extends State<PagosPage> {
  List<PagoPendienteModel> _pagosPendientes = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _cargarPagosPendientes();
  }

  Future<void> _cargarPagosPendientes() async {
    setState(() => _isLoading = true);
    try {
      final pagos = await PagoService.getPagosPendientes();
      setState(() {
        _pagosPendientes = pagos;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar pagos: $e')),
        );
      }
    }
  }

  void _onAlumnoTap(PagoPendienteModel pago) {
    showDialog(
      context: context,
      builder: (context) => RegistrarPagoDialog(
        alumnoId: pago.alumnoId,
        nombreAlumno: pago.nombreAlumno,
        totalPendiente: pago.totalAPagar,
        tieneDescuento: pago.tieneDescuento,
      ),
    ).then((resultado) {
      if (resultado == true) {
        _cargarPagosPendientes();
      }
    });
  }

  void _onEditPressed() {
    // Navegar a la página de editar cuotas
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const EditarCuotasPage(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pagos Pendientes'),
        backgroundColor: const Color(0xFFE0F6FF),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _cargarPagosPendientes,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _pagosPendientes.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.check_circle_outline,
                        size: 64,
                        color: Colors.green,
                      ),
                      SizedBox(height: 16),
                      Text(
                        'No hay pagos pendientes',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _pagosPendientes.length,
                  itemBuilder: (context, index) {
                    final pago = _pagosPendientes[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      elevation: 2,
                      child: InkWell(
                        onTap: () => _onAlumnoTap(pago),
                        borderRadius: BorderRadius.circular(12),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Expanded(
                                    child: Text(
                                      pago.nombreAlumno,
                                      style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  Text(
                                    '\$${pago.totalAPagar.toStringAsFixed(2)}',
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.red,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                pago.mesFormateado,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: _onEditPressed,
        backgroundColor: const Color(0xFF87CEEB),
        child: const Icon(Icons.edit, color: Colors.white),
      ),
    );
  }
}