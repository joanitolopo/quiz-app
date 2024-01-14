import sqlite3
from flask import g
import os

def connect_to_database():
    db_path = os.path.join(os.path.dirname(__file__), "quizapp.db")
    sql = sqlite3.connect(db_path)
    sql.row_factory = sqlite3.Row
    return sql

def getDatabase():
    if not hasattr(g, "quizapp_db"):
        g.quizapp_db = connect_to_database()
    return g.quizapp_db
