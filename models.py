from datetime import datetime
from db import db


# USER TABLE
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reports = db.relationship('Report', backref='user', lazy=True)


# REPORT TABLE
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    report_id = db.Column(db.String(50))
    summary = db.Column(db.Text)
    severity = db.Column(db.String(50))

    full_data = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)