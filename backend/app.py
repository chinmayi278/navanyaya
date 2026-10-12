import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ml_pipeline.extractor import extract_legal_data
from ml_pipeline.causal_engine import compute_strength_score

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            pass # clean up file if needed
            
    return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
