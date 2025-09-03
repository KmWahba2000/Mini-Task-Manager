from flask import Flask, request, jsonify
import psycopg2
import os, time

app = Flask(__name__)

# Environment variables
db_host = os.getenv("POSTGRES_HOST", "db")
db_name = os.getenv("POSTGRES_DB", "tasksdb")
db_user = os.getenv("POSTGRES_USER", "postgres")
db_pass = os.getenv("POSTGRES_PASSWORD", "postgres")

# Function to get a new connection
def get_connection():
    return psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_pass
    )

# Ensure tasks table exists
for i in range(10):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL
                );
                """)
            conn.commit()
        break
    except Exception as e:
        print("DB not ready:", e)
        time.sleep(3)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Mini Task Manager API is running 🚀", "endpoints": ["/tasks"]})

@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM tasks;")
                rows = cur.fetchall()
                tasks = [{"id": r[0], "title": r[1]} for r in rows]
                return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    title = data.get("title")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id;", (title,))
                new_id = cur.fetchone()[0]
                conn.commit()
                return jsonify({"id": new_id, "title": title}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id=%s RETURNING id;", (task_id,))
                deleted = cur.fetchone()
                conn.commit()

                if deleted:
                    return jsonify({"message": f"Task {task_id} deleted"})
                else:
                    return jsonify({"error": f"Task {task_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
