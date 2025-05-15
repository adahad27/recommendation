from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from os import path
from flask_login import LoginManager
import pandas as pd

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abcdefg'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix = "/")
    app.register_blueprint(auth, url_prefix = "/")
    
    from .models import User
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    if(not path.exists(f"webapp/instance/{DB_NAME}")):
        with app.app_context():
            from .models import Rating, Movie
            db.create_all()
            movies_metadata_df = pd.read_csv("data/movie_supplementary_data/movies.csv")
            ratings = pd.read_csv("data/movie_ratings.csv")
            for index, movie in movies_metadata_df.iterrows():
                new_movie = Movie(id = index, movie_name = movie["title"])
                db.session.add(new_movie)
            
            for index, rating_block in ratings.iterrows():
                new_rating = Rating(id=index, movie_id=rating_block['movieId'], user_id=rating_block['userId'], rating=rating_block['rating'])
                db.session.add(new_rating)
            
            db.session.commit()
        print("Created Database!")