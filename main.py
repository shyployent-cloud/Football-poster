from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import base64

app = Flask(__name__)

def get_flag_emoji(team_name):
    flags = {
        'Turkey': '🇹🇷', 'Türkiye': '🇹🇷',
        'USA': '🇺🇸', 'United States': '🇺🇸',
        'France': '🇫🇷', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'Germany': '🇩🇪', 'Spain': '🇪🇸',
        'Brazil': '🇧🇷', 'Argentina': '🇦🇷',
        'Portugal': '🇵🇹', 'Netherlands': '🇳🇱',
        'Italy': '🇮🇹', 'Belgium': '🇧🇪',
        'Croatia': '🇭🇷', 'Morocco': '🇲🇦',
        'Senegal': '🇸🇳', 'Iraq': '🇮🇶',
        'Norway': '🇳🇴', 'Australia': '🇦🇺',
        'Paraguay': '🇵🇾', 'Japan': '🇯🇵',
        'South Korea': '🇰🇷', 'Mexico': '🇲🇽',
        'Colombia': '🇨🇴', 'Uruguay': '🇺🇾',
        'Switzerland': '🇨🇭', 'Poland': '🇵🇱',
        'Denmark': '🇩🇰', 'Serbia': '🇷🇸',
    }
    return flags.get(team_name, '🏳️')

def create_stats_image(data):
    # Canvas size
    width, height = 1200, 900
    
    # Colors
    bg_color = (15, 15, 25)
    header_color = (20, 20, 40)
    accent_color = (0, 200, 100)
    text_color = (255, 255, 255)
    dim_color = (150, 150, 170)
    row_alt = (25, 25, 45)
    divider_color = (50, 50, 80)

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load fonts
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_tiny = ImageFont.load_default()

    # Header background
    draw.rectangle([0, 0, width, 160], fill=header_color)

    # Team names and score
    home_team = data.get('home_team', 'Home')
    away_team = data.get('away_team', 'Away')
    home_score = str(data.get('home_score', 0))
    away_score = str(data.get('away_score', 0))
    competition = data.get('competition', 'World Cup 2026')

    # Home team
    draw.text((60, 40), home_team, fill=text_color, font=font_medium)
    
    # Score in center
    score_text = f"{home_score} - {away_score}"
    draw.text((600, 30), score_text, fill=accent_color, font=font_large, anchor="mt")
    
    # Away team (right aligned)
    draw.text((1140, 40), away_team, fill=text_color, font=font_medium, anchor="ra")

    # Competition label
    draw.text((600, 120), competition, fill=dim_color, font=font_tiny, anchor="mt")

    # Divider line
    draw.rectangle([0, 160, width, 163], fill=accent_color)

    # Stats
    stats = data.get('stats', [])
    
    row_height = 58
    start_y = 180
    col_home = 180
    col_label = 600
    col_away = 1020

    for i, stat in enumerate(stats):
        y = start_y + (i * row_height)
        
        # Alternating row background
        if i % 2 == 0:
            draw.rectangle([0, y, width, y + row_height], fill=row_alt)

        # Home value
        home_val = str(stat.get('home', '-'))
        draw.text((col_home, y + 15), home_val, fill=text_color, font=font_small, anchor="mt")

        # Stat label in center
        label = stat.get('label', '')
        draw.text((col_label, y + 15), label, fill=dim_color, font=font_small, anchor="mt")

        # Away value
        away_val = str(stat.get('away', '-'))
        draw.text((col_away, y + 15), away_val, fill=text_color, font=font_small, anchor="mt")

    # Watermark
    draw.text((600, height - 30), "⚽ @YourXHandle", fill=dim_color, font=font_tiny, anchor="mb")

    # Save and encode
    output_path = "/tmp/stats_image.png"
    img.save(output_path)
    
    with open(output_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    
    return encoded

@app.route('/create-stats-image', methods=['POST'])
def stats_image():
    data = request.json
    encoded = create_stats_image(data)
    return jsonify({'image_base64': encoded})

@app.route('/create-image', methods=['POST'])
def create_image():
    return jsonify({'image_base64': ''})

@app.route('/')
def home():
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
