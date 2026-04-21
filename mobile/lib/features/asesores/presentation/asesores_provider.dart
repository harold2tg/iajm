import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/asesores_repository.dart';
import '../domain/models/asesor.dart';

final asesoresProvider = FutureProvider<List<Asesor>>((ref) {
  return ref.watch(asesoresRepositoryProvider).getAll();
});

final asesorDetailProvider =
    FutureProvider.family<Asesor, String>((ref, id) {
  return ref.watch(asesoresRepositoryProvider).getById(id);
});
