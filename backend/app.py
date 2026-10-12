import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ml_pipeline.extractor import extract_legal_data
from ml_pipeline.causal_engine import compute_strength_score

FRONTEND_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'frontend')
)
app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path='')
CORS(app)  # Enable CORS for frontend requests

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/analyze', methods=['POST'])
def analyze_petition():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Phase A: Extraction
            extracted_data = extract_legal_data(filepath)
            
            # Phase B: Causal Engine (Strength Score)
            causal_results = compute_strength_score(extracted_data)
            
            return jsonify({
                'status': 'success',
                'extracted_data': extracted_data,
                'causal_inference': causal_results
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
            
    return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG') == '1',
    )
