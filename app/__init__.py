from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Create a Flask application instance
app = Flask(__name__)

# Initialize the SQLAlchemy extension
db = SQLAlchemy(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        # Validate the username and password

        # if validate_user(username, password):
        #     user = User.query.filter_by(username=username).first()
        #     login_user(user)
        #     return redirect(url_for('index'))
        # else:
        #     # Login failed, redirect back to the login page
        #     return redirect(url_for('login'))