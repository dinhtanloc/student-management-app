import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'home.dart';

class FaceLogin extends StatefulWidget {
  @override
  _FaceLoginState createState() => _FaceLoginState();
}

class _FaceLoginState extends State<FaceLogin> {
  CameraController? _controller;
  bool _isCameraInitialized = false; // Trạng thái khởi tạo camera

  @override
  void initState() {
    super.initState();
    initializeCamera();
  }

  Future<void> initializeCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        print("No cameras available.");
        return;
      }

      _controller = CameraController(
        cameras[0],
        ResolutionPreset.high,
      );

      await _controller!.initialize();
      setState(() {
        _isCameraInitialized = true; // Cập nhật trạng thái camera đã khởi tạo
      });
      print("Camera initialized successfully.");
    } catch (e) {
      print("Error initializing camera: $e");
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    try {
      final image = await _controller!.takePicture();
      final imageBytes = await image.readAsBytes();
      final base64Image = base64Encode(imageBytes);

      final url = 'http://10.0.2.2:5000/login';
      final headers = {'Content-Type': 'application/json'};
      final response = await http.post(
        Uri.parse(url),
        headers: headers,
        body: json.encode({'image': base64Image}),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        final message = result['message'];
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => Home()),
        );
      } else {
        final result = json.decode(response.body);
        final message = result['message'];
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      }
    } catch (e) {
      print("Error: $e");
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Đã xảy ra lỗi!")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Face Login'),
      ),
      body: _isCameraInitialized // Sử dụng trạng thái khởi tạo camera
          ? Column(
        children: [
          Expanded(child: CameraPreview(_controller!)),
          ElevatedButton(
            onPressed: _login,
            child: Text('Chụp và Đăng Nhập'),
          ),
        ],
      )
          : Center(child: CircularProgressIndicator()), // Hiển thị loading khi camera chưa khởi tạo
    );
  }
}
