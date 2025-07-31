from flask import abort
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    print(DATABASE_URL)
    return psycopg2.connect(DATABASE_URL)

def check_if_in_db(url):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
            row = cur.fetchone()
            if row:
                return row[0]
            return None

def add_in_db(url):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url,))
            new_id = cur.fetchone()[0]
        conn.commit()
    return new_id

def return_urls():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    urls.id,
                    urls.name,
                    uc.created_at::date AS last_check_date,
                    uc.status_code
                FROM urls
                LEFT JOIN (
                    SELECT DISTINCT ON (url_id) id, url_id, status_code, created_at
                    FROM url_checks
                    ORDER BY url_id, created_at DESC
                ) AS uc ON urls.id = uc.url_id
                ORDER BY urls.id DESC
            """)
            urls = cur.fetchall()
            return urls

def return_url_checks(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at::date FROM urls WHERE id = %s;", (id,))
            row = cur.fetchone()
            if row is None:
                abort(404)
            url = {
            'id': row[0],
            'name': row[1],
            'created_at': row[2]
            }
            cur.execute("""
                SELECT id, status_code, h1, title, description, created_at::date
                FROM url_checks
                WHERE url_id = %s
                ORDER BY created_at DESC, id DESC
            """, (id,))
            checks = cur.fetchall()
            return url, checks

def insert_into_url_checks(id, status_code, h1, title, description):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO url_checks (url_id, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (id, status_code, h1, title, description))
            conn.commit()

def get_url(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM urls WHERE id = %s;", (id,))
            url = cur.fetchone()
            if url:
                return url[0]
            else:
                return None
