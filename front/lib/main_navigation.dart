import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'features/home/presentation/pages/home_page.dart';
import 'features/personas/presentation/pages/personas_page.dart';
import 'features/clases/presentation/pages/clases_page.dart';
import 'features/pagos/presentation/pages/pagos_page.dart';
import 'core/constants/app_colors.dart';
import 'features/home/presentation/widgets/custom_app_bar.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _selectedIndex = 0;

  // Lista de páginas
  static const List<Widget> _pages = <Widget>[
    HomePage(),
    AlumnosPage(),
    ClasesPage(),
    PagosPage(),
  ];

  // Títulos para la AppBar
  final List<String> _titles = const [
    'Inicio',
    'Alumnos',
    'Clases',
    'Pagos',
  ];

  // Iconos SVG
  final List<String> _iconPaths = const [
    'assets/icons/home.svg',
    'assets/icons/person.svg',
    'assets/icons/book.svg',
    'assets/icons/money.svg',
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(
        title: 'Academia Irupe',
        onBackPressed: () {
          // En la página principal, el botón atrás podría salir de la app
          // o mostrar un mensaje
          debugPrint('Botón atrás presionado en main');
        },
      ),
      body: _pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        backgroundColor: AppColors.primaryBlue,
        selectedItemColor: Colors.white,
        unselectedItemColor: Colors.white.withOpacity(0.6),
        selectedFontSize: 12,
        unselectedFontSize: 12,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        items: List.generate(4, (index) {
          return BottomNavigationBarItem(
            icon: SvgPicture.asset(
              _iconPaths[index],
              colorFilter: ColorFilter.mode(
                _selectedIndex == index 
                    ? Colors.white 
                    : Colors.white.withOpacity(0.6),
                BlendMode.srcIn,
              ),
              width: 24,
              height: 24,
            ),
            label: _titles[index],
          );
        }),
      ),
    );
  }
}