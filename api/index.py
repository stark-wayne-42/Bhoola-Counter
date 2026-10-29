import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Hardcoded password check directly in the code
ADMIN_PASSWORD = "DoomKaPapaTonyMark42"

# Fallback in-memory counter if local/no Vercel credentials set
local_counter = 0

def get_current_count():
    val = os.environ.get("COUNTER_VALUE")
    if val is not None:
        try:
            return int(val)
        except ValueError:
            return 0
    return local_counter

def persist_to_vercel(new_val):
    global local_counter
    local_counter = new_val

    # Read Vercel project credentials from Vercel's runtime
    project_id = os.environ.get("VERCEL_PROJECT_ID")
    token = os.environ.get("VERCEL_TOKEN") # Personal Access Token added to settings
    team_id = os.environ.get("VERCEL_TEAM_ID")

    if not project_id or not token:
        return

    # Update or create the environment variable via Vercel API
    url = f"https://api.vercel.com/v10/projects/{project_id}/env"
    params = {"teamId": team_id} if team_id else {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Attempt to post as production variable
    data = {
        "key": "COUNTER_VALUE",
        "value": str(new_val),
        "type": "plain",
        "target": ["production", "preview", "development"]
    }
    requests.post(url, json=data, headers=headers, params=params)


@app.route("/api/count", methods=["GET"])
def get_count():
    return jsonify({"count": get_current_count()})


@app.route("/api/update", methods=["POST"])
def update_count():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    action = data.get("action", "")

    # Hardcoded string password verification
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized: Incorrect password"}), 401

    current = get_current_count()

    if action == "increment":
        new_val = current + 1
    elif action == "decrement":
        new_val = current - 1
    else:
        return jsonify({"error": "Invalid action"}), 400

    persist_to_vercel(new_val)
    return jsonify({"count": new_val})


if __name__ == "__main__":
    app.run(port=5000)