import 'package:flutter/material.dart';
import '../../services/personas_service.dart';
import '../../models/persona_model.dart';
import '../widgets/form_alumno.dart';
import '../widgets/form_profesor.dart';

class AlumnosPage extends StatefulWidget {
  const AlumnosPage({super.key});

  @override
  State<AlumnosPage> createState() => _AlumnosPageState();
}

class _AlumnosPageState extends State<AlumnosPage> {
  int _selectedTab = 0; // 0 = Alumnos, 1 = Profesores
  List<AlumnoModel> _alumnos = [];
  List<ProfesorModel> _profesores = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _cargarAlumnos();
  }

  Future<void> _cargarAlumnos() async {
    setState(() => _isLoading = true);
    final alumnos = await PersonasService.getAlumnos();
    setState(() {
      _alumnos = alumnos;
      _isLoading = false;
    });
  }

  Future<void> _cargarProfesores() async {
    setState(() => _isLoading = true);
    final profesores = await PersonasService.getProfesores();
    setState(() {
      _profesores = profesores;
      _isLoading = false;
    });
  }

  void _onTabChanged(int index) {
    setState(() => _selectedTab = index);
    if (index == 0) {
      _cargarAlumnos();
    } else {
      _cargarProfesores();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Toggle Alumnos | Profesores
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
            child: Row(
              children: [
                _buildTabButton('Alumnos', 0),
                const SizedBox(width: 10),
                _buildTabButton('Profesores', 1),
              ],
            ),
          ),
          
          // Lista de alumnos o profesores
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _selectedTab == 0
                    ? _buildAlumnosList()
                    : _buildProfesoresList(),
          ),
        ],
      ),
      // 👇🏻 ESTO ES LO QUE HAY QUE AGREGAR (el botón flotante)
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          if (_selectedTab == 0) {
            // Navegar a formulario de alumno
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => FormAlumno(
                  onAlumnoCreado: () {
                    if (_selectedTab == 0) _cargarAlumnos();
                  },
                ),
              ),
            );
          } else {
            // Navegar a formulario de profesor
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => FormProfesor(
                  onProfesorCreado: () {
                    if (_selectedTab == 1) _cargarProfesores();
                  },
                ),
              ),
            );
          }
        },
        backgroundColor: const Color(0xFF87CEEB),
        child: const Icon(Icons.add, color: Colors.white),
      ),
      // 👆🏻 HASTA ACÁ EL CÓDIGO NUEVO
    );
  }

  Widget _buildTabButton(String text, int index) {
    final isSelected = _selectedTab == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => _onTabChanged(index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected 
                ? const Color(0xFF87CEEB)
                : Colors.grey.shade200,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Center(
            child: Text(
              text,
              style: TextStyle(
                fontFamily: 'Roboto',
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                color: isSelected ? Colors.white : Colors.black87,
                fontSize: 16,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAlumnosList() {
    if (_alumnos.isEmpty) {
      return const Center(
        child: Text('No hay alumnos cargados'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: _alumnos.length,
      itemBuilder: (context, index) {
        final alumno = _alumnos[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 6),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: const Color(0xFF87CEEB).withOpacity(0.2),
              child: Text(
                alumno.nombApel.substring(0, 1).toUpperCase(),
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF87CEEB),
                ),
              ),
            ),
            title: Text(
              alumno.nombApel,
              style: const TextStyle(
                fontFamily: 'Roboto',
                fontWeight: FontWeight.w500,
              ),
            ),
            subtitle: Text('DNI: ${alumno.dni}'),
            trailing: alumno.estadoActivo
                ? const Icon(Icons.check_circle, color: Colors.green)
                : const Icon(Icons.cancel, color: Colors.red),
          ),
        );
      },
    );
  }

  Widget _buildProfesoresList() {
    if (_profesores.isEmpty) {
      return const Center(
        child: Text('No hay profesores cargados'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: _profesores.length,
      itemBuilder: (context, index) {
        final profesor = _profesores[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 6),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: const Color(0xFF87CEEB).withOpacity(0.2),
              child: Text(
                profesor.nombApel.substring(0, 1).toUpperCase(),
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF87CEEB),
                ),
              ),
            ),
            title: Text(
              profesor.nombApel,
              style: const TextStyle(
                fontFamily: 'Roboto',
                fontWeight: FontWeight.w500,
              ),
            ),
            subtitle: profesor.alias != null 
                ? Text('Alias: ${profesor.alias}')
                : const Text('Profesor'),
            trailing: const Icon(Icons.chevron_right),
          ),
        );
      },
    );
  }
}