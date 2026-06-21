from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# -------------------------
# MongoDB SAFE CONNECTION
# -------------------------
MONGO_URI = "mongodb+srv://realview_user:Realview12345@cluster0.zh0qpbq.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["realview"]
jobs_collection = db["jobs"]

# -------------------------
# HOME PAGE
# -------------------------
@app.route("/")
def home():
    try:
        jobs = list(jobs_collection.find())
    except:
        jobs = []
    return render_template("index.html", jobs=jobs)

# -------------------------
# POST JOB
# -------------------------
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

# -------------------------
# SEARCH API
# -------------------------
@app.route("/search")
def search():
    q = request.args.get("q", "")

    results = list(jobs_collection.find({
        "title": {"$regex": q, "$options": "i"}
    }))

    for r in results:
        r["_id"] = str(r["_id"])

    return jsonify(results)

# -------------------------
# TEST ROUTE (FOR DEBUG)
# -------------------------
@app.route("/test")
def test():
    return "RealView server is working 🚀"

# -------------------------
# RUN APP (LOCAL ONLY)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)