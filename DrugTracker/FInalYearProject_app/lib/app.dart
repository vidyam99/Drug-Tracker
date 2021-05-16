import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

// class App extends StatelessWidget {
//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       home: LocationDetail(),
//       theme: ThemeData(textTheme: TextTheme(body1: Body1Style)),
//     );
//   }
// }

class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DrugTracker',
      home: Scaffold(
        appBar: AppBar(
          title: Text('D.O.T - Drug Origin Tracker'),
        ),
        body: WebView(initialUrl: "http://41f0018330cc.ngrok.io/",
        javascriptMode: JavascriptMode.unrestricted,
        )
      ),
    );
  }
}