from flask import Flask, request, jsonify
from agents import app as graph_app  # Rename to avoid conflict
import uuid

from dotenv import load_dotenv
import uuid

load_dotenv()

# app = Flask(__name__)

# @app.route("/health", methods=["GET"])
# def health():
#     return {"status": " Ready!"}

# @app.route("/submit_lead", methods=["POST"])
# def submit_lead():
#     data = request.json
#     message = data.get("message", "")
#     if not message:
#         return jsonify({"error": "No message"}), 400
    
#     # Invoke Graph
#     result = graph_app.invoke({
#         "raw_message": message
#     })
    
#     return jsonify({
#         "success": True,
#         "lead_id": result["lead_id"],
#         "score": result["score"],
#         "action": result["suggested_action"]
#     })

# @app.route("/leads", methods=["GET"])
# def list_leads():
#     # TODO: Query DB and return
#     return jsonify({"leads": "Implement query here for demo"})

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)



# ──────────────────────────────────────────────────────────────
# app.py   (copy-paste this entire file, replace the old one)
# ──────────────────────────────────────────────────────────────
from flask import Flask, request, jsonify, render_template_string
from agents import app as graph_app          # <-- LangGraph compiled graph
from database import get_db
from models import Lead
from dotenv import load_dotenv
import uuid

load_dotenv()

# app.py — FINAL VERSION
from flask import Flask, request, jsonify, render_template_string
from agents import app as graph_app
from database import get_db
from models import Lead
from dotenv import load_dotenv
import traceback

load_dotenv()
app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "Ready!"}, 200

@app.route("/submit_lead", methods=["POST"])
def submit_lead():
    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "No message"}), 400

        result = graph_app.invoke({"raw_message": message})

        return jsonify({
            "success": True,
            "lead_id": result.get("lead_id", -1),
            "score": result.get("score", 0.0),
            "action": result.get("suggested_action", "Manual review")
        })
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return jsonify({"error": "Agent failed"}), 500

@app.route("/leads")
def list_leads():
    try:
        with get_db() as db:
            leads = db.query(Lead).order_by(Lead.id.desc()).limit(10).all()
            return jsonify([{
                "id": l.id,
                "raw_message": (l.raw_message or "")[:100],
                "score": float(l.score) if l.score else 0.0,
                "action": l.suggested_action or "N/A",
                "created_at": l.created_at.isoformat() if l.created_at else None,
            } for l in leads])
    except Exception as e:
        print(f"LEADS ERROR: {e}")
        return jsonify({"leads": []}), 500

HOME_HTML = """
<!doctype html>
<html><head><meta charset="utf-8"><title>AI Lead Qualifier</title>
<style>
  body{font-family:system-ui;max-width:800px;margin:40px auto;padding:0 20px;}
  textarea{width:100%;height:120px;font-family:monospace;padding:10px;border:1px solid #ccc;border-radius:6px;}
  button{background:#0066cc;color:white;border:none;padding:12px 24px;font-size:1rem;border-radius:6px;cursor:pointer;margin-top:10px;}
  .result{margin-top:20px;padding:16px;background:#f0f8ff;border-radius:8px;}
  .error{color:#c00;font-weight:bold;}
  table{width:100%;border-collapse:collapse;margin-top:30px;}
  th,td{border:1px solid #ddd;padding:10px;}
  th{background:#f4f4f4;}
</style>
</head><body>
<h1>AI Lead Qualifier</h1>
<textarea id="msg" placeholder="e.g. electric SUV under €40k, family of 4, ASAP! John – john@test.com"></textarea><br>
<button onclick="qualify()">Qualify Lead</button>
<div id="output"></div>
<h2>Recent Leads</h2><div id="leads">Loading...</div>

<script>
async function qualify() {
  const msg = document.getElementById('msg').value.trim();
  if (!msg) return alert('Enter message');
  const out = document.getElementById('output');
  out.innerHTML = '<i>Thinking…</i>';
  try {
    const res = await fetch('/submit_lead', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    const data = await res.json();
    if (data.error) throw data.error;
    out.innerHTML = `<div class="result"><strong>Score:</strong> ${data.score}/10<br><strong>Action:</strong> ${data.action}<br><strong>Lead ID:</strong> ${data.lead_id}</div>`;
  } catch (e) {
    out.innerHTML = `<div class="error">Error: ${e}</div>`;
  }
}
async function loadLeads() {
  const res = await fetch('/leads');
  const {leads} = await res.json();
  document.getElementById('leads').innerHTML = leads.length ? `<table><tr><th>ID</th><th>Score</th><th>Action</th><th>Message</th></tr>${leads.map(l=>`<tr><td>${l.id}</td><td>${l.score}</td><td>${l.action}</td><td title="${l.raw_message}">${l.raw_message.slice(0,60)}${l.raw_message.length>60?'…':''}</td></tr>`).join('')}</table>` : '<p>No leads yet.</p>';
}
loadLeads();
</script>
</body></html>
"""

@app.route("/")
def index():
    return render_template_string(HOME_HTML)

if __name__ == "__main__":
    print("Starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)