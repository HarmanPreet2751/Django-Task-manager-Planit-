from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import logging

# Set up logging to help debug issues
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SECRET_KEY"] = "welcome"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True

db = SQLAlchemy(app)
api = Api(app)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    task = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    username = db.Column(db.String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "task": self.task,
            "date": self.date.isoformat() if self.date else None,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "username": self.username
        }

class Task(Resource):
    def get(self, task_id=None):
        try:
            username = request.args.get("username")
            if not username:
                data = request.get_json(silent=True)
                username = data.get("username") if data else None

            if task_id:
                task = db.session.get(TaskModel, task_id)
                if not task:
                    return {"msg": "Task not found"}, 404
                if username and task.username != username:
                    return {"msg": "Access denied"}, 403
                return jsonify(task.to_dict())
            else:
                if username:
                    tasks = TaskModel.query.filter_by(username=username).all()
                else:
                    tasks = TaskModel.query.all()
                return jsonify([task.to_dict() for task in tasks])
        except Exception as e:
            app.logger.error(f"Error in GET: {str(e)}")
            return {"msg": f"Error: {str(e)}"}, 500

    def post(self):
        try:
            app.logger.debug(f"Received POST data: {request.data}")
            data = request.get_json(force=True, silent=True)
            if not data:
                data = request.form.to_dict()
            if not data:
                app.logger.debug(f"Headers: {dict(request.headers)}")
                return {"msg": "No data received. Send JSON or form data."}, 400

            app.logger.debug(f"Processed data: {data}")

            if not data.get("title"):
                return {"msg": "Title is required"}, 400

            task_content = data.get("task", "No description provided")
            date_str = data.get("date")
            if not date_str:
                date_obj = datetime.utcnow().date()
            else:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    try:
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
                    except ValueError:
                        return {"msg": "Invalid date format. Use YYYY-MM-DD or MM/DD/YYYY"}, 400

            task = TaskModel(
                title=data.get("title"),
                task=task_content,
                date=date_obj,
                priority=bool(data.get("priority", False)),
                completed=bool(data.get("completed", False)),
                username=data.get("username", "default_user")
            )

            db.session.add(task)
            db.session.commit()
            return {"msg": "Task added successfully", "task": task.to_dict()}, 201

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error in POST: {str(e)}")
            return {"msg": f"Server error: {str(e)}"}, 500

    def put(self, task_id):
        try:
            data = request.get_json(force=True, silent=True)
            if not data:
                data = request.form.to_dict()

            task = db.session.get(TaskModel, task_id)
            if not task:
                return {"msg": "Task not found"}, 404

            username = data.get("username")
            if username and task.username != username:
                return {"msg": "Access denied"}, 403

            if "title" in data:
                task.title = data["title"]
            if "task" in data:
                task.task = data["task"]
            if "date" in data:
                try:
                    task.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
                except ValueError:
                    try:
                        task.date = datetime.strptime(data["date"], "%m/%d/%Y").date()
                    except ValueError:
                        return {"msg": "Invalid date format"}, 400
            if "priority" in data:
                task.priority = bool(data["priority"])
            if "completed" in data:
                task.completed = bool(data["completed"])

            db.session.commit()
            return {"msg": "Task updated", "task": task.to_dict()}, 200

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error in PUT: {str(e)}")
            return {"msg": f"Error: {str(e)}"}, 500

    def delete(self, task_id):
        try:
            username = request.args.get("username")
            if not username:
                data = request.get_json(silent=True)
                username = data.get("username") if data else None

            task = db.session.get(TaskModel, task_id)
            if not task:
                return {"msg": "Task not found"}, 404

            if username and task.username != username:
                return {"msg": "Access denied"}, 403

            db.session.delete(task)
            db.session.commit()
            return {"msg": "Task deleted"}, 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error in DELETE: {str(e)}")
            return {"msg": f"Error: {str(e)}"}, 500

api.add_resource(Task, "/tasks", "/tasks/<int:task_id>")

@app.route("/debug", methods=["GET"])
def debug():
    return jsonify({
        "status": "API is running",
        "request_headers": dict(request.headers),
        "method": request.method,
        "endpoint": request.endpoint,
    })

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
