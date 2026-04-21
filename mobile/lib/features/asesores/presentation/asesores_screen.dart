import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'asesores_provider.dart';

class AsesoresScreen extends ConsumerWidget {
  const AsesoresScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asesoresAsync = ref.watch(asesoresProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Asesores')),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await context.push('/asesores/new');
          if (result == true) {
            ref.invalidate(asesoresProvider);
          }
        },
        child: const Icon(Icons.person_add),
      ),
      body: asesoresAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (asesores) => RefreshIndicator(
          onRefresh: () => ref.refresh(asesoresProvider.future),
          child: asesores.isEmpty
              ? const Center(child: Text('No hay asesores registrados'))
              : ListView.builder(
                  itemCount: asesores.length,
                  itemBuilder: (context, i) {
                    final a = asesores[i];
                    return ListTile(
                      leading: const CircleAvatar(
                          child: Icon(Icons.person_outline)),
                      title: Text(a.nombreCompleto),
                      subtitle: Text(a.telefono ?? ''),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => context.go('/asesores/${a.id}'),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
