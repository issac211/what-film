from flask import Flask, request, render_template, redirect, url_for
import requests
import os

app = Flask(__name__)
my_omdb_key = os.getenv('MY_API_KEY')

@app.route("/")
def home():
    return render_template("index.html", not_found=False)

@app.route("/n")
def film_not_found():
    return render_template("index.html", not_found=True)

@app.route("/<film_name>")
def film_details(film_name):
    resp = requests.get(f"http://www.omdbapi.com/?i={my_omdb_key}&t={film_name}&plot=full")
    resp_json = resp.json()
    return render_template("film-page.html", film_info=resp_json)

@app.route("/search/")
def search():
    title_search = request.args.get("film-title")
    if title_search == "":
        return redirect(url_for("film_not_found"))
    resp = requests.get(f"http://www.omdbapi.com/?i={my_omdb_key}&s={title_search}")
    resp_json = resp.json()
    if resp_json['Response'] == 'True':
        results_num = resp_json['totalResults']
        search_page = resp_json['Search']
        return render_template("search.html", page_info=enumerate(search_page), results_num=results_num)
    else:
        return redirect(url_for("film_not_found"))


if __name__ == "__main__":
    app.run(debug=True)