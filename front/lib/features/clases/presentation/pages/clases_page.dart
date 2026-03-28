// lib/pages/clases_page.dart
import 'package:flutter/material.dart';
import '../../services/clases_service_check.dart';
import '../../models/clase_model_check.dart';
import 'inscription_page_check.dart';
import 'edicion_check.dart';

class ClasesPage extends StatefulWidget {
  const ClasesPage({super.key});

  @override
  State<ClasesPage> createState() => _ClasesPageState();
}

class _ClasesPageState extends State<ClasesPage> {
  final List<String> dias = [
    'Lunes',
    'Martes',
    'Miércoles',
    'Jueves',
    'Viernes',
    'Sábado',
  ];

  final List<String> horas = [
    '09:00', '10:00', '11:00', '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00',
  ];

  String? diaSeleccionado;
  Map<String, Map<String, List<Clase>>> clasesPorHoraYAula = {};
  String? horaExpandida;
  bool cargando = false;

  final ClasesService _clasesService = ClasesService();

  Future<void> _handleTapHora(String hora) async {
    if (diaSeleccionado == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('⚠️ Por favor, selecciona un día primero'),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }

    if (horaExpandida == hora) {
      setState(() {
        horaExpandida = null;
      });
      return;
    }

    setState(() {
      horaExpandida = hora;
    });

    if (!clasesPorHoraYAula.containsKey(hora)) {
      setState(() {
        cargando = true;
      });

      try {
        final clases = await _clasesService.getClases(
          diaSeleccionado!,
          hora,
        );

        final Map<String, Map<int, Clase>> agrupadoPorAula = {};
        
        for (var clase in clases) {
          final aula = clase.aula ?? 'Sin aula';
          if (!agrupadoPorAula.containsKey(aula)) {
            agrupadoPorAula[aula] = {};
          }
          
          if (!agrupadoPorAula[aula]!.containsKey(clase.claseId)) {
            agrupadoPorAula[aula]![clase.claseId] = clase;
          } else {
            final claseExistente = agrupadoPorAula[aula]![clase.claseId]!;
            final alumnosCombinados = [...claseExistente.alumnos, ...clase.alumnos];
            agrupadoPorAula[aula]![clase.claseId] = Clase(
              alumnoClaseId: claseExistente.alumnoClaseId,
              claseId: claseExistente.claseId,
              nombreClase: claseExistente.nombreClase,
              profesorNombre: claseExistente.profesorNombre,
              duracion: claseExistente.duracion,
              horario: claseExistente.horario,
              alumnos: alumnosCombinados.toSet().toList(),
              aula: aula,
            );
          }
        }
        
        final Map<String, List<Clase>> resultado = {};
        agrupadoPorAula.forEach((aula, clasesPorId) {
          resultado[aula] = clasesPorId.values.toList();
        });
        
        setState(() {
          clasesPorHoraYAula[hora] = resultado;
          cargando = false;
        });
      } catch (e) {
        setState(() {
          cargando = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  void _abrirInscripcion() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const InscriptionPage(),
      ),
    ).then((_) {
      if (diaSeleccionado != null && horaExpandida != null) {
        _handleTapHora(horaExpandida!);
      }
    });
  }

  void _abrirEdicion() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const EditarPage(),
      ),
    ).then((_) {
      // Recargar datos si es necesario cuando vuelva
      if (diaSeleccionado != null && horaExpandida != null) {
        _handleTapHora(horaExpandida!);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // HEADER DE DIAS (Se queda arriba al hacer scroll general)
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.only(top: 20, bottom: 20),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                alignment: WrapAlignment.center,
                children: dias.map((dia) {
                  return FilterChip(
                    label: Text(dia),
                    selected: diaSeleccionado == dia,
                    onSelected: (selected) {
                      setState(() {
                        if (selected) {
                          diaSeleccionado = dia;
                          clasesPorHoraYAula.clear();
                          horaExpandida = null;
                        } else {
                          diaSeleccionado = null;
                          clasesPorHoraYAula.clear();
                          horaExpandida = null;
                        }
                      });
                    },
                    selectedColor: Colors.blue.shade100,
                    checkmarkColor: Colors.blue,
                  );
                }).toList(),
              ),
            ),
          ),

