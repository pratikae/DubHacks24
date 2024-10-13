from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from google.cloud import vision
import io

app = Flask(__name__, static_folder='static')
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the path to your Google Cloud credentials JSON file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/pratikaeswaran/Downloads/divine-vehicle-438505-f9-5317eb4aee49.json'

# Initialize the Vision client
vision_client = vision.ImageAnnotatorClient()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    age = request.form.get('age')
    sex = request.form.get('sex')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        result = analyze_image(file_path, age, sex)
        
        return jsonify(result), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

def analyze_image(image_path, age, sex):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Perform label detection
    response = vision_client.label_detection(image=image)
    labels = response.label_annotations

    # Generate a mock clinical description (replace this with actual analysis)
    description = "Analysis for {}-year-old {}: ".format(age, sex)
    description += ", ".join([label.description for label in labels[:3]])

    # Mock similar images (replace with actual similar image finding logic)
    similar_images = ["image1.jpg", "image2.jpg", "image3.jpg"]

    return {
        "description": description,
        "images": similar_images
    }

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)