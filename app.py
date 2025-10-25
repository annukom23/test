from flask import Flask, request, jsonify, abort
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Server is running! Use /status for token check."

@app.route("/status", methods=["GET"])
def status():
    if not os.path.exists("activation.txt"):
        return ("", 404)
    with open("activation.txt", "r") as f:
        token = f.read().strip()
    return token, 200

@app.route("/admin/set", methods=["POST"])
def admin_set():
    key = request.headers.get("X-Admin-Key")
    if key != os.environ.get("APP_SECRET", "mySecret123"):
        return abort(401)
    j = request.get_json(force=True)
    token = j.get("token", "").strip()
    if not token:
        return abort(400)
    with open("activation.txt", "w") as f:
        f.write(token)
    return jsonify({"status": "ok", "token": token})

@app.route("/admin/clear", methods=["POST"])
def admin_clear():
    key = request.headers.get("X-Admin-Key")
    if key != os.environ.get("APP_SECRET", "mySecret123"):
        return abort(401)
    try:
        os.remove("activation.txt")
    except FileNotFoundError:
        pass
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
