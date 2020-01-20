import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
db = conn.cursor()

if (db):
    db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);")
    conn.commit()
    print("Database is good to go.")
else:
    print("Database failure.")
