import 'home_widget.dart';
import 'package:flutter/material.dart';
import 'utils/shared_prefs.dart';
// void main() => runApp(App());
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await sharedPrefs.init();
  runApp(App(),
  );
}
class App extends StatelessWidget {
 @override
 Widget build(BuildContext context) {
   return MaterialApp(
     title: 'D.O.T.',
     home: Home(),
   );
 }
}