from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

# Carrega as configurações do arquivo config.json
with open('config.json', 'r') as f:
    config = json.load(f)

DEEPL_API_KEY = config.get('deepl_api_key')
DEEPL_URL = 'https://api-free.deepl.com/v2/translate'

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    response = requests.post(
        DEEPL_URL,
        data={
            'auth_key': DEEPL_API_KEY,
            'text': text,
            'source_lang': 'IT',  # Italiano
            'target_lang': 'EN'   # Inglês
        }
    )

    if response.status_code != 200:
        return jsonify({'error': 'Translation failed', 'details': response.text}), 500

    result = response.json()
    translated_text = result['translations'][0]['text']
    return jsonify({'translated': translated_text})

if __name__ == '__main__':
    app.run(debug=True, port=5001)