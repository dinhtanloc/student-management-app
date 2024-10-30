import 'package:flutter/material.dart';

class Home extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Trang Chủ"),
      ),
      body: Center(
        child: Text(
          "Ở trang Home",
          style: TextStyle(fontSize: 24),
        ),
      ),
    );
  }
}
