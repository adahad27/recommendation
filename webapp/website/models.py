from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    movie_name = db.Column(db.String(1000), unique = True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    ratings = db.relationship('Rating')