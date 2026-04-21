import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/auth_provider.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/grupos/presentation/grupos_screen.dart';
import '../../features/grupos/presentation/grupo_detail_screen.dart';
import '../../features/grupos/presentation/grupo_form_screen.dart';
import '../../features/grupos/domain/models/grupo.dart';
import '../../features/miembros/presentation/miembros_screen.dart';
import '../../features/miembros/presentation/miembro_detail_screen.dart';
import '../../features/miembros/presentation/miembro_form_screen.dart';
import '../../features/miembros/domain/models/miembro.dart';
import '../../features/asesores/presentation/asesores_screen.dart';
import '../../features/asesores/presentation/asesor_detail_screen.dart';
import '../../features/asesores/presentation/asesor_form_screen.dart';
import '../../features/asesores/domain/models/asesor.dart';
import '../../features/encuentros/presentation/encuentros_screen.dart';
import '../../features/encuentros/presentation/encuentro_detail_screen.dart';
import '../../features/encuentros/presentation/encuentro_form_screen.dart';
import '../../features/encuentros/domain/models/encuentro.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final isAuthenticated = authState.status == AuthStatus.authenticated;
      final isLoggingIn = state.matchedLocation == '/login';

      if (!isAuthenticated && !isLoggingIn) return '/login';
      if (isAuthenticated && isLoggingIn) return '/grupos';
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),

      // ── Formularios fuera del shell (sin bottom nav) ──────────────────
      GoRoute(
        path: '/grupos/:grupoId/edit',
        builder: (context, state) => GrupoFormScreen(
          grupo: state.extra as Grupo,
        ),
      ),
      GoRoute(
        path: '/grupos/:grupoId/miembros/new',
        builder: (context, state) => MiembroFormScreen(
          grupoId: state.pathParameters['grupoId']!,
        ),
      ),
      GoRoute(
        path: '/grupos/:grupoId/miembros/:miembroId/edit',
        builder: (context, state) => MiembroFormScreen(
          grupoId: state.pathParameters['grupoId']!,
          miembro: state.extra as Miembro,
        ),
      ),
      GoRoute(
        path: '/grupos/:grupoId/encuentros/new',
        builder: (context, state) => EncuentroFormScreen(
          grupoId: state.pathParameters['grupoId']!,
        ),
      ),
      GoRoute(
        path: '/grupos/:grupoId/encuentros/:encuentroId/edit',
        builder: (context, state) => EncuentroFormScreen(
          grupoId: state.pathParameters['grupoId']!,
          encuentro: state.extra as Encuentro,
        ),
      ),
      GoRoute(
        path: '/asesores/new',
        builder: (context, state) => const AsesorFormScreen(),
      ),
      GoRoute(
        path: '/asesores/:asesorId/edit',
        builder: (context, state) => AsesorFormScreen(
          asesor: state.extra as Asesor,
        ),
      ),

      // ── Shell con bottom nav ──────────────────────────────────────────
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
        routes: [
          GoRoute(
            path: '/grupos',
            builder: (context, state) => const GruposScreen(),
            routes: [
              GoRoute(
                path: ':grupoId',
                builder: (context, state) => GrupoDetailScreen(
                  grupoId: state.pathParameters['grupoId']!,
                ),
                routes: [
                  GoRoute(
                    path: 'miembros',
                    builder: (context, state) => MiembrosScreen(
                      grupoId: state.pathParameters['grupoId'],
                    ),
                    routes: [
                      GoRoute(
                        path: ':miembroId',
                        builder: (context, state) => MiembroDetailScreen(
                          miembroId: state.pathParameters['miembroId']!,
                        ),
                      ),
                    ],
                  ),
                  GoRoute(
                    path: 'encuentros',
                    builder: (context, state) => EncuentrosScreen(
                      grupoId: state.pathParameters['grupoId'],
                    ),
                    routes: [
                      GoRoute(
                        path: ':encuentroId',
                        builder: (context, state) => EncuentroDetailScreen(
                          encuentroId: state.pathParameters['encuentroId']!,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
          GoRoute(
            path: '/asesores',
            builder: (context, state) => const AsesoresScreen(),
            routes: [
              GoRoute(
                path: ':asesorId',
                builder: (context, state) => AsesorDetailScreen(
                  asesorId: state.pathParameters['asesorId']!,
                ),
              ),
            ],
          ),
        ],
      ),
    ],
  );
});

class AppShell extends ConsumerWidget {
  final Widget child;
  const AppShell({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location = GoRouterState.of(context).matchedLocation;

    int currentIndex = 0;
    if (location.startsWith('/asesores')) currentIndex = 1;

    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (index) {
          switch (index) {
            case 0:
              context.go('/grupos');
              break;
            case 1:
              context.go('/asesores');
              break;
          }
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.group), label: 'Grupos'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Asesores'),
        ],
      ),
    );
  }
}
