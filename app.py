from flask import Flask, request, jsonify, render_template
import redis
import json
import time

app = Flask(__name__)

# Connect to the Redis container using the service name 'redis'
# decode_responses=True ensures we get strings, not bytes
db = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.route('/')
def index():
    # Serves the HTML file from the /templates folder
    return render_template('index.html')

@app.route('/tasks', methods=['GET', 'POST', 'DELETE'])
def tasks_api():
    # --- GET: Fetch and Parse Tasks ---
    if request.method == 'GET':
        raw_tasks = db.lrange("my_tasks", 0, -1)
        tasks = []
        for t in raw_tasks:
            try:
                # Attempt to parse the string as a JSON object
                tasks.append(json.loads(t))
            except (json.JSONDecodeError, TypeError):
                # If it's an old plain string (like "Study"), 
                # convert it to a valid JSON-like dict so it doesn't crash
                tasks.append({"id": 0, "task": t})
        return jsonify({"tasks": tasks})

    # --- POST: Create a New Task with a Unique ID ---
    if request.method == 'POST':
        data = request.get_json()
        task_text = data.get("task")
        if task_text:
            # We store tasks as JSON strings to allow for IDs and metadata
            new_task = {
                "id": int(time.time()), 
                "task": task_text
            }
            db.rpush("my_tasks", json.dumps(new_task))
            return jsonify({"message": "Task added!"}), 201
        return jsonify({"error": "No task text provided"}), 400

    # --- DELETE: Remove a Specific Task ---
    if request.method == 'DELETE':
        data = request.get_json()
        task_to_delete = data.get("task")
        if task_to_delete:
            # In a real app, we'd delete by ID, but for now, 
            # we'll find and remove the exact JSON string match.
            # We fetch all, find the one with the matching text, and remove it.
            all_raw = db.lrange("my_tasks", 0, -1)
            for raw in all_raw:
                try:
                    parsed = json.loads(raw)
                    if parsed.get("task") == task_to_delete:
                        db.lrem("my_tasks", 1, raw)
                except:
                    # Handle old-style plain strings
                    if raw == task_to_delete:
                        db.lrem("my_tasks", 1, raw)
            
            return jsonify({"message": "Task deleted!"}), 200
        return jsonify({"error": "No task specified"}), 400

if __name__ == "__main__":
    # 0.0.0.0 is required for Docker to expose the app to your Mac
    app.run(host="0.0.0.0", port=5000, debug=True)
