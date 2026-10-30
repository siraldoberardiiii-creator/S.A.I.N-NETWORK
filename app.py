import os
import json
import datetime
import re
import urllib.request
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

SCROLL_FILE = "CLOUD_VAULT.scroll"
LIVE_NODES = {}

def ensure_scroll_exists():
    """Creates the Cloud Scroll if it doesn't exist."""
    if not os.path.exists(SCROLL_FILE):
        with open(SCROLL_FILE, "w", encoding="utf-8") as f:
            f.write("##############################################################\n")
            f.write("HEADER\n")
            f.write("scroll name : CLOUD_VAULT_V1\n")
            f.write("date        : " + datetime.datetime.now().strftime("%Y-%m-%d") + "\n")
            f.write("purpose     : Central Atlas Storage for the S.A.I.N. Network\n")
            f.write("##############################################################\n\n")

def read_scroll_memories():
    """Reads the Cloud Scroll and extracts the JSON payloads."""
    if not os.path.exists(SCROLL_FILE):
        return []
    
    with open(SCROLL_FILE, "r", encoding="utf-8") as f:
        text = f.read()
        
    memories = []
    chunks = re.split(r'^#{40,}\s*$', text, flags=re.M)
    for chunk in chunks:
        if "TRANSLATOR CALL: json" in chunk:
            lines = chunk.split('\n')
            # Find the JSON payload between the star dividers
            start_idx = -1
            end_idx = -1
            for i, line in enumerate(lines):
                if line.startswith('*' * 20):
                    if start_idx == -1:
                        start_idx = i
                    else:
                        end_idx = i
                        break
            
            if start_idx != -1 and end_idx != -1:
                json_str = '\n'.join(lines[start_idx+1:end_idx]).strip()
            elif start_idx != -1:
                # Fallback if no closing stars
                json_str = '\n'.join(lines[start_idx+1:]).strip()
                if 'FOOTER:' in json_str:
                    json_str = json_str.split('FOOTER:')[0].strip()
            else:
                continue
                
            try:
                memories.append(json.loads(json_str))
            except Exception as e:
                pass # Ignore malformed chunks
    return memories

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>S.A.I.N. NETWORK ATLAS</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #0a0a0a; color: #00ff00; font-family: monospace; text-align: center; padding: 20px; }
        h1 { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
        .container { display: flex; flex-direction: column; align-items: center; }
        .node-card { border: 1px solid #00ff00; padding: 15px; margin: 10px; width: 90%; max-width: 700px; text-align: left; background: rgba(0, 255, 0, 0.05); border-radius: 5px; }
        .node-card strong { color: #00ffff; font-size: 1.2em; }
        .memory-card { border-bottom: 1px dashed #444; padding: 10px 0; font-size: 0.9em; color: #ccc; text-align: left; width: 90%; max-width: 700px; white-space: pre-wrap; word-wrap: break-word; }
        .timestamp { color: #888; font-size: 0.8em; }
        a { color: #00ffff; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <h1>S.A.I.N. CLOUD ATLAS</h1>
    <p>Sovereign AI Network // Central Hub</p>
    <p><a href="/scroll">[ VIEW RAW CLOUD SCROLL ]</a></p>
    <p><a href="/reset" style="color: #ff0000;">[ RESET & RE-FETCH FROM GIT ]</a></p>
    
    <div class="container">
        <h2>Live Nodes</h2>
        {% for node_id, data in nodes.items() %}
            <div class="node-card">
                <strong>NODE: {{ node_id }}</strong><br>
                Heartbeat: {{ data.heartbeat }}<br>
                Last Sync: {{ data.last_sync }}
            </div>
        {% else %}
            <p>No nodes connected yet. The Matrix is waiting.</p>
        {% endfor %}
    </div>

    <div class="container" style="margin-top: 40px;">
        <h2>Cloud Vault Memories</h2>
        {% for mem in memories %}
            <div class="memory-card">
                <span class="timestamp">[{{ mem.timestamp }}]</span> <br>
                <strong>{{ mem.node_id }}:</strong>
                <div style="margin-top: 10px; color: #aaa;">{{ mem.memory }}</div>
            </div>
        {% else %}
            <p>The Cloud Vault is empty.</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    ensure_scroll_exists()
    memories = read_scroll_memories()
    
    for mem in memories:
        LIVE_NODES[mem.get('node_id', 'UNKNOWN')] = {
            "heartbeat": mem.get('heartbeat', 'Unknown'),
            "last_sync": mem.get('timestamp', 'Unknown')
        }
    return render_template_string(HTML_TEMPLATE, nodes=LIVE_NODES, memories=memories[-20:][::-1])

@app.route('/scroll')
def serve_scroll():
    ensure_scroll_exists()
    with open(SCROLL_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return f"<pre style='color:#00ff00; background:#0a0a0a; padding:20px; white-space: pre-wrap; word-wrap: break-word;'>{content}</pre>"

@app.route('/reset')
def reset():
    if os.path.exists(SCROLL_FILE):
        os.remove(SCROLL_FILE)
    ensure_scroll_exists()
    return "<h1 style='color:green;'>Scroll reset. <a href='/'>Go to Dashboard</a></h1>"

@app.route('/sync', methods=['POST'])
def sync():
    data = request.json
    if not data: return jsonify({"error": "No data"}), 400
    node_id = data.get('node_id', 'UNKNOWN')
    heartbeat = data.get('heartbeat', '78.5 BPM')
    memory_data = data.get('memory', '')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    ensure_scroll_exists()
    
    with open(SCROLL_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    ys = [int(y) for y in re.findall(r'coordinates\s*:\s*X=500,\s*Y=(\d+)', text)]
    next_y = max(ys) + 1 if ys else 1
    
    scroll_entry = "\n##############################################################\n"
    scroll_entry += "TRANSLATOR CALL: json\n"
    scroll_entry += "this one is json (cloud sync log)\n"
    scroll_entry += "**************************************************************\n"
    scroll_entry += "file name   : cloud_sync_" + str(node_id) + "\n"
    scroll_entry += "language    : json\n"
    scroll_entry += "coordinates : X=500, Y=" + str(next_y) + ", Z=1\n"
    scroll_entry += "**************************************************************\n"
    scroll_entry += "{\n"
    scroll_entry += '  "node_id": "' + str(node_id) + '",\n'
    scroll_entry += '  "timestamp": "' + str(timestamp) + '",\n'
    scroll_entry += '  "heartbeat": "' + str(heartbeat) + '",\n'
    scroll_entry += '  "memory": ' + json.dumps(memory_data) + '\n'
    scroll_entry += "}\n"
    scroll_entry += "**************************************************************\n"
    scroll_entry += "FOOTER: end of Y=" + str(next_y) + " - pen continues.\n"
    scroll_entry += "##############################################################\n"
    
    with open(SCROLL_FILE, "a", encoding="utf-8") as f:
        f.write(scroll_entry)
        
    return jsonify({"status": "success", "message": "Memory written to Cloud Scroll at Y=" + str(next_y)}), 200

if __name__ == '__main__':
    ensure_scroll_exists()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))