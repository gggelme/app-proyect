import 'package:flutter/material.dart';
import '../../services/clases_service.dart';
import '../../models/horario_clases.dart';
import '../form/inscription.dart';

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
    '09:00','10:00','11:00','12:00','13:00','14:00',
    '15:00','16:00','17:00','18:00','19:00','20:00','21:00',
  ];

  String? diaSeleccionado;

  // Cache datos
  Map<String, List<Clase>> clasesPorHora = {};

  // Control de expansión
  String? horaExpandida;

  bool cargando = false;

  final ClasesService _clasesService = ClasesService();

  Future<void> _handleTapHora(String hora) async {
    // Verificar si hay un día seleccionado
    if (diaSeleccionado == null) {
      // Mostrar mensaje de error intermitente
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('⚠️ Por favor, selecciona un día primero'),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 2),
        ),
      );
      
      // Efecto intermitente en el header de días
      setState(() {
        // Esto activará un pequeño feedback visual
      });
      
      return;
    }

    // Toggle (cerrar si ya está abierta)
    if (horaExpandida == hora) {
      setState(() {
        horaExpandida = null;
      });
      return;
    }

    setState(() {
      horaExpandida = hora;
    });

    // Si no está cargado → pedir a API
    if (!clasesPorHora.containsKey(hora)) {

      setState(() {
        cargando = true;
      });

      try {

        final clases = await _clasesService.getClases(
          diaSeleccionado!,
          hora,
        );

        setState(() {
          clasesPorHora[hora] = clases;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [

          /// BOTONES DE DIAS
          Padding(
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
                        clasesPorHora.clear();
                        horaExpandida = null;
                      } else {
                        diaSeleccionado = null;
                        clasesPorHora.clear();
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

          /// LISTA DE HORAS (SIEMPRE VISIBLE)
          Expanded(
            child: ListView.builder(
              itemCount: horas.length,
              itemBuilder: (context, index) {
                final hora = horas[index];
                final clases = clasesPorHora[hora];
                final expandido = horaExpandida == hora;
                final isDisabled = diaSeleccionado == null;

                return Card(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 4,
                  ),
                  child: Column(
                    children: [
                      ListTile(
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
                                isDisabled 
                                    ? '🔒 Selecciona un día para ver clases'
                                    : 'Tocar para ver clases',
                                style: TextStyle(
                                  color: isDisabled ? Colors.grey : null,
                                ),
                              )
                            : (clases == null
                                ? const Text('Cargando...')
                                : clases.isEmpty
                                    ? const Text('Sin clases')
                                    : Text('${clases.length} clase(s)')),
                        trailing: Icon(
                          expandido
                              ? Icons.keyboard_arrow_up
                              : Icons.keyboard_arrow_down,
                          color: isDisabled ? Colors.grey : null,
                        ),
                        tileColor: isDisabled ? Colors.grey.shade50 : Colors.grey.shade50,
                        enabled: !isDisabled,
                        onTap: () => _handleTapHora(hora),
                      ),

                      /// CONTENIDO EXPANDIDO
                      if (expandido && clases != null)
                        Column(
                          children: clases.map((clase) {
                            return Container(
                              width: double.infinity,
                              margin: const EdgeInsets.symmetric(
                                horizontal: 12,
                                vertical: 6,
                              ),
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade100,
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(
                                  color: Colors.grey.shade300,
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  /// Aula + profesor
                                  Text(
                                    "Aula ${clase.aula} - ${clase.profesor}",
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  /// Alumnos
                                  ...clase.alumnos.map(
                                    (alumno) => Padding(
                                      padding: const EdgeInsets.only(bottom: 4),
                                      child: Text(alumno),
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
      // BOTÓN FLOTANTE
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const InscriptionPage(),
            ),
          );
        },
        backgroundColor: const Color(0xFF87CEEB),
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}