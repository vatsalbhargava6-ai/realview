from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
import os
import traceback

app = Flask(__name__)
app.secret_key = "realview_secret"

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- DATABASE ----------------
MONGO_URI = "mongodb+srv://realview_user:Realview12345@cluster0.zh0qpbq.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client["realview"]

jobs_collection = db["jobs"]
users_collection = db["users"]


# ---------------- USER ----------------
class User(UserMixin):
    def __init__(self, data):
        self.id = str(data["_id"])
        self.name = data.get("name", "")
        self.role = data.get("role", "user")


@login_manager.user_loader
def load_user(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(user)
    except:
        pass
    return None


# ---------------- SAFE ADMIN CHECK ----------------
def is_admin():
    try:
        if not current_user.is_authenticated:
            return False

        if not ObjectId.is_valid(current_user.id):
            return False

        user = users_collection.find_one({"_id": ObjectId(current_user.id)})

        if not user:
            return False

        return user.get("role") == "admin"

    except Exception as e:
        print("is_admin error:", e)
        return False


# ---------------- HOME ----------------
@app.route("/")
def home():
    jobs = list(jobs_collection.find({}).limit(20))
    return render_template("index.html", jobs=jobs)


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        if users_collection.find_one({"username": request.form["username"]}):
            return "Username already exists ❌"

        users_collection.insert_one({
            "name": request.form["name"],
            "username": request.form["username"],
            "password": bcrypt.generate_password_hash(request.form["password"]).decode("utf-8"),
            "role": request.form.get("role", "user"),
            "city": request.form["city"]
        })

        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        user = users_collection.find_one({"username": request.form["username"]})

        if user and bcrypt.check_password_hash(user["password"], request.form["password"]):
            login_user(User(user))
            return redirect("/dashboard")

        return "Invalid credentials ❌"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    my_jobs = list(jobs_collection.find({"owner_id": current_user.id}))
    return render_template("dashboard.html", user=current_user, jobs=my_jobs)


# ---------------- POST JOB ----------------
@app.route("/post", methods=["GET", "POST"])
@login_required
def post_job():
    if request.method == "POST":

        jobs_collection.insert_one({
            "title": request.form["title"],
            "company": request.form["company"],
            "city": request.form["city"],
            "area": request.form["area"],
            "category": request.form["category"],
            "salary": request.form["salary"],
            "phone": request.form["phone"],
            "owner_id": current_user.id
        })

        return redirect("/dashboard")

    return render_template("post_job.html")


# ---------------- EDIT JOB ----------------
@app.route("/edit/<job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):

    try:
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
    except Exception as e:
        return str(e)

    if not job:
        return "Job not found ❌"

    if job.get("owner_id") != current_user.id:
        return "Not allowed ❌"

    if request.method == "POST":

        jobs_collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "title": request.form["title"],
                "company": request.form["company"],
                "city": request.form["city"],
                "area": request.form["area"],
                "category": request.form["category"],
                "salary": request.form["salary"],
                "phone": request.form["phone"]
            }}
        )

        return redirect("/dashboard")

    return render_template("edit_job.html", job=job)


# ---------------- DELETE JOB ----------------
@app.route("/delete/<job_id>")
@login_required
def delete_job(job_id):

    try:
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
    except Exception as e:
        return str(e)

    if not job:
        return "Job not found ❌"

    if job.get("owner_id") != current_user.id:
        return "Not allowed ❌"

    jobs_collection.delete_one({"_id": ObjectId(job_id)})

    return redirect("/dashboard")


# ---------------- ADMIN PANEL (DEBUG MODE) ----------------
@app.route("/admin")
@login_required
def admin_panel():

    try:
        print("ADMIN HIT")

        if not is_admin():
            return "Access Denied ❌"

        users = list(users_collection.find())
        jobs = list(jobs_collection.find())

        print("ADMIN LOADED")

        return render_template("admin.html", users=users, jobs=jobs)

    except Exception:
        print(traceback.format_exc())
        return "<pre>" + traceback.format_exc() + "</pre>"


# ---------------- ADMIN DELETE USER ----------------
@app.route("/admin/delete-user/<user_id>")
@login_required
def admin_delete_user(user_id):

    if not is_admin():
        return "Access Denied ❌"

    users_collection.delete_one({"_id": ObjectId(user_id)})
    return redirect("/admin")


# ---------------- ADMIN DELETE JOB ----------------
@app.route("/admin/delete-job/<job_id>")
@login_required
def admin_delete_job(job_id):

    if not is_admin():
        return "Access Denied ❌"

    jobs_collection.delete_one({"_id": ObjectId(job_id)})
    return redirect("/admin")


# ---------------- SEARCH ----------------
@app.route("/search")
def search():
    q = request.args.get("q", "").strip()

    if not q:
        return jsonify([])

    results = list(jobs_collection.find({
        "title": {"$regex": q, "$options": "i"}
    }))

    for r in results:
        r["_id"] = str(r["_id"])

    return jsonify(results)

# ---------------- EXPLORE ----------------
@app.route("/explore")
@login_required
def explore():
    cities = jobs_collection.distinct("city") or []
    return render_template("explore.html", cities=cities)


# ---------------- CITY JOBS ----------------
@app.route("/jobs/<city>")
@login_required
def city_jobs(city):
    categories = jobs_collection.distinct("category", {"city": city}) or []
    return render_template("categories.html", city=city, categories=categories)


# ---------------- CATEGORY JOBS ----------------
@app.route("/jobs/<city>/<category>")
@login_required
def category_jobs(city, category):
    jobs = list(jobs_collection.find({"city": city, "category": category}))
    return render_template("city_jobs.html", jobs=jobs, city=city, category=category)


# ---------------- TEST ----------------
@app.route("/test")
def test():
    return "RealView is live 🚀"


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)