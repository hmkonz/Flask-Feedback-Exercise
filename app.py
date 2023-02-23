from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
from sqlalchemy.exc import IntegrityError
import pdb

app=Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = 'abc123'
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]=False

app.app_context().push()

connect_db(app)
db.create_all()

toolbar=DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods =["GET", "POST"])
def register_user():
    form = RegisterForm()
    # execute the following if request is a POST request AND token is valid 
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        # In case username is already taken, catch the error, send a message to pick another username and then render the register.html form so user can input another username
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('register.html', form=form)

        # add username to session so it will be remembered when login again
        session['username'] = new_user.username
        flash("Welcome! Successfully created your account!", 'success')
        return redirect(f'/users/{username}')

    # For GET request or if token is invalid, render the template again
    return render_template('register.html', form=form)


@app.route('/login', methods =["GET", "POST"])
def login_user():
    """Show login form if GET request, handle login if POST request"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form=LoginForm()
    # execute the following if a POST request AND token is valid 
    if form.validate_on_submit():
        username=form.username.data
        password = form.password.data

        # authenticate will return a user or False
        user=User.authenticate(username, password)

        if user:
            flash(f"Welcome Back {user.username}!", "primary")
            # add username to session when login so it will be remembered
            session['username']=user.username #stay logged in
            return redirect (f'/users/{username}')
            
        else:
            form.username.errors = ["Invalid username/password"]
            return render_template ('login.html', form=form)

    # render template if a GET request
    return render_template("login.html", form=form)


@app.route('/logout')
def logout_user():
    """Logs user out and redirects to homepage"""

    session.pop("username")
    return redirect ('/')


@app.route('/users/<username>')
def show_user(username):   
    """Show a page with info on a specific user. Must be logged in to see this page"""  
   
    if "username" not in session or username != session['username']:
        flash ("You must be logged in to view this page")                          
        return redirect ("/")

    else:
        user=User.query.get_or_404(username)
        form = DeleteForm()

        return render_template('show_user.html', user=user, form=form)
       

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    """Show a form to add feedback if a GET request. Handle form if a POST request. Must be logged in to see this page"""

    if "username" not in session or username != session['username']:
        flash ("You must be logged in to view this page")                          
        return redirect ("/")

   
    form=FeedbackForm()

    # execute the following if a POST request AND token is valid 
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback Created!", 'success')

        return redirect(f"/users/{feedback.username}")

    # else return template if a GET request or if token is invalid
    else:
        return render_template('feedback_form.html', form=form, title="Add")

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Delete a user from the database and redirect to login page"""

    if "username" not in session or username != session['username']:
        flash ("You must be logged in to view this page")                          
        return redirect ("/")

    user = User.query.get(username)

    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    flash("User deleted!", "danger")

    return redirect('/')


@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show a form to edit feedback and process it"""

    if "username" not in session:
        flash ("You must be logged in to view this page")                          
        return redirect ("/")


    feedback=Feedback.query.get_or_404(feedback_id)

    form=FeedbackForm(obj=feedback)
   
    # execute the following if a POST request AND token is valid 
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        flash("Feedback Updated!", 'success')

        return redirect(f"/users/{feedback.username}")

    # else return template if a GET request or if token is invalid
    else:
        return render_template('feedback_form.html', form=form, feedback=feedback, title="Edit")


   
@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Delete a user's specific feedback and redirect to user's page"""

    if "username" not in session:
        flash ("You must be logged in to view this page")                          
        return redirect ("/")


    feedback = Feedback.query.get(feedback_id)
    
    db.session.delete(feedback)
    db.session.commit()
   
    flash("Feedback deleted!", "danger")

    return redirect(f"/users/{feedback.username}")
  




   

   
  

  
        



        








