# Project 1

Web Programming with Python and JavaScript

# Setup
This project runs on Flask, SQLAlchemy, Bootstrap and uses Python, HTML and Jinja.
This project is built on Flask. Remember to set the following before running ` flask run `
```bash
export FLASK_APP=application.py
export DATABASE_URL="link to database"
export FLASK_DEBUG=1 # optional
```

You would also have to run `pip3 install -r requirements.txt` if not already done so/facing import errors.

---

# So basically, the project is titled The Books Project (TBP).
## Homepage
At the homepage, a user is redirected to login if there is no session logged in data.

## Register
There is also a register page.  
The register page will hash the password created and store it in the database.  
Currently, the register function doesn't really care for min/max len and complexity of passwords.  
It is also not using any OAuth frameworks/libraries.  

## Login
At the login page, the password entered will be hashed, and then checked against the stored hash password in the database.
If credentials matches, the person will be logged in, and the @login_required decorator will be true.
The login and register is built by referencing how it works in CS50x Web.

## Index / Search page / Book Search Nook Lurch 5000
Now, the user will be redirected to the book search page, where the user can search by ISBN, author or book title, or a combination of the 3.
The LIKE %query% will be sent to the DB where all matches are returned. 
The query is powerful enough to return "A Christmas Carol" if query terms were merely "Carol" or to return books by "Charles Dickens" if the query was merely "dick".
Initially, the queries needed to be exact such that to query for works by "Philip K Dick", you had to search for "Philip K. Dick", however, now you can ommit the punctuation points.
Currently, the order of words matter such that if you queried "a carol", "A Christmas Carol" would probably not be returned.
The results page shows the query results, rendered in the HTML through Jinja, and has a "More Information" link.
### Note: Although the placeholder data is for the book "Do Androids Dream of Electric Sheep?", that book is actually not in the database, so it would not return that query. It just so happened to be the exact book I was reading so I used it as placeholder. Other works of Philip K. Dick can also be found.

## More Infomration / book/isbn
When the link is clicked, you get redirected to a page with the book's ISBN.
The page sends a POST request to GoodReads API to display certain data on top of the data we already have in our local database on the book.
It will also display reviews submitted by users of TBP.
If the current user has already submitted a review previously, he would be disabled from submittin another one. (Exception is the user by the username 'user' which was used to do some test data -- the data is not erased just to show that it works as per intended, but the data can be easily removed.)
Else, the user can choose to submit a review with 3 fields:
1. Review Title
2. Rating (selector from 1-5)
3. Review itself
Once submitted, you would be redirected to a submitted page just for sanity check, with a back button I believe.

## API/isbn
There's an API where if you send a POST request to the link 'api/<isbn>', you'll receive a JSON data of whatever I needed to include as part of the project requirement.

---

## Database
These are the tables that I have created in the DB:

### books table
```sql
CREATE TABLE IF NOT EXISTS books (isbn TEXT PRIMARY KEY NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL, year NUMERIC);
```

### users table
```sql
CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT NO NULL, hash TEXT NOT NULL);
```

### reviews table
```sql
CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, uid INTEGER REFERENCES users (id), risbn TEXT REFERENCES books (isbn), rTitle TEXT, rRating INTEGER, review TEXT);
```
