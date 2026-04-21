import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/grupos_repository.dart';
import '../domain/models/grupo.dart';

class GrupoFormScreen extends ConsumerStatefulWidget {
  final Grupo grupo;
  const GrupoFormScreen({super.key, required this.grupo});

  @override
  ConsumerState<GrupoFormScreen> createState() => _GrupoFormScreenState();
}

class _GrupoFormScreenState extends ConsumerState<GrupoFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nombreCtrl;
  late final TextEditingController _edadMinCtrl;
  late final TextEditingController _edadMaxCtrl;
  late String _tipo;
  bool _loading = false;

  static const _tipos = ['infancia', 'adolescencia', 'juventud'];

  @override
  void initState() {
    super.initState();
    _nombreCtrl = TextEditingController(text: widget.grupo.nombre);
    _edadMinCtrl = TextEditingController(
        text: widget.grupo.edadMinima?.toString() ?? '');
    _edadMaxCtrl = TextEditingController(
        text: widget.grupo.edadMaxima?.toString() ?? '');
    _tipo = widget.grupo.tipo.isNotEmpty ? widget.grupo.tipo : _tipos.first;
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _edadMinCtrl.dispose();
    _edadMaxCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      final data = <String, dynamic>{
        'nombre': _nombreCtrl.text.trim(),
        'tipo': _tipo,
        if (_edadMinCtrl.text.isNotEmpty)
          'edad_minima': int.parse(_edadMinCtrl.text),
        if (_edadMaxCtrl.text.isNotEmpty)
          'edad_maxima': int.parse(_edadMaxCtrl.text),
      };
      await ref
          .read(gruposRepositoryProvider)
          .update(widget.grupo.id, data);
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
        title: const Text('Editar Grupo'),
        actions: [
          if (_loading)
            const Padding(
              padding: EdgeInsets.all(16),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            )
          else
            TextButton(
              onPressed: _save,
              child: const Text('Guardar'),
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nombreCtrl,
              decoration: const InputDecoration(labelText: 'Nombre *'),
              validator: (v) =>
                  v == null || v.trim().isEmpty ? 'Requerido' : null,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: _tipos.contains(_tipo) ? _tipo : _tipos.first,
              decoration: const InputDecoration(labelText: 'Tipo'),
              items: _tipos
                  // ignore: deprecated_member_use
                  .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                  .toList(),
              onChanged: (v) => setState(() => _tipo = v ?? _tipo),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _edadMinCtrl,
                    decoration:
                        const InputDecoration(labelText: 'Edad mínima'),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _edadMaxCtrl,
                    decoration:
                        const InputDecoration(labelText: 'Edad máxima'),
                    keyboardType: TextInputType.number,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
