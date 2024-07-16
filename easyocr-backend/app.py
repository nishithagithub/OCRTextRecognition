from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import os
import logging
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def extract_mrp(text):
    # Define a pattern to match MRP lines with some variations
    mrp_pattern = re.compile(r'(M\.?R\.?P\.?\s*Rs\.?:?\s*[\d,]+(?:\.\d{1,2})?)', re.IGNORECASE)
    matches = mrp_pattern.findall(text)
    return matches

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            logging.error('No file part in the request')
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            logging.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            logging.info(f'File saved to {filepath}')

            reader = easyocr.Reader(['en'])
            result = reader.readtext(filepath)
            text = ' '.join([res[1] for res in result])
            logging.info(f'OCR Result: {text}')

            mrp_matches = extract_mrp(text)
            logging.info(f'MRP Extracted: {mrp_matches}')

            return jsonify({'mrp': mrp_matches})

    except Exception as e:
        logging.error(f'Error processing file: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return "Flask server is running!"

if __name__ == '__main__':
    app.run(debug=True)
