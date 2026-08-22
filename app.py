import os
from flask import Flask
import psycopg2

app = Flask(__name__)

@app.route("/")
def home():
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM students;")
    students = cur.fetchall()

    cur.close()
    conn.close()

    return str(students)

@app.route("/health")
def health():
    return "OK", 200

app.run(host="0.0.0.0", port=5000)
