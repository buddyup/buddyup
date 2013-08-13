from flask import url_for, redirect, g

from buddyup.app import app
from buddyup.templating import render_template
from buddyup.util import login_required

# Expect behavior: '/' redirects to 


@app.route('/')
def index():
    if g.user is None:
        return render_template('intro.html')
    else:
        return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    return render_template('index.html')