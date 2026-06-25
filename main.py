from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import textwrap

app = Flask(__name__)

def create_event_image(player_name, event_type, score, team, minute, image_url=None):
    # Background colour based on event
    colours = {
        "GOAL": "#1a1a2e",
        "RED CARD": "#8B0000", 
        "FULL TIME": "#0d3b1e",
        "TRANSFER": "#1a3a5c"
    }
    bg_colour = colours.get(event_type, "#1a1a2e")
    
    # Create base image
    img = Image.new('RGB', (1200, 675), color=bg_colour)
    draw = ImageDraw.Draw(img)
    
    # Try to load player image
    if image_url:
        try:
            response = requests.get(image_url, timeout=5)
            player_img = Image.open(BytesIO(response.content))
            player_img = player_img.resize((400, 450))
            img.paste(player_img, (750, 112))
        except:
            pass
    
    # Event type banner
    event_colours = {"GOAL": "#00ff88", "RED CARD": "#ff3333", 
                     "FULL TIME": "#ffd700", "TRANSFER": "#00aaff"}
    accent = event_colours.get(event_type, "#ffffff")
    draw.rectangle([0, 0, 1200, 80], fill=accent)
    draw.text((600, 40), f"⚽ {event_type}", fill="#000000", anchor="mm")
    
    # Score
    draw.text((100, 150), score, fill="#ffffff")
    
    # Player name
    draw.text((100, 280), player_name.upper(), fill=accent)
    
    # Minute
    if minute:
        draw.text((100, 380), f"{minute}'", fill="#ffffff")
    
    # Team name
    draw.text((100, 450), team, fill="#aaaaaa")
    
    # Watermark
    draw.text((20, 640), "@YourAccountName", fill="#555555")
    
    # Save image
    output_path = "/tmp/event_image.png"
    img.save(output_path)
    return output_path

@app.route('/create-image', methods=['POST'])
def create_image():
    data = request.json
    image_path = create_event_image(
        player_name=data.get('player_name', 'Unknown'),
        event_type=data.get('event_type', 'GOAL'),
        score=data.get('score', '0-0'),
        team=data.get('team', ''),
        minute=data.get('minute', ''),
        image_url=data.get('image_url', None)
    )
    with open(image_path, 'rb') as f:
        import base64
        encoded = base64.b64encode(f.read()).decode()
    return jsonify({'image_base64': encoded})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
