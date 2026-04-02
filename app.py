from flask import Flask, request, jsonify, render_template
import redis
import json
import time

app = Flask(__name__)

# Connect to Redis (decode_responses=True gives us strings instead of bytes)
db = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET', 'POST', 'DELETE'])
def tasks_api():
    # GET: Fetch all tasks and handle old data safety
    if request.method == 'GET':
        raw_tasks = db.lrange("my_tasks", 0, -1)
        tasks = []
        for t in raw_tasks:
            try:
                tasks.append(json.loads(t))
            except (json.JSONDecodeError, TypeError):
                # Safety for old plain-string data
                tasks.append({"id": int(time.time()), "task": t, "completed": False})
        return jsonify({"tasks": tasks})

    # POST: Create a new task object
    if request.method == 'POST':
        data = request.get_json()
        task_text = data.get("task")
        if task_text:
            new_task = {
                "id": int(time.time()), 
                "task": task_text,
                "completed": False
            }
            db.rpush("my_tasks", json.dumps(new_task))
            return jsonify({"message": "Task added!"}), 201
        return jsonify({"error": "No task"}), 400

    # DELETE: Find and remove the task by its text
    if request.method == 'DELETE':
        data = request.get_json()
        task_to_delete = data.get("task")
        all_raw = db.lrange("my_tasks", 0, -1)
        for raw in all_raw:
            try:
                if json.loads(raw).get("task") == task_to_delete:
                    db.lrem("my_tasks", 1, raw)
            except:
                if raw == task_to_delete:
                    db.lrem("my_tasks", 1, raw)
        return jsonify({"message": "Deleted"}), 200

@app.route('/tasks/toggle', methods=['POST'])
def toggle_task():
    data = request.get_json()
    task_id = data.get("id")
    
    all_raw = db.lrange("my_tasks", 0, -1)
    for i, raw in enumerate(all_raw):
        parsed = json.loads(raw)
        if parsed.get("id") == task_id:
            # Flip the completed status
            parsed["completed"] = not parsed.get("completed", False)
            db.lset("my_tasks", i, json.dumps(parsed))
            return jsonify({"status": "success", "completed": parsed["completed"]})
            
    return jsonify({"error": "Task not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
