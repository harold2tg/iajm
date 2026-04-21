import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'miembros_provider.dart';

class MiembrosScreen extends ConsumerWidget {
  final String? grupoId;
  const MiembrosScreen({super.key, this.grupoId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (grupoId == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Miembros')),
        body: const Center(
          child: Text('Selecciona un grupo para ver sus miembros'),
        ),
      );
    }

    final miembrosAsync = ref.watch(miembrosProvider(grupoId!));

    return Scaffold(
      appBar: AppBar(title: const Text('Miembros')),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await context.push(
            '/grupos/$grupoId/miembros/new',
          );
          if (result == true) {
            ref.invalidate(miembrosProvider(grupoId!));
          }
        },
        child: const Icon(Icons.person_add),
      ),
      body: miembrosAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (miembros) => RefreshIndicator(
          onRefresh: () => ref.refresh(miembrosProvider(grupoId!).future),
          child: miembros.isEmpty
              ? const Center(child: Text('No hay miembros en este grupo'))
              : ListView.builder(
                  itemCount: miembros.length,
                  itemBuilder: (context, i) {
                    final m = miembros[i];
                    return ListTile(
                      leading: const CircleAvatar(
                          child: Icon(Icons.person)),
                      title: Text(m.nombreCompleto),
                      subtitle: Text('${m.tipo} · ${m.edad} años'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => context.go(
                          '/grupos/$grupoId/miembros/${m.id}'),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
