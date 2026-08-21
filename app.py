from flask import Flask
import psycopg2

app = Flask(__name__)


@app.route("/")
def home():
    conn = psycopg2.connect(
        host="postgres",
        database="edumind",
        user="edumind",
        password="edumindpass"
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM students;")
    students = cur.fetchall()

    cur.close()
    conn.close()

    return str(students)


app.run(host="0.0.0.0", port=5000)
