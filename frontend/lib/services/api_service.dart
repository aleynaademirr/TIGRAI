import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../models/icerik.dart';
import '../models/kullanici.dart';
import '../models/puan.dart';
import '../models/oneri.dart';
import '../constants/app_constants.dart';
class ApiService {
static String baseUrl = AppConstants.baseUrl;
  static Future<List<Icerik>> getIcerikler({
    String? tur,
    int skip = 0,
    int limit = 500,
  }) async {
    try {
      String url = '$baseUrl/api/icerikler?skip=$skip&limit=$limit';
      if (tur != null) {
        url += '&tur=$tur';
      }
      if (kDebugMode) {
        print('[API] İçerikler çekiliyor: $url');
      }
      final response = await http.get(
        Uri.parse(url),
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('Bağlantı zaman aşımına uğradı. Backend çalışıyor mu kontrol edin: $baseUrl');
        },
      );
      if (kDebugMode) {
        print('[API] Response status: ${response.statusCode}');
        print('[API] Response body length: ${response.body.length}');
      }
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        if (kDebugMode) {
          print('[API] ${data.length} içerik alındı');
        }
        return data.map((json) => Icerik.fromJson(json)).toList();
      } else {
        throw Exception('İçerikler yüklenemedi: ${response.statusCode} - ${response.body}');
      }
    } on http.ClientException catch (e) {
      throw Exception('Bağlantı hatası: Backend\'e ulaşılamıyor ($baseUrl). Hata: $e');
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Icerik> getIcerik(int icerikId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/icerikler/$icerikId'));
      if (response.statusCode == 200) {
        return Icerik.fromJson(json.decode(response.body));
      } else {
        throw Exception('İçerik bulunamadı: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> register(String kullaniciAdi, String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'kullanici_adi': kullaniciAdi,
          'email': email,
          'password': password,
        }),
      );
      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'Kayıt başarısız: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'Giriş başarısız: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> forgotPassword(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/forgot-password'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'email': email}),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'İstek başarısız');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> resetPassword(String token, String newPassword) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/reset-password'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'token': token,
          'new_password': newPassword,
        }),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'Şifre sıfırlama başarısız');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> changePassword(int userId, String oldPassword, String newPassword) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/change-password'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_id': userId,
          'old_password': oldPassword,
          'new_password': newPassword,
        }),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'Şifre değiştirme başarısız');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Kullanici> getKullanici(int kullaniciId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/kullanicilar/$kullaniciId'));
      if (response.statusCode == 200) {
        return Kullanici.fromJson(json.decode(response.body));
      } else {
        throw Exception('Kullanıcı bulunamadı: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Puan> puanVer(int kullaniciId, int icerikId, int puan) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/puanlar'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'kullanici_id': kullaniciId,
          'icerik_id': icerikId,
          'puan': puan,
        }),
      );
      if (response.statusCode == 201) {
        return Puan.fromJson(json.decode(response.body));
      } else {
        throw Exception('Puan verilemedi: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<List<Puan>> getKullaniciPuanlari(int kullaniciId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/kullanicilar/$kullaniciId/puanlar'));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Puan.fromJson(json)).toList();
      } else {
        throw Exception('Puanlar yüklenemedi: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<OneriResponse> oneriAl(int kullaniciId, int icerikId, int puan) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/oneriler'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'kullanici_id': kullaniciId,
          'icerik_id': icerikId,
          'puan': puan,
        }),
      );
      if (response.statusCode == 200) {
        return OneriResponse.fromJson(json.decode(response.body));
      } else {
        throw Exception('Öneri alınamadı: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<List<Icerik>> getGenelOneriler(int kullaniciId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/kullanicilar/$kullaniciId/oneriler'));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Icerik.fromJson(json)).toList();
      } else {
        throw Exception('Öneriler yüklenemedi: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> sendChatMessage({
    required String message,
    required int kullaniciId,
  }) async {
    try {
      if (kDebugMode) {
        print('[CHATBOT] Mesaj gönderiliyor: $message');
      }
      final response = await http.post(
        Uri.parse('$baseUrl/api/chatbot/sohbet'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'message': message,
          'kullanici_id': kullaniciId,
        }),
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('Chatbot zaman aşımına uğradı');
        },
      );
      if (kDebugMode) {
        print('[CHATBOT] Response status: ${response.statusCode}');
      }
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (kDebugMode) {
          print('[CHATBOT] Cevap alındı: ${data['bot_response']}');
        }
        return data;
      } else {
        throw Exception('Chatbot cevap veremedi: ${response.statusCode}');
      }
    } on http.ClientException catch (e) {
      throw Exception('Chatbot bağlantı hatası: $e');
    } catch (e) {
      throw Exception('Chatbot hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> smartSearch({
    required String query,
    required int kullaniciId,
  }) async {
    try {
      if (kDebugMode) {
        print('[SMART_SEARCH] Arama: $query');
      }
      final response = await http.get(
        Uri.parse('$baseUrl/api/chatbot/akilli-arama?query=${Uri.encodeComponent(query)}&kullanici_id=$kullaniciId'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('Akıllı arama zaman aşımına uğradı');
        },
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (kDebugMode) {
          print('[SMART_SEARCH] ${data['total_results']} sonuç bulundu');
        }
        return data;
      } else {
        throw Exception('Akıllı arama başarısız: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Arama hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> yorumYap(int kullaniciId, int icerikId, String yorumMetni) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/yorumlar'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'kullanici_id': kullaniciId,
          'icerik_id': icerikId,
          'yorum_metni': yorumMetni,
        }),
      );
      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        throw Exception('Yorum yapılamadı: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<List<dynamic>> getIcerikYorumlari(int icerikId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/icerikler/$icerikId/yorumlar'));
      if (response.statusCode == 200) {
        return json.decode(response.body); 
      } else {
        throw Exception('Yorumlar yüklenemedi: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<List<dynamic>> getKullaniciGecmisi(int kullaniciId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/kullanicilar/$kullaniciId/gecmis'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Geçmiş yüklenemedi: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
  static Future<Map<String, dynamic>> getChatbotCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/chatbot/oneri-kategorileri'),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Kategoriler alınamadı: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Kategori hatası: $e');
    }
  }

  static Future<Map<String, dynamic>> addToWatchlist(int kullaniciId, int icerikId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/watchlist'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'kullanici_id': kullaniciId,
          'icerik_id': icerikId,
        }),
      );
      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'Listeye eklenemedi: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }

  static Future<Map<String, dynamic>> removeFromWatchlist(int watchlistId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/api/watchlist/$watchlistId'),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Listeden çıkarılamadı: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }

  static Future<List<dynamic>> getWatchlist(int kullaniciId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/kullanicilar/$kullaniciId/watchlist'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('İzlenecekler listesi yüklenemedi: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('API hatası: $e');
    }
  }
}