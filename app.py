from flask import Flask, request, jsonify, render_template 
import redis 
import json
import time 
app = Flask(__name__)
db=redis.Redis(host='redis', port=6379, decode_responses=True)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET', 'POST', 'DELETE'])
def tasks_api():
    if request.method == 'GET':
        # Get all raw strings from Redis
        raw_tasks = db.lrange("my_tasks", 0, -1)
        # Convert strings back into Python dictionaries
        tasks = [json.loads(t) for t in raw_tasks]
        return jsonify({"tasks": tasks})

    if request.method == 'POST':
        data = request.get_json()
        task_text = data.get("task")
        if task_text:
            # Create a structured "Task Object"
            task_obj = {
                "id": int(time.time()),      # Unique ID using timestamp
                "content": task_text,
                "status": "pending",         # Default status
                "created_at": time.ctime()   # Human readable time
            }
            # Save as a JSON string
            db.rpush("my_tasks", json.dumps(task_obj))
            return jsonify(task_obj), 201
        return jsonify({"error": "No task"}), 400

    if request.method == 'DELETE':
        # Deleting becomes trickier now because the strings must match exactly.
        # For now, we'll keep it simple, but usually, we'd delete by 'id'.
        data = request.get_json()
        task_to_delete = data.get("task") 
        # (Logic for finding the specific JSON string goes here)
        return jsonify({"message": "Delete logic needs ID update"}), 200 
        
if __name__=="__main__":
	app.run(host="0.0.0.0", port=5000)
