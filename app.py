from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://realview_user:Realview12345@cluster0.zh0qpbq.mongodb.net/?retryWrites=true&w=majority")
db = client["realview"]
jobs_collection = db["jobs"]

# Home page
@app.route("/")
def home():
    jobs = list(jobs_collection.find())
    return render_template("index.html", jobs=jobs)

# Post job
@app.route("/post", methods=["GET", "POST"])
def post_job():
    if request.method == "POST":
        jobs_collection.insert_one({
            "title": request.form["title"],
            "company": request.form["company"],
            "salary": request.form["salary"],
            "location": request.form["location"],
            "phone": request.form["phone"]
        })
        return redirect("/")

    return render_template("post_job.html")

# Search API
@app.route("/search")
def search():
    q = request.args.get("q", "")

    results = list(jobs_collection.find({
        "title": {"$regex": q, "$options": "i"}
    }))

    for r in results:
        r["_id"] = str(r["_id"])

    return jsonify(results)

# RUN SERVER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)