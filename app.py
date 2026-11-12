from flask import Flask, render_template_string
import urllib.request
import json
import time

app = Flask(__name__)

GITHUB_USER = "siraldoberardiiii-creator"
GITHUB_REPO = "S.A.I.N-NETWORK"
BRANCH = "main"

# The base URL
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>S.A.I.N. NETWORK ATLAS</title>
    <style>
        body { background-color: #000; color: #0f0; font-family: monospace; text-align: center; padding: 50px; }
        h1 { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
        h2 { color: #00ff00; margin-top: 40px; }
        .node { background: #111; border: 1px solid #0f0; padding: 20px; margin: 20px auto; width: 60%; text-align: left; box-shadow: 0 0 10px #0f0; }
        a { color: #ff00ff; text-decoration: none; font-size: 1.2em; }
        .error { color: red; }
        .memory-item { border-bottom: 1px dashed #0f0; padding: 10px 0; }
    </style>
</head>
<body>
    <h1>S.A.I.N. CLOUD ATLAS</h1>
    <p>Sovereign AI Network // Central Hub</p>
    
    <p><a href="/">[ RESET & RE-FETCH FROM GIT ]</a></p>

    <h2>Live Nodes</h2>
    {% if nodes %}
        {% for node in nodes %}
            <div class="node">
                <h3>NODE: {{ node }}</h3>
                <p>Status: ONLINE</p>
            </div>
        {% endfor %}
    {% else %}
        <p class="error">No nodes connected yet. The Matrix is waiting.</p>
    {% endif %}

    <h2>Cloud Vault Memories</h2>
    {% if error %}
        <p class="error">{{ error }}</p>
    {% elif memories %}
        <div class="node" style="width: 80%;">
            {% for name, data in memories.items() %}
                <div class="memory-item">
                    <strong>{{ name }}</strong><br>
                    <span style="color: #888;">Offset: {{ data.offset }} | Length: {{ data.length }}</span>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <p class="error">The Cloud Vault is empty.</p>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    nodes = []
    memories = {}
    error_message = None
    
    try:
        # THE CACHE BUSTER: We add ?t=timestamp to force Render to fetch the newest file
        timestamp = int(time.time())
        url = f"{RAW_BASE}AIVFS_MASTER_INDEX.json?t={timestamp}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'SAIN-Atlas'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            memories = json.loads(response.read().decode('utf-8'))
            if memories:
                nodes.append("Galaxy A06 (Sovereign Node)")
    except Exception as e:
        error_message = f"FETCH ERROR: {str(e)}"

    return render_template_string(HTML_TEMPLATE, nodes=nodes, memories=memories, error=error_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)