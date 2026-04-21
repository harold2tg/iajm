import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../domain/models/asesor.dart';

class AsesoresRepository {
  final ApiClient _client;
  AsesoresRepository(this._client);

  Future<List<Asesor>> getAll() async {
    final response = await _client.get('/asesores/');
    final list = response.data as List;
    return list.map((e) => Asesor.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Asesor> getById(String id) async {
    final response = await _client.get('/asesores/$id');
    return Asesor.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Asesor> create(Map<String, dynamic> data) async {
    final response = await _client.post('/asesores/', data: data);
    return Asesor.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Asesor> update(String id, Map<String, dynamic> data) async {
    final response = await _client.patch('/asesores/$id', data: data);
    return Asesor.fromJson(response.data as Map<String, dynamic>);
  }
}

final asesoresRepositoryProvider = Provider<AsesoresRepository>((ref) {
  return AsesoresRepository(ref.watch(apiClientProvider));
});
