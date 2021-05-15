import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'utils/shared_prefs.dart';

class WebViewWidget extends StatefulWidget{
  WebViewWidgetState createState()=>new WebViewWidgetState();
}

class WebViewWidgetState extends State<WebViewWidget> {
String url=sharedPrefs.urllink;

 @override
 Widget build(BuildContext context) {
   return WebView(initialUrl: url,
        javascriptMode: JavascriptMode.unrestricted,
        );
 }}