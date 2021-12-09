# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.models import Post
from werkzeug.urls import url_parse
from app.forms import RegistrationForm
from app.forms import PostForm, EditPostForm



@app.route('/editpost/<postid>', methods=['GET', 'POST'])
@login_required
def editpost(postid):
    form = EditPostForm()
    if form.validate_on_submit():
       post = Post.query.get(postid)
       if post:
          authorpost = User.query.get(post.user_id)
          db.session.delete(post)
          db.session.commit()
          posttext = request.form['post']
          editedpost = Post(id=postid, body=posttext, author=authorpost)
          db.session.add(editedpost)
          db.session.commit()
          flash('Your changes have been saved.')
          #return redirect(url_for('showpost', postid=postid))
          return redirect(url_for('index'))
    elif request.method == 'GET':
        post1 = Post.query.get(postid)
        form.post.data = post1.body
    return render_template('editpost.html', title='Edit Post',
                           form=form)


@app.route('/showpost/<postid>')
@login_required
def showpost(postid):
    post = Post.query.get(postid)
    return render_template('post.html', title='Post', post=post)


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = Post.query.all()
    # filter_by(user_id=current_user.id)
    return render_template('index.html', title='Home', posts=posts)


@app.route('/newpost', methods=['GET', 'POST'])
@login_required
def newpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Congratulations, new post added!')
        return redirect(url_for('index'))
    return render_template('newpost.html', title='New post', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


