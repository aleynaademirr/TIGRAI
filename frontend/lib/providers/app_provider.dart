import 'package:flutter/foundation.dart';
import '../models/icerik.dart';
import '../models/kullanici.dart';
import '../models/puan.dart';
import '../models/oneri.dart';
import '../services/api_service.dart';
class AppProvider with ChangeNotifier {
  Kullanici? _currentUser;
  List<Icerik> _icerikler = [];
  List<Puan> _kullaniciPuanlari = [];
  List<dynamic> _userHistory = [];
  List<dynamic> get userHistory => _userHistory;
  
  List<dynamic> _watchlist = [];
  List<dynamic> get watchlist => _watchlist;
  
  // Missing fields
  List<Icerik> _oneriler = [];
  bool _isLoading = false;
  String? _error;

  // Missing getters
  Kullanici? get currentUser => _currentUser;
  List<Icerik> get icerikler => _icerikler;
  List<Icerik> get oneriler => _oneriler;
  List<Puan> get kullaniciPuanlari => _kullaniciPuanlari;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> login(String email, String password) async {
    _setLoading(true);
    _error = null;
    try {
      final response = await ApiService.login(email, password);
      if (response.containsKey('user')) {
        _currentUser = Kullanici.fromJson(response['user']);
      } else {
        if (response.containsKey('id')) {
             _currentUser = Kullanici.fromJson(response);
        } else if (response.containsKey('user_id')) {
             _currentUser = await ApiService.getKullanici(response['user_id']);
        }
      }
      await Future.wait([
        loadIcerikler(),
        loadUserHistory(),
        loadWatchlist(),
      ]);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow; 
    } finally {
      _setLoading(false);
    }
  }

  Future<void> register(String kullaniciAdi, String email, String password) async {
    _setLoading(true);
    _error = null;
    try {
      await ApiService.register(kullaniciAdi, email, password);
      // Register sonrası auto-login yapılıyor mu? Genelde hayır, ama yapılırsa history boş gelir zaten.
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadIcerikler({String? tur}) async {
    _setLoading(true);
    _error = null;
    notifyListeners();
    try {
      if (tur != null) {
        final icerikler = await ApiService.getIcerikler(tur: tur, limit: 100);
        _icerikler = icerikler;
      } else {
        final results = await Future.wait([
          ApiService.getIcerikler(tur: 'Film', limit: 500),
          ApiService.getIcerikler(tur: 'Dizi', limit: 500),
          ApiService.getIcerikler(tur: 'Kitap', limit: 500),
        ]);
        _icerikler = [
          ...results[0],
          ...results[1],
          ...results[2],
        ];
        _icerikler.shuffle();
      }
      if (_icerikler.isEmpty) {
        _error = 'Henüz içerik bulunmuyor. Backend bağlantısını kontrol edin.';
      }
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _icerikler = [];
      notifyListeners();
    } finally {
      _setLoading(false);
      notifyListeners();
    }
  }

  List<Icerik> searchIcerikler(String query) {
    if (query.isEmpty) return _icerikler;
    final lowerQuery = query.toLowerCase();
    return _icerikler.where((icerik) {
      final baslikMatch = icerik.baslik.toLowerCase().contains(lowerQuery);
      final kategoriMatch = icerik.kategoriler?.toLowerCase().contains(lowerQuery) ?? false;
      final turMatch = icerik.tur.toLowerCase().contains(lowerQuery);
      return baslikMatch || kategoriMatch || turMatch;
    }).toList();
  }

  Future<OneriResponse?> puanVerVeOneriAl(int icerikId, int puan) async {
    if (_currentUser == null) {
      _error = 'Önce giriş yapmalısınız';
      notifyListeners();
      return null;
    }
    _setLoading(true);
    _error = null;
    try {
      await ApiService.puanVer(_currentUser!.id, icerikId, puan);
      await loadKullaniciPuanlari(); // Puanları güncelle
      await loadUserHistory(); // Geçmişi GÜNCELLE (Burası önemli)
      
      final oneriResponse = await ApiService.oneriAl(_currentUser!.id, icerikId, puan);
      _oneriler = oneriResponse.oneriler;
      notifyListeners();
      return oneriResponse;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return null;
    } finally {
      _setLoading(false);
    }
  }
  
  // YENİ METOT: Sadece puan verip (öneri almadan) çıkmak için de kullanılabilir
  Future<void> sadecePuanVer(int icerikId, int puan) async {
    if (_currentUser == null) return;
    try {
      await ApiService.puanVer(_currentUser!.id, icerikId, puan);
      await loadUserHistory(); // Profil güncellensin
      notifyListeners();
    } catch (e) {
      print("Puan verme hatası: $e");
    }
  }

  Future<void> loadKullaniciPuanlari() async {
    if (_currentUser == null) return;
    // _setLoading(true); // Loading user experience'ı bozabilir arka planda yapıyorsak
    try {
      _kullaniciPuanlari = await ApiService.getKullaniciPuanlari(_currentUser!.id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  Future<void> loadUserHistory() async {
    if (_currentUser == null) return;
    try {
      final history = await ApiService.getKullaniciGecmisi(_currentUser!.id);
      _userHistory = history;
      notifyListeners(); // Profile ekranını tetikler
    } catch (e) {
      print("History load error: $e");
    }
  }

  Future<void> loadGenelOneriler() async {
    if (_currentUser == null) return;
    _setLoading(true);
    _error = null;
    try {
      _oneriler = await ApiService.getGenelOneriler(_currentUser!.id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void logout() {
    _currentUser = null;
    _kullaniciPuanlari = [];
    _userHistory = [];
    _watchlist = [];
    _oneriler = [];
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  // Watchlist Methods
  Future<void> loadWatchlist() async {
    if (_currentUser == null) return;
    try {
      final list = await ApiService.getWatchlist(_currentUser!.id);
      _watchlist = list;
      notifyListeners();
    } catch (e) {
      print("Watchlist load error: $e");
    }
  }

  Future<void> addToWatchlist(int icerikId) async {
    if (_currentUser == null) return;
    try {
      await ApiService.addToWatchlist(_currentUser!.id, icerikId);
      await loadWatchlist();
      notifyListeners();
    } catch (e) {
      print("Watchlist add error: $e");
      rethrow;
    }
  }

  Future<void> removeFromWatchlist(int watchlistId) async {
    if (_currentUser == null) return;
    try {
      await ApiService.removeFromWatchlist(watchlistId);
      await loadWatchlist();
      notifyListeners();
    } catch (e) {
      print("Watchlist remove error: $e");
      rethrow;
    }
  }
}