import 'inpusetting_widget.dart';
import 'package:flutter/material.dart';
import 'qrscanner_widget.dart';
import 'webview_widget.dart';

class Home extends StatefulWidget {
 @override
 State<StatefulWidget> createState() {
    return _HomeState();
  }
}

class _HomeState extends State<Home> {
  int _currentIndex = 0;
 final List<Widget> _children = [
   WebViewWidget(),
   ScanQR(),
   MyCustomForm()
 ];

@override
 Widget build(BuildContext context) {
   return Scaffold(
     appBar: PreferredSize(
       preferredSize:Size.fromHeight(0.0),
     child:AppBar(
     )
     ),
     body: _children[_currentIndex], // new
     bottomNavigationBar: BottomNavigationBar(
       onTap: onTabTapped, // new
       currentIndex: _currentIndex, // new
       items: [
         new BottomNavigationBarItem(
           icon: Icon(Icons.home),
           label: 'Home',
         ),
         new BottomNavigationBarItem(
           icon: Icon(Icons.qr_code_scanner_rounded),
           label: 'Scan',
         ),
         new BottomNavigationBarItem(
           icon: Icon(Icons.settings),
           label: 'Settings',
         )
       ],
     ),
   );
 }
 void onTabTapped(int index) {
   setState(() {
     _currentIndex = index;
   });
 }
}
