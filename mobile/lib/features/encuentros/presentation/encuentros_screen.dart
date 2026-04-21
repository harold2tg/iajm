import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'encuentros_provider.dart';

class EncuentrosScreen extends ConsumerWidget {
  final String? grupoId;
  const EncuentrosScreen({super.key, this.grupoId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (grupoId == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Encuentros')),
        body: const Center(
          child: Text('Selecciona un grupo para ver sus encuentros'),
        ),
      );
    }

    final encuentrosAsync = ref.watch(encuentrosProvider(grupoId!));

    return Scaffold(
      appBar: AppBar(title: const Text('Encuentros')),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await context.push(
            '/grupos/$grupoId/encuentros/new',
          );
          if (result == true) {
            ref.invalidate(encuentrosProvider(grupoId!));
          }
        },
        child: const Icon(Icons.add),
      ),
      body: encuentrosAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (encuentros) => RefreshIndicator(
          onRefresh: () => ref.refresh(encuentrosProvider(grupoId!).future),
          child: encuentros.isEmpty
              ? const Center(child: Text('No hay encuentros registrados'))
              : ListView.builder(
                  itemCount: encuentros.length,
                  itemBuilder: (context, i) {
                    final e = encuentros[i];
                    final isClosed = e.estado == 'cerrado';
                    return ListTile(
                      leading: Icon(
                        isClosed ? Icons.lock : Icons.lock_open,
                        color: isClosed ? Colors.grey : Colors.green,
                      ),
                      title: Text(e.fecha),
                      subtitle: e.tema != null ? Text(e.tema!) : null,
                      trailing: Chip(
                        label: Text(e.estado,
                            style: const TextStyle(fontSize: 12)),
                        backgroundColor:
                            isClosed ? Colors.grey[200] : Colors.green[100],
                      ),
                      onTap: () => context.go(
                          '/grupos/$grupoId/encuentros/${e.id}'),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
