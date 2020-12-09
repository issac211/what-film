import math
import os

from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
import requests


app = Flask(__name__)

app.secret_key = os.getenv('MY_API_KEY')
my_omdb_key = os.getenv('MY_API_KEY')

postgre_database_url = os.getenv('DATABASE_URL')

app.config["SQLALCHEMY_DATABASE_URI"] = postgre_database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users._id'), nullable=False),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies._id'), nullable=False),
)


class Movies(db.Model):
    _id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    poster = db.Column(db.String)
    year = db.Column(db.String)
    m_type = db.Column(db.String)
    favor = db.relationship('Users', secondary=favorites, backref=db.backref('favor', lazy='dynamic'))

    def __init__(self, title, poster, m_type, year):
        self.title = title
        self.poster = poster
        self.m_type = m_type
        self.year = year


class Users(db.Model):
    _id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password


class Film:
    def __init__(self, film_info):
        self.resp = True
        if film_info['Response'] == 'False':
            self.type = None
            self.year = None
            self.resp = False
            self.poster = None
            self.rated = None
            self.title = None
            self.imdb_rating = None
            self.imdb_votes = None
            self.released = None
            self.runtime = None
            self.actors = None
            self.plot = None
            self.language = None
            self.awards = None
        else:
            self.type = film_info['Type']
            self.year = film_info['Year']
            self.poster = film_info['Poster']
            self.rated = film_info['Rated']
            self.title = film_info['Title']
            self.imdb_rating = film_info['imdbRating']
            self.imdb_votes = film_info['imdbVotes']
            self.released = film_info['Released']
            self.runtime = film_info['Runtime']
            self.actors = film_info['Actors']
            self.plot = film_info['Plot']
            self.language = film_info['Language']
            self.awards = film_info['Awards']


def check_username_password(username, password, from_log=False):
    MAX_SIZE = 12
    MIN_SIZE = 3
    NOT_ALLOWED = ",:';\/[]()=+*{}"
    is_ok = True
    if MAX_SIZE < len(username) or len(username) < MIN_SIZE:
        if not from_log:
            flash(f"Username must be at least {MIN_SIZE} digits and no more than {MAX_SIZE} digits.", 'log-warning')
        is_ok = False
    if MAX_SIZE < len(password) or len(password) < MIN_SIZE:
        if not from_log:
            flash(f"Password must be at least {MIN_SIZE} digits and no more than {MAX_SIZE} digits.", 'log-warning')
        is_ok = False

    if username in password:
        if not from_log:
            flash("Username must not be inside the password.", 'log-warning')
        is_ok = False
        
    if " " in username or " " in password:
        if not from_log:
            flash("There must be no spaces within the username and password.", 'log-warning')
        is_ok = False

    for dig in NOT_ALLOWED:
        if dig in username or dig in password:
            if not from_log:
                flash(f"The digits: {NOT_ALLOWED} are not allowed in the username or password.", 'log-warning')
            is_ok = False
            break

    return is_ok


def add_user(username, password):
    username = username.strip()
    if check_username_password(username, password):
        found_user = Users.query.filter_by(name=username).first()
        if found_user:
            return False
        user = Users(username, password)
        db.session.add(user)
        db.session.commit()
        session["logged_user"] = {"user_id": user._id, "user_name": user.name}
        return True
    else:
        return None


def get_logged_user():
    if "logged_user" in session:
        logged_user = session["logged_user"]
        found_user = Users.query.filter_by(name=logged_user["user_name"]).first()
        if found_user:
            return found_user
    return False


def get_movie_from_db(movie_title):
    movie = Movies.query.filter_by(title=movie_title).first()
    return movie


def add_movie(film_data):
    movie_title = film_data[0]
    movie = get_movie_from_db(movie_title)
    if movie:
        return False
    movie = Movies(*film_data)
    db.session.add(movie)
    db.session.commit()
    return True


def add_movie_to_user_fav(user, film_data):
    added = add_movie(film_data)
    if added:
        flash("You're the first to find this film!", 'achieve-message')
    movie_title = film_data[0]
    movie = get_movie_from_db(movie_title)
    if movie and (movie not in user.favor):
        user.favor.append(movie)
        db.session.commit()
        return True
    return False


def remove_from_fav(user, film_data):
    movie_title = film_data[0]
    movie = get_movie_from_db(movie_title)
    if movie and movie in user.favor:
        movie_list = [m for m in user.favor if m != movie]
        user.favor = movie_list
        db.session.commit()
        return True
    return False


def from_session(title_search, logged_user):
    pages_num = session["pages_num"]
    search_page = session["search_page"]
    current_page = session["current_page"]
    pre_title_search = session["page_search_val"]

    for d in search_page:
        film = Movies(d['Title'], d['Poster'], d['Type'], d['Year'])
        is_favor = check_if_favor(film, logged_user)
        fav_num = get_users_fav_num(film)
        d['is_favor'] = is_favor
        d['fav_num'] = fav_num

    return render_template(
        "search.j2", 
        page_info=enumerate(search_page),
        search_val=title_search,
        current_page=int(current_page),
        pages_num=pages_num,
        page_search_val=pre_title_search,
        logged_user=logged_user,
    )


