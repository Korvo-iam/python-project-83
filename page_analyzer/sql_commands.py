from flask import abort
import psycopg2
import os


DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
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
            cur.execute("SELECT id, name, created_at FROM urls ORDER BY id DESC, created_at DESC")
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
