from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

with open('templates/config.json', 'r') as c:
    params = json.load(c)['params']

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# adding configuration for using a mysql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/codingthunder'

# Creating an SQLAlchemy instance
db = SQLAlchemy(app)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    img_file = db.Column(db.String(12), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(80), nullable=False)
    phone_num = db.Column(db.String(21), nullable=False)
    msg = db.Column(db.Text(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    email = db.Column(db.Text(50), nullable=False)


@app.route("/about")
def about():
    return render_template("about.html", params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/logout")
def logout():
    if 'user' in session and session['user'] == params['admin_user']:
        session.pop('user')
        return redirect('/dashboard')
    else:
        return redirect('/dashboard')


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('username')
        userpass = request.form.get('password')
        if username == params['admin_user'] and userpass == params['admin_password']:
            # set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)

    return render_template('signin.html', params=params)


@app.route("/")
def index():
    # posts = Posts.query.filter_by().limit(params['no_of_posts']).all()

    posts = Posts.query.filter_by().all()

    # get the page number from the query string or default to 1
    page = int(request.args.get('page', 1))

    # set the number of posts per page
    per_page = params['no_of_posts']

    # calculate the start and end index of the posts to display
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    # get the previous and next page links
    prev = url_for('index', page=page - 1) if page > 1 else None
    next = url_for('index', page=page + 1) if end_index < len(posts) else None

    # get the posts to display on the current page
    current_posts = posts[start_index:end_index]

    # render the template with the posts and pagination links
    return render_template('index.html', posts=current_posts, prev=prev, next=next, params=params)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        # adding entry to the database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, phone_num=phone, msg=message, email=email, date=datetime.now())
        db.session.add(entry)
        db.session.commit()

    return render_template("contact.html", params=params)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                post = Posts(title=title, slug=slug, content=content, tagline=tagline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.slug = slug
                post.content = content
                post.tagline = tagline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)


app.run(debug=True)
