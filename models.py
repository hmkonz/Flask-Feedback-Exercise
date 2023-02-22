from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db=SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """connects to database"""
    db.app=app
    db.init_app(app)
   

class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key = True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user with hashed password, email address, first and last names and return user"""
        hashed=bcrypt.generate_password_hash(pwd)

        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user with username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate (cls, username, pwd):
        """Validate that user exists and their password is correct
        Return user if valid; else return False
        """
        # find first user with 'username' that's in the database 
        user=User.query.filter_by(username=username).first()
        # If there is a user with that name and the hashed input password (pwd) matches the hashed password in the database (user.password), return the user; else return false
        if user and bcrypt.check_password_hash(user.password, pwd):
            # return User instance
            return user
        else:
            return False


class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('users.username'), nullable=False)

