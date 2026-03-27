import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/icerik.dart';
import 'icerik_detail_screen.dart';
class SmartSearchScreen extends StatefulWidget {
  final int kullaniciId;
  const SmartSearchScreen({super.key, required this.kullaniciId});
  @override
  _SmartSearchScreenState createState() => _SmartSearchScreenState();
}
class _SmartSearchScreenState extends State<SmartSearchScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<Icerik> _searchResults = [];
  bool _isLoading = false;
  String? _explanation;
  String _lastQuery = '';
  final List<String> _searchSuggestions = [
    "90'lardan romantik komedi",
    "Üzücü dram filmi",
    "Bilim kurgu kitabı",
    "Komedi dizisi",
    "Aksiyon filmi",
    "Fantastik kitap",
    "2000'lerden film",
    "Mutlu hissettiren içerik",
    "Gerilim dizisi",
    "Klasik kitap"
  ];
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Akıllı Arama'),
        backgroundColor: Colors.green.shade700,
        elevation: 0,
      ),
      backgroundColor: Colors.grey[50],
      body: Column(
        children: [
          Container(
            padding: EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.green.shade700,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Doğal dille arama yapın',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Örnek: "90\'lardan romantik komedi" veya "üzgünken izlenecek film"',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                  ),
                ),
                SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _searchController,
                        style: TextStyle(color: Colors.black),
                        decoration: InputDecoration(
                          hintText: 'Arama yapın... (örn: "komedi filmi")',
                          hintStyle: TextStyle(color: Colors.grey[600]),
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide.none,
                          ),
                          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        ),
                        onSubmitted: (query) => _performSearch(query),
                      ),
                    ),
                    SizedBox(width: 12),
                    FloatingActionButton(
                      onPressed: _isLoading ? null : () {
                        final query = _searchController.text.trim();
                        if (query.isNotEmpty) {
                          _performSearch(query);
                        }
                      },
                      backgroundColor: Colors.white,
                      mini: true,
                      child: Icon(
                        _isLoading ? Icons.hourglass_empty : Icons.search,
                        color: Colors.green.shade700,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          if (_searchResults.isEmpty && !_isLoading && _lastQuery.isEmpty)
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Örnek Aramalar',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                    SizedBox(height: 16),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _searchSuggestions.map((suggestion) {
                        return ActionChip(
                          label: Text(suggestion),
                          onPressed: () {
                            _searchController.text = suggestion;
                            _performSearch(suggestion);
                          },
                          backgroundColor: Colors.green.shade50,
                          labelStyle: TextStyle(color: Colors.green.shade700),
                        );
                      }).toList(),
                    ),
                    SizedBox(height: 32),
                    _buildSearchTips(),
                  ],
                ),
              ),
            ),
          if (_isLoading)
            Expanded(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(color: Colors.green),
                    SizedBox(height: 16),
                    Text(
                      'AI arama yapıyor...',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          if (_searchResults.isNotEmpty)
            Expanded(
              child: Column(
                children: [
                  if (_explanation != null)
                    Container(
                      width: double.infinity,
                      padding: EdgeInsets.all(16),
                      margin: EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.green.shade200),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.lightbulb, color: Colors.green.shade700),
                              SizedBox(width: 8),
                              Text(
                                'AI Açıklaması',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.green.shade700,
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 8),
                          Text(
                            _explanation!,
                            style: TextStyle(color: Colors.green.shade800),
                          ),
                        ],
                      ),
                    ),
                  Expanded(
                    child: ListView.builder(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      itemCount: _searchResults.length,
                      itemBuilder: (context, index) {
                        return _buildResultCard(_searchResults[index]);
                      },
                    ),
                  ),
                ],
              ),
            ),
          if (_searchResults.isEmpty && !_isLoading && _lastQuery.isNotEmpty)
            Expanded(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.search_off,
                      size: 64,
                      color: Colors.grey[400],
                    ),
                    SizedBox(height: 16),
                    Text(
                      'Sonuç bulunamadı',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[600],
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      '"$_lastQuery" için uygun içerik yok',
                      style: TextStyle(color: Colors.grey[500]),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: () {
                        setState(() {
                          _lastQuery = '';
                          _searchController.clear();
                        });
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                      ),
                      child: Text('Yeni Arama Yap'),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
  Widget _buildResultCard(Icerik icerik) {
    return Container(
      margin: EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => IcerikDetailScreen(
                  icerik: icerik,
                  kullaniciId: widget.kullaniciId,
                ),
              ),
            );
          },
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: _getContentColor(icerik.tur),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    _getContentIcon(icerik.tur),
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        icerik.baslik,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      SizedBox(height: 4),
                      Row(
                        children: [
                          Container(
                            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: _getContentColor(icerik.tur).withOpacity(0.1),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              icerik.tur,
                              style: TextStyle(
                                fontSize: 12,
                                color: _getContentColor(icerik.tur),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          if (icerik.yil != null) ...[
                            SizedBox(width: 8),
                            Text(
                              '${icerik.yil}',
                              style: TextStyle(
                                color: Colors.grey[600],
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ],
                      ),
                      if (icerik.kategoriler != null) ...[
                        SizedBox(height: 4),
                        Text(
                          icerik.kategoriler!,
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 12,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                      if (icerik.imdbPuani != null) ...[
                        SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(Icons.star, color: Colors.amber, size: 14),
                            SizedBox(width: 4),
                            Text(
                              '${icerik.imdbPuani}/10',
                              style: TextStyle(
                                color: Colors.amber[700],
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
                Icon(Icons.chevron_right, color: Colors.grey),
              ],
            ),
          ),
        ),
      ),
    );
  }
  Widget _buildSearchTips() {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.tips_and_updates, color: Colors.blue.shade700),
              SizedBox(width: 8),
              Text(
                'Arama İpuçları',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue.shade700,
                ),
              ),
            ],
          ),
          SizedBox(height: 12),
          _buildTip('Ruh halinizi belirtin:', '"Üzgünüm, neşelendirici bir film"'),
          _buildTip('Zaman belirtin:', '"90\'lardan aksiyon filmi"'),
          _buildTip('Tür belirtin:', '"Romantik komedi öner"'),
          _buildTip('Benzerlik isteyin:', '"Inception benzeri film"'),
        ],
      ),
    );
  }
  Widget _buildTip(String title, String example) {
    return Padding(
      padding: EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('• ', style: TextStyle(color: Colors.blue.shade700)),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: TextStyle(color: Colors.blue.shade800, fontSize: 14),
                children: [
                  TextSpan(text: title, style: TextStyle(fontWeight: FontWeight.w600)),
                  TextSpan(text: ' $example'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
  void _performSearch(String query) async {
    if (query.trim().isEmpty) return;
    setState(() {
      _isLoading = true;
      _searchResults.clear();
      _explanation = null;
      _lastQuery = query;
    });
    try {
      final response = await ApiService.smartSearch(
        query: query,
        kullaniciId: widget.kullaniciId,
      );
      if (response['success'] == true) {
        final results = response['results'] as List;
        setState(() {
          _searchResults = results.map((json) => Icerik.fromJson(json)).toList();
          _explanation = response['explanation'];
          _isLoading = false;
        });
      } else {
        throw Exception('Arama başarısız');
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _searchResults.clear();
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Arama hatası: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  IconData _getContentIcon(String tur) {
    switch (tur.toLowerCase()) {
      case 'film':
        return Icons.movie;
      case 'dizi':
        return Icons.tv;
      case 'kitap':
        return Icons.book;
      default:
        return Icons.play_circle;
      }
  }
  Color _getContentColor(String tur) {
    switch (tur.toLowerCase()) {
      case 'film':
        return Colors.red.shade400;
      case 'dizi':
        return Colors.blue.shade400;
      case 'kitap':
        return Colors.orange.shade400;
      default:
        return Colors.grey.shade400;
    }
  }
}