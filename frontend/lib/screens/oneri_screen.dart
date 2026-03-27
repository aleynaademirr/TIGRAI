import 'package:flutter/material.dart';
import '../models/oneri.dart';
import '../models/icerik.dart';
import 'icerik_detail_screen.dart';
class OneriScreen extends StatelessWidget {
  final OneriResponse oneriResponse;
  const OneriScreen({super.key, required this.oneriResponse});
  @override
  Widget build(BuildContext context) {
    final isBenzer = oneriResponse.oneriTipi == 'benzer';
    return Scaffold(
      appBar: AppBar(
        title: const Text('Öneriler'),
      ),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            color: isBenzer ? Colors.green[100] : Colors.orange[100],
            child: Column(
              children: [
                Icon(
                  isBenzer ? Icons.thumb_up : Icons.explore,
                  size: 48,
                  color: isBenzer ? Colors.green : Colors.orange,
                ),
                const SizedBox(height: 8),
                Text(
                  isBenzer ? 'Benzer İçerikler' : 'Alternatif Öneriler',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: isBenzer ? Colors.green[900] : Colors.orange[900],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  oneriResponse.aciklama,
                  style: TextStyle(
                    fontSize: 14,
                    color: isBenzer ? Colors.green[800] : Colors.orange[800],
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
          Expanded(
            child: oneriResponse.oneriler.isEmpty
                ? const Center(
                    child: Text('Henüz öneri bulunmuyor'),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(8),
                    itemCount: oneriResponse.oneriler.length,
                    itemBuilder: (context, index) {
                      final icerik = oneriResponse.oneriler[index];
                      return _OneriCard(icerik: icerik);
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
class _OneriCard extends StatelessWidget {
  final Icerik icerik;
  const _OneriCard({required this.icerik});
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
      elevation: 4,
      color: const Color(0xFF1E1E1E),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => IcerikDetailScreen(icerikId: icerik.id),
            ),
          );
        },
        borderRadius: BorderRadius.circular(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                bottomLeft: Radius.circular(16),
              ),
              child: Container(
                width: 120,
                height: 180,
                color: Colors.grey[900],
                child: icerik.posterUrl != null && icerik.posterUrl!.isNotEmpty
                    ? Image.network(
                        icerik.posterUrl!,
                        fit: BoxFit.cover,
                        headers: const {
                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        },
                        errorBuilder: (context, error, stackTrace) {
                          return Container(
                            color: Colors.grey[850],
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.broken_image, color: Colors.white24, size: 30),
                                const SizedBox(height: 4),
                                Text(
                                  "Resim Yok",
                                  style: TextStyle(color: Colors.white24, fontSize: 10),
                                )
                              ],
                            ),
                          );
                        },
                        loadingBuilder: (context, child, loadingProgress) {
                          if (loadingProgress == null) return child;
                          return Center(
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              value: loadingProgress.expectedTotalBytes != null
                                  ? loadingProgress.cumulativeBytesLoaded /
                                      loadingProgress.expectedTotalBytes!
                                  : null,
                              color: Colors.amber,
                            ),
                          );
                        },
                      )
                    : Container(
                        color: Colors.grey[800],
                        child: const Icon(Icons.movie, color: Colors.white54, size: 40),
                      ),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      icerik.baslik,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: _getTypeColor(icerik.tur),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            icerik.tur,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ),
                        if (icerik.yil != null) ...[
                          const SizedBox(width: 8),
                          Text(
                            '${icerik.yil}',
                            style: const TextStyle(
                              fontSize: 14,
                              color: Colors.white70,
                            ),
                          ),
                        ],
                      ],
                    ),
                    if (icerik.kategoriler != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        icerik.kategoriler!,
                        style: const TextStyle(
                          fontSize: 13,
                          color: Colors.white60,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    if (icerik.imdbPuani != null) ...[
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          const Icon(Icons.star, color: Colors.amber, size: 18),
                          const SizedBox(width: 4),
                          Text(
                            icerik.imdbPuani!.toStringAsFixed(1),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.amber,
                            ),
                          ),
                          const Text(
                            ' / 10',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.white54,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const Padding(
              padding: EdgeInsets.all(16),
              child: Icon(Icons.arrow_forward_ios, size: 20, color: Colors.white54),
            ),
          ],
        ),
      ),
    );
  }
  Color _getTypeColor(String tur) {
    switch (tur.toLowerCase()) {
      case 'film':
        return Colors.red.shade700;
      case 'dizi':
        return Colors.blue.shade700;
      case 'kitap':
        return Colors.orange.shade700;
      default:
        return Colors.grey.shade700;
    }
  }
}