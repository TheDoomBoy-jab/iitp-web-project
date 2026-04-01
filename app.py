from flask import Flask, request, jsonify, render_template 
import redis 
import json 
app = Flask(__name__)
db=redis.Redis(host='redis', port=6379, decode_responses=True)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
	tasks = db.lrange("my_tasks", 0, -1)
	return jsonify({"tasks": tasks})
@app.route('/tasks', methods=['POST'])
def add_task():
	data=request.json
	task=data.get("task")
	if task:
		db.rpush("my_tasks", task)
		return jsonify({"message": "Task Added!"}), 201
	return jsonify({"error": "No Task Provided"}), 400
@app.route('/tasks', methods=['DELETE'])
def delete_task():
    data = request.json
    task = data.get("task")
    
    if task:
        # LREM removes the task from the list
        # The '0' means "remove all occurrences of this task"
        removed_count = db.lrem("my_tasks", 0, task)
        
        if removed_count > 0:
            return jsonify({"message": f"Deleted task: {task}"}), 200
        return jsonify({"error": "Task not found"}), 404
        
    return jsonify({"error": "No task provided"}), 400
if __name__=="__main__":
	app.run(host="0.0.0.0", port=5000)
