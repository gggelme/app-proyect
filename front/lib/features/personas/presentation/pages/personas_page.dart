import 'package:flutter/material.dart';
import '../../services/personas_service.dart';
import '../../models/persona_model.dart';
import '../widgets/form_alumno.dart';
import '../widgets/form_profesor.dart';
import 'alumno_detail_page.dart';
import 'profesor_detail_page.dart';

class AlumnosPage extends StatefulWidget {
  const AlumnosPage({super.key});

  @override
  State<AlumnosPage> createState() => _AlumnosPageState();
}

class _AlumnosPageState extends State<AlumnosPage> {
  int _selectedTab = 0; // 0 = Alumnos, 1 = Profesores
  List<AlumnoModel> _alumnos = [];
  List<ProfesorModel> _profesores = [];
  List<AlumnoModel> _alumnosFiltrados = [];
  List<ProfesorModel> _profesoresFiltrados = [];
  bool _isLoading = false;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _cargarAlumnos();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _cargarAlumnos() async {
    setState(() => _isLoading = true);
    final alumnos = await PersonasService.getAlumnos();
    setState(() {
      _alumnos = alumnos;
      _alumnosFiltrados = alumnos;
      _isLoading = false;
    });
  }

  Future<void> _cargarProfesores() async {
    setState(() => _isLoading = true);
    final profesores = await PersonasService.getProfesores();
    setState(() {
      _profesores = profesores;
      _profesoresFiltrados = profesores;
      _isLoading = false;
    });
  }

  void _onTabChanged(int index) {
    setState(() => _selectedTab = index);
    _searchController.clear();
    _searchQuery = '';
    if (index == 0) {
      _cargarAlumnos();
    } else {
      _cargarProfesores();
    }
  }

  void _filterSearch(String query) {
    setState(() {
      _searchQuery = query;
      
      if (_selectedTab == 0) {
        if (query.isEmpty) {
          _alumnosFiltrados = _alumnos;
        } else {
          _alumnosFiltrados = _alumnos.where((alumno) =>
            alumno.nombApel.toLowerCase().contains(query.toLowerCase()) ||
            alumno.dni.contains(query)
          ).toList();
        }
      } else {
        if (query.isEmpty) {
          _profesoresFiltrados = _profesores;
        } else {
          _profesoresFiltrados = _profesores.where((profesor) =>
            profesor.nombApel.toLowerCase().contains(query.toLowerCase()) ||
            (profesor.alias?.toLowerCase().contains(query.toLowerCase()) ?? false)
          ).toList();
        }
      }
    });
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
          
          // Barra de búsqueda
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: _selectedTab == 0 ? 'Buscar alumno...' : 'Buscar profesor...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _filterSearch('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
                filled: true,
                fillColor: Colors.grey[50],
              ),
              onChanged: _filterSearch,
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
    if (_alumnosFiltrados.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              _searchQuery.isEmpty
                  ? 'No hay alumnos cargados'
                  : 'No se encontraron resultados para "$_searchQuery"',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: _alumnosFiltrados.length,
      itemBuilder: (context, index) {
        final alumno = _alumnosFiltrados[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 6),
          child: ListTile(
            onTap: () {
              // Navegar a la página de detalle del alumno
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => AlumnoDetailPage(
                    alumno: alumno,
                    onAlumnoActualizado: () {
                      // Recargar la lista cuando se actualice el alumno
                      if (_selectedTab == 0) _cargarAlumnos();
                    },
                  ),
                ),
              );
            },
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
            trailing: const Icon(Icons.chevron_right, color: Colors.grey),
          ),
        );
      },
    );
  }

  Widget _buildProfesoresList() {
    if (_profesoresFiltrados.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              _searchQuery.isEmpty
                  ? 'No hay profesores cargados'
                  : 'No se encontraron resultados para "$_searchQuery"',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: _profesoresFiltrados.length,
      itemBuilder: (context, index) {
        final profesor = _profesoresFiltrados[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 6),
          child: ListTile(
            onTap: () {
              // Navegar a la página de detalle del profesor
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => ProfesorDetailPage(
                    profesor: profesor,
                    onProfesorActualizado: () {
                      // Recargar la lista cuando se actualice el profesor
                      if (_selectedTab == 1) _cargarProfesores();
                    },
                  ),
                ),
              );
            },
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
            trailing: const Icon(Icons.chevron_right, color: Colors.grey),
          ),
        );
      },
    );
  }
  
}