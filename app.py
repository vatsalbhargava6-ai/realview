from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)


# -------------------------
# MongoDB CONNECTION
# -------------------------

MONGO_URI = "mongodb+srv://realview_user:Realview12345@cluster0.zh0qpbq.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    serverSelectionTimeoutMS=15000
)

db = client["realview"]
jobs_collection = db["jobs"]


# -------------------------
# HOME PAGE
# -------------------------

@app.route("/")
def home():

    try:
        jobs = list(
            jobs_collection
            .find({}, {"_id": 0})
            .limit(20)
        )

    except Exception as e:
        print(e)
        jobs = []

    return render_template(
        "index.html",
        jobs=jobs
    )


# -------------------------
# POST JOB
# -------------------------

@app.route("/post", methods=["GET", "POST"])
def post_job():

    if request.method == "POST":

        job = {
            "title": request.form["title"],
            "company": request.form["company"],
            "salary": request.form["salary"],
            "location": request.form["location"],
            "phone": request.form["phone"]
        }

        jobs_collection.insert_one(job)

        return redirect("/")


    return render_template("post_job.html")



# -------------------------
# SEARCH
# -------------------------

@app.route("/search")
def search():

    q = request.args.get("q", "")

    results = list(
        jobs_collection.find(
            {
                "title": {
                    "$regex": q,
                    "$options": "i"
                }
            },
            {"_id": 0}
        ).limit(20)
    )


    return jsonify(results)



# -------------------------
# TEST
# -------------------------

@app.route("/test")
def test():
    return "RealView is live 🚀"



# -------------------------
# START
# -------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )