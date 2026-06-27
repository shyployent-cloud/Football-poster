from flask import Flask, request, jsonify, send_file
import os
import base64
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

app = Flask(__name__)

# Store images in memory with a unique ID
image_store = {}

@app.route('/')
def home():
    return jsonify({'status': 'running'})

@app.route('/create-image', methods=['POST'])
def create_image():
    return jsonify({'image_base64': ''})

@app.route('/image/<image_id>')
def serve_image(image_id):
    if image_id in image_store:
        path = image_store[image_id]
        return send_file(path, mimetype='image/png')
    return jsonify({'error': 'Image not found'}), 404

@app.route('/html-to-image', methods=['POST'])
def html_to_image():
    try:
        data = request.json
        stats = data.get('stats', [])
        home_team = data.get('home_team', 'Home')
        away_team = data.get('away_team', 'Away')
        home_score = data.get('home_score', 0)
        away_score = data.get('away_score', 0)
        competition = data.get('competition', 'World Cup 2026')

        fig, ax = plt.subplots(figsize=(8, 12))
        fig.patch.set_facecolor('#0d1117')
        ax.set_facecolor('#0d1117')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, len(stats) + 4)
        ax.axis('off')

        ax.text(5, len(stats)+3.5, competition,
                ha='center', va='center', fontsize=10,
                color='#f0b429', fontweight='bold')
        ax.text(2, len(stats)+2.8, home_team,
                ha='center', va='center', fontsize=14,
                color='white', fontweight='bold')
        ax.text(5, len(stats)+2.8, f"{home_score}  -  {away_score}",
                ha='center', va='center', fontsize=22,
                color='white', fontweight='bold')
        ax.text(8, len(stats)+2.8, away_team,
                ha='center', va='center', fontsize=14,
                color='white', fontweight='bold')
        ax.axhline(y=len(stats)+2.3, xmin=0.05, xmax=0.95,
                   color='#f0b429', linewidth=1.5, alpha=0.5)
        ax.text(1.5, len(stats)+1.9, 'HOME',
                ha='center', fontsize=8, color='#3b82f6', fontweight='bold')
        ax.text(5, len(stats)+1.9, 'STAT',
                ha='center', fontsize=8, color='#888888', fontweight='bold')
        ax.text(8.5, len(stats)+1.9, 'AWAY',
                ha='center', fontsize=8, color='#f59e0b', fontweight='bold')

        for i, stat in enumerate(stats):
            y = len(stats) - i + 0.5
            bg_color = '#1a1f2e' if i % 2 == 0 else '#0d1117'
            bg = FancyBboxPatch((0.1, y-0.4), 9.8, 0.8,
                                boxstyle="round,pad=0.05",
                                facecolor=bg_color, edgecolor='none')
            ax.add_patch(bg)
            home_val = str(stat.get('home', '-'))
            away_val = str(stat.get('away', '-'))
            label = stat.get('label', '')
            try:
                h = float(str(home_val).replace('%', ''))
                a = float(str(away_val).replace('%', ''))
                total = h + a
                if total > 0:
                    home_pct = h / total
                    bar_y = y - 0.05
                    ax.barh(bar_y, home_pct*4, left=1, height=0.15,
                            color='#3b82f6', alpha=0.7)
                    ax.barh(bar_y, (1-home_pct)*4, left=1+home_pct*4,
                            height=0.15, color='#f59e0b', alpha=0.7)
            except:
                pass
            ax.text(1.5, y+0.15, home_val,
                    ha='center', va='center', fontsize=13,
                    color='#60a5fa', fontweight='bold')
            ax.text(5, y+0.15, label,
                    ha='center', va='center', fontsize=9,
                    color='#aaaaaa')
            ax.text(8.5, y+0.15, away_val,
                    ha='center', va='center', fontsize=13,
                    color='#fbbf24', fontweight='bold')

        ax.text(5, 0.2, '@YourXHandle ⚽',
                ha='center', fontsize=8, color='#444444')

        plt.tight_layout(pad=0.5)

        # Save with unique ID
        image_id = str(uuid.uuid4())
        output_path = f'/tmp/{image_id}.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                    facecolor='#0d1117', edgecolor='none')
        plt.close()

        # Store path and return URL
        image_store[image_id] = output_path
        image_url = f'https://football-poster-production.up.railway.app/image/{image_id}'

        # Also return base64 for backup
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
