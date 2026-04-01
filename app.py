from flask import Flask, request, jsonify 
import redis 
import json 
app = Flask(__name__)
db=redis.Redis(host='redis', port=6379, decode_responses=True)

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
if __name__=="__main__":
	app.run(host="0.0.0.0", port=5000)
