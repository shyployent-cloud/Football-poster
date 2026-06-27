from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import base64

import subprocess
import sys

# Install playwright browser on startup
subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=False)
subprocess.run([sys.executable, '-m', 'playwright', 'install-deps', 'chromium'], check=False)

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'status': 'running'})

@app.route('/create-image', methods=['POST'])
def create_image():
    return jsonify({'image_base64': ''})

@app.route('/create-stats-image', methods=['POST'])
def stats_image():
    data = request.json
    img = Image.new('RGB', (1200, 675), color='#0f0f19')
    encoded = ''
    output_path = '/tmp/stats.png'
    img.save(output_path)
    with open(output_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    return jsonify({'image_base64': encoded})

@app.route('/html-to-image', methods=['POST'])
def html_to_image():
    try:
        from playwright.sync_api import sync_playwright
        data = request.json
        html_content = data.get('html', '')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 640, 'height': 900})
            page.set_content(html_content)
            page.wait_for_timeout(500)
            screenshot = page.screenshot(full_page=True)
            browser.close()
        encoded = base64.b64encode(screenshot).decode()
        return jsonify({'image_base64': encoded})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
