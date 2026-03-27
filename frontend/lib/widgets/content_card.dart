import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/icerik.dart';
import '../constants/app_theme.dart';
import '../screens/icerik_detail_screen.dart';
class ContentCard extends StatelessWidget {
  final Icerik icerik;
  final double width;
  final double height;
  final bool showTitle;
  const ContentCard({
    super.key,
    required this.icerik,
    this.width = 120,
    this.height = 180,
    this.showTitle = true,
  });
  @override
  Widget build(BuildContext context) {
    Color accentColor = _getAccentColor(icerik.tur);
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => IcerikDetailScreen(icerikId: icerik.id)),
        );
      },
      child: Container(
        width: width,
        margin: const EdgeInsets.only(right: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: height,
              width: width,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                color: AppTheme.cardDark,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              clipBehavior: Clip.antiAlias,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  if (icerik.posterUrl != null && icerik.posterUrl!.isNotEmpty && icerik.posterUrl != 'null')
                    CachedNetworkImage(
                      imageUrl: icerik.posterUrl!,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => Container(color: AppTheme.cardDark),
                      errorWidget: (_, __, ___) => _buildPlaceholder(accentColor),
                    )
                  else
                    _buildPlaceholder(accentColor),
                  if (icerik.imdbPuani != null && icerik.imdbPuani! > 0)
                    Positioned(
                      top: 6,
                      right: 6,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.7),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: accentColor.withOpacity(0.5), width: 1),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.star, color: accentColor, size: 10),
                            const SizedBox(width: 2),
                            Text(
                              icerik.imdbPuani!.toStringAsFixed(1),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
            if (showTitle) ...[
              const SizedBox(height: 8),
              Text(
                icerik.baslik,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  height: 1.2,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  Widget _buildPlaceholder(Color color) {
    return Container(
      color: AppTheme.cardDark,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _getIcon(icerik.tur),
              color: color.withOpacity(0.5),
              size: 32,
            ),
          ],
        ),
      ),
    );
  }
  Color _getAccentColor(String tur) {
    if (tur == 'Film') return AppTheme.primaryGreen;
    if (tur == 'Dizi') return AppTheme.primaryBlue;
    return AppTheme.primaryOrange;
  }
  IconData _getIcon(String tur) {
    if (tur == 'Film') return Icons.movie;
    if (tur == 'Dizi') return Icons.tv;
    return Icons.book;
  }
}