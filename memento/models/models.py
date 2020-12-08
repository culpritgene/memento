from datetime import datetime

import numpy as np
from flask_login import UserMixin

from memento import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False, default=datetime(1990, 1, 1))
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(280), nullable=False, default='static/profile_pics/default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    lifelines = db.relationship('Lifeline', backref='user', uselist=False, lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Lifeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mood = db.Column(db.ARRAY(db.Integer, dimensions=4), nullable=True)
    efficiency = db.Column(db.ARRAY(db.Integer, dimensions=4), nullable=True)
    imagination = db.Column(db.ARRAY(db.Integer, dimensions=4), nullable=True)
    diary = db.Column(db.ARRAY(db.Text, dimensions=4), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"LifeLine('{self.title}', '{self.date_updated}', mood nonzero entries: '{np.array(self.mood).sum()}, diary nonzero entries: '{np.array(self.diary).sum()}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"