          // LISTADO DE HORAS CON STICKY HEADERS SIMULADOS
          ...horas.map((hora) {
            final expandido = horaExpandida == hora;
            final aulasMap = clasesPorHoraYAula[hora];
            final isDisabled = diaSeleccionado == null;

            return SliverMainAxisGroup(
              slivers: [
                // ESTA ES LA HORA QUE SE QUEDA FIJA
                SliverPersistentHeader(
                  pinned: true,
                  delegate: _StickyHoraDelegate(
                    hora: hora,
                    expandido: expandido,
                    isDisabled: isDisabled,
                    aulasMap: aulasMap,
                    onTap: () => _handleTapHora(hora),
                  ),
                ),
                
                // CONTENIDO DESPLEGABLE (Aulas y Clases)
                if (expandido)
                  SliverToBoxAdapter(
                    child: (aulasMap == null)
                        ? const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()))
                        : (aulasMap.isEmpty)
                            ? const Center(child: Padding(padding: EdgeInsets.all(20), child: Text('Sin clases')))
                            : Column(
                                children: aulasMap.entries.map((entry) {
                                  final aula = entry.key;
                                  final clases = entry.value;
                                  return _buildAulaCard(aula, clases);
                                }).toList(),
                              ),
                  ),
              ],
            );
          }),
          
          // Espacio final para que el FAB no tape el contenido
          const SliverToBoxAdapter(child: SizedBox(height: 100)),
        ],
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: _buildFABs(),
    );
  }

  // Widget de la tarjeta de Aula (Extraído para limpieza)
  Widget _buildAulaCard(String aula, List<Clase> clases) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade200, width: 2),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              borderRadius: const BorderRadius.only(topLeft: Radius.circular(10), topRight: Radius.circular(10)),
            ),
            child: Row(
              children: [
                Icon(Icons.meeting_room, size: 20, color: Colors.blue.shade800),
                const SizedBox(width: 8),
                Text('Aula $aula', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blue.shade900)),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
                  child: Text('${clases.length} clase${clases.length != 1 ? 's' : ''}', style: TextStyle(fontSize: 12, color: Colors.blue.shade700)),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Column(
              children: clases.map((clase) => _buildClaseItem(clase)).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildClaseItem(Clase clase) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [BoxShadow(color: Colors.grey.withOpacity(0.1), spreadRadius: 1, blurRadius: 3, offset: const Offset(0, 1))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(clase.nombreClase, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.person, size: 14, color: Colors.grey.shade600),
                        const SizedBox(width: 4),
                        Text(clase.profesorNombre, style: TextStyle(fontSize: 12, color: Colors.grey.shade700)),
                        const SizedBox(width: 12),
                        Icon(Icons.access_time, size: 14, color: Colors.grey.shade600),
                        const SizedBox(width: 4),
                        Text('${clase.duracion ?? 60} min', style: TextStyle(fontSize: 12, color: Colors.grey.shade700)),
                      ],
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(color: Colors.orange.shade100, borderRadius: BorderRadius.circular(12)),
                child: Text('${clase.alumnos.length} alumnos', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.orange.shade800)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Divider(height: 1),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: clase.alumnos.map((alumno) => Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(color: Colors.grey.shade200, borderRadius: BorderRadius.circular(16)),
              child: Text(alumno, style: const TextStyle(fontSize: 11)),
            )).toList(),
          ),
        ],
      ),
    );
  }

 Widget _buildFABs() {
  return LayoutBuilder(
    builder: (context, constraints) {
      final width = constraints.maxWidth;
      return SizedBox(
        width: width,
        height: 80,
        child: Stack(
          children: [
            // Botón izquierdo - Lápiz (Editar) - AHORA ABRE EditarPage
            Positioned(
              left: (width * 0.15) - 28,
              bottom: 5,
              child: FloatingActionButton(
                heroTag: 'btn_edit',
                onPressed: _abrirEdicion,  // ← Cambiado a _abrirEdicion
                backgroundColor: const Color(0xFF87CEEB),
                child: const Icon(Icons.edit, color: Colors.white),
              ),
            ),
            // Botón derecho - Más (Agregar inscripción)
            Positioned(
              right: (width * 0.15) - 28,
              bottom: 5,
              child: FloatingActionButton(
                heroTag: 'btn_add',
                onPressed: _abrirInscripcion,
                backgroundColor: const Color(0xFF87CEEB),
                child: const Icon(Icons.add, color: Colors.white),
              ),
            ),
          ],
        ),
      );
    },
  );
}
}

// DELEGADO PARA EL HEADER STICKY
class _StickyHoraDelegate extends SliverPersistentHeaderDelegate {
  final String hora;
  final bool expandido;
  final bool isDisabled;
  final Map? aulasMap;
  final VoidCallback onTap;

  _StickyHoraDelegate({
    required this.hora,
    required this.expandido,
    required this.isDisabled,
    required this.aulasMap,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Card(
      elevation: overlapsContent ? 4 : 1,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        title: Text(
          hora,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w500,
            color: isDisabled ? Colors.grey : Colors.black,
          ),
        ),
        subtitle: !expandido
            ? Text(
                isDisabled ? '🔒 Selecciona un día' : 'Tocar para ver clases',
                style: TextStyle(color: isDisabled ? Colors.grey : null),
              )
            : (aulasMap == null ? const Text('Cargando...') : Text('${aulasMap!.length} aula(s)')),
        trailing: Icon(
          expandido ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
          color: isDisabled ? Colors.grey : null,
        ),
        tileColor: Colors.grey.shade50,
        onTap: onTap,
      ),
    );
  }

  @override
  double get maxExtent => 72.0;
  @override
  double get minExtent => 72.0;
  @override
  bool shouldRebuild(covariant _StickyHoraDelegate oldDelegate) => true;
}