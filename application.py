import os
import requests
import string
import re
import json

from flask import Flask, flash, jsonify, render_template, session, g, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from utils import login_required 

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set up API_KEY
API_KEY = "RWcKnUzbhqbexHH9B6KrUg"
if not API_KEY:
    raise RuntimeError("API_KEY not set")



@app.route("/")
@login_required
def index():
    """ Returns search page if logged in """
    
    return render_template("book.html")

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": "9781632168146"})
    return res.json()



@app.route("/register", methods=['GET', 'POST'])
def register():
    """ Register account """
    if request.method == "POST":

        if not request.form.get("username"):
            return "Please submit a proper username."
        elif not request.form.get("password"):
            return "Please enter a password."
        elif not request.form.get("confirmation"):
            return "Please confirm your password."
        elif request.form.get("password") != request.form.get("confirmation"):
            return "Your passwords must match."
        
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username=:username;", {"username":username})
        # return str(rows.fetchall())
        if rows.fetchone() != None:
            return "Username already exists!<br>Please choose another!"
        else:
            password = request.form.get("password")
            passwordHash = generate_password_hash(password)
            db.execute("INSERT INTO users(username, hash) VALUES(:username, :password);", {"username":username, "password":passwordHash})
            db.commit()

        return redirect("/")
    else:
        return render_template("register.html")



@app.route("/login", methods=['GET', 'POST'])
def login():
    """ Log in """
    if request.method == 'POST':
        
        if not request.form.get("username"):
            return "Enter a username!"
        elif not request.form.get("password"):
            return "Please enter a password!"
        rows = db.execute("SELECT * FROM users WHERE username=:username;", {"username":request.form.get("username")}).fetchone()
        if rows == None or not check_password_hash(rows[2], request.form.get("password")):
            return "Enter a valid password!"

        session["username"] = request.form.get("username")
        
        return redirect("/")
    
    else: 
        return render_template("login.html")



@app.route("/logout")
def logout():
    """ Log out """
    session.clear()
    return redirect("/")



@app.route("/book", methods=['GET', 'POST'])
@login_required
def booksearch():
    """ Search Function """
    if request.method == "POST":
        if not request.form.get("isbn") and not request.form.get("title") and not request.form.get("author"):
            message = "bad search"
            return render_template("error.html", message=message)

        query = "SELECT * FROM books WHERE "
        isbnBool = False
        titleBool = False

        if request.form.get("isbn"):
            query += "isbn LIKE '%" + request.form.get("isbn") + "%'"
            isbnBool = True
        if request.form.get("title"):
            if isbnBool:
                query += " OR LOWER(title) LIKE LOWER('%" + formatS(request.form.get("title")) + "%')"
                titleBool = True
            else:
                query += "LOWER(title) LIKE LOWER('%" + formatS(request.form.get("title")) + "%')"
        if request.form.get("author"):
            if titleBool or isbnBool:
                query += " OR LOWER(author) LIKE LOWER('%" + formatS(request.form.get("author")) + "%')"
            else:
                query += "LOWER(author) LIKE LOWER('%" + formatS(request.form.get("author")) + "%')"
        query += ";"
        # return query
        rows = db.execute(query).fetchall()
        return render_template("results.html", rows=rows)
        return redirect(url_for('search', isbn=request.form.get("isbn"), title=request.form.get("title"), author=request.form.get("author"), **request.args))
    else:
        return render_template("book.html")



@app.route("/book/<isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    if request.method == "GET":
        """ Returns book information """
        query = db.execute("SELECT * FROM books WHERE isbn='" + isbn + "';").fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": isbn})
        res = res.json()["books"][0]
        rtitle = " "
        review= " "

        reviews = (db.execute("SELECT reviews.id, uid, username, risbn, rtitle, rrating, review FROM reviews JOIN users ON reviews.uid=users.id WHERE risbn='" + isbn + "';").fetchall())

        submittedBefore = False
        for x in reviews:
            if x[2] == session['username']:
                submittedBefore = True
       
        return render_template("isbn.html", res=res, query=query, rtitle=rtitle, review=review, reviews=reviews, submittedBefore=submittedBefore)
        # return (res)
        return str(res["books"][0]["id"])

    else:
        query = db.execute("SELECT * FROM books WHERE isbn='" + isbn + "';").fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": isbn})
        res = res.json()["books"][0]
        uid = db.execute("SELECT id FROM users WHERE username=:username", {"username":session['username']}).fetchone()[0]
        rtitle = str(request.form.get("reviewTitle"))
        rating = int(request.form.get("rating"))
        review = str(request.form.get("review"))

        if rtitle == "" or review == "":
            return render_template("isbn.html", res=res, query=query, rtitle=rtitle, review=review)
        else:
            #return render_template("isbn.html", res=res, query=query, rtitle=rtitle, review=review)
            test = str(request.form.get("reviewTitle")) + " has been awarded a rating of " + str(request.form.get("rating")) + " with the review of: <br>" + str(request.form.get("review"))
            db.execute("INSERT INTO reviews(uid, risbn, rtitle, rrating, review) VALUES(:uid, :risbn, :rtitle, :rrating, :review)", {"uid": uid, "risbn":query[0], "rtitle":rtitle, "rrating":rating, "review":review})
            db.commit()
            return redirect("/submitted")
        # return test

        """ Sample Data
        {
        "books": [
            {
            "average_rating": "4.02", 
            "id": 14817, 
            "isbn": "057507681X", 
            "isbn13": "9780575076815", 
            "ratings_count": 70123, 
            "reviews_count": 137566, 
            "text_reviews_count": 1908, 
            "work_ratings_count": 81214, 
            "work_reviews_count": 161365, 
            "work_text_reviews_count": 2897
            }
        ]  
        }
        """



@app.route("/submitted")
@login_required
def submitted():
    return render_template("submitted.html")



@app.route("/api/<isbn>", methods=["GET"])
@login_required
def api(isbn):
    """ Returns a json of data """
    query = "SELECT books.title, books.author, books.year, books.isbn, COUNT(*) AS review_count, ROUND(AVG((rrating)), 5) AS average_score FROM reviews JOIN users ON reviews.uid=users.id JOIN books ON reviews.risbn=books.isbn WHERE risbn='" + isbn + "' GROUP BY books.title, books.author, books.year, books.isbn;"
    results = (db.execute(query)).fetchone()

    if not results:
        return "<h1>404: ISBN Not Found</h1>"

    x = {
        "title": results[0],
        "author": results[1],
        "year": str(results[2]),
        "isbn": results[3],
        "review_count": results[4],
        "average_score": str(results[5])
    }

    return json.dumps(x)



def formatS(unfString):
    fString = unfString.replace(" ", "%")
    return fString