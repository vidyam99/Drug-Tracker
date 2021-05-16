import 'package:shared_preferences/shared_preferences.dart';
class SharedPreferencesHelper {
  static final String _linkURL = "https://www.google.com/";
  static Future<String> getURL() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();

    return prefs.getString(_linkURL) ?? 'https://www.google.com/';
  }
  static Future<bool> setLanguageCode(String value) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();

    return prefs.setString(_linkURL, value);
  }
}