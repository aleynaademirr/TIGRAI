import 'package:flutter/material.dart';
import 'dart:ui';
import '../screens/home_screen.dart';
import '../screens/chatbot_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/admin_screen.dart';
import '../providers/app_provider.dart';
import 'package:provider/provider.dart';
class BottomNavBar extends StatelessWidget {
  final int currentIndex;
  const BottomNavBar({super.key, required this.currentIndex});
  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AppProvider>(context);
    final bool isAdmin = provider.currentUser?.isAdmin ?? false;
    return Container(
      margin: const EdgeInsets.only(left: 20, right: 20, bottom: 20),
      height: 70,
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E).withOpacity(0.9),
        borderRadius: BorderRadius.circular(35),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
        border: Border.all(color: Colors.white.withOpacity(0.1)),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(35),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildNavItem(context, 0, Icons.home_rounded, "Ana Sayfa"),
              _buildNavItem(context, 1, Icons.smart_toy_rounded, "Asistan"),
              _buildNavItem(context, 2, Icons.person_rounded, "Profil"),
              if (isAdmin)
                _buildNavItem(context, 3, Icons.admin_panel_settings_rounded, "Admin"),
            ],
          ),
        ),
      ),
    );
  }
  Widget _buildNavItem(BuildContext context, int index, IconData icon, String label) {
    final bool isSelected = currentIndex == index;
    return GestureDetector(
      onTap: () {
        if (isSelected) return;
        if (index == 0) {
          Navigator.pushReplacement(
            context,
            PageRouteBuilder(
              pageBuilder: (_, __, ___) => const HomeScreen(),
              transitionDuration: Duration.zero,
            ),
          );
        } else if (index == 1) {
          final provider = Provider.of<AppProvider>(context, listen: false);
          if (provider.currentUser != null) {
            Navigator.pushReplacement(
              context,
              PageRouteBuilder(
                pageBuilder: (_, __, ___) => ChatbotScreen(kullaniciId: provider.currentUser!.id),
                transitionDuration: Duration.zero,
              ),
            );
          }
        } else if (index == 2) {
          Navigator.pushReplacement(
            context,
            PageRouteBuilder(
              pageBuilder: (_, __, ___) => const ProfileScreen(),
              transitionDuration: Duration.zero,
            ),
          );
        } else if (index == 3) {
           Navigator.pushReplacement(
            context,
            PageRouteBuilder(
              pageBuilder: (_, __, ___) => const AdminScreen(),
              transitionDuration: Duration.zero,
            ),
          );
        }
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? Colors.amber.withOpacity(0.2) : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.amber : Colors.grey,
              size: 26,
            ),
            if (isSelected) ...[
              const SizedBox(height: 4),
              Text(
                label,
                style: const TextStyle(
                  color: Colors.amber,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }
}