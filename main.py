from playwright.sync_api import sync_playwright
import base64

@app.route('/html-to-image', methods=['POST'])
def html_to_image():
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
