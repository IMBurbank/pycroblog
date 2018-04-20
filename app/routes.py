from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Isaac'}
    posts = [
        {
            'author': {'username': 'Quincy Adams'},
            'body': 'Morning in America'
        },
        {
            'author': {'username': 'Anon'},
            'body': 'Sister Jeans FTW!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            login_form.username.data, login_form.remember_me.data))
        return redirect(url_for('index'))
        return render_template('login.html', title='Sign In', form=login_form)
