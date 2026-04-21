import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../../../core/storage/secure_storage.dart';
import '../domain/models/token_response.dart';
import '../domain/models/usuario.dart';

class AuthRepository {
  final ApiClient _client;
  final SecureStorage _storage;

  AuthRepository(this._client, this._storage);

  Future<TokenResponse> login(String email, String password) async {
    final response = await _client.post(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    final token = TokenResponse.fromJson(response.data as Map<String, dynamic>);
    await _storage.write(kAccessToken, token.accessToken);
    await _storage.write(kRefreshToken, token.refreshToken);
    return token;
  }

  Future<Usuario> getMe() async {
    final response = await _client.get('/usuarios/me');
    return Usuario.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> logout() async {
    await _storage.clear();
  }

  Future<bool> hasValidToken() async {
    final token = await _storage.read(kAccessToken);
    return token != null && token.isNotEmpty;
  }
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    ref.watch(apiClientProvider),
    ref.watch(secureStorageProvider),
  );
});
