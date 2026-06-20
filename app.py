from flask import Flask, render_template, request, redirect, jsonify
import sqlite3

app = Flask(__name__)

# DB setup
def init_db():
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            salary TEXT,
            location TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Home page (show jobs)
@app.route("/")
def home():
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute("SELECT * FROM jobs ORDER BY id DESC")
    jobs = c.fetchall()
    conn.close()

    return render_template("index.html", jobs=jobs)

# Post job page
@app.route("/post", methods=["GET", "POST"])
def post_job():
    if request.method == "POST":
        title = request.form["title"]
        company = request.form["company"]
        salary = request.form["salary"]
        location = request.form["location"]
        phone = request.form["phone"]

        conn = sqlite3.connect("jobs.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO jobs (title, company, salary, location, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (title, company, salary, location, phone))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("post_job.html")

# API search
@app.route("/search")
def search():
    q = request.args.get("q", "")

    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE title LIKE ? OR location LIKE ?",
              ('%'+q+'%', '%'+q+'%'))
    jobs = c.fetchall()
    conn.close()

    return jsonify(jobs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))