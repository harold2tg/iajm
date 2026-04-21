import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../domain/models/grupo.dart';

class GruposRepository {
  final ApiClient _client;
  GruposRepository(this._client);

  Future<List<Grupo>> getAll() async {
    final response = await _client.get('/grupos/');
    final list = response.data as List;
    return list.map((e) => Grupo.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Grupo> getById(String id) async {
    final response = await _client.get('/grupos/$id');
    return Grupo.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Grupo> update(String id, Map<String, dynamic> data) async {
    final response = await _client.patch('/grupos/$id', data: data);
    return Grupo.fromJson(response.data as Map<String, dynamic>);
  }
}

final gruposRepositoryProvider = Provider<GruposRepository>((ref) {
  return GruposRepository(ref.watch(apiClientProvider));
});
