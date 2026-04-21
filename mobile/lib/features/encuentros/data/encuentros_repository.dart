import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../domain/models/encuentro.dart';
import '../domain/models/asistencia.dart';

class EncuentrosRepository {
  final ApiClient _client;
  EncuentrosRepository(this._client);

  Future<List<Encuentro>> getByGrupo(String grupoId) async {
    final response = await _client.get(
      '/encuentros/',
      queryParameters: {'grupo_id': grupoId},
    );
    final list = response.data as List;
    return list
        .map((e) => Encuentro.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Encuentro> getById(String id) async {
    final response = await _client.get('/encuentros/$id');
    return Encuentro.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<Asistencia>> getAsistencia(String encuentroId) async {
    final response =
        await _client.get('/encuentros/$encuentroId/asistencia');
    final list = response.data as List;
    return list
        .map((e) => Asistencia.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> bulkUpdate(
      String encuentroId, List<Map<String, dynamic>> updates) async {
    await _client.post(
        '/encuentros/$encuentroId/asistencia/bulk',
        data: {'asistencias': updates});
  }

  Future<Encuentro> create(Map<String, dynamic> data) async {
    final response = await _client.post('/encuentros/', data: data);
    return Encuentro.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Encuentro> update(String id, Map<String, dynamic> data) async {
    final response = await _client.patch('/encuentros/$id', data: data);
    return Encuentro.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Encuentro> cerrar(String id) async {
    final response = await _client.post('/encuentros/$id/cerrar');
    final data = response.data as Map<String, dynamic>;
    return Encuentro.fromJson(data['encuentro'] as Map<String, dynamic>);
  }

  Future<Encuentro> reabrir(String id, {String? motivo}) async {
    final response = await _client.post(
      '/encuentros/$id/reabrir',
      data: motivo != null ? {'motivo': motivo} : null,
    );
    return Encuentro.fromJson(response.data as Map<String, dynamic>);
  }
}

final encuentrosRepositoryProvider = Provider<EncuentrosRepository>((ref) {
  return EncuentrosRepository(ref.watch(apiClientProvider));
});
