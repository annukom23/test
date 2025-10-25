from flask import Flask, request, jsonify, abort
import os, json, datetime

app = Flask(__name__)

DATAFILE = "users.json"
APP_SECRET = os.environ.get("APP_SECRET", "myStrongSecret123")

# Initialize user database
if not os.path.exists(DATAFILE):
    with open(DATAFILE, "w") as f:
        json.dump({}, f)

@app.route("/")
def home():
    return "✅ Bot License Server is running!"

# 🧠 Step 1: Bot checks authorization
@app.route("/status/<mac>", methods=["GET"])
def check_user(mac):
    with open(DATAFILE, "r") as f:
        data = json.load(f)

    user = data.get(mac)
    if not user:
        return jsonify({"status": "❌ Not Approved"}), 403

    expiry = datetime.datetime.strptime(user["expiry"], "%Y-%m-%d")
    if datetime.datetime.now() > expiry:
        return jsonify({"status": "❌ License Expired"}), 403

    return jsonify({"status": "✅ Valid", "expiry": user["expiry"]}), 200


# 🧑‍💻 Step 2: Admin approves a MAC
@app.route("/admin/approve", methods=["POST"])
def approve_user():
    key = request.headers.get("X-Admin-Key")
    if key != APP_SECRET:
        return abort(401)

    j = request.get_json(force=True)
    mac = j.get("mac")
    days = int(j.get("days", 7))  # default 7 days validity

    if not mac:
        return abort(400, "Missing MAC address")

    expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

    with open(DATAFILE, "r") as f:
        data = json.load(f)

    data[mac] = {"expiry": expiry}

    with open(DATAFILE, "w") as f:
        json.dump(data, f, indent=2)

    return jsonify({"status": "approved", "mac": mac, "expiry": expiry})


# ❌ Step 3: Admin revoke access
@app.route("/admin/revoke", methods=["POST"])
def revoke_user():
    key = request.headers.get("X-Admin-Key")
    if key != APP_SECRET:
        return abort(401)

    j = request.get_json(force=True)
    mac = j.get("mac")
    if not mac:
        return abort(400, "Missing MAC address")

    with open(DATAFILE, "r") as f:
        data = json.load(f)

    if mac in data:
        del data[mac]
        with open(DATAFILE, "w") as f:
            json.dump(data, f, indent=2)
        return jsonify({"status": "revoked", "mac": mac})
    return jsonify({"status": "not_found", "mac": mac})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
