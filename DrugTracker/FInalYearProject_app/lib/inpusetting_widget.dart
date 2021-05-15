import 'package:flutter/material.dart';
import 'utils/shared_prefs.dart';

// Define a custom Form widget.
class MyCustomForm extends StatefulWidget {
  @override
  MyCustomFormState createState() {
    return MyCustomFormState();
  }
}
class MyCustomFormState extends State<MyCustomForm> {
  final _formKey = GlobalKey<FormState>();
  final urlController=TextEditingController();

  @override
  Widget build(BuildContext context) {
    // Build a Form widget using the _formKey created above.
    String url = "";
    return Scaffold(
      body: Container(
          width: double.infinity,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children:[
              Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            Form(
              key: _formKey,
              child: Column(
                children: <Widget>[
                  TextFormField(
                    decoration: InputDecoration(labelText: 'Endpoint URL'),
                    keyboardType: TextInputType.url,
                    controller:urlController,
                    onFieldSubmitted: (value) {
                      setState(() {
                        url = value;
                      });
                    },
                    validator: (value) {
                      if (value.isEmpty) {
                        return 'Invalid email!';
                      }
                      return null;
                    },
                  ),
                  ElevatedButton(
                    onPressed: ()=> _navigationToRoute(url),
                    child: Text("submit"),
                  ),
                ],
              ),
            ),
            SizedBox(
              height: 20,
            ),
            Column(
              children: <Widget>[
                urlController.text.isEmpty ? Text("No data") : Text(url),
                SizedBox(
                  height: 10,
                ),
              ],
            )
          ],
        ),
      ),
    ]
    )
    )
    );
  }

  void _navigationToRoute(String url)
  {
    print(urlController.text);
    print(url);
    sharedPrefs.urllink=urlController.text; 
    print(sharedPrefs.urllink);
    print("Hi");
  }
}