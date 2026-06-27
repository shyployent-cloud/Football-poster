from flask import Flask, request, jsonify
import os
import base64
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'status': 'running'})

@app.route('/create-image', methods=['POST'])
def create_image():
    return jsonify({'image_base64': ''})

@app.route('/html-to-image', methods=['POST'])
def html_to_image():
    try:
        import imgkit
        data = request.json
        html_content = data.get('html', '')
        img_bytes = imgkit.from_string(html_content, False)
        encoded = base64.b64encode(img_bytes).decode()
        return jsonify({'image_base64': encoded})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create-stats-image', methods=['POST'])
def stats_image():
    img = Image.new('RGB', (1200, 675), color='#0f0f19')
    output_path = '/tmp/stats.png'
    img.save(output_path)
    with open(output_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    return jsonify({'image_base64': encoded})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
