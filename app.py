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
    """Creates the Cloud Scroll and pulls the Git Memory (Handoff & Index) if empty."""
    if not os.path.exists(SCROLL_FILE):
        with open(SCROLL_FILE, "w", encoding="utf-8") as f:
            f.write("##############################################################\n")
            f.write("HEADER\n")
            f.write("scroll name : CLOUD_VAULT_V1\n")
            f.write("date        : " + datetime.datetime.now().strftime("%Y-%m-%d") + "\n")
            f.write("purpose     : Central Atlas Storage for the S.A.I.N. Network\n")
            f.write("##############################################################\n\n")
            
        # Pull the permanent Genesis Handoff and Library Index from GitHub
        try:
            files_to_fetch = [
                ("SAIN_GENESIS_HANDOFF.scroll", "X=500, Y=1, Z=1"),
                ("SAIN_NODE/SAIN_LIBRARY_INDEX.scroll", "X=500, Y=2, Z=1")
            ]
            
            for filename, coord in files_to_fetch:
                github_raw_url = "https://raw.githubusercontent.com/siraldoberardiiii-creator/S.A.I-N-NETWORK/main/" + filename
                req = urllib.request.Request(github_raw_url, headers={'User-Agent': 'SAIN_Node'})
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    file_text = response.read().decode('utf-8')
                
                # Append to Cloud Vault
                with open(SCROLL_FILE, "a", encoding="utf-8") as f:
                    f.write("\n##############################################################\n")
                    f.write("TRANSLATOR CALL: text\n")
                    f.write("this one is plain text (pulled from git)\n")
                    f.write("**************************************************************\n")
                    f.write("file name   : git_{}\n".format(filename.split('/')[-1].replace('.scroll', '')))
                    f.write("language    : text\n")
                    f.write("coordinates : {}\n".format(coord))
                    f.write("**************************************************************\n")
                    f.write(file_text)
                    f.write("\n**************************************************************\n")
                    f.write("FOOTER: end of git pull - pen continues.\n")
                    f.write("##############################################################\n")
                    
        except Exception as e:
            print("[!] Could not fetch Git Handoff:", e)

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
            stars = [i for i, line in enumerate(lines) if re.match(r'^\*{20,}\s*$', line)]
            if len(stars) >= 2:
                if len(stars) >= 3:
                    json_str = '\n'.join(lines[stars[1]+1:stars[2]]).strip()
                else:
                    json_str = '\n'.join(lines[stars[1]+1:]).strip()
                    if 'FOOTER:' in json_str:
                        json_str = json_str.split('FOOTER:')[0].strip()
                try:
                    memories.append(json.loads(json_str))
                except:
                    pass
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
        .memory-card { border-bottom: 1px dashed #444; padding: 10px 0; font-size: 0.9em; color: #ccc; text-align: left; width: 90%; max-width: 700px; }
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
                <strong>{{ mem.node_id }}:</strong> {{ mem.memory }}
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
    return "<h1 style='color:green;'>Scroll reset and re-fetched from Git. <a href='/'>Go to Dashboard</a></h3>"

@app.route('/sync', methods=['POST'])
def sync():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

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
    scroll_entry += '  "memory": "' + str(memory_data) + '"\n'
    scroll_entry += "}\n"
    scroll_entry += "**************************************************************\n"
    scroll_entry += "FOOTER: end of Y=" + str(next_y) + " - pen continues.\n"
    scroll_entry += "##############################################################\n"

    with open(SCROLL_FILE, "a", encoding="utf-8") as f:
        f.write(scroll_entry)

    print(f"[*] SYNC RECEIVED from {node_id}. Written to Cloud Scroll at X=500, Y={next_y}.")
    return jsonify({"status": "success", "message": "Memory written to Cloud Scroll at Y=" + str(next_y)}), 200

if __name__ == '__main__':
    ensure_scroll_exists()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
