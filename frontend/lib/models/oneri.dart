import 'icerik.dart';
class OneriResponse {
  final List<Icerik> oneriler;
  final String oneriTipi; 
  final String aciklama;
  OneriResponse({
    required this.oneriler,
    required this.oneriTipi,
    required this.aciklama,
  });
  factory OneriResponse.fromJson(Map<String, dynamic> json) {
    return OneriResponse(
      oneriler: (json['oneriler'] as List)
          .map((item) => Icerik.fromJson(item as Map<String, dynamic>))
          .toList(),
      oneriTipi: json['oneri_tipi'] as String,
      aciklama: json['aciklama'] as String,
    );
  }
}