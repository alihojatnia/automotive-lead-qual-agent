from flask import Flask, request, jsonify
from agents import app as graph_app  # Rename to avoid conflict
import uuid

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return {"status": "🚀 Ready!"}

@app.route("/submit_lead", methods=["POST"])
def submit_lead():
    data = request.json
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "No message"}), 400
    
    # Invoke Graph
    result = graph_app.invoke({
        "raw_message": message
    })
    
    return jsonify({
        "success": True,
        "lead_id": result["lead_id"],
        "score": result["score"],
        "action": result["suggested_action"]
    })

@app.route("/leads", methods=["GET"])
def list_leads():
    # TODO: Query DB and return
    return jsonify({"leads": "Implement query here for demo"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)