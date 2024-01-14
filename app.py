from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session
from database import getDatabase
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import requests, sqlite3, os, json, random

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.urandom(24)

questions_file_path = os.path.join(os.path.dirname(__file__), "questions.json")
with open(questions_file_path, "r") as json_file:
    questions_data = json.load(json_file)

questions = questions_data.get("questions", [])

def get_date_str(offset):
    date = datetime.now() + timedelta(days=offset)
    return date.strftime('%A')

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, "quizapp_db"):
        g.quizapp_db.close()

def get_current_user():
    user_result = None
    if "user" in session:
        user = session["user"]
        db = getDatabase()
        user_cursor = db.execute("SELECT * FROM users WHERE name = ?", [user])
        user_result = user_cursor.fetchone()
    return user_result

@app.route("/")
def index():
    user = get_current_user()
    return render_template("home.html", today_day=get_date_str(0), tomorrow_day=get_date_str(1), day_after_tomorrow_day=get_date_str(2), user=user)

@app.route("/login", methods=["POST", "GET"])
def login():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = getDatabase()
        name = request.form["name"]
        password = request.form["password"]
        fetchedperson_cursor = db.execute("SELECT * FROM users WHERE name = ?", [name])
        personfromdatabase = fetchedperson_cursor.fetchone()
        if personfromdatabase:
            if check_password_hash(personfromdatabase["password"], password):
                session["user"] = personfromdatabase["name"]
                return redirect(url_for("index"))
            else:
                error = "Username or password did not match. Try again."
                # return render_template("login.html", error=error)
        else:
            error = "Username or password did not match. Try again."
            # return redirect(url_for("login"))
    return render_template("login.html", user=user, error=error)

@app.route("/register", methods=["POST", "GET"])
def register():
    error = None
    success_message = None
    if request.method == "POST":
        db = getDatabase()
        name = request.form["name"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        user_fetching_cursor = db.execute("SELECT * FROM users WHERE name = ?", [name])
        existing_user = user_fetching_cursor.fetchone()

        if existing_user:
            error = "Username already taken, please choose a different username"
        elif password != confirm_password:
            error = "Password and confirmation password do not match"
        else:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            db.execute("insert into users (name, password, teacher, admin) values (?,?,?,?)", [name, hashed_password, "0", "0"])
            db.commit()
            success_message = "Registration successful! You can now log in."

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        db.execute("insert into users (name, password, teacher, admin) values (?,?,?,?)", [name, hashed_password, "0", "0"])
        db.commit()
        # return redirect(url_for("register"))
    return render_template("register.html", error=error, success_message=success_message)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/kuis")
def kuis():
    user = get_current_user()
    random_question = random.choice(questions)

    # Fetch user's score from the database
    db = getDatabase()
    user_id = user["id"]
    user_score_cursor = db.execute(
        "SELECT COUNT(id) AS score FROM answer_history WHERE user_id = ? AND is_correct = True",
        [user_id]
    )
    user_score = user_score_cursor.fetchone()["score"]
    return render_template("kuis.html", user=user, question=random_question, user_score=user_score)

@app.route("/leaderboard")
def leaderboard():
    db = getDatabase()
    user = get_current_user()
    leaderboard_data = db.execute(
        '''SELECT users.name, COUNT(answer_history.id) AS score
        FROM users JOIN answer_history
        ON users.id == answer_history.user_id
        WHERE answer_history.is_correct = True
        GROUP BY users.id
        ORDER BY score DESC'''
    ).fetchall()
    return render_template("leaderboard.html", user=user, leaderboard_data = leaderboard_data)

@app.route("/get_weather", methods=["POST"])
def get_weather():
    try:
        data = request.get_json()
        city_name = data.get('city')

        if not city_name:
            raise ValueError("City name is missing in the request")

        WEATHER_API_KEY = "95946d1d50304a9db6e22237241301"
        response = requests.get(f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city_name}&days=3")

        if response.status_code == 200:
            weather_data = response.json()
            return jsonify(weather_data)
        else:
            return jsonify({
                "error": "Failed to fetch weather data"
            })
    except Exception as e:
        return jsonify({"error":str(e)})

@app.route("/quiz_result", methods=["POST"])
def quiz_result():
    try:
        data = request.get_json()
        selected_option = data.get("selected_option")
        is_correct = data.get("is_correct")

        user = get_current_user()
        user_id = user["id"]

        db = getDatabase()
        db.execute("INSERT INTO answer_history (user_id, selected_option, is_correct) VALUES (?, ?, ?)", [user_id, selected_option, is_correct])
        db.commit()
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"error": str(e)})

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), "quizapp.db")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                       id integer primary key autoincrement,
                       name text not null,
                       password text not null,
                       teacher boolean not null,
                       admin boolean not null);
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answer_history (
                       id integer primary key autoincrement,
                       user_id integer not null,
                       timestamp timestamp default current_timestamp,
                       selected_option text not null,
                       is_correct boolean not null,
                       foreign key (user_id) references users(id));
            ''')
if __name__ == "__main__":
    init_db()
    app.run(debug=True)