def get_page(favorite_movies, page):
    limit_offset = (page * 10) - 10
    movie_list = []
    for i, f in enumerate(favorite_movies, 1):
        if i > limit_offset:
            movie_list.append(f)
    return movie_list


def check_if_favor(film, logged_user):
    is_favor = None
    if logged_user:
        if isinstance(film, Film):
            if film.resp:
                movie = get_movie_from_db(film.title)
                if movie and movie in logged_user.favor:
                    is_favor = True
                else:
                    is_favor = False
        elif isinstance(film, Movies):
            movie = get_movie_from_db(film.title)
            if movie in logged_user.favor:
                is_favor = True
            else:
                is_favor = False
    return is_favor


def get_users_fav_num(film):
    fav_num = 0
    if isinstance(film, Film):
        if film.resp:
            movie = get_movie_from_db(film.title)
            if movie:
                fav_num = len(movie.favor)
    elif isinstance(film, Movies):
        movie = get_movie_from_db(film.title)
        if movie:
            fav_num = len(movie.favor)
    return fav_num


def get_top_movies(num):
    join = db.session.query(Movies, db.func.count(Users._id).label('count_likes')).select_from(favorites).join(Movies).join(Users)
    top_movies = join.group_by(Movies._id).order_by(db.desc('count_likes')).limit(num).all()
    return top_movies


def change_p(logged_user, new_password):
    if check_username_password("user1", new_password):
        logged_user.password = new_password
        db.session.commit()
        return True
    else:
        return False


@app.route("/")
def home():
    logged_user = get_logged_user()
    session.pop('results_num', None)
    session.pop('search_page', None)
    return render_template("index.j2", logged_user=logged_user, active_page="home")


@app.route("/<film_name>/", methods=["POST", "GET"])
def film_details(film_name):
    logged_user = get_logged_user()
    if request.method == "POST":
        film_name = request.form["fav_title"]
        
        if logged_user:
            film_data = []
            film_data.append(film_name)
            film_data.append(request.form["fav_poster"])
            film_data.append(request.form["fav_type"])
            film_data.append(request.form["fav_year"])
            add_rem = request.form["add_rem"]
            
            if add_rem == "add":
                if add_movie_to_user_fav(logged_user, film_data):
                    flash("movie added to your favorites", 'message')
            elif add_rem == "rem":
                if remove_from_fav(logged_user, film_data):
                    flash("Movie deleted from favorites", 'message')
            else:
                flash("Unable to add or remove movie to favorites", 'error')
        else:
            flash("You need to be logged in to do this action", ' warning')
    resp = requests.get(f"http://www.omdbapi.com/?i={my_omdb_key}&t={film_name}&plot=full")
    film = Film(resp.json())

    is_favor = check_if_favor(film, logged_user)

    if not film.resp:
        flash("There is no further details on the film", 'error')

    fav_num = get_users_fav_num(film)

    search_val = session["page_search_val"]
    return render_template(
        "film-page.j2",
        film=film,
        logged_user=logged_user,
        is_favor=is_favor,
        search_val=search_val,
        fav_num=fav_num
    )


@app.route("/search/", methods=["POST", "GET"])
def search():
    logged_user = get_logged_user()

    if request.method == "POST":
        if logged_user:
            film_data = []
            film_data.append(request.form["fav_title"])
            film_data.append(request.form["fav_poster"])
            film_data.append(request.form["fav_type"])
            film_data.append(request.form["fav_year"])
            add_rem = request.form["add_rem"]
            
            if add_rem == "add":
                if add_movie_to_user_fav(logged_user, film_data):
                    flash("movie added to your favorites", 'message')
            elif add_rem == "rem":
                if remove_from_fav(logged_user, film_data):
                    flash("Movie deleted from favorites", 'message')
            else:
                flash("Unable to add or remove movie to favorites", 'error')
        else:
            flash("You need to be logged in to do this action", 'warning')

    title_search = request.args.get("film-title")
    page = request.args.get("page")

    session["search_val"] = title_search

    if title_search == "":
        flash("Try writing the name of the movie you want to search for", 'info')
        if ("search_page" in session) and ("pages_num" in session) and ("current_page" in session):
            return from_session(title_search, logged_user)
        else:
            return redirect(url_for("home"))

    resp = requests.get(f"http://www.omdbapi.com/?i={my_omdb_key}&s={title_search}&page={page}")
    resp_json = resp.json()

    if (resp_json['Response'] == 'True'):
        results_num = resp_json['totalResults']
        pages_num = math.ceil(int(results_num) / 10)
        search_page = resp_json['Search']

        session["pages_num"] = pages_num
        session["search_page"] = search_page
        session["current_page"] = page
        session["page_search_val"] = title_search

        for d in search_page:
            film = Movies(d['Title'], d['Poster'], d['Type'], d['Year'])
            is_favor = check_if_favor(film, logged_user)
            fav_num = get_users_fav_num(film)
            d['is_favor'] = is_favor
            d['fav_num'] = fav_num

        return render_template("search.j2", 
        page_info=enumerate(search_page), 
        search_val=title_search,
        current_page=int(page),
        pages_num=pages_num,
        page_search_val=title_search,
        logged_user=logged_user,
    )

    elif ("search_page" in session) and ("pages_num" in session) and ("current_page" in session):
        flash("The film name doesn't exist in the system", 'info')
        return from_session(title_search, logged_user)
    else:
        flash("The film name doesn't exist in the system", 'info')
        return redirect(url_for("home"))


