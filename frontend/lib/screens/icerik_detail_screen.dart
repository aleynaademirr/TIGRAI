import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../models/icerik.dart';
import '../services/api_service.dart';
import 'oneri_screen.dart';
class IcerikDetailScreen extends StatefulWidget {
  final int? icerikId;
  final Icerik? icerik; 
  final int? kullaniciId; 
  const IcerikDetailScreen({
    super.key, 
    this.icerikId,
    this.icerik,
    this.kullaniciId,
  });
  @override
  State<IcerikDetailScreen> createState() => _IcerikDetailScreenState();
}
class _IcerikDetailScreenState extends State<IcerikDetailScreen> {
  Icerik? _icerik;
  bool _isLoading = true;
  String? _error;
  int _selectedPuan = 5;
  List<dynamic> _yorumlar = [];
  bool _commentsLoading = true;
  final TextEditingController _commentController = TextEditingController();
  @override
  void initState() {
    super.initState();
    if (widget.icerik != null) {
      _icerik = widget.icerik;
      _isLoading = false;
      _loadComments(_icerik!.id);
    } else if (widget.icerikId != null) {
      _loadIcerik();
    }
  }
  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }
  Future<void> _loadIcerik() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final icerik = await ApiService.getIcerik(widget.icerikId!);
      setState(() {
        _icerik = icerik;
        _isLoading = false;
      });
      _loadComments(icerik.id);
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }
  Future<void> _loadComments(int icerikId) async {
    try {
      final comments = await ApiService.getIcerikYorumlari(icerikId);
      if (mounted) {
        setState(() {
          _yorumlar = comments;
          _commentsLoading = false;
        });
      }
    } catch (e) {
      print("Yorum yükleme hatası: $e");
      if (mounted) {
        setState(() {
          _commentsLoading = false;
        });
      }
    }
  }
  Future<void> _sendComment() async {
    if (_commentController.text.trim().isEmpty) return;
    final user = Provider.of<AppProvider>(context, listen: false).currentUser;
    if (user == null || _icerik == null) return;
    try {
      await ApiService.yorumYap(user.id, _icerik!.id, _commentController.text.trim());
      _commentController.clear();
      _loadComments(_icerik!.id); 
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Yorum gönderildi! ✅")),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Hata: $e")),
      );
    }
  }
  Future<void> _puanVerVeOneriAl() async {
    final idToUse = widget.icerikId ?? _icerik?.id;
    if (idToUse == null) return;
    final provider = Provider.of<AppProvider>(context, listen: false);
    if (provider.currentUser == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Önce giriş yapmalısınız')),
      );
      return;
    }
    final oneriResponse = await provider.puanVerVeOneriAl(
      idToUse,
      _selectedPuan,
    );
    if (oneriResponse != null && mounted) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => OneriScreen(oneriResponse: oneriResponse),
        ),
      );
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(provider.error ?? 'Bir hata oluştu')),
      );
    }
  }
  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (_error != null || _icerik == null) return Scaffold(body: Center(child: Text("Hata: $_error")));
    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      appBar: AppBar(
        title: Text(_icerik!.baslik, style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                if (_icerik!.posterUrl != null)
                  Container(
                    height: 300,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      image: DecorationImage(
                        image: NetworkImage(_icerik!.posterUrl!),
                        fit: BoxFit.cover,
                        colorFilter: ColorFilter.mode(Colors.black.withOpacity(0.7), BlendMode.darken),
                      ),
                    ),
                  )
                else
                   Container(height: 300, color: const Color(0xFF1E1E1E)),
                Positioned.fill(
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    alignment: Alignment.bottomLeft,
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [Colors.transparent, Color(0xFF121212)],
                      ),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Hero(
                          tag: 'poster_${_icerik!.id}',
                          child: Container(
                            width: 100,
                            height: 150,
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(12),
                              boxShadow: const [BoxShadow(blurRadius: 10, color: Colors.black45)],
                              color: Colors.grey[900],
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(12),
                              child: _icerik!.posterUrl != null
                                  ? Image.network(
                                      _icerik!.posterUrl!,
                                      fit: BoxFit.cover,
                                      headers: const {
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                                      },
                                      errorBuilder: (context, error, stackTrace) {
                                        return const Center(
                                          child: Icon(Icons.broken_image, color: Colors.white24, size: 40),
                                        );
                                      },
                                    )
                                  : const Center(child: Icon(Icons.movie, color: Colors.white54, size: 40)),
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _icerik!.baslik,
                                style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 5),
                              Text(
                                '${_icerik!.tur} • ${_icerik!.yil ?? "Bilinmiyor"}',
                                style: const TextStyle(color: Colors.white70, fontSize: 14),
                              ),
                              const SizedBox(height: 5),
                              if (_icerik!.imdbPuani != null)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: Colors.amber, 
                                    borderRadius: BorderRadius.circular(6)
                                  ),
                                  child: Text(
                                    '${_icerik!.tur == 'Kitap' ? 'Puan' : 'IMDB'} ${_icerik!.imdbPuani}',
                                    style: const TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 12),
                                  ),
                                ),
                            ],
                          ),
                        )
                      ],
                    ),
                  ),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Özet", style: TextStyle(color: Colors.amber[200], fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(
                    _icerik!.ozet ?? "Özet bulunamadı.",
                    style: const TextStyle(color: Colors.white70, fontSize: 15, height: 1.5),
                  ),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () async {
                            final provider = Provider.of<AppProvider>(context, listen: false);
                            if (provider.currentUser == null) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Önce giriş yapmalısınız')),
                              );
                              return;
                            }
                             try {
                               await provider.sadecePuanVer(
                                 _icerik!.id, 
                                 0 // 0 puan (İzlendi/Okundu olarak işaretle)
                               );
                               ScaffoldMessenger.of(context).showSnackBar(
                                 SnackBar(
                                   content: Text("Kütüphanenize '${_icerik!.tur == 'Kitap' ? 'Okundu' : 'İzlendi'}' olarak eklendi! ✅"), 
                                   backgroundColor: Colors.green
                                 ),
                               );
                             } catch (e) {
                               ScaffoldMessenger.of(context).showSnackBar(
                                 SnackBar(content: Text("Hata: $e"), backgroundColor: Colors.red),
                               );
                             }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green.withOpacity(0.2),
                            foregroundColor: Colors.green[200],
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            side: BorderSide(color: Colors.green.withOpacity(0.5)),
                          ),
                          child: Text(_icerik!.tur == 'Kitap' ? "Okundu" : "İzlendi"),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Consumer<AppProvider>(
                          builder: (context, provider, child) {
                            final isInWatchlist = provider.watchlist.any((item) => item['id'] == _icerik!.id);
                            final watchlistId = isInWatchlist 
                                ? provider.watchlist.firstWhere((item) => item['id'] == _icerik!.id)['watchlist_id'] 
                                : null;
                                
                            return ElevatedButton.icon(
                              onPressed: () async {
                                if (provider.currentUser == null) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Önce giriş yapmalısınız')),
                                  );
                                  return;
                                }
                                try {
                                  if (isInWatchlist) {
                                      await provider.removeFromWatchlist(watchlistId);
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(content: Text("Listeden çıkarıldı"), backgroundColor: Colors.grey),
                                      );
                                  } else {
                                      await provider.addToWatchlist(_icerik!.id);
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(content: Text("İzlenecekler listesine eklendi! 📌"), backgroundColor: Colors.blue),
                                      );
                                  }
                                } catch (e) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(content: Text("Hata: $e"), backgroundColor: Colors.red),
                                  );
                                }
                              },
                              icon: Icon(isInWatchlist ? Icons.bookmark_added : Icons.bookmark_add_outlined),
                              label: Text(isInWatchlist ? "Listede" : "Listeye Ekle"),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: isInWatchlist ? Colors.blue : Colors.blue.withOpacity(0.2),
                                foregroundColor: isInWatchlist ? Colors.white : Colors.blue[200],
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                side: BorderSide(color: Colors.blue.withOpacity(0.5)),
                              ),
                            );
                          }
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 30),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E1E1E),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.white10),
                    ),
                    child: Column(
                      children: [
                        const Text("Bu içeriği nasıl buldun?", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: List.generate(10, (index) {
                            int puan = index + 1;
                            return GestureDetector(
                              onTap: () => setState(() => _selectedPuan = puan),
                              child: Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 2.0),
                                child: Icon(
                                  puan <= _selectedPuan ? Icons.star : Icons.star_border,
                                  color: Colors.amber,
                                  size: 28,
                                ),
                              ),
                            );
                          }),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _selectedPuan <= 4 
                              ? "Anlaşıldı! Buna benzer içerikleri DAHAN AZ önereceğiz. 👎"
                              : _selectedPuan <= 6 
                                  ? "Ortalama olarak kaydedildi. 🤔" 
                                  : "Harika! Buna benzer içerikleri DAHA ÇOK göreceksin. 🌟",
                          style: TextStyle(
                            color: _selectedPuan <= 4 ? Colors.redAccent : (_selectedPuan <= 6 ? Colors.orangeAccent : Colors.greenAccent),
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: _puanVerVeOneriAl,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.amber,
                              foregroundColor: Colors.black,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                            child: const Text("Puanla & Benzerlerini Bul", style: TextStyle(fontWeight: FontWeight.bold)),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 30),
                  const Divider(color: Colors.white24),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text("Yorumlar (${_yorumlar.length})", style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                      Icon(Icons.comment, color: Colors.amber[200]),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Consumer<AppProvider>(
                    builder: (context, auth, _) {
                      if (auth.currentUser == null) return const SizedBox.shrink();
                      return Container(
                        margin: const EdgeInsets.only(bottom: 24),
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _commentController,
                                style: const TextStyle(color: Colors.white),
                                decoration: InputDecoration(
                                  hintText: "Bir yorum yaz...",
                                  hintStyle: TextStyle(color: Colors.grey[600]),
                                  filled: true,
                                  fillColor: const Color(0xFF1E1E1E),
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(30), borderSide: BorderSide.none),
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            IconButton(
                              onPressed: _sendComment,
                              icon: const Icon(Icons.send),
                              color: Colors.amber,
                              style: IconButton.styleFrom(backgroundColor: const Color(0xFF1E1E1E)),
                            )
                          ],
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 30),
                  const Divider(color: Colors.white10),
                  const SizedBox(height: 20),
                  if (_commentsLoading)
                    const Center(child: CircularProgressIndicator())
                  else if (_yorumlar.isEmpty)
                    Center(child: Text("Henüz yorum yok. İlk sen yaz!", style: TextStyle(color: Colors.grey[600])))
                  else
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _yorumlar.length,
                      itemBuilder: (context, index) {
                        final comment = _yorumlar[index];
                        return Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E1E1E),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  CircleAvatar(
                                    radius: 14,
                                    backgroundColor: Colors.amber,
                                    child: Text(
                                      comment['kullanici_adi'] != null ? comment['kullanici_adi'][0].toUpperCase() : '?',
                                      style: const TextStyle(color: Colors.black, fontSize: 12, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    comment['kullanici_adi'] ?? 'Anonim',
                                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                  ),
                                  const Spacer(),
                                  Text(
                                    comment['olusturma_tarihi'] != null 
                                      ? comment['olusturma_tarihi'].toString().split('T')[0] 
                                      : '',
                                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                comment['yorum_metni'] ?? '',
                                style: const TextStyle(color: Colors.white70),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 50),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}