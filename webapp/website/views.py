from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from . import db
from .models import Rating, Movie, User
from .rec_algorithm import *

views = Blueprint('views', __name__)
@views.route("/")
@login_required
def home():
    return render_template("home.html", user = current_user)

"""
Rating page will also be used to cold-start users when needed. Users need to be
able to post a rating about a movie as well.
"""
@views.route("/rating", methods = ['GET', 'POST'])
@login_required
def rating_page():
    if(request.method == 'POST'):
        """ Assume that the user passes in a valid movie_id """
        movie_id = int(request.form.get('movie_id'))
        rating = int(request.form.get('rating'))
        
        if(rating < 1 or rating > 5):
            flash("Please rate the movie in between 1 and 5 inclusive", category="error")
        new_rating = Rating(movie_id = movie_id, user_id = current_user.id, rating = rating)
        
        current_user.cold_start = True
        
        #This should update cold_start state just in case the line above does not
        current_user_model = db.session.get(User, current_user.id)
        current_user_model.cold_start = True

        db.session.add(new_rating)
        db.session.commit()

        alter_matrix_data_mem(user_id=current_user.id, medium_id=movie_id, rating=rating)
        return redirect(url_for("views.home"))
    return render_template("rating.html", user = current_user)

@views.route("/recommendation", methods = ['GET', 'POST'])
def recommendation_page():
    prediction_list = []
    generated = False
    if(request.method == 'POST'):
        """ First we validate that it is an API call to our recommendation system """
        prediction_list = return_prediction_list(userId=current_user.id, k = 3, elements_to_return=5)
        generated = True
        for index, movie in enumerate(prediction_list):
            prediction_list[index] = db.session.get(Movie, movie).movie_name
    return render_template("recommendation.html", prediction_list=prediction_list, user = current_user, generated = generated)