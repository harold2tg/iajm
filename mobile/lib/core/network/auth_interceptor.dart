import 'package:dio/dio.dart';
import '../storage/secure_storage.dart';

// Android emulator: http://10.0.2.2:8000/api/v1
// iOS simulator:    http://localhost:8000/api/v1
const String kBaseUrl = 'http://10.0.2.2:8000/api/v1';

class AuthInterceptor extends Interceptor {
  final SecureStorage storage;

  AuthInterceptor({required this.storage});

  @override
  void onRequest(
      RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await storage.read(kAccessToken);
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final refreshToken = await storage.read(kRefreshToken);
      if (refreshToken != null) {
        try {
          final dio = Dio();
          final response = await dio.post(
            '$kBaseUrl/auth/refresh',
            data: {'refresh_token': refreshToken},
          );
          final newAccess = response.data['access_token'] as String;
          final newRefresh =
              response.data['refresh_token'] as String? ?? refreshToken;
          await storage.write(kAccessToken, newAccess);
          await storage.write(kRefreshToken, newRefresh);

          final opts = err.requestOptions;
          opts.headers['Authorization'] = 'Bearer $newAccess';
          final retryDio = Dio();
          final retryResponse = await retryDio.fetch(opts);
          return handler.resolve(retryResponse);
        } catch (_) {
          await storage.clear();
        }
      } else {
        await storage.clear();
      }
    }
    handler.next(err);
  }
}
