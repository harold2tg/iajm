import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../domain/models/miembro.dart';

class MiembrosRepository {
  final ApiClient _client;
  MiembrosRepository(this._client);

  Future<List<Miembro>> getByGrupo(String grupoId) async {
    final response = await _client.get(
      '/miembros/',
      queryParameters: {'grupo_id': grupoId},
    );
    final list = response.data as List;
    return list.map((e) => Miembro.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Miembro> getById(String id) async {
    final response = await _client.get('/miembros/$id');
    return Miembro.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Miembro> create(Map<String, dynamic> data) async {
    final response = await _client.post('/miembros/', data: data);
    return Miembro.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Miembro> update(String id, Map<String, dynamic> data) async {
    final response = await _client.patch('/miembros/$id', data: data);
    return Miembro.fromJson(response.data as Map<String, dynamic>);
  }
}

final miembrosRepositoryProvider = Provider<MiembrosRepository>((ref) {
  return MiembrosRepository(ref.watch(apiClientProvider));
});
