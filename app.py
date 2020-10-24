from flask import Flask, request, render_template, redirect, url_for, session
import requests
import os
import math


class Film:
    def __init__(self, film_info):
        self.resp = True
        if film_info['Response'] == 'False':
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


app = Flask(__name__)
app.secret_key = os.getenv('MY_API_KEY')
my_omdb_key = os.getenv('MY_API_KEY')



def from_session(title_search):
    pages_num = session["pages_num"]
    search_page = session["search_page"]
    current_page = session["current_page"]

    return render_template(
        "search.html", 
        not_found=True, 
        page_info=enumerate(search_page),
        search_val=title_search,
        current_page=int(current_page),
        pages_num=pages_num,
    )




@app.route("/")
def home():
    session.pop('results_num', None)
    session.pop('search_page', None)
    return render_template("index.html", not_found=False)


@app.route("/<film_name>")
def film_details(film_name):
    resp = requests.get(f"http://www.omdbapi.com/?i={my_omdb_key}&t={film_name}&plot=full")
    film = Film(resp.json())
    return render_template("film-page.html", film=film)


@app.route("/search/")
def search():
    title_search = request.args.get("film-title")
    page = request.args.get("page")

    session["search_val"] = title_search

    if title_search == "":
        if ("search_page" in session) and ("pages_num" in session) and ("current_page" in session):
            return from_session(title_search)
        else:
            return render_template("index.html", not_found=True)

    resp = requests.get(f"http://www.omdbapi.com/?i={my_omdb_key}&s={title_search}&page={page}")
    resp_json = resp.json()

    if (resp_json['Response'] == 'True'):
        results_num = resp_json['totalResults']
        pages_num = math.ceil(int(results_num) / 10)
        search_page = resp_json['Search']

        session["pages_num"] = pages_num
        session["search_page"] = search_page
        session["current_page"] = page

        return render_template("search.html", 
        not_found=False, 
        page_info=enumerate(search_page), 
        search_val=title_search,
        current_page=int(page),
        pages_num=pages_num,
    )

    elif ("search_page" in session) and ("pages_num" in session) and ("current_page" in session):
        return from_session(title_search)
    else:
        return render_template("index.html", not_found=True)



if __name__ == "__main__":
    app.run(debug=True)