import csv
import os
import StringIO

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Create the table if it does not already exist
db.execute("DROP TABLE books;")
db.execute("CREATE TABLE IF NOT EXISTS books (isbn TEXT PRIMARY KEY NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL, year NUMERIC);")
# db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT NOT NULL, hash TEXT NOT NULL);")

# copy the csv file
# db.execute("\copy books FROM '/books.csv' DELIMITER ',' CSV")
# db.execute("\copy books(isbn,title,author,year) FROM '/books.csv' DELIMITER ',' CSV")

counter = 1
with open('books.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        print("Insert number " + str(counter) + " completed!")
        counter += 1
db.commit()
print("Successfuly imported all records in the CSV!")