from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route("/login", methods = ['GET', 'POST'])
def login():
    data = request.form
    return render_template("login.html", text = "Testing")

@auth.route("/logout")
def logout():
    
    return "<p>Logout</p>"

@auth.route("/signup", methods = ['GET', 'POST'])
def signup():
    if(request.method == 'POST'):
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if(len(email) < 4):
            flash('Email must be greater than 3 characters', category='error')
        elif(len(first_name) < 2):
            flash('First name must be greater than 1 character', category='error')
        elif(password1 != password2):
            flash('Passwords do not match', category='error')
        else:
            flash('Account created successfully!', category='success')

    return render_template("sign_up.html")


