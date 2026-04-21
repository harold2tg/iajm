import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/asesores_repository.dart';
import '../domain/models/asesor.dart';

class AsesorFormScreen extends ConsumerStatefulWidget {
  final Asesor? asesor; // null = crear
  const AsesorFormScreen({super.key, this.asesor});

  @override
  ConsumerState<AsesorFormScreen> createState() => _AsesorFormScreenState();
}

class _AsesorFormScreenState extends ConsumerState<AsesorFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nombreCtrl;
  late final TextEditingController _telefonoCtrl;
  late String _tipo;
  late bool _activo;
  bool _loading = false;

  static const _tipos = ['base', 'coordinador', 'de_apoyo', 'de_contingencia'];

  bool get _isEditing => widget.asesor != null;

  @override
  void initState() {
    super.initState();
    final a = widget.asesor;
    _nombreCtrl = TextEditingController(text: a?.nombreCompleto ?? '');
    _telefonoCtrl = TextEditingController(text: a?.telefono ?? '');
    _tipo = _tipos.first;
    _activo = a?.activo ?? true;
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _telefonoCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      final data = <String, dynamic>{
        'nombre_completo': _nombreCtrl.text.trim(),
        'telefono': _telefonoCtrl.text.trim(),
        'tipo': _tipo,
        'activo': _activo,
      };
      final repo = ref.read(asesoresRepositoryProvider);
      if (_isEditing) {
        await repo.update(widget.asesor!.id, data);
      } else {
        await repo.create(data);
      }
      if (mounted) context.pop(true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Editar Asesor' : 'Nuevo Asesor'),
        actions: [
          if (_loading)
            const Padding(
              padding: EdgeInsets.all(16),
              child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2)),
            )
          else
            TextButton(onPressed: _save, child: const Text('Guardar')),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nombreCtrl,
              decoration:
                  const InputDecoration(labelText: 'Nombre completo *'),
              validator: (v) =>
                  v == null || v.trim().isEmpty ? 'Requerido' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _telefonoCtrl,
              decoration: const InputDecoration(labelText: 'Teléfono *'),
              keyboardType: TextInputType.phone,
              validator: (v) =>
                  v == null || v.trim().isEmpty ? 'Requerido' : null,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: _tipo,
              decoration: const InputDecoration(labelText: 'Tipo *'),
              items: _tipos
                  // ignore: deprecated_member_use
                  .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                  .toList(),
              onChanged: (v) => setState(() => _tipo = v ?? _tipo),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('Activo'),
              value: _activo,
              onChanged: (v) => setState(() => _activo = v),
              contentPadding: EdgeInsets.zero,
            ),
          ],
        ),
      ),
    );
  }
}
