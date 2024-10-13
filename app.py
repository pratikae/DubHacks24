from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from google.cloud import vision
import io
import random
from skin_conditions_data import skin_conditions_by_tone

app = Flask(__name__, static_folder='static')
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the path to your Google Cloud credentials JSON file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/key.json'

# Initialize the Vision client
vision_client = vision.ImageAnnotatorClient()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_skin_tone(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.image_properties(image=image)
    
    dominant_color = response.image_properties_annotation.dominant_colors.colors[0].color
    
    # Convert RGB to HSV
    r, g, b = dominant_color.red / 255.0, dominant_color.green / 255.0, dominant_color.blue / 255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val
    
    if max_val == min_val:
        h = 0
    elif max_val == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_val == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    s = 0 if max_val == 0 else (diff / max_val) * 100
    v = max_val * 100

    # Determine skin tone based on HSV
    if v < 20:
        return 'black'
    elif v > 80 and s < 30:
        return 'white'
    elif h < 25 and s > 20 and v > 40:
        return 'tan'
    elif h < 40 and s > 30 and v > 60:
        return 'yellow'
    else:
        return 'brown'

def analyze_image(image_path, age, sex):
    detected_skin_tone = detect_skin_tone(image_path)
    skin_condition_dataset = skin_conditions_by_tone[detected_skin_tone]

    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.label_detection(image=image)
    labels = response.label_annotations

    detected_features = [label.description.lower() for label in labels[:5]]
    possible_conditions = [cond for cond, desc in skin_condition_dataset.items() 
                           if any(feature in desc.lower() for feature in detected_features)]

    if not possible_conditions:
        possible_conditions = random.sample(list(skin_condition_dataset.keys()), 3)

    description = f"Clinical analysis for {age}-year-old {sex} with {detected_skin_tone} skin tone:\n\n"
    description += "Observed features:\n"
    for label in labels[:5]:
        description += f"- {label.description}\n"
    
    description += f"\nPossible conditions based on visual features for {detected_skin_tone} skin:\n"
    for condition in possible_conditions[:3]:
        description += f"- {condition.capitalize()}: {skin_condition_dataset[condition]}\n"
    
    description += "\nPlease note: This analysis is based on visual features only and should not be considered a definitive medical diagnosis. Consult with a dermatologist for accurate diagnosis and treatment."

    similar_image_data = []
    for i in range(3):
        condition = random.choice(list(skin_condition_dataset.keys()))
        similar_image_data.append({
            "url": f"https://example.com/image{i+1}.jpg",  # Replace with actual image URLs
            "label": f"{condition.capitalize()}: {skin_condition_dataset[condition]}"
        })

    result = {
        "description": description,
        "similar_images": similar_image_data
    }
    print("Returning result:", result)
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received upload request")
    if 'image' not in request.files:
        print("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    age = request.form.get('age')
    sex = request.form.get('sex')
    
    print(f"Received file: {file.filename}, age: {age}, sex: {sex}")
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        result = analyze_image(file_path, age, sex)
        
        return jsonify(result), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
