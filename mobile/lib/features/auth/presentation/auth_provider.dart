import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/auth_repository.dart';
import '../domain/models/usuario.dart';

enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthState {
  final AuthStatus status;
  final Usuario? usuario;
  final String? error;

  const AuthState({
    this.status = AuthStatus.unknown,
    this.usuario,
    this.error,
  });

  AuthState copyWith({
    AuthStatus? status,
    Usuario? usuario,
    String? error,
    bool clearError = false,
  }) {
    return AuthState(
      status: status ?? this.status,
      usuario: usuario ?? this.usuario,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repo;

  AuthNotifier(this._repo) : super(const AuthState()) {
    _init();
  }

  Future<void> _init() async {
    try {
      final hasToken = await _repo.hasValidToken();
      if (hasToken) {
        final usuario = await _repo.getMe();
        state = AuthState(status: AuthStatus.authenticated, usuario: usuario);
      } else {
        state = const AuthState(status: AuthStatus.unauthenticated);
      }
    } catch (_) {
      // Token expirado o inválido — limpiarlo para no reintentar
      await _repo.logout();
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> login(String email, String password) async {
    state = const AuthState(status: AuthStatus.unknown);
    try {
      await _repo.login(email, password);
      final usuario = await _repo.getMe();
      state = AuthState(status: AuthStatus.authenticated, usuario: usuario);
    } catch (e) {
      state = AuthState(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
    }
  }

  Future<void> logout() async {
    await _repo.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void clearError() {
    if (state.error != null) {
      state = state.copyWith(clearError: true);
    }
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(authRepositoryProvider));
});
