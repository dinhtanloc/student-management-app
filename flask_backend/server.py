from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def verify_faces():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'message': 'No image provided'}), 400

    # Giải mã hình ảnh từ Base64
    image_data = base64.b64decode(data['image'])
    img1 = Image.open(io.BytesIO(image_data))
    print("dfklbjdflbjdflbjkdfl")


    img_path = "temp_image.jpg"
    with open(img_path, 'wb') as img_file:
        img_file.write(image_data)

    # Giả sử img2 là hình ảnh đã lưu trong cơ sở dữ liệu
    # Bạn có thể lấy hình ảnh từ cơ sở dữ liệu của bạn
    img2_path = 'data/user1.jpg'  # Thay bằng đường dẫn đến ảnh trong DB

    # Kiểm tra xem hai hình ảnh có khớp hay không
    result = DeepFace.verify(img1_path=img_path, img2_path=img2_path, model_name='VGG-Face', enforce_detection=False)

    if result["verified"]:
        return jsonify({'message': 'Faces Matched!'}), 200
    else:
        return jsonify({'message': "Faces Don't Match"}), 401


@app.route('/home', methods=['GET'])
def view():
    return jsonify({'message': 'Faces Matched!'}), 200
if __name__ == '__main__':
    app.run(debug=True, host="localhost")
