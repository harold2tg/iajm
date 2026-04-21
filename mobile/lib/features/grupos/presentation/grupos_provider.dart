import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/grupos_repository.dart';
import '../domain/models/grupo.dart';

final gruposProvider = FutureProvider<List<Grupo>>((ref) {
  return ref.watch(gruposRepositoryProvider).getAll();
});

final grupoDetailProvider = FutureProvider.family<Grupo, String>((ref, id) {
  return ref.watch(gruposRepositoryProvider).getById(id);
});
