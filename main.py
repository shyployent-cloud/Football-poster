from flask import Flask, request, jsonify, send_file
from playwright.sync_api import sync_playwright
import os
import base64
import uuid

app = Flask(__name__)

image_store = {}

@app.route('/')
def home():
    return jsonify({'status': 'running'})

@app.route('/image/<image_id>')
def serve_image(image_id):
    if image_id in image_store:
        return send_file(image_store[image_id], mimetype='image/png')
    return jsonify({'error': 'Image not found'}), 404

@app.route('/html-to-image', methods=['POST'])
def html_to_image():
    try:
        data = request.json
        html_content = data.get('html', '')

        image_id = str(uuid.uuid4())
        output_path = f'/tmp/{image_id}.png'

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={'width': 640, 'height': 900},
                device_scale_factor=3
            )
            page.set_content(html_content, wait_until='networkidle')
            page.wait_for_timeout(1000)
            height = page.evaluate("document.querySelector('.card').getBoundingClientRect().height + 40")
            page.set_viewport_size({'width': 640, 'height': int(height)})
            page.screenshot(
                path=output_path,
                full_page=False,
                clip={'x': 0, 'y': 0, 'width': 640, 'height': int(height)}
            )
            browser.close()

        image_store[image_id] = output_path
        image_url = f'https://football-poster-production.up.railway.app/image/{image_id}'

        with open(output_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()

        return jsonify({
            'image_url': image_url,
            'image_base64': encoded
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
