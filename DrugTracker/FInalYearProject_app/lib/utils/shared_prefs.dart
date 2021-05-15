import 'package:shared_preferences/shared_preferences.dart';
import 'package:drugtracker/constants/strings.dart';

class SharedPrefs {
  static SharedPreferences _sharedPrefs;
  init() async {
    if (_sharedPrefs == null) {
      _sharedPrefs = await SharedPreferences.getInstance();
    }
  }
  String get urllink => _sharedPrefs.getString(endpointURL) ?? "";

  set urllink(String value) {
    _sharedPrefs.setString(endpointURL, value);
  }
}

final sharedPrefs = SharedPrefs();