from flask import Flask, request, jsonify, abort
import os

app = Flask(__name__)
APP_SECRET = os.environ.get("APP_SECRET", "mySecret123")
DATAFILE = "activation.txt"

@app.route("/status")
def status():
    if not os.path.exists(DATAFILE):
        return ("", 404)
    with open(DATAFILE) as f:
        return f.read().strip(), 200

@app.route("/admin/set", methods=["POST"])
def admin_set():
    key = request.headers.get("X-Admin-Key")
    if key != APP_SECRET:
        return abort(401)
    j = request.get_json(force=True)
    token = j.get("token", "").strip()
    if not token:
        return abort(400)
    with open(DATAFILE, "w") as f:
        f.write(token)
    return jsonify({"status": "ok", "token": token})

@app.route("/admin/clear", methods=["POST"])
def admin_clear():
    key = request.headers.get("X-Admin-Key")
    if key != APP_SECRET:
        return abort(401)
    try:
        os.remove(DATAFILE)
    except FileNotFoundError:
        pass
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
