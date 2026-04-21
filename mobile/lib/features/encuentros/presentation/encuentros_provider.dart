import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/encuentros_repository.dart';
import '../domain/models/encuentro.dart';
import '../domain/models/asistencia.dart';

final encuentrosProvider = FutureProvider.family<List<Encuentro>, String>((ref, grupoId) {
  return ref.watch(encuentrosRepositoryProvider).getByGrupo(grupoId);
});

final encuentroDetailProvider = FutureProvider.family<Encuentro, String>((ref, id) {
  return ref.watch(encuentrosRepositoryProvider).getById(id);
});

final asistenciaProvider = FutureProvider.family<List<Asistencia>, String>((ref, encuentroId) {
  return ref.watch(encuentrosRepositoryProvider).getAsistencia(encuentroId);
});

class PaseListaState {
  final Map<String, String> estados;
  final bool saving;
  final String? error;

  const PaseListaState({
    this.estados = const {},
    this.saving = false,
    this.error,
  });

  PaseListaState copyWith({
    Map<String, String>? estados,
    bool? saving,
    String? error,
  }) {
    return PaseListaState(
      estados: estados ?? this.estados,
      saving: saving ?? this.saving,
      error: error ?? this.error,
    );
  }
}

class PaseListaNotifier extends StateNotifier<PaseListaState> {
  final EncuentrosRepository _repo;
  final String encuentroId;

  PaseListaNotifier(this._repo, this.encuentroId) : super(const PaseListaState());

  void initFromAsistencia(List<Asistencia> asistencias) {
    final map = {for (final a in asistencias) a.miembroId: a.estado};
    state = state.copyWith(estados: map);
  }

  void toggleEstado(String miembroId, String nuevoEstado) {
    final updated = Map<String, String>.from(state.estados);
    updated[miembroId] = nuevoEstado;
    state = state.copyWith(estados: updated);
  }

  Future<void> guardar() async {
    state = state.copyWith(saving: true, error: null);
    try {
      final updates = state.estados.entries
          .map((e) => {'miembro_id': e.key, 'estado': e.value})
          .toList();
      await _repo.bulkUpdate(encuentroId, updates);
      state = state.copyWith(saving: false);
    } catch (e) {
      state = state.copyWith(saving: false, error: e.toString());
    }
  }
}

final paseListaProvider =
    StateNotifierProvider.family<PaseListaNotifier, PaseListaState, String>(
  (ref, encuentroId) => PaseListaNotifier(
    ref.watch(encuentrosRepositoryProvider),
    encuentroId,
  ),
);
