from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

jobs = [
    {"id": 1, "title": "Cook Needed", "company": "Taj Restaurant", "salary": 12000, "location": "Bhopal", "phone": "9999999999"},
    {"id": 2, "title": "Delivery Boy", "company": "Zomato Partner", "salary": 15000, "location": "Indore", "phone": "8888888888"}
]

@app.route("/")
def home():
    return render_template("index.html")

# get jobs
@app.route("/jobs")
def get_jobs():
    return jsonify(jobs)

# add job (POST JOB FORM)
@app.route("/add-job", methods=["POST"])
def add_job():
    data = request.json

    new_job = {
        "id": len(jobs) + 1,
        "title": data["title"],
        "company": data["company"],
        "salary": data["salary"],
        "location": data["location"],
        "phone": data["phone"]
    }

    jobs.append(new_job)
    return jsonify({"message": "Job added", "job": new_job})

# search + near me (simple filter)
@app.route("/search")
def search():
    q = request.args.get("q", "").lower()

    result = [
        j for j in jobs
        if q in j["title"].lower() or q in j["location"].lower()
    ]

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)