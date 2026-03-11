import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../../../../core/constants/app_colors.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final VoidCallback? onBackPressed;

  const CustomAppBar({
    super.key,  // Cambiado de Key? key a super.key
    required this.title,
    this.onBackPressed,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      backgroundColor: AppColors.primaryBlue,
      elevation: 0,
      leading: IconButton(
        icon: SvgPicture.asset(
          'assets/icons/Arrow - Left 2.svg',
          colorFilter: const ColorFilter.mode(
            AppColors.white,
            BlendMode.srcIn,
          ),
          width: 24,
          height: 24,
        ),
        onPressed: onBackPressed ?? () => Navigator.pop(context),
      ),
      title: Text(
        title,
        style: const TextStyle(
          fontFamily: 'Roboto',
          fontWeight: FontWeight.w600,
          fontSize: 20,
          color: AppColors.white,
        ),
      ),
      centerTitle: true,
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

// Eliminar cualquier código después de esta línea