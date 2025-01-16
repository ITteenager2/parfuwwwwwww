import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY, username TEXT, last_active DATETIME)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS recommendations
                            (id INTEGER PRIMARY KEY, user_id INTEGER, recommendation TEXT, rating INTEGER, timestamp DATETIME)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS feedback
                            (id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT, timestamp DATETIME)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS support_requests
                            (id INTEGER PRIMARY KEY, user_id INTEGER, request TEXT, timestamp DATETIME)''')
        self.conn.commit()

    def add_user(self, user_id, username):
        self.cur.execute("INSERT OR IGNORE INTO users (id, username, last_active) VALUES (?, ?, ?)",
                         (user_id, username, datetime.now()))
        self.conn.commit()

    def update_user_activity(self, user_id):
        self.cur.execute("UPDATE users SET last_active = ? WHERE id = ?", (datetime.now(), user_id))
        self.conn.commit()

    def add_recommendation(self, user_id, recommendation):
        self.cur.execute("INSERT INTO recommendations (user_id, recommendation, timestamp) VALUES (?, ?, ?)",
                         (user_id, recommendation, datetime.now()))
        self.conn.commit()

    def add_rating(self, user_id, rating):
        self.cur.execute("""
            UPDATE recommendations 
            SET rating = ? 
            WHERE id = (
                SELECT id 
                FROM recommendations 
                WHERE user_id = ? AND rating IS NULL 
                ORDER BY timestamp DESC 
                LIMIT 1
            )
        """, (rating, user_id))
        self.conn.commit()


    def add_feedback(self, user_id, text):
        self.cur.execute("INSERT INTO feedback (user_id, text, timestamp) VALUES (?, ?, ?)",
                         (user_id, text, datetime.now()))
        self.conn.commit()

    def add_support_request(self, user_id, request):
        self.cur.execute("INSERT INTO support_requests (user_id, request, timestamp) VALUES (?, ?, ?)",
                         (user_id, request, datetime.now()))
        self.conn.commit()

    def get_statistics(self):
        total_users = self.cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active_users = self.cur.execute("SELECT COUNT(*) FROM users WHERE last_active >= date('now', '-1 day')").fetchone()[0]
        avg_rating = self.cur.execute("SELECT AVG(rating) FROM recommendations WHERE rating IS NOT NULL").fetchone()[0]
        total_recommendations = self.cur.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
        total_feedback = self.cur.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        total_support_requests = self.cur.execute("SELECT COUNT(*) FROM support_requests").fetchone()[0]
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "avg_rating": avg_rating,
            "total_recommendations": total_recommendations,
            "total_feedback": total_feedback,
            "total_support_requests": total_support_requests
        }

    def get_feedback(self, page, per_page=5):
        offset = (page - 1) * per_page
        self.cur.execute("SELECT text, timestamp FROM feedback ORDER BY timestamp DESC LIMIT ? OFFSET ?", (per_page, offset))
        return self.cur.fetchall()

    def get_total_feedback_pages(self, per_page=5):
        total = self.cur.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        return (total + per_page - 1) // per_page

db = Database("perfume_bot.db")

