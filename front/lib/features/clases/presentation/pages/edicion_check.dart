// lib/features/clases/presentation/pages/editar_page.dart
import 'package:flutter/material.dart';
import 'edicion_clases.dart';
import 'edicion_sesiones.dart';

enum TipoEdicion { sesion, clase }

class EditarPage extends StatefulWidget {
  const EditarPage({super.key});

  @override
  State<EditarPage> createState() => _EditarPageState();
}

class _EditarPageState extends State<EditarPage> {
  TipoEdicion? _tipoSeleccionado;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Editar'),
        backgroundColor: const Color(0xFF87CEEB),
        toolbarHeight: 50,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          /// BOTONES DE SELECCIÓN
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: _buildBotonSeleccion(
                    texto: 'Sesión',
                    tipo: TipoEdicion.sesion,
                    icon: Icons.calendar_today,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildBotonSeleccion(
                    texto: 'Clase',
                    tipo: TipoEdicion.clase,
                    icon: Icons.class_,
                  ),
                ),
              ],
            ),
          ),
          
          /// CONTENIDO PRINCIPAL - CONTAINER CON ALTURA RESTRINGIDA
          Expanded(
            child: _tipoSeleccionado == null
                ? _buildMensajeSeleccion()
                : _tipoSeleccionado == TipoEdicion.sesion
                    ? _buildFormularioSesion()
                    : _buildFormularioClase(),  // ← Esto ya no está dentro de SingleChildScrollView
          ),
        ],
      ),
    );
  }

  Widget _buildBotonSeleccion({
    required String texto,
    required TipoEdicion tipo,
    required IconData icon,
  }) {
    final isSelected = _tipoSeleccionado == tipo;
    
    return ElevatedButton(
      onPressed: () {
        setState(() {
          _tipoSeleccionado = tipo;
        });
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected ? Colors.blue : Colors.grey.shade300,
        foregroundColor: isSelected ? Colors.white : Colors.black87,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 18),
          const SizedBox(width: 8),
          Text(texto, style: const TextStyle(fontSize: 14)),
        ],
      ),
    );
  }

  Widget _buildMensajeSeleccion() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.edit_note,
            size: 48,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 12),
          Text(
            'Seleccionar edición',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Elija entre Sesión o Clase para editar',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFormularioSesion() {
    return const EditarSesionesPage();
  }

  Widget _buildFormularioClase() {
    // IMPORTANTE: EditarClasesPage ya tiene su propio ListView
    // No necesita estar envuelto en otro scroll
    return const EditarClasesPage();
  }
}