@app.route("/login/", methods=["POST", "GET"])
def login():
    logged_user = get_logged_user()
    if logged_user:
        return redirect(url_for("log_out"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        username = username.strip()
        if not username or not password:
            flash("username and password need to be entered", 'log-warning')
            return render_template("login.j2", logged_user=logged_user)

        if check_username_password(username, password, from_log=True):
            found_user = Users.query.filter_by(name=username).first()
            if found_user and found_user.password == password:
                session["logged_user"] = {"user_id": found_user._id, "user_name": found_user.name}
                logged_user = get_logged_user()
                flash("Login successfully!!", 'log-message')
                return redirect(url_for("home"))
        flash("Incorrect username or password", 'log-warning')
    return render_template("login.j2", logged_user=logged_user)


@app.route("/log-out/", methods=["POST", "GET"])
def log_out():
    logged_user = get_logged_user()
    if logged_user:
        if request.method == "POST":
            if request.form["log-out"] == "1":
                session.pop("logged_user", None)
                flash("you have logged out", 'log-message')
                return redirect(url_for("home"))
            elif request.form["delete-user"] == "1":
                flash("are you sure you want to delete your user?", 'log-warning')
                return redirect(url_for("delete_user"))
        flash("are you sure you want to log out?", 'log-warning')
    else:
        return redirect(url_for("login"))

    return render_template("log-out.j2", logged_user=logged_user, active_page="log_out")


@app.route("/delete-user/", methods=["POST", "GET"])
def delete_user():
    logged_user = get_logged_user()
    if logged_user:
        if request.method == "POST":
            password = request.form["password_d"]
            password = password.strip()
            if password == logged_user.password:
                flash(f"the user {logged_user.name} has been deleted", 'log-message')
                session.pop("logged_user", None)
                db.session.delete(logged_user)
                db.session.commit()
                return redirect(url_for("home"))
            else:
                flash("Incorrect password", 'log-warning')
        return render_template("delete-user.j2", logged_user=logged_user)
    else:
        return redirect(url_for("home"))


@app.route("/change-password/", methods=["POST", "GET"])
def change_password():
    logged_user = get_logged_user()
    if logged_user:
        if request.method == "POST":
            c_password = request.form["c_password"]
            n_password = request.form["n_password"]
            c_password = c_password.strip()
            n_password = n_password.strip()

            if c_password == logged_user.password:
                changed = change_p(logged_user, n_password)
                if changed:
                    flash("Password changed", 'log-message')
                    return redirect(url_for("home"))
            else:
                flash("Incorrect password", 'log-warning')
        return render_template("change-p.j2", logged_user=logged_user)
    else:
        return redirect(url_for("home"))


@app.route("/register/", methods=["POST", "GET"])
def register():
    logged_user = get_logged_user()
    if logged_user:
        return render_template("index.j2", logged_user=logged_user)
    if request.method == "POST":
        username = request.form["username_r"]
        password = request.form["password_r"]

        added = add_user(username, password)
        if added is None:
            return render_template("register.j2")
        elif added:
            flash(f"Welcome {username}!!", 'log-message')
            found_user = Users.query.filter_by(name=username).first()
            session["logged_user"] = {"user_id": found_user._id, "user_name": found_user.name}
            return redirect(url_for("home"))
        else:
            flash("user name already exists", 'log-warning')
            return render_template("register.j2")
    return render_template("register.j2", logged_user=logged_user)


@app.route("/favorites/")
def my_favorites():
    page = request.args.get("page")
    if page is None:
        page = 1
    else:
        page = int(page)

    logged_user = get_logged_user()
    if logged_user:
        favorite_movies = logged_user.favor
        pages_num = math.ceil(len(favorite_movies.all()) / 10)
        if page > 1:
            movie_list = get_page(favorite_movies.all(), page)
            return render_template(
                "favorites.j2",
                logged_user=logged_user,
                favorite_movies=movie_list,
                pages_num=pages_num,
                current_page=page,
                active_page="favorites",
            )
        return render_template(
            "favorites.j2",
            logged_user=logged_user,
            favorite_movies=favorite_movies,
            pages_num=pages_num,
            current_page=page,
            active_page="favorites",
        )
    return redirect(url_for("home"))


@app.route("/top_movies/")
def top_movies():
    logged_user = get_logged_user()
    movies_likes = get_top_movies(5)
    return render_template(
        "top-movies.j2",
        logged_user=logged_user,
        movies_likes=movies_likes,
        active_page="top_movies",
    )


if __name__ == "__main__":
    db.create_all()
    app.run()