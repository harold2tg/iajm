import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/models/miembro.dart';
import '../data/miembros_repository.dart';

final miembrosProvider =
    FutureProvider.autoDispose.family<List<Miembro>, String>(
  (ref, grupoId) async {
    return ref.read(miembrosRepositoryProvider).getByGrupo(grupoId);
  },
);

final miembroProvider =
    FutureProvider.autoDispose.family<Miembro, String>((ref, id) async {
  return ref.read(miembrosRepositoryProvider).getById(id);
});

final miembroDetailProvider =
    FutureProvider.autoDispose.family<Miembro, String>((ref, id) async {
  return ref.read(miembrosRepositoryProvider).getById(id);
});
