from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from . import db
from .models import Rating
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
        user_id = int(request.form.get('user_id'))
        rating = int(request.form.get('rating'))

        if(rating < 1 or rating > 5):
            flash("Please rate the movie in between 1 and 5 inclusive", category="error")
        new_rating = Rating(movie_id = movie_id, user_id = user_id, rating = rating)
        db.session.add(new_rating)
        db.session.commit()
        return redirect(url_for("views.home"))
    return render_template("rating.html", user = current_user)

@views.route("/recommendation")
def recommendation_page():